import json
import math
import os
from typing import Optional

from PIL import Image, ImageDraw

from ramp_base import (BaseConfig, RampBase, dist, format_float,
                       radian_to_degree)
from ramp_math import kicker_from_angle_and_height


class KickerConfig(BaseConfig):
    def __init__(self, angle_degree: float, radius_inches: Optional[float] = None, height_inches: Optional[float] = None, output_dir=None, filename=None,
                 pixels_per_inch=20, mode='RGB', show_rungs=True, show_frame=True, add_text=True, rung_width=5.5, debug=False):

        self.debug = debug
        print(f"debug = {self.debug}")
        self.radius_inches = radius_inches
        self.height_inches = height_inches
        self.angle_degree = angle_degree
        self.angle_radian = self.angle_degree * math.pi / 180.0

        if (radius_inches):
            filename = f"ramp_a{angle_degree}_r{radius_inches}.png"
        elif (height_inches):
            filename = f"ramp_r{angle_degree}_h{height_inches}.png"
        else:
            raise Exception("You must provide a radius or a height in inches")

        self.pixels_per_inch = pixels_per_inch
        self.mode = mode
        self.show_rungs = show_rungs
        self.show_frame = show_frame
        self.rung_width = rung_width
        self.add_text = add_text

        output_dir = output_dir if output_dir else "output"

        super().__init__(filename, output_dir, pixels_per_inch,
                         mode=mode, show_frame=show_frame, add_text=add_text, debug=debug)


