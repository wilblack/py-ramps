
from math import pi, sqrt
from typing import Tuple


TO_DEGREES = 180.0 / pi
TO_RADIANS = pi / 180.0


def format_float(f: float):
    if isinstance(f, float):
        return float(f"{f:.5}")
    else:
        return f


def dist(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def radian_to_degree(rads: float) -> float:
    return rads * TO_DEGREES


def degree_to_radian(degrees: float) -> float:
    return degrees * TO_RADIANS

