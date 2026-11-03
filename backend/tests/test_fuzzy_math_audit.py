"""
Independent mathematical verification audit for Mamdani Fuzzy Logic inference.
Verifies boundary conditions, continuity, crossover points, coverage, rule activations,
and numerical integration of centroid defuzzification against independent references.
"""

import pytest
from app.ai.fuzzy_logic.membership import (
    trimf,
    trapmf,
    LoadMembership,
    HealthMembership,
    TemperatureMembership,
    RiskMembership,
)
from app.ai.fuzzy_logic.rules import get_rule_base
from app.ai.fuzzy_logic.defuzzification import (
    centroid_defuzzification,
    classify_risk_score,
)
from app.ai.fuzzy_logic.inference import evaluate_fuzzy_risk


def test_boundary_values_membership():
    """Verifies that 0 and maximum boundary values produce exact 1.0 memberships for shoulder categories."""
    # 0% Load -> Low must be 1.0
    load_0 = LoadMembership.evaluate(0.0)
    assert load_0["low"] == 1.0
    assert load_0["medium"] == 0.0
    assert load_0["high"] == 0.0

    # 100% Load -> High must be 1.0
    load_100 = LoadMembership.evaluate(100.0)
    assert load_100["high"] == 1.0
    assert load_100["medium"] == 0.0
    assert load_100["low"] == 0.0

    # 0% Health -> Poor must be 1.0
    health_0 = HealthMembership.evaluate(0.0)
    assert health_0["poor"] == 1.0
    assert health_0["good"] == 0.0

    # 100% Health -> Good must be 1.0
    health_100 = HealthMembership.evaluate(100.0)
    assert health_100["good"] == 1.0
    assert health_100["poor"] == 0.0

    # 0°C Temp -> Normal must be 1.0
    temp_0 = TemperatureMembership.evaluate(0.0)
    assert temp_0["normal"] == 1.0
    assert temp_0["critical"] == 0.0

    # 120°C Temp -> Critical must be 1.0
    temp_120 = TemperatureMembership.evaluate(120.0)
    assert temp_120["critical"] == 1.0
    assert temp_120["normal"] == 0.0


def test_membership_coverage_no_gaps():
    """Ensures that for every single point in the universe of discourse, at least one term has membership > 0."""
    for load in range(0, 101):
        mu = LoadMembership.evaluate(float(load))
        assert sum(mu.values()) > 0.0, f"Gap found in Load membership at {load}%"
        for val in mu.values():
            assert 0.0 <= val <= 1.0

    for health in range(0, 101):
        mu = HealthMembership.evaluate(float(health))
        assert sum(mu.values()) > 0.0, f"Gap found in Health membership at {health}%"
        for val in mu.values():
            assert 0.0 <= val <= 1.0

    for temp in range(0, 121):
        mu = TemperatureMembership.evaluate(float(temp))
        assert sum(mu.values()) > 0.0, f"Gap found in Temperature membership at {temp}°C"
        for val in mu.values():
            assert 0.0 <= val <= 1.0


def test_crossover_continuity():
    """Tests continuity and expected values around crossover points."""
    # Load crossover at 37.5%: between Low and Medium
    mu_37_5 = LoadMembership.evaluate(37.5)
    assert mu_37_5["low"] > 0.0
    assert mu_37_5["medium"] > 0.0

    # Health crossover at 42.5%: between Poor and Average
    mu_h = HealthMembership.evaluate(42.5)
    assert mu_h["poor"] > 0.0
    assert mu_h["average"] > 0.0


def test_centroid_defuzzification_independent_reference():
    """Compares the production centroid against an independently computed analytical discrete integral."""
    # Triangular distribution peaking at 50, zero at 25 and 75
    dist = [0.0] * 101
    for i in range(25, 51):
        dist[i] = (i - 25) / 25.0
    for i in range(51, 76):
        dist[i] = (75 - i) / 25.0

    ref_num = sum(i * dist[i] for i in range(101))
    ref_den = sum(dist[i] for i in range(101))
    ref_centroid = round(ref_num / ref_den, 2)

    actual_centroid = centroid_defuzzification(dist, 0.0, 100.0)
    assert actual_centroid == ref_centroid == 50.0

    # Asymmetric distribution: right-skewed plateau between 70 and 100
    dist_asym = [1.0 if 70 <= i <= 100 else 0.0 for i in range(101)]
    ref_asym_centroid = round(sum(i * dist_asym[i] for i in range(101)) / sum(dist_asym), 2)
    actual_asym = centroid_defuzzification(dist_asym, 0.0, 100.0)
    assert actual_asym == ref_asym_centroid == 85.0


def test_zero_denominator_defuzzification_safety():
    """Verifies that an all-zero distribution falls back safely without division by zero."""
    empty_dist = [0.0] * 101
    score = centroid_defuzzification(empty_dist, 0.0, 100.0)
    assert score == 20.0


def test_all_20_rules_reachability():
    """Verifies that each of the 20 rules can be individually activated under representative inputs."""
    rules = get_rule_base()
    assert len(rules) == 20

    # Input exemplars for linguistic terms
    exemplars = {
        "load": {"low": 10.0, "medium": 55.0, "high": 90.0, "any": 50.0},
        "health": {"poor": 15.0, "average": 60.0, "good": 95.0, "any": 60.0},
        "temp": {"normal": 30.0, "elevated": 70.0, "critical": 105.0, "any": 45.0},
    }

    for rule in rules:
        l_in = exemplars["load"][rule.load]
        h_in = exemplars["health"][rule.health]
        t_in = exemplars["temp"][rule.temp]

        res = evaluate_fuzzy_risk(l_in, h_in, t_in, "TEST", "TestComp")
        activated_ids = [r.rule_id for r in res.activated_rules]
        assert rule.rule_id in activated_ids, f"Rule #{rule.rule_id} ({rule.description}) was not reachable under its canonical input!"