class Kicker(RampBase):

    def __init__(self, config: KickerConfig, image=None):
        print("in Kicker")
        self.config = config
        super().__init__(self.config)

        if (config.radius_inches):
            [self.height_inches, self.length_inches, self.radius_inches,
                theta] = self.compute_height(config.angle_radian, config.radius_inches)
        elif (config.height_inches):
            print(f"config.height_inches {config.height_inches}")
            self.geo = kicker_from_angle_and_height(config.angle_degree, config.height_inches * 12.0)
            self.height_inches = self.geo["height"]
            self.length_inches = self.geo["length"]
            self.radius_inches = self.geo["radius"]
            theta = theta = math.pi / 2.0 - self.geo["angle"]

            # [self.height_inches, self.length_inches, self.radius_inches,
            #     theta] = self.compute_radius(config.angle_radian, config.height_inches)
            
        else:
            raise Exception("You must provide a radius or a height in inches")

        self.height_feet = self.height_inches / 12.0
        self.length_feet = self.length_inches / 12.0
        self.radius_feet = self.radius_inches / 12.0
        self.theta_radian = theta
        self.theta_degree = self.theta_radian * 180.0 / math.pi

    
        self.X = int(self.length_feet * 12 * config.pixels_per_inch)
        self.Y = int(self.height_feet * 12 * config.pixels_per_inch)
        self.curve_x = []
        self.curve_y = []
        self.out_path = os.path.join(config.output_dir, config.filename)

        self.size = (self.padding["left"] + self.X + self.padding["right"], self.padding["bottom"] + self.Y + self.padding["top"])
        self.mode = config.mode
        self.color = 'white'
        self.fill_width = 10
        print("in Kicker 3")
        self.image = image if image else Image.new(
            self.mode, self.size, self.color)
        print("in Kicker 4")

        print(f"Height: {self.height_inches:.1f} Length: {self.length_feet:.1f} Radius: {self.radius_feet:.1f} Angle: {config.angle_degree} Theta: {self.theta_degree: .1f}")

        self.stats.update({
            "height_feet": format_float(self.height_feet),
            "height_inches": format_float(self.height_inches),
            "length_feet": format_float(self.length_feet),
            "length_inches": format_float(self.length_inches),
            "radius_feet": format_float(self.radius_feet),
            "radius_inches": format_float(self.radius_inches),
            "takeoff_angle_degrees": format_float(self.config.angle_degree),
            "takeoff_angle_radians": format_float(self.config.angle_radian),
            "arclength_inches": format_float(self.config.angle_radian * self.radius_inches),
            "arclength_feet": format_float(self.config.angle_radian * self.radius_feet),
        })

        print(json.dumps(self.stats))

    def compute_radius(self, angle_radian: float, height_inches: float):
        print(f"in compute_radius height: {height_inches}")
        if (angle_radian < 0 or angle_radian > math.pi / 2.0):
            raise Exception(
                f"Angle must be between 0 and pi / 4 radians. You gave ${angle_radian}")
        theta = math.pi / 2.0 - angle_radian
        r = height_inches / (1 - math.sin(theta))
        l = r * math.cos(theta)
        print("done compute_radius")
        return [height_inches, l, r, theta]

    def compute_height(self, angle_radian: float, radius_inches: float):
        print("in compute_height")
        if (angle_radian < 0 or angle_radian > math.pi / 2.0):
            raise Exception(
                f"Angle must be between 0 and pi / 4 radians. You gave ${angle_radian}")

        theta = math.pi / 2.0 - angle_radian
        h = radius_inches - radius_inches * math.sin(theta)
        l = radius_inches * math.cos(theta)
        print(f"Done computing height")
        return [h, l, radius_inches, theta]

    def draw_image(self):
        self.draw = ImageDraw.Draw(self.image)

        self.curve_points, self.curve_x, self.curve_y = self.compute_curve()
        self.render_grid()
        self.draw.line(self.curve_points, fill='black', width=self.fill_width)

        text_rows = [
            f"Height (ft): {self.stats['height_feet']}",
            f"Length (ft): {self.stats['length_feet']}",
            f"Ramp Length (ft): {self.stats['arclength_feet']}",
            f"Takeoff Angle (degrees): {self.stats['takeoff_angle_degrees']}"
        ]
        if self.config.show_rungs:
            rung_count = self.add_rungs()
            text_rows.append(f"Rungs: {rung_count}")

        if self.config.add_text:
            self.add_text(text_rows)

        if self.config.show_frame:
            self.draw_frame()
            text_rows.extend([
                f"Left Frame Board Bottom Length: {self.stats['left_board_bottom_length']}",
                f"Left Frame Board Top Length: {self.stats['left_board_top_length']}"
            ])

    def save(self) -> str:
        return self._create("Kicker", self.stats)

    def compute_curve(self) -> tuple[tuple[float, float], list[float], list[float]]:
        points = []
        x = []
        y = []
        # import pdb; pdb.set_trace()

        dt = (math.pi / 2 - self.theta_radian) / float(self.X)
        for i in range(self.X):
            theta = math.pi / 2 - dt * i
            _x = self.inches(self.radius_inches * math.cos(theta)) + self.padding["left"]
            _y = self.padding["top"] + self.inches(self.height_inches) - self.inches(self.radius_inches) + \
                self.inches(self.radius_inches * math.sin(theta))
            points.append((_x, _y))
            x.append(_x)
            y.append(_y)
        return tuple(points), x, y

    def draw_frame(self):
        width = 11 * self.config.pixels_per_inch
        mid = self.get_midpoint()
        
        # Bottom left beam
        b1_lt = (self.curve_x[0], self.curve_y[0])
        b1_rt = (mid["x"], mid["y"])
        length = dist(b1_lt, b1_rt)
        angle_radian = math.atan((b1_rt[1] - b1_lt[1]) / (b1_rt[0] - b1_lt[0]))
        if self.config.debug:
            print(
            f"[draw_frame] length {length}, angle: {radian_to_degree(angle_radian)}, b1_lt: {b1_lt}, width: {width}")
        self.render_beam(b1_lt, length, width, angle_radian)

        # Top right beam 
        lt = (mid["x"], mid["y"])
        rt = (self.curve_x[-1], self.curve_y[-1])
        length = dist(lt, rt)
        angle_radian = math.atan((rt[1] - lt[1]) / (rt[0] - lt[0]))
        self.render_beam(lt, length, width, angle_radian)
