"""
API Quality Assurance & Robustness Audit Tests for AEGIS REST Endpoints.
Tests:
1. Pydantic validation rejects out-of-range fuzzy inputs (Load < 0 or > 100, Health < 0 or > 100, Temp < 0 or > 120).
2. Pydantic validation rejects out-of-range failure severity (< 0 or > 1).
3. Non-existent node IDs in A* search return graceful path_found=False without crashing 500.
4. GA optimization endpoint validates and returns valid chromosome, generation history, and baseline comparison.
5. Experiment execution endpoint runs and returns comparative benchmark metrics.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_fuzzy_out_of_range_rejection():
    """Verifies that out-of-bound fuzzy inputs trigger HTTP 422 Unprocessable Entity."""
    # Load > 100%
    res1 = client.post("/api/ai/fuzzy/evaluate", json={"load_percentage": 105.0, "health_percentage": 50.0, "temperature": 50.0})
    assert res1.status_code == 422

    # Negative health
    res2 = client.post("/api/ai/fuzzy/evaluate", json={"load_percentage": 50.0, "health_percentage": -10.0, "temperature": 50.0})
    assert res2.status_code == 422

    # Temperature > 120°C
    res3 = client.post("/api/ai/fuzzy/evaluate", json={"load_percentage": 50.0, "health_percentage": 50.0, "temperature": 150.0})
    assert res3.status_code == 422


def test_api_failure_injection_validation():
    """Verifies that malformed failure requests return HTTP 422."""
    # Negative severity
    res1 = client.post("/api/failures/trigger", json={
        "component_id": "SUB1",
        "component_type": "substation",
        "failure_type": "substation_failure",
        "severity": -0.5
    })
    assert res1.status_code == 422

    # Severity > 1.0
    res2 = client.post("/api/failures/trigger", json={
        "component_id": "SUB1",
        "component_type": "substation",
        "failure_type": "substation_failure",
        "severity": 2.0
    })
    assert res2.status_code == 422


def test_api_astar_nonexistent_nodes_handled_gracefully():
    """Verifies that searching routes between non-existent nodes returns path_found=False without a 500 error."""
    payload = {
        "source_id": "NON_EXISTENT_STATION",
        "destination_id": "SUB3",
        "required_capacity": 10.0
    }
    response = client.post("/api/ai/astar/find-route", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["path_found"] is False
    assert "Cannot route" in data["explanation"] or "No operational route" in data["explanation"] or "not found" in data["explanation"].lower()


def test_api_fuzzy_rules_metadata():
    """Verifies that the /api/ai/fuzzy/rules endpoint returns all 20 documented rules with valid weights."""
    response = client.get("/api/ai/fuzzy/rules")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 20
    for r in data:
        assert "rule_id" in r
        assert "risk_consequent" in r
        assert r["risk_consequent"].upper() in ["LOW", "MODERATE", "HIGH", "CRITICAL"]


def test_api_ga_optimize_custom_config():
    """Verifies that /api/ai/genetic/optimize processes custom population and generation parameters."""
    client.post("/api/simulation/reset")
    client.post("/api/simulation/preset/scenario_a")

    payload = {
        "population_size": 20,
        "generations": 10,
        "random_seed": 123
    }
    response = client.post("/api/ai/genetic/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert len(data["generations_history"]) == 10
    assert "baseline_comparison" in data
    assert data["baseline_comparison"]["cost"] >= data["best_cost"]


def test_api_experiment_run():
    """Verifies that /api/experiments/run executes reproducible baseline vs AI comparison."""
    payload = {
        "scenario_id": "scenario_a",
        "ga_config": {
            "population_size": 15,
            "generations": 8,
            "random_seed": 42
        }
    }
    response = client.post("/api/experiments/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "baseline" in data
    assert "ai_assisted" in data
    assert data["ai_assisted"]["fitness"] > 0.0
