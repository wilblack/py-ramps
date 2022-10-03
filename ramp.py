
import json
import math
import os
from typing import Optional

from PIL import Image, ImageDraw

from ramp_base import LINE_WIDTH_THIN, BaseConfig, RampBase


def format_float(f: float):
    if isinstance(f, float):
        return float(f"{f:.1}")
    else:
        return f

class RampConfig(BaseConfig):
    def __init__(self, angle_degree: float, radius_inches: Optional[float] = None, height_inches: Optional[float] = None, output_dir=None, filename=None,
        pixels_per_inch=100, mode='RGB', show_rungs=True, show_frame=True, add_text=True, rung_width=5.5):
        

        self.radius_inches = radius_inches
        self.height_inches = height_inches
        self.angle_degree = angle_degree
        self.angle_radian = self.angle_degree * math.pi / 180.0

        if (radius_inches):
            filename = f"ramp_a{self.angle_degree}_h{height_inches}.png"
        elif (height_inches):
            filename = f"ramp_r{radius_inches}_h{height_inches}.png"
        else:
            raise Exception("You must provide a radius or a height in inches")

        
        self.pixels_per_inch = pixels_per_inch
        self.mode = mode
        self.show_rungs = show_rungs
        self.show_frame = show_frame
        self.rung_width = rung_width
        self.add_text = add_text

        output_dir = output_dir if output_dir else "output"
        
        super().__init__(filename, output_dir, pixels_per_inch, mode=mode, show_frame=show_frame, add_text=add_text)



class Ramp(RampBase):
    
    def __init__(self, config: RampConfig, image=None):

        self.config = config
        if (config.radius_inches):
            [self.height_inches, self.length_inches, self.radius_inches, theta] = self.compute_height(config.angle_radian, config.radius_inches)
        elif (config.height_inches):
            [self.height_inches, self.length_inches, self.radius_inches, theta] = self.compute_radius(config.angle_radian, config.height_inches)
        else:
            raise Exception("You must provide a radius or a height in inches")

        self.height_feet = self.height_inches / 12.0
        self.length_feet = self.length_inches / 12.0
        self.radius_feet = self.radius_inches / 12.0
        self.theta_radian = theta
        self.theta_degree = self.theta_radian * 180.0 / math.pi
        
        self.X = int(self.length_feet * 12 * config.pixels_per_inch)
        self.Y = int(self.height_feet * 12 * config.pixels_per_inch)
        self.OUT_PATH = os.path.join(config.output_dir, config.filename)
        
        self.size = (self.X, self.Y)
        self.mode = config.mode
        self.color = 'white'
        self.fill_width = 10
        self.image = image if image else Image.new(self.mode, self.size, self.color)

        print(f"Height: {self.height_feet:.1f} Length: {self.length_feet:.1f} Radius: {self.radius_feet:.1f} Angle: {config.angle_degree} Theta: {self.theta_degree: .1f}")
        self.stats = {
            "height_feet": format_float(self.height_feet),
            "height_inches": format_float(self.height_inches),
            "length_feet": format_float(self.length_feet),
            "length_inches": format_float(self.length_inches),
            "radius_feet": format_float(self.radius_feet),
            "radius_inches": format_float(self.radius_inches),
            "takeoff_angle_degrees": format_float(self.config.angle_degree),
            "takeoff_angle_radians": format_float(self.config.angle_radian),
            "subtended_angle_degrees": format_float(self.theta_degree),
            "subtended_angle_radians": format_float(self.theta_radian),
            "arclength_inches": format_float(self.theta_radian * self.radius_inches),
            "arclength_feet": format_float(self.theta_radian * self.radius_feet) 

        }
        self.draw_image()

    def compute_radius(self, angle_radian: float, height_inches: float):
        if (angle_radian < 0 or angle_radian > math.pi / 2.0):
            raise Exception(f"Angle must be between 0 and pi / 4 radians. You gave ${angle_radian}")
        theta = math.pi / 2.0 - angle_radian
        l = math.cos(theta)
        r = height_inches / (1 - math.sin(theta))
        return [height_inches, l * r, r, theta]
    


    def compute_height(self, angle_radian: float, radius_inches: float):
        if (angle_radian < 0 or angle_radian > math.pi / 2.0):
            raise Exception(f"Angle must be between 0 and pi / 4 radians. You gave ${angle_radian}")

        theta = math.pi / 2.0 - angle_radian
        h = radius_inches - radius_inches * math.sin(theta) 
        l = radius_inches * math.cos(theta) 
        return [h, l, theta]




    def draw_image(self):
        self.draw = ImageDraw.Draw(self.image)

        self.points, self.x, self.y = self.compute_curve()
        self.draw.line(self.points, fill='black', width=self.fill_width)
        # if self.config.show_rungs:
        #     self.add_rungs()

        # if self.config.show_frame:
        #     self.render_frame()

        self.render_grid()
        # if self.config.add_text:
        #     rows = [
        #         "Length: {0} feet".format(self.config.L / 12.0),
        #         "Max Height: {0} inches".format(self.config.H),
        #         "Max Slope: {0:.2f}".format(self.max_slope())
        #     ]
        #     if self.config.show_rungs:
        #         rows.extend([
        #             "Number of Rungs: {0}".format(self.rung_count),
        #             "Rung Width: {0}".format(self.config.rung_width)
        #         ])

        #     self.add_text(rows)
        self.image.save(self.OUT_PATH)



    def compute_curve(self):
        points = []
        x = []
        y = []
        # import pdb; pdb.set_trace()

        dt = (math.pi / 2  - self.theta_radian) / 100
        for i in range(100):
            theta = math.pi / 2  - dt * i
            _x = self.inches(self.radius_inches * math.cos(theta))
            _y = self.inches(self.height_inches) - self.inches(self.radius_inches) + self.inches(self.radius_inches * math.sin(theta)) 
            points.append((_x ,_y))
            x.append(_x)
            y.append(_y)
        return points, x, y


    def render_grid(self):
        delta_x = 12.0 * self.config.pixels_per_inch
        delta_y = delta_x
        while delta_x < self.X:
            print(f"draw grid delta_x {delta_x}")
            self.draw.line([(delta_x, 0), (delta_x, self.Y)], fill='grey', width=LINE_WIDTH_THIN)
            delta_x = delta_x + 12.0 * self.config.pixels_per_inch

        while delta_y < self.Y:
            print(f"draw grid delta_y {delta_y}")
            self.draw.line([(0, delta_y), (self.X, delta_y)], fill='grey', width=LINE_WIDTH_THIN)
            delta_y = delta_y + 12.0 * self.config.pixels_per_inch







if __name__ == "__main__":
    # config = RampConfig(1, height_inches=6*12.0)
    # ramp = Ramp(config)
    # config = RampConfig(40, height_inches=6*12.0)
    # ramp = Ramp(config)
    # config = RampConfig(44, height_inches=6 * 12.0)
    # ramp = Ramp(config)
    # config = RampConfig(89, height_inches=6*12.0)
    # ramp = Ramp(config)
    config = RampConfig(50, height_inches=7.0 * 12.0)
    ramp = Ramp(config)
    print(json.dumps(ramp.stats, indent=2))
    


 

