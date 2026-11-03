"""
Unit tests for A* Search algorithm.
"""

import pytest
from app.simulation.default_network import get_default_network
from app.models.recovery import AStarRouteRequest
from app.ai.astar.algorithm import astar_search
from app.models.infrastructure import OperationalStatus


def test_astar_finds_valid_shortest_path():
    network = get_default_network()
    # Route from Power Station 1 (PS1) to Substation 3 (SUB3)
    req = AStarRouteRequest(source_id="PS1", destination_id="SUB3", required_capacity=20.0)
    result = astar_search(network, req)

    assert result.path_found is True
    assert result.path_nodes[0] == "PS1"
    assert result.path_nodes[-1] == "SUB3"
    assert result.total_cost > 0.0
    assert result.nodes_explored_count > 0
    assert len(result.exploration_steps) > 0


def test_astar_avoids_failed_line():
    network = get_default_network()
    # Direct line TL1 connects PS1 -> SUB1. If we avoid TL1, A* must find an alternate path (e.g. via SUB6)
    req = AStarRouteRequest(source_id="PS1", destination_id="SUB1", required_capacity=10.0, avoid_edge_ids=["TL1"])
    result = astar_search(network, req)

    assert result.path_found is True
    assert "TL1" not in result.path_edges
    assert "SUB6" in result.path_nodes  # Routed through alternate substation


def test_astar_respects_capacity_constraint():
    network = get_default_network()
    # Request huge capacity that exceeds all available lines (e.g. 500 MW)
    req = AStarRouteRequest(source_id="PS1", destination_id="SUB3", required_capacity=500.0)
    result = astar_search(network, req)

    assert result.path_found is False
    assert "without finding a path" in result.explanation


def test_astar_fails_gracefully_when_destination_failed():
    network = get_default_network()
    req = AStarRouteRequest(source_id="PS1", destination_id="SUB3", required_capacity=10.0, avoid_node_ids=["SUB3"])
    result = astar_search(network, req)

    assert result.path_found is False
    assert "FAILED/UNAVAILABLE" in result.explanation
