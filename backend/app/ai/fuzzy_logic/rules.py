"""
Fuzzy Rule Base for Infrastructure Risk Assessment.
Defines Mamdani linguistic rules mapping operating conditions to risk classifications.
"""

from typing import Dict, List, Tuple


class FuzzyRule:
    def __init__(
        self,
        rule_id: int,
        load: str,
        health: str,
        temp: str,
        risk: str,
        description: str,
    ):
        self.rule_id = rule_id
        self.load = load.lower()        # "low", "medium", "high", or "any"
        self.health = health.lower()    # "poor", "average", "good", or "any"
        self.temp = temp.lower()        # "normal", "elevated", "critical", or "any"
        self.risk = risk.lower()        # "low", "moderate", "high", "critical"
        self.description = description

    def evaluate_antecedent(
        self,
        load_mu: Dict[str, float],
        health_mu: Dict[str, float],
        temp_mu: Dict[str, float],
    ) -> float:
        """
        Computes rule firing strength using the standard Mamdani MIN operator for AND.
        """
        strengths = []
        if self.load != "any":
            strengths.append(load_mu.get(self.load, 0.0))
        if self.health != "any":
            strengths.append(health_mu.get(self.health, 0.0))
        if self.temp != "any":
            strengths.append(temp_mu.get(self.temp, 0.0))

        if not strengths:
            return 0.0
        return min(strengths)


# Exhaustive domain rule base covering operational regimes
FUZZY_RULE_BASE: List[FuzzyRule] = [
    # Critical risk rules
    FuzzyRule(1, "high", "poor", "any", "critical", "IF Load is High AND Health is Poor THEN Risk is Critical"),
    FuzzyRule(2, "high", "any", "critical", "critical", "IF Load is High AND Temperature is Critical THEN Risk is Critical"),
    FuzzyRule(3, "any", "poor", "critical", "critical", "IF Health is Poor AND Temperature is Critical THEN Risk is Critical"),
    FuzzyRule(4, "high", "average", "elevated", "critical", "IF Load is High, Health is Average AND Temp is Elevated THEN Risk is Critical"),
    
    # High risk rules
    FuzzyRule(5, "high", "average", "normal", "high", "IF Load is High AND Health is Average THEN Risk is High"),
    FuzzyRule(6, "medium", "poor", "elevated", "high", "IF Load is Medium, Health is Poor AND Temp is Elevated THEN Risk is High"),
    FuzzyRule(7, "medium", "poor", "normal", "high", "IF Load is Medium AND Health is Poor THEN Risk is High"),
    FuzzyRule(8, "low", "poor", "elevated", "high", "IF Load is Low, Health is Poor AND Temp is Elevated THEN Risk is High"),
    FuzzyRule(9, "any", "average", "critical", "high", "IF Health is Average AND Temp is Critical THEN Risk is High"),
    FuzzyRule(10, "high", "good", "elevated", "high", "IF Load is High, Health is Good AND Temp is Elevated THEN Risk is High"),

    # Moderate risk rules
    FuzzyRule(11, "medium", "average", "normal", "moderate", "IF Load is Medium, Health is Average AND Temp is Normal THEN Risk is Moderate"),
    FuzzyRule(12, "high", "good", "normal", "moderate", "IF Load is High, Health is Good AND Temp is Normal THEN Risk is Moderate"),
    FuzzyRule(13, "medium", "good", "elevated", "moderate", "IF Load is Medium, Health is Good AND Temp is Elevated THEN Risk is Moderate"),
    FuzzyRule(14, "low", "poor", "normal", "moderate", "IF Load is Low, Health is Poor AND Temp is Normal THEN Risk is Moderate"),
    FuzzyRule(15, "low", "average", "elevated", "moderate", "IF Load is Low, Health is Average AND Temp is Elevated THEN Risk is Moderate"),
    FuzzyRule(16, "medium", "average", "elevated", "moderate", "IF Load is Medium, Health is Average AND Temp is Elevated THEN Risk is Moderate"),

    # Low risk rules
    FuzzyRule(17, "low", "good", "normal", "low", "IF Load is Low, Health is Good AND Temp is Normal THEN Risk is Low"),
    FuzzyRule(18, "low", "average", "normal", "low", "IF Load is Low, Health is Average AND Temp is Normal THEN Risk is Low"),
    FuzzyRule(19, "medium", "good", "normal", "low", "IF Load is Medium, Health is Good AND Temp is Normal THEN Risk is Low"),
    FuzzyRule(20, "low", "good", "elevated", "low", "IF Load is Low, Health is Good AND Temp is Elevated THEN Risk is Low"),
]


def get_rule_base() -> List[FuzzyRule]:
    return FUZZY_RULE_BASE
