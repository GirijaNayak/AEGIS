"""
Integration tests for FastAPI endpoints.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Fuzzy Logic (Mamdani)" in data["ai_modules"]


def test_infrastructure_endpoint():
    response = client.get("/api/infrastructure")
    assert response.status_code == 200
    data = response.json()
    assert len(data["power_stations"]) == 2
    assert len(data["substations"]) == 6
    assert len(data["consumers"]) == 12


def test_simulation_state_and_reset():
    response = client.get("/api/simulation/state")
    assert response.status_code == 200
    data = response.json()
    assert "network" in data
    assert "metrics" in data

    reset_res = client.post("/api/simulation/reset")
    assert reset_res.status_code == 200


def test_ai_fuzzy_evaluate_endpoint():
    payload = {
        "load_percentage": 85.0,
        "health_percentage": 30.0,
        "temperature": 92.0,
    }
    response = client.post("/api/ai/fuzzy/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_category"] in ["High", "Critical"]
    assert data["defuzzified_risk_score"] > 60.0
    assert len(data["activated_rules"]) > 0


def test_ai_astar_route_endpoint():
    payload = {
        "source_id": "PS1",
        "destination_id": "SUB3",
        "required_capacity": 20.0,
    }
    response = client.post("/api/ai/astar/find-route", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["path_found"] is True
    assert data["total_cost"] > 0.0


def test_recovery_analysis_and_execution():
    # Load Scenario A (SUB3 failure)
    load_res = client.post("/api/simulation/preset/scenario_a")
    assert load_res.status_code == 200

    # Run analysis
    analysis_res = client.post("/api/recovery/analyze")
    assert analysis_res.status_code == 200
    analysis_data = analysis_res.json()
    assert "SUB3" in analysis_data["failed_components"]
    assert len(analysis_data["fuzzy_risk_assessments"]) > 0
    assert analysis_data["recommended_ga_plan"] is not None

    # Execute recommended plan
    plan = analysis_data["recommended_ga_plan"]["best_chromosome"]
    exec_res = client.post("/api/recovery/execute", json={"recovery_plan": plan})
    assert exec_res.status_code == 200
    exec_data = exec_res.json()
    assert exec_data["success"] is True
