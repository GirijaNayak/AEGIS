"""
Load distribution and power allocation engine for AEGIS.
Simplified graph-based network flow solver calculating node loads, line flows,
capacity violations, consumer curtailments, and global grid reliability metrics.
"""

from typing import Dict, List, Set, Tuple
import networkx as nx
from app.models.infrastructure import (
    InfrastructureNetwork,
    OperationalStatus,
    ConsumerCategory,
    CriticalityLevel,
    RiskCategory,
)
from app.models.events import SimulationMetrics


def calculate_load_distribution(network: InfrastructureNetwork) -> SimulationMetrics:
    """
    Executes a deterministic load flow and power allocation on the network.
    Updates component states in-place and returns updated simulation metrics.
    """
    # 1. Build graph of operational components
    G = nx.Graph()

    # Add active power stations
    active_power_stations = {
        ps.id: ps for ps in network.power_stations
        if ps.operational_status == OperationalStatus.OPERATIONAL
    }
    for ps_id, ps in active_power_stations.items():
        G.add_node(ps_id, node_type="power_station", capacity=ps.generation_capacity)

    # Add active backup generators
    active_generators = {
        bg.id: bg for bg in network.backup_generators
        if bg.is_active and bg.operational_status == OperationalStatus.OPERATIONAL
    }
    for bg_id, bg in active_generators.items():
        G.add_node(bg_id, node_type="backup_generator", capacity=bg.capacity)

    # Add substations (unless FAILED)
    operational_substations = {
        sub.id: sub for sub in network.substations
        if sub.operational_status != OperationalStatus.FAILED
    }
    for sub_id, sub in operational_substations.items():
        G.add_node(sub_id, node_type="substation", max_capacity=sub.max_capacity)

    # Reset all transmission line flows to 0
    for line in network.transmission_lines:
        line.current_flow = 0.0

    # Add operational transmission lines to graph
    for line in network.transmission_lines:
        if (
            line.operational_status == OperationalStatus.OPERATIONAL
            and line.source_id in G
            and line.destination_id in G
        ):
            G.add_edge(
                line.source_id,
                line.destination_id,
                id=line.id,
                max_capacity=line.max_capacity,
                weight=line.transfer_cost,
            )

    # 2. Map consumers to substations and compute nominal substation demands
    substation_consumers: Dict[str, List] = {sub.id: [] for sub in network.substations}
    substation_demand: Dict[str, float] = {sub.id: 0.0 for sub in network.substations}

    for consumer in network.consumers:
        if consumer.connected_substation_id in substation_consumers:
            substation_consumers[consumer.connected_substation_id].append(consumer)
            substation_demand[consumer.connected_substation_id] += consumer.demand

    # 3. Determine power supply to each substation
    # Sources include active power stations and active backup generators
    all_sources = list(active_power_stations.keys()) + list(active_generators.keys())
    substation_available_power: Dict[str, float] = {sub.id: 0.0 for sub in network.substations}
    line_flows: Dict[str, float] = {line.id: 0.0 for line in network.transmission_lines}

    # Dispatch power from sources to substations using shortest paths
    for sub_id, dem in substation_demand.items():
        if dem <= 0 or sub_id not in G:
            continue

        needed = dem
        # Try to find routes to available sources, sorted by distance/cost
        source_paths = []
        for src_id in all_sources:
            if src_id in G and nx.has_path(G, src_id, sub_id):
                try:
                    path = nx.shortest_path(G, source=src_id, target=sub_id, weight="weight")
                    cost = nx.shortest_path_length(G, source=src_id, target=sub_id, weight="weight")
                    source_paths.append((cost, src_id, path))
                except nx.NetworkXNoPath:
                    pass

        source_paths.sort(key=lambda x: x[0])

        for cost, src_id, path in source_paths:
            if needed <= 0:
                break
            
            # Determine maximum bottleneck along this path
            path_edge_caps = []
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                edge_data = G[u][v]
                line_id = edge_data["id"]
                rem_cap = max(0.0, edge_data["max_capacity"] - line_flows[line_id])
                path_edge_caps.append((line_id, rem_cap))

            if not path_edge_caps:
                continue

            bottleneck = min(c for _, c in path_edge_caps)
            transfer_amount = min(needed, bottleneck)

            if transfer_amount > 0:
                for line_id, _ in path_edge_caps:
                    line_flows[line_id] += transfer_amount
                substation_available_power[sub_id] += transfer_amount
                needed -= transfer_amount

    # Update line flows in network model and check overloads
    overloaded_lines_count = 0
    for line in network.transmission_lines:
        line.current_flow = round(line_flows.get(line.id, 0.0), 2)
        if line.operational_status == OperationalStatus.FAILED:
            continue
        if line.current_flow > line.max_capacity:
            line.operational_status = OperationalStatus.OVERLOADED
            overloaded_lines_count += 1
        elif line.operational_status == OperationalStatus.OVERLOADED and line.current_flow <= line.max_capacity:
            line.operational_status = OperationalStatus.OPERATIONAL

    # 4. Allocate available power to consumers at each substation by priority
    total_supplied = 0.0
    total_demand = 0.0
    critical_unserved = 0.0
    critical_total_count = 0
    critical_supplied_count = 0

    for sub in network.substations:
        consumers = substation_consumers.get(sub.id, [])
        sorted_consumers = sorted(consumers, key=lambda c: (c.priority, -c.demand))

        if sub.operational_status == OperationalStatus.FAILED:
            sub.current_load = 0.0
            sub.temperature = 105.0
            for cons in sorted_consumers:
                total_demand += cons.demand
                is_critical = cons.category == ConsumerCategory.HOSPITAL or cons.criticality == CriticalityLevel.CRITICAL
                if is_critical:
                    critical_total_count += 1
                    critical_unserved += cons.demand
                cons.supplied_power = 0.0
                cons.operational_status = OperationalStatus.FAILED
            continue

        available = substation_available_power.get(sub.id, 0.0)
        # Cap throughput by substation max capacity
        effective_capacity = min(sub.max_capacity, available)
        sub.current_load = round(effective_capacity, 2)

        # Update substation operating temperature based on load ratio
        load_ratio = sub.current_load / max(1.0, sub.max_capacity)
        sub.temperature = round(40.0 + (load_ratio * 45.0), 1)

        # Update status if overloaded
        if sub.current_load >= sub.max_capacity * 1.05:
            sub.operational_status = OperationalStatus.OVERLOADED
        else:
            sub.operational_status = OperationalStatus.OPERATIONAL

        rem_power = effective_capacity
        for cons in sorted_consumers:
            total_demand += cons.demand
            is_critical = cons.category == ConsumerCategory.HOSPITAL or cons.criticality == CriticalityLevel.CRITICAL
            if is_critical:
                critical_total_count += 1

            if rem_power >= cons.demand:
                cons.supplied_power = round(cons.demand, 2)
                cons.operational_status = OperationalStatus.OPERATIONAL
                rem_power -= cons.demand
                total_supplied += cons.supplied_power
                if is_critical:
                    critical_supplied_count += 1
            elif rem_power > 0.0:
                cons.supplied_power = round(rem_power, 2)
                cons.operational_status = OperationalStatus.DEGRADED
                total_supplied += cons.supplied_power
                rem_unserved = cons.demand - rem_power
                rem_power = 0.0
                if is_critical:
                    critical_unserved += rem_unserved
            else:
                cons.supplied_power = 0.0
                cons.operational_status = OperationalStatus.FAILED
                if is_critical:
                    critical_unserved += cons.demand

    # 5. Calculate generation dispatch and generator utilization
    total_gen_dispatched = 0.0
    for ps in network.power_stations:
        if ps.operational_status == OperationalStatus.OPERATIONAL:
            # Power station supplies connected lines
            station_flow = sum(l.current_flow for l in network.transmission_lines if l.source_id == ps.id)
            ps.current_generation = round(min(ps.generation_capacity, station_flow), 2)
            total_gen_dispatched += ps.current_generation
        else:
            ps.current_generation = 0.0

    for bg in network.backup_generators:
        if bg.is_active and bg.operational_status == OperationalStatus.OPERATIONAL:
            bg_flow = sum(l.current_flow for l in network.transmission_lines if l.source_id == bg.id)
            bg.current_utilization = round(min(bg.capacity, bg_flow), 2)
            total_gen_dispatched += bg.current_utilization
        else:
            bg.current_utilization = 0.0

    # 6. Global system metrics
    total_demand = round(total_demand, 2)
    total_supplied = round(total_supplied, 2)
    unserved_demand = round(max(0.0, total_demand - total_supplied), 2)
    critical_unserved = round(critical_unserved, 2)
    restoration_pct = round((total_supplied / max(1.0, total_demand)) * 100.0, 1)

    total_gen_capacity = sum(ps.generation_capacity for ps in network.power_stations if ps.operational_status == OperationalStatus.OPERATIONAL)
    total_gen_capacity += sum(bg.capacity for bg in network.backup_generators if bg.is_active and bg.operational_status == OperationalStatus.OPERATIONAL)

    operational_count = 0
    failed_count = 0
    for ps in network.power_stations:
        if ps.operational_status == OperationalStatus.OPERATIONAL:
            operational_count += 1
        elif ps.operational_status == OperationalStatus.FAILED:
            failed_count += 1

    for sub in network.substations:
        if sub.operational_status == OperationalStatus.OPERATIONAL:
            operational_count += 1
        elif sub.operational_status == OperationalStatus.FAILED:
            failed_count += 1

    for line in network.transmission_lines:
        if line.operational_status == OperationalStatus.OPERATIONAL:
            operational_count += 1
        elif line.operational_status == OperationalStatus.FAILED:
            failed_count += 1

    for cons in network.consumers:
        if cons.operational_status == OperationalStatus.OPERATIONAL:
            operational_count += 1
        elif cons.operational_status == OperationalStatus.FAILED:
            failed_count += 1

    health_vals = [sub.health_percentage for sub in network.substations] + [ps.health_percentage for ps in network.power_stations]
    avg_health = round(sum(health_vals) / max(1, len(health_vals)), 1)
    
    # Grid reliability index: combination of demand served, critical facilities, and line overloads
    crit_ratio = critical_supplied_count / max(1, critical_total_count)
    dem_ratio = total_supplied / max(1.0, total_demand)
    overload_penalty = max(0.0, 1.0 - (overloaded_lines_count * 0.1))
    reliability_index = round((dem_ratio * 50.0 + crit_ratio * 40.0 + overload_penalty * 10.0), 1)

    return SimulationMetrics(
        total_demand=total_demand,
        total_generation_capacity=round(total_gen_capacity, 2),
        current_generation=round(total_gen_dispatched, 2),
        total_supplied_power=total_supplied,
        unserved_demand=unserved_demand,
        restoration_percentage=restoration_pct,
        critical_facilities_total=critical_total_count,
        critical_facilities_supplied=critical_supplied_count,
        critical_facilities_unserved=critical_total_count - critical_supplied_count,
        critical_unserved_demand=critical_unserved,
        operational_components_count=operational_count,
        failed_components_count=failed_count,
        overloaded_lines_count=overloaded_lines_count,
        grid_reliability_index=reliability_index,
        system_health_average=avg_health,
    )
