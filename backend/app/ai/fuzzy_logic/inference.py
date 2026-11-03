"""
Mamdani Fuzzy Inference System for Infrastructure Risk Assessment.
Executes Fuzzification -> Rule Evaluation (MIN) -> Aggregation (MAX) -> Defuzzification (Centroid).
"""

from typing import Dict, List, Tuple
from app.models.recovery import (
    FuzzyInputValues,
    MembershipDegrees,
    HealthMemberships,
    TemperatureMemberships,
    ActivatedFuzzyRule,
    FuzzyEvaluationResult,
)
from app.ai.fuzzy_logic.membership import (
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


def evaluate_fuzzy_risk(
    load: float,
    health: float,
    temperature: float,
    component_id: str = "SUB",
    component_name: str = "Substation",
) -> FuzzyEvaluationResult:
    """
    Evaluates complete Mamdani fuzzy risk inference for a given infrastructure component.
    """
    # 1. Fuzzification
    load_mu = LoadMembership.evaluate(load)
    health_mu = HealthMembership.evaluate(health)
    temp_mu = TemperatureMembership.evaluate(temperature)

    # 2. Rule Evaluation using Mamdani MIN operator
    rule_base = get_rule_base()
    activated_rules: List[ActivatedFuzzyRule] = []
    consequent_strengths: Dict[str, float] = {
        "low": 0.0,
        "moderate": 0.0,
        "high": 0.0,
        "critical": 0.0,
    }

    for rule in rule_base:
        firing_strength = rule.evaluate_antecedent(load_mu, health_mu, temp_mu)
        if firing_strength > 0.001:
            activated_rules.append(
                ActivatedFuzzyRule(
                    rule_id=rule.rule_id,
                    antecedent=f"Load={rule.load}, Health={rule.health}, Temp={rule.temp}",
                    consequent=rule.risk.upper(),
                    firing_strength=round(firing_strength, 3),
                )
            )
            # Mamdani MAX aggregation for identical consequents
            consequent_strengths[rule.risk] = max(consequent_strengths[rule.risk], firing_strength)

    # 3. Rule Aggregation across the output universe [0, 100] (101 sample points)
    num_samples = 101
    aggregated_distribution: List[float] = []

    for i in range(num_samples):
        z = float(i)
        # For each point z, the clipped output membership is max_c (min(alpha_c, mu_c(z)))
        point_mu = 0.0
        for category, alpha in consequent_strengths.items():
            if alpha > 0.0:
                clipped = min(alpha, RiskMembership.evaluate_at(z, category))
                point_mu = max(point_mu, clipped)
        aggregated_distribution.append(round(point_mu, 4))

    # 4. Centroid Defuzzification
    crisp_score = centroid_defuzzification(aggregated_distribution, 0.0, 100.0)
    risk_category = classify_risk_score(crisp_score)

    # 5. Explanatory text for student viva / presentation
    top_rules = sorted(activated_rules, key=lambda r: -r.firing_strength)[:3]
    rules_summary = ", ".join(f"Rule #{r.rule_id} (weight {r.firing_strength})" for r in top_rules) if top_rules else "No significant rules"
    explanation = (
        f"{component_name} evaluated under operating load {round(load, 1)}%, "
        f"health {round(health, 1)}%, and temperature {round(temperature, 1)}°C. "
        f"Fuzzy inference activated {len(activated_rules)} rules. "
        f"Strongest rules: {rules_summary}. "
        f"Centroid defuzzification produced crisp risk score {crisp_score}/100 ({risk_category} Risk)."
    )

    return FuzzyEvaluationResult(
        component_id=component_id,
        component_name=component_name,
        inputs=FuzzyInputValues(
            load_percentage=round(load, 1),
            health_percentage=round(health, 1),
            temperature=round(temperature, 1),
        ),
        load_memberships=MembershipDegrees(
            low=round(load_mu["low"], 3),
            medium=round(load_mu["medium"], 3),
            high=round(load_mu["high"], 3),
        ),
        health_memberships=HealthMemberships(
            poor=round(health_mu["poor"], 3),
            average=round(health_mu["average"], 3),
            good=round(health_mu["good"], 3),
        ),
        temperature_memberships=TemperatureMemberships(
            normal=round(temp_mu["normal"], 3),
            elevated=round(temp_mu["elevated"], 3),
            critical=round(temp_mu["critical"], 3),
        ),
        activated_rules=activated_rules,
        aggregated_risk_distribution=aggregated_distribution,
        defuzzified_risk_score=crisp_score,
        risk_category=risk_category,
        explanation=explanation,
    )
