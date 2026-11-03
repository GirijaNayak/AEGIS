"""
Mathematical membership functions for Fuzzy Logic inference.
Includes standard Triangular and Trapezoidal membership functions with analytical verification.
"""

from typing import Tuple


def trimf(x: float, params: Tuple[float, float, float]) -> float:
    """
    Triangular membership function.
    params = (a, b, c) where a <= b <= c
    Handles shoulders when a == b or b == c.
    """
    a, b, c = float(params[0]), float(params[1]), float(params[2])
    x = float(x)
    if a == b and x <= b:
        return 1.0
    if b == c and x >= c:
        return 1.0
    if x < a or x > c:
        return 0.0
    if a <= x <= b:
        return 1.0 if a == b else (x - a) / (b - a)
    if b < x <= c:
        return 1.0 if b == c else (c - x) / (c - b)
    return 0.0


def trapmf(x: float, params: Tuple[float, float, float, float]) -> float:
    """
    Trapezoidal membership function.
    params = (a, b, c, d) where a <= b <= c <= d
    Handles left shoulder when a == b and right shoulder when c == d.
    """
    a, b, c, d = float(params[0]), float(params[1]), float(params[2]), float(params[3])
    x = float(x)
    # Left shoulder: core extends to left boundary
    if a == b and x <= b:
        return 1.0
    # Right shoulder: core extends to right boundary
    if c == d and x >= c:
        return 1.0
    if x < a or x > d:
        return 0.0
    if a <= x < b:
        return 1.0 if a == b else (x - a) / (b - a)
    if b <= x <= c:
        return 1.0
    if c < x <= d:
        return 1.0 if c == d else (d - x) / (d - c)
    return 0.0


class LoadMembership:
    """Load % in range [0, 100]"""
    # Low: Trapezoidal [0, 0, 25, 45]
    LOW_PARAMS = (0.0, 0.0, 25.0, 45.0)
    # Medium: Triangular [30, 55, 75]
    MEDIUM_PARAMS = (30.0, 55.0, 75.0)
    # High: Trapezoidal [65, 80, 100, 100]
    HIGH_PARAMS = (65.0, 80.0, 100.0, 100.0)

    @classmethod
    def evaluate(cls, load: float):
        x = max(0.0, min(100.0, float(load)))
        return {
            "low": trapmf(x, cls.LOW_PARAMS),
            "medium": trimf(x, cls.MEDIUM_PARAMS),
            "high": trapmf(x, cls.HIGH_PARAMS),
        }


class HealthMembership:
    """Health % in range [0, 100]"""
    # Poor: Trapezoidal [0, 0, 30, 50]
    POOR_PARAMS = (0.0, 0.0, 30.0, 50.0)
    # Average: Triangular [35, 60, 80]
    AVERAGE_PARAMS = (35.0, 60.0, 80.0)
    # Good: Trapezoidal [70, 85, 100, 100]
    GOOD_PARAMS = (70.0, 85.0, 100.0, 100.0)

    @classmethod
    def evaluate(cls, health: float):
        x = max(0.0, min(100.0, float(health)))
        return {
            "poor": trapmf(x, cls.POOR_PARAMS),
            "average": trimf(x, cls.AVERAGE_PARAMS),
            "good": trapmf(x, cls.GOOD_PARAMS),
        }


class TemperatureMembership:
    """Temperature in °C in range [0, 120]"""
    # Normal: Trapezoidal [0, 0, 45, 60]
    NORMAL_PARAMS = (0.0, 0.0, 45.0, 60.0)
    # Elevated: Triangular [50, 70, 88]
    ELEVATED_PARAMS = (50.0, 70.0, 88.0)
    # Critical: Trapezoidal [80, 95, 120, 120]
    CRITICAL_PARAMS = (80.0, 95.0, 120.0, 120.0)

    @classmethod
    def evaluate(cls, temp: float):
        x = max(0.0, min(120.0, float(temp)))
        return {
            "normal": trapmf(x, cls.NORMAL_PARAMS),
            "elevated": trimf(x, cls.ELEVATED_PARAMS),
            "critical": trapmf(x, cls.CRITICAL_PARAMS),
        }


class RiskMembership:
    """Output Risk Score in range [0, 100]"""
    # Low: Trapezoidal [0, 0, 20, 35]
    LOW_PARAMS = (0.0, 0.0, 20.0, 35.0)
    # Moderate: Triangular [25, 45, 65]
    MODERATE_PARAMS = (25.0, 45.0, 65.0)
    # High: Triangular [55, 75, 90]
    HIGH_PARAMS = (55.0, 75.0, 90.0)
    # Critical: Trapezoidal [80, 92, 100, 100]
    CRITICAL_PARAMS = (80.0, 92.0, 100.0, 100.0)

    @classmethod
    def evaluate_at(cls, z: float, category: str) -> float:
        cat = category.lower()
        if cat == "low":
            return trapmf(z, cls.LOW_PARAMS)
        elif cat == "moderate":
            return trimf(z, cls.MODERATE_PARAMS)
        elif cat == "high":
            return trimf(z, cls.HIGH_PARAMS)
        elif cat == "critical":
            return trapmf(z, cls.CRITICAL_PARAMS)
        return 0.0
