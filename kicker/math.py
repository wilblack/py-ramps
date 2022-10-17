
from math import pi, sin, cos, tan, atan
from typing import Optional
import json
from .utils import dist, format_float, degree_to_radian, radian_to_degree



def kicker(angle: float, height: float):
    """
    angle: degrees
    height: feet

    """
    
    theta = degree_to_radian(angle)
    h = height * 12.0

    
    r = h / (1 - sin(pi / 2.0 - theta))
    l = r * cos(pi /2.0 - theta)
    m_x = r * sin(theta / 2.0)
    m_y = r * (1 - cos(theta / 2.0))

    l_b = dist((0.0, 0.0), (m_x, m_y))
    curve_depth_major = r * (1.0 - cos(theta / 2.0))
    curve_depth_minor = r * (1.0 - cos(theta / 4.0))
    
    join_angle = pi - 2.0 * atan(curve_depth_major / l_b)

    out = {
        "angle": angle,
        "height":format_float(h / 12.0),
        "length": format_float(l / 12.0),
        "radius": format_float(r / 12.0),
        "arclength": format_float(r * theta / 12.0),
        "mid_x": format_float(m_x / 12.0),
        "mid_y": format_float(m_y / 12.0),
        "board_length": format_float(l_b / 12.0),
        "curve_depth_major": format_float(curve_depth_major),
        "curve_depth_minor": format_float(curve_depth_minor),
        "join_angle": format_float(radian_to_degree(join_angle))



    }
    return out


if __name__ == '__main__':
    res = kicker(55.0, 6.5)
    print(json.dumps(res, indent=2))