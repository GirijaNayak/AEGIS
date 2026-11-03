"""
Admissible heuristic function for A* Search on the infrastructure graph.
Uses Euclidean distance scaled by the minimum cost-per-distance ratio to ensure mathematical admissibility.
"""

import math
from typing import Dict, Tuple


def calculate_euclidean_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    return math.sqrt(dx * dx + dy * dy)


class AdmissibleHeuristic:
    """
    Guarantees h(n) <= h*(n) by scaling Euclidean distance with the global minimum unit cost.
    """
    def __init__(self, node_positions: Dict[str, Tuple[float, float]], min_cost_per_unit: float = 0.002):
        self.positions = node_positions
        self.scale = min_cost_per_unit

    def __call__(self, current_node: str, goal_node: str) -> float:
        if current_node == goal_node:
            return 0.0
        pos1 = self.positions.get(current_node)
        pos2 = self.positions.get(goal_node)
        if not pos1 or not pos2:
            return 0.0
        dist = calculate_euclidean_distance(pos1, pos2)
        # Scaled distance provides an admissible lower-bound estimate
        return round(dist * self.scale, 4)
