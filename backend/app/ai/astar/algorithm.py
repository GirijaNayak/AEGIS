"""
A* Search Algorithm implementation from scratch.
Finds optimal alternative power transmission routes respecting capacity constraints,
tracking open/closed sets, and maintaining full explainability of node explorations.
"""

import heapq
import math
from typing import Dict, List, Optional, Set, Tuple
from app.models.infrastructure import (
    InfrastructureNetwork,
    OperationalStatus,
)
from app.models.recovery import (
    AStarRouteRequest,
    AStarRouteResult,
    ExploredNodeStep,
)
from app.ai.astar.heuristic import (
    AdmissibleHeuristic,
    calculate_euclidean_distance,
)


def astar_search(
    network: InfrastructureNetwork,
    request: AStarRouteRequest,
) -> AStarRouteResult:
    """
    Executes A* search on the network graph from source_id to destination_id.
    """
    source_id = request.source_id
    goal_id = request.destination_id
    req_cap = request.required_capacity

    # 1. Extract positions and node name mappings
    node_positions: Dict[str, Tuple[float, float]] = {}
    node_names: Dict[str, str] = {}
    failed_nodes: Set[str] = set(request.avoid_node_ids)

    for ps in network.power_stations:
        node_positions[ps.id] = (ps.position.x, ps.position.y)
        node_names[ps.id] = ps.name
        if ps.operational_status == OperationalStatus.FAILED:
            failed_nodes.add(ps.id)

    for sub in network.substations:
        node_positions[sub.id] = (sub.position.x, sub.position.y)
        node_names[sub.id] = sub.name
        if sub.operational_status == OperationalStatus.FAILED:
            failed_nodes.add(sub.id)

    for bg in network.backup_generators:
        node_positions[bg.id] = (bg.position.x, bg.position.y)
        node_names[bg.id] = bg.name
        if bg.operational_status == OperationalStatus.FAILED:
            failed_nodes.add(bg.id)

    # 2. Extract edges and compute minimum unit cost for admissibility
    # Graph adjacency: node -> list of (neighbor_id, edge_id, transfer_cost, max_cap, rem_cap)
    adj: Dict[str, List[Tuple[str, str, float, float, float]]] = {n: [] for n in node_positions}
    failed_edges: Set[str] = set(request.avoid_edge_ids)
    min_unit_cost = 999.0

    for line in network.transmission_lines:
        if line.id in failed_edges or line.operational_status == OperationalStatus.FAILED:
            continue
        
        # Calculate available remaining transmission capacity
        rem_cap = max(0.0, line.max_capacity - line.current_flow)
        
        # Skip if line cannot carry required capacity
        if rem_cap < req_cap:
            continue

        p1 = node_positions.get(line.source_id)
        p2 = node_positions.get(line.destination_id)
        if p1 and p2:
            dist = max(1.0, calculate_euclidean_distance(p1, p2))
            unit_cost = line.transfer_cost / dist
            if unit_cost < min_unit_cost:
                min_unit_cost = unit_cost

        # Bidirectional graph for electrical transmission lines
        if line.source_id in adj and line.destination_id in adj:
            adj[line.source_id].append((line.destination_id, line.id, line.transfer_cost, line.max_capacity, rem_cap))
            adj[line.destination_id].append((line.source_id, line.id, line.transfer_cost, line.max_capacity, rem_cap))

    if min_unit_cost >= 900.0:
        min_unit_cost = 0.001

    heuristic = AdmissibleHeuristic(node_positions, min_cost_per_unit=min_unit_cost)

    # 3. Check trivial failure conditions
    if source_id in failed_nodes or goal_id in failed_nodes:
        return AStarRouteResult(
            source_id=source_id,
            destination_id=goal_id,
            path_found=False,
            path_nodes=[],
            path_node_names=[],
            path_edges=[],
            total_cost=0.0,
            total_distance_km=0.0,
            bottleneck_capacity_mw=0.0,
            nodes_explored_count=0,
            explanation=f"Cannot route: Source ({source_id}) or Destination ({goal_id}) is marked FAILED/UNAVAILABLE.",
        )

    if source_id not in node_positions or goal_id not in node_positions:
        return AStarRouteResult(
            source_id=source_id,
            destination_id=goal_id,
            path_found=False,
            path_nodes=[],
            path_node_names=[],
            path_edges=[],
            total_cost=0.0,
            total_distance_km=0.0,
            bottleneck_capacity_mw=0.0,
            nodes_explored_count=0,
            explanation=f"Invalid node identifiers: {source_id} or {goal_id} not found in infrastructure network.",
        )

    # 4. A* Search Execution
    # Priority Queue elements: (f_score, g_score, counter, current_node, parent_node, edge_used)
    open_heap: List[Tuple[float, float, int, str, Optional[str], Optional[str]]] = []
    entry_counter = 0

    h_start = heuristic(source_id, goal_id)
    heapq.heappush(open_heap, (h_start, 0.0, entry_counter, source_id, None, None))
    entry_counter += 1

    g_score: Dict[str, float] = {source_id: 0.0}
    came_from: Dict[str, Tuple[Optional[str], Optional[str]]] = {source_id: (None, None)}
    closed_set: Set[str] = set()
    exploration_steps: List[ExploredNodeStep] = []

    step_counter = 1
    found = False

    while open_heap:
        f, g, _, current, parent, edge_id = heapq.heappop(open_heap)

        if current in closed_set:
            continue

        closed_set.add(current)
        h = heuristic(current, goal_id)

        exploration_steps.append(
            ExploredNodeStep(
                step=step_counter,
                node_id=current,
                node_name=node_names.get(current, current),
                g_cost=round(g, 3),
                h_cost=round(h, 3),
                f_cost=round(f, 3),
                parent_id=parent,
            )
        )
        step_counter += 1

        if current == goal_id:
            found = True
            break

        # Explore neighbors
        for neighbor, e_id, cost, max_cap, rem_cap in adj.get(current, []):
            if neighbor in failed_nodes or neighbor in closed_set:
                continue

            tentative_g = g + cost

            if tentative_g < g_score.get(neighbor, float("inf")):
                g_score[neighbor] = tentative_g
                came_from[neighbor] = (current, e_id)
                h_neighbor = heuristic(neighbor, goal_id)
                f_neighbor = tentative_g + h_neighbor
                heapq.heappush(open_heap, (f_neighbor, tentative_g, entry_counter, neighbor, current, e_id))
                entry_counter += 1

    # 5. Path Reconstruction
    if not found:
        return AStarRouteResult(
            source_id=source_id,
            destination_id=goal_id,
            path_found=False,
            path_nodes=[],
            path_node_names=[],
            path_edges=[],
            total_cost=0.0,
            total_distance_km=0.0,
            bottleneck_capacity_mw=0.0,
            nodes_explored_count=len(closed_set),
            exploration_steps=exploration_steps,
            explanation=f"A* Search exhausted all {len(closed_set)} reachable nodes without finding a path with >= {req_cap} MW capacity.",
        )

    # Backtrack path
    path_nodes: List[str] = []
    path_edges: List[str] = []
    curr: Optional[str] = goal_id

    while curr is not None:
        path_nodes.append(curr)
        prev_node, e_id = came_from[curr]
        if e_id:
            path_edges.append(e_id)
        curr = prev_node

    path_nodes.reverse()
    path_edges.reverse()

    # Calculate bottleneck capacity and total physical distance
    bottleneck_cap = float("inf")
    total_dist = 0.0

    for i in range(len(path_nodes) - 1):
        u, v = path_nodes[i], path_nodes[i + 1]
        p1 = node_positions[u]
        p2 = node_positions[v]
        total_dist += calculate_euclidean_distance(p1, p2)

    for e_id in path_edges:
        for line in network.transmission_lines:
            if line.id == e_id:
                rem = line.max_capacity - line.current_flow
                if rem < bottleneck_cap:
                    bottleneck_cap = rem

    if math.isinf(bottleneck_cap):
        bottleneck_cap = 0.0

    total_cost = round(g_score[goal_id], 2)
    path_names = [node_names.get(n, n) for n in path_nodes]

    explanation = (
        f"A* found optimal feasible route {source_id} -> {goal_id} "
        f"via {len(path_nodes)} nodes ({' -> '.join(path_nodes)}). "
        f"Total route transfer cost: {total_cost}. Explored {len(closed_set)} nodes. "
        f"Minimum bottleneck capacity along route: {round(bottleneck_cap, 1)} MW."
    )

    return AStarRouteResult(
        source_id=source_id,
        destination_id=goal_id,
        path_found=True,
        path_nodes=path_nodes,
        path_node_names=path_names,
        path_edges=path_edges,
        total_cost=total_cost,
        total_distance_km=round(total_dist * 0.5, 1),  # Scaling factor to simulated km
        bottleneck_capacity_mw=round(bottleneck_cap, 1),
        nodes_explored_count=len(closed_set),
        exploration_steps=exploration_steps,
        explanation=explanation,
    )
