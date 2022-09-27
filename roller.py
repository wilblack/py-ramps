import os
from math import atan, cos, floor, pi, sin, sqrt

from PIL import Image, ImageDraw

LINE_WIDTH = 100
LINE_WIDTH_THIN = 20
TO_DEGREES = 180.0 / pi
TO_RADIANS = pi / 180.0

def dist(p1, p2):
    return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)



class RollerConfig():
    def __init__(self, length_in_inches, height_inches, output_dir=None, filename=None,
        pixels_per_inch=100, mode='RGB', show_rungs=True, show_frame=True, add_text=True, rung_width=5.5):

        self.L = length_in_inches
        self.H = height_inches
        self.LENGTH_IN_FEET = self.L / 12.0
        self.output_dir = output_dir if output_dir else "output"
        self.filename = filename if filename else "roller_{0}ft_by_{1}in.png".format(self.LENGTH_IN_FEET, self.H)
        self.pixels_per_inch = pixels_per_inch
        self.mode = mode
        self.show_rungs = show_rungs
        self.show_frame = show_frame
        self.rung_width = rung_width
        self.add_text = add_text

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
        self.X = int(config.LENGTH_IN_FEET * 12 * config.pixels_per_inch)
        self.Y = int(4 * 12 * config.pixels_per_inch)
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

    def compute_curve(self):
        points = []
        x = []
        y = []
        for i in range(self.X):
            _y = self.A * sin(self.w * i + self.phase) + (self.Y - self.H) - self.Y_OFFSET
            points.append((i ,_y))
            x.append(i)
            y.append(_y)
        return points, x, y


    # def rung(self, p1, p2):
    #     self.draw.line([p1, p2], fill=black, width=30)

    def add_rungs(self):
        p1 = (self.x[0], self.y[0])
        in_gap = False
        for i in range(self.X):
            p2 = (self.x[i], self.y[i])
            if in_gap:
                if dist(p1, p2) > self.inches(1.5):
                    in_gap = False
                    p1 = p2

            if not in_gap and dist(p1, p2) > self.inches(self.config.rung_width):
                in_gap = True
                self.draw.line([p1, p2], fill='red', width=LINE_WIDTH)
                self.rung_count = self.rung_count + 1
                p1 = p2


    def rotate(self, point, angle):
        out = (
            point[0] * cos(angle) - point[1] * sin(angle),
            point[1] * cos(angle) + point[0] * sin(angle)
        )
        print("point ", point)
        print("rotated ", out)
        return out

    def translate(self, point, anchor):
        return (point[0] + anchor[0], point[1] + anchor[1])

    def render_beam(self, anchor, length, width, angle):
        points = [
            (0, 0),
            (length, 0),
            (length, width),
            (0, width)
        ]

        # rotate
        points = [self.rotate(p, angle) for p in points]

        # translate
        points = [self.translate(p, anchor) for p in points]

        self.draw.line([points[0], points[1]], fill='red', width=LINE_WIDTH_THIN)
        self.draw.line([points[1], points[2]], fill='red', width=LINE_WIDTH_THIN)
        self.draw.line([points[2], points[3]], fill='red', width=LINE_WIDTH_THIN)
        self.draw.line([points[3], points[0]], fill='red', width=LINE_WIDTH_THIN)

    def get_midpoint(self):

        index = floor(len(self.x) / 2)
        print("len(self.x)", len(self.x))
        print("mid index", index)
        return (self.x[index], self.y[index])

    def render_frame(self):
        mid = self.get_midpoint()
        anchor = (mid[0], mid[1] - 3 * self.config.pixels_per_inch)
        angle = 16 * TO_RADIANS
        length = 8 * 12.0 * self.config.pixels_per_inch
        width = 11.5  * self.config.pixels_per_inch

        self.render_beam(anchor, length, width, angle)
        self.render_beam(anchor, -length, width, -angle)




    def render_grid(self):
        delta_x = 12.0 * self.config.pixels_per_inch
        delta_y = delta_x
        while delta_x < self.X:
            self.draw.line([(delta_x, 0), (delta_x, self.Y)], fill='grey', width=LINE_WIDTH_THIN)
            delta_x = delta_x + 12.0 * self.config.pixels_per_inch

        while delta_y < self.Y:
            self.draw.line([(0, delta_y), (self.X, delta_y)], fill='grey', width=LINE_WIDTH_THIN)
            delta_y = delta_y + 12.0 * self.config.pixels_per_inch
