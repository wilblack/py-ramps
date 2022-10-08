import os
from math import atan, floor, pi, sin

from PIL import Image, ImageDraw

from ramp_base_org import BaseConfig, RampBase

LINE_WIDTH = 100
LINE_WIDTH_THIN = 20
TO_DEGREES = 180.0 / pi
TO_RADIANS = pi / 180.0



class RollerConfig(BaseConfig):
    def __init__(self, length_in_inches, height_inches, output_dir=None, filename=None,pixels_per_inch=100, mode='RGB', show_rungs=True, show_frame=True, add_text=True, rung_width=5.5):
        self.L = length_in_inches
        self.H = height_inches
        self.LENGTH_IN_FEET = self.L / 12.0
        filename = filename if filename else "roller_{0}ft_by_{1}in.png".format(self.LENGTH_IN_FEET, self.H)
        output_dir = output_dir if output_dir else "output"
        self.show_rungs = show_rungs
        self.rung_width = rung_width

        super().__init__(filename, output_dir, pixels_per_inch, mode=mode, show_frame=show_frame, add_text=add_text)

class MultiDrawRollers():
    def __init__(self, configs):

        self.image = Image.new('RGB', self.size, 'white')
        self.rollers = []
        for config in configs:
            self.rollers.append(Roller(config, image))

    def draw_image(self, ):
        for roller in self.rollers:
            roller.draw_image()


class Roller(RampBase):
    def __init__(self, config, image=None):


        self.config = config
        self.X = int(config.LENGTH_IN_FEET * 12 * config.pixels_per_inch) # Total number of pixels of the feature in the horizontal
        self.Y = int(4 * 12 * config.pixels_per_inch)                     # Total number of pixels in the vertical
        self.x = []
        self.y = []
        self.points = []
        self.A = self.inches(config.H / 2.0)
        self.w = 2 * pi / self.X
        self.H = self.A
        self.Y_OFFSET = self.inches(1.5)
        self.phase = pi / 2
        self.OUT_PATH = os.path.join(config.output_dir, config.filename)
        self.rung_count = 0

        self.size = (self.X, self.Y)
        self.mode = config.mode
        self.color = 'white'
        self.fill_width = 10

        self.image = image if image else Image.new(self.mode, self.size, self.color)

        if not os.path.exists(config.output_dir):
            print(f"output directory ${config.output_dir} does not exist so making it.")
            os.mkdir(config.output_dir)

    def draw_image(self):
        self.draw = ImageDraw.Draw(self.image)

        self.points, self.x, self.y = self.compute_curve()
        self.draw.line(self.points, fill='black', width=self.fill_width)
        if self.config.show_rungs:
            self.add_rungs()

        if self.config.show_frame:
            self.render_frame()

        self.render_grid()
        if self.config.add_text:
            rows = [
                "Length: {0} feet".format(self.config.L / 12.0),
                "Max Height: {0} inches".format(self.config.H),
                "Max Slope: {0:.2f}".format(self.max_slope())
            ]
            if self.config.show_rungs:
                rows.extend([
                    "Number of Rungs: {0}".format(self.rung_count),
                    "Rung Width: {0}".format(self.config.rung_width)
                ])

            self.add_text(rows)
        self.image.save(self.OUT_PATH)

    def max_slope(self):
        mid_point = floor(len(self.x) / 4)
        slope =  self.A * self.w
        return atan(slope) * TO_DEGREES

    def compute_curve(self) -> tuple[list[tuple[float, float]], list[float], list[float]]:
        points = []
        x = []
        y = []
        for i in range(self.X):
            _y = self.A * sin(self.w * i + self.phase) + (self.Y - self.H) - self.Y_OFFSET
            points.append((i ,_y))
            x.append(i)
            y.append(_y)
        return points, x, y




    def render_frame(self):
        mid = self.get_midpoint()
        anchor = (mid[0], mid[1] - 3 * self.config.pixels_per_inch)
        angle = 16 * TO_RADIANS
        length = 8 * 12.0 * self.config.pixels_per_inch
        width = 11.5  * self.config.pixels_per_inch

        self.render_beam(anchor, length, width, angle)
        self.render_beam(anchor, -length, width, -angle)




