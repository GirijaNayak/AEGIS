"""
Independent mathematical and algorithmic audit tests for A* Search.
Verifies strict admissibility (h(n) <= h*(n)), capacity-constrained route feasibility,
and optimality against an independent reference Dijkstra implementation on standard and synthetic graphs.
"""

import math
import heapq
import random
import pytest
import networkx as nx
from app.simulation.default_network import get_default_network
from app.models.recovery import AStarRouteRequest
from app.ai.astar.algorithm import astar_search
from app.ai.astar.heuristic import calculate_euclidean_distance
from app.models.infrastructure import (
    InfrastructureNetwork,
    PowerStation,
    Substation,
    TransmissionLine,
    Position,
    OperationalStatus,
)


def run_reference_dijkstra(network: InfrastructureNetwork, source: str, target: str, req_cap: float, avoid_nodes=None, avoid_edges=None):
    """
    Independent reference Dijkstra implementation for ground-truth shortest path comparison.
    """
    avoid_nodes = set(avoid_nodes or [])
    avoid_edges = set(avoid_edges or [])

    # Filter available nodes
    valid_nodes = set()
    for ps in network.power_stations:
        if ps.operational_status != OperationalStatus.FAILED and ps.id not in avoid_nodes:
            valid_nodes.add(ps.id)
    for sub in network.substations:
        if sub.operational_status != OperationalStatus.FAILED and sub.id not in avoid_nodes:
            valid_nodes.add(sub.id)
    for bg in network.backup_generators:
        if bg.operational_status != OperationalStatus.FAILED and bg.id not in avoid_nodes:
            valid_nodes.add(bg.id)

    if source not in valid_nodes or target not in valid_nodes:
        return None, float("inf")

    # Build adjacency
    adj = {n: [] for n in valid_nodes}
    for line in network.transmission_lines:
        if line.id in avoid_edges or line.operational_status == OperationalStatus.FAILED:
            continue
        rem_cap = max(0.0, line.max_capacity - line.current_flow)
        if rem_cap < req_cap:
            continue
        if line.source_id in valid_nodes and line.destination_id in valid_nodes:
            adj[line.source_id].append((line.destination_id, line.transfer_cost))
            adj[line.destination_id].append((line.source_id, line.transfer_cost))

    dist = {n: float("inf") for n in valid_nodes}
    dist[source] = 0.0
    pq = [(0.0, source)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u == target:
            break
        for v, weight in adj.get(u, []):
            if dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight
                heapq.heappush(pq, (dist[v], v))

    return dist[target] if dist[target] != float("inf") else None, dist[target]


def test_heuristic_strict_admissibility():
    """
    Verifies that for every node pair (u, goal) in the network, h(u) <= h*(u).
    The heuristic must NEVER overestimate the true shortest path cost.
    """
    network = get_default_network()
    goal = "SUB3"

    # Compute node positions
    positions = {}
    for ps in network.power_stations:
        positions[ps.id] = (ps.position.x, ps.position.y)
    for sub in network.substations:
        positions[sub.id] = (sub.position.x, sub.position.y)

    # Find minimum unit cost
    min_unit_cost = 999.0
    for line in network.transmission_lines:
        p1 = positions.get(line.source_id)
        p2 = positions.get(line.destination_id)
        if p1 and p2:
            d = max(1.0, calculate_euclidean_distance(p1, p2))
            min_unit_cost = min(min_unit_cost, line.transfer_cost / d)

    scale = min_unit_cost * 0.999

    for node in positions:
        # Calculate heuristic h(node)
        p1 = positions[node]
        p2 = positions[goal]
        h_val = calculate_euclidean_distance(p1, p2) * scale

        # Calculate true shortest path cost h*(node) using reference Dijkstra
        ref_cost, _ = run_reference_dijkstra(network, source=node, target=goal, req_cap=5.0)
        if ref_cost is not None:
            assert h_val <= ref_cost + 1e-6, f"Heuristic overestimation violation at {node}: h={h_val} > h*={ref_cost}"


def test_astar_optimality_vs_reference_dijkstra():
    """
    Compares the A* search result against the independent reference Dijkstra implementation
    across multiple source-destination pairs.
    """
    network = get_default_network()
    test_pairs = [
        ("PS1", "SUB3"),
        ("PS1", "SUB4"),
        ("PS2", "SUB6"),
        ("PS2", "SUB1"),
        ("SUB1", "SUB5"),
        ("SUB6", "SUB4"),
    ]

    for src, dst in test_pairs:
        req = AStarRouteRequest(source_id=src, destination_id=dst, required_capacity=10.0)
        astar_res = astar_search(network, req)
        ref_cost, _ = run_reference_dijkstra(network, source=src, target=dst, req_cap=10.0)

        assert astar_res.path_found is True
        assert abs(astar_res.total_cost - ref_cost) < 0.05, (
            f"A* cost ({astar_res.total_cost}) does not match optimal Dijkstra cost ({ref_cost}) for {src} -> {dst}"
        )


def test_intermediate_edge_capacity_enforcement():
    """
    Verifies that A* rejects paths if an intermediate edge along the multi-hop route
    does not meet the capacity requirement.
    """
    network = get_default_network()
    # Route from PS1 to SUB4 typically hops: PS1 -> SUB1 -> SUB2 -> SUB4
    # Let's set capacity of SUB2 -> SUB4 (TL8) to 15 MW and request 20 MW
    for line in network.transmission_lines:
        if line.id == "TL8":
            line.max_capacity = 15.0
            line.current_flow = 0.0

    req = AStarRouteRequest(source_id="PS1", destination_id="SUB4", required_capacity=20.0)
    res = astar_search(network, req)

    # Route should either be not found or routed through an alternate path avoiding TL8
    if res.path_found:
        assert "TL8" not in res.path_edges
        assert res.bottleneck_capacity_mw >= 20.0
