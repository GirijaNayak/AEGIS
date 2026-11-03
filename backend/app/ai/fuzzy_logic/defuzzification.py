"""
Centroid (Center of Gravity) Defuzzification module.
Numerically integrates the aggregated fuzzy output distribution to compute the crisp risk score.
"""

from typing import List, Tuple


def centroid_defuzzification(distribution: List[float], z_min: float = 0.0, z_max: float = 100.0) -> float:
    """
    Computes the crisp center of gravity:
    Centroid = sum(z_i * mu(z_i)) / sum(mu(z_i))
    """
    n = len(distribution)
    if n <= 1:
        return 50.0

    step = (z_max - z_min) / (n - 1)
    numerator = 0.0
    denominator = 0.0

    for i, mu in enumerate(distribution):
        z = z_min + (i * step)
        numerator += z * mu
        denominator += mu

    if denominator <= 1e-7:
        return 20.0  # Default safe baseline if no rules fire significantly

    centroid = numerator / denominator
    return round(float(centroid), 2)


def classify_risk_score(score: float) -> str:
    """
    Maps numerical defuzzified risk score [0, 100] to standard linguistic category.
    """
    if score < 30.0:
        return "Low"
    elif score < 55.0:
        return "Moderate"
    elif score < 75.0:
        return "High"
    else:
        return "Critical"
