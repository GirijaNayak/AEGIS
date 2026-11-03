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
    Guarantees h(n) <= h*(n) by scaling Euclidean distance with a conservative
    lower-bound factor (0.999 * min_cost_per_unit) ensuring strict mathematical admissibility.
    """
    def __init__(self, node_positions: Dict[str, Tuple[float, float]], min_cost_per_unit: float = 0.002):
        self.positions = node_positions
        # Using 0.999 factor guarantees no floating-point rounding up can ever exceed h*(n)
        self.scale = min_cost_per_unit * 0.999

    def __call__(self, current_node: str, goal_node: str) -> float:
        if current_node == goal_node:
            return 0.0
        pos1 = self.positions.get(current_node)
        pos2 = self.positions.get(goal_node)
        if not pos1 or not pos2:
            return 0.0
        dist = calculate_euclidean_distance(pos1, pos2)
        # Conservative lower-bound estimate
        return float(dist * self.scale)
