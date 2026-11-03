"""
Unit tests for Fuzzy Logic risk assessment module.
"""

import pytest
from app.ai.fuzzy_logic.membership import (
    trimf,
    trapmf,
    LoadMembership,
    HealthMembership,
    TemperatureMembership,
)
from app.ai.fuzzy_logic.inference import evaluate_fuzzy_risk
from app.ai.fuzzy_logic.defuzzification import centroid_defuzzification


def test_membership_functions():
    # Triangular function test: peak at 50, zero at <= 30 or >= 70
    assert trimf(30.0, (30.0, 50.0, 70.0)) == 0.0
    assert trimf(50.0, (30.0, 50.0, 70.0)) == 1.0
    assert trimf(40.0, (30.0, 50.0, 70.0)) == 0.5
    assert trimf(75.0, (30.0, 50.0, 70.0)) == 0.0

    # Trapezoidal function test: plateau between 40 and 60
    assert trapmf(30.0, (30.0, 40.0, 60.0, 70.0)) == 0.0
    assert trapmf(45.0, (30.0, 40.0, 60.0, 70.0)) == 1.0
    assert trapmf(55.0, (30.0, 40.0, 60.0, 70.0)) == 1.0
    assert trapmf(65.0, (30.0, 40.0, 60.0, 70.0)) == 0.5


def test_fuzzy_risk_low_regime():
    # Load 15% (Low), Health 95% (Good), Temp 35°C (Normal) -> Low risk
    result = evaluate_fuzzy_risk(load=15.0, health=95.0, temperature=35.0, component_name="TestSub")
    assert result.defuzzified_risk_score < 35.0
    assert result.risk_category == "Low"
    assert len(result.activated_rules) > 0


def test_fuzzy_risk_critical_regime():
    # Load 95% (High), Health 20% (Poor), Temp 105°C (Critical) -> Critical risk
    result = evaluate_fuzzy_risk(load=95.0, health=20.0, temperature=105.0, component_name="TestSub")
    assert result.defuzzified_risk_score >= 75.0
    assert result.risk_category == "Critical"
    assert any(r.consequent == "CRITICAL" for r in result.activated_rules)


def test_fuzzy_risk_moderate_regime():
    # Load 50% (Medium), Health 60% (Average), Temp 45°C (Normal) -> Moderate risk
    result = evaluate_fuzzy_risk(load=50.0, health=60.0, temperature=45.0, component_name="TestSub")
    assert 25.0 <= result.defuzzified_risk_score <= 65.0
    assert result.risk_category in ["Moderate", "Low"]


def test_centroid_defuzzification_uniform():
    # Symmetric distribution centered at 50 should yield centroid near 50
    dist = [1.0 if 40 <= i <= 60 else 0.0 for i in range(101)]
    score = centroid_defuzzification(dist, 0.0, 100.0)
    assert abs(score - 50.0) < 1.0
