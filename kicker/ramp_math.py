
import json
from math import atan, cos, pi, sin, tan
from typing import TypedDict

from ramp_base import format_float
from utils import degree_to_radian, dist, radian_to_degree


class RampGeometry(TypedDict):
    angle: float
    height: float
    length: float
    radius: float
    arclength: float
    mid_x: float
    mid_y: float
    bottom_board_total_length: float
    bottom_board_total_length_inches: float
    bottom_board_a: float
    bottom_board_b: float
    board_width: float
    curve_depth_major: float
    curve_depth_minor: float
    join_angle: float


def kicker_from_angle_and_height(angle_degree: float, height_feet: float, board_width_inches: float = 11.5) -> RampGeometry:
    """
    angle: degrees
    height: feet

    """
    
    theta = degree_to_radian(angle_degree)
    h = height_feet * 12.0
    r = h / (1 - sin(pi / 2.0 - theta))
    l = r * cos(pi /2.0 - theta)
    
    return common(r, l, h, theta)


def kicker_from_angle_and_radius(angle: float, radius: float, board_width_inches: float = 11.5) -> RampGeometry:
    """
    angle: degrees
    radius: feet

    """
    
    theta = degree_to_radian(angle)
    r = radius * 12.0
    # Compute height
    h = r - r * cos(theta)
    l = r * cos(pi /2.0 - theta)

    return common(r, l, h, theta, board_width_inches)


def common(r, l, h, theta, board_width_inches: float = 11.5) -> RampGeometry:
    m_x = r * sin(theta / 2.0)
    m_y = r * (1 - cos(theta / 2.0))

    l_b = dist((0.0, 0.0), (m_x, m_y))
    curve_depth_major = r * (1.0 - cos(theta / 2.0))
    curve_depth_minor = r * (1.0 - cos(theta / 4.0))

    bottom_board_a = 2.0 * r * sin(theta / 4.0)
    bottom_board_b = board_width_inches / tan(pi / 2.0 - theta / 4.0)
    bottom_board_total_length_inches = bottom_board_a + bottom_board_b
    join_angle = pi - 2.0 * atan(curve_depth_major / l_b)

    out: RampGeometry = {
        "angle": radian_to_degree(theta),
        "height":h / 12.0,
        "length": l / 12.0,
        "radius": r / 12.0,
        "arclength": r * theta / 12.0,
        "mid_x": m_x / 12.0,
        "mid_y": m_y / 12.0,
        "bottom_board_total_length": bottom_board_total_length_inches / 12.0,
        "bottom_board_total_length_inches": bottom_board_total_length_inches,
        "bottom_board_a": bottom_board_a,
        "bottom_board_b": bottom_board_b,
        "board_width": board_width_inches,
        "curve_depth_major": curve_depth_major,
        "curve_depth_minor": curve_depth_minor,
        "join_angle": radian_to_degree(join_angle)
    }
    return out


if __name__ == '__main__':
    res = kicker_from_angle_and_radius(55.0, 16.0)
    formatted_geo = {key: format_float(res[key]) for key in res}
    print(json.dumps(res, indent=2))
