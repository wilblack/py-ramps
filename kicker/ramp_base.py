
from math import cos, pi, sin, sqrt

from PIL import ImageFont

LINE_WIDTH = 100
LINE_WIDTH_THIN = 5
TO_DEGREES = 180.0 / pi
TO_RADIANS = pi / 180.0

def format_float(f: float):
    if isinstance(f, float):
        return float(f"{f:.2}")
    else:
        return f

def dist(p1, p2):
    return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)




class BaseConfig():
    def __init__(self, filename:str, output_dir: str=None, pixels_per_inch=100, mode='RGB', show_frame=True, add_text=True, rung_width: float = 5.5):
        self.output_dir = output_dir if output_dir else "output"
        self.filename = filename

        self.rung_width = rung_width
        self.pixels_per_inch = pixels_per_inch
        self.mode = mode
        self.show_frame = show_frame
        self.add_text = add_text


class RampBase():

    def init(self, config: BaseConfig):
        self.config = config
        self.draw = None
        self.stats = {}

    def draw_image(self):
        raise NotImplemented("Must be implemented by subclass.") 

    def compute_curve(self) -> tuple[list[tuple[float, float]], list[float], list[float]]:
        raise NotImplemented("Must be implemented by subclass.") 

    def add_text(self, rows: list[str], position: str="top"):
        if not self.draw:
            raise Exception("You must instantiate self.draw as an instance of Image.draw()")
        font_size = self.config.pixels_per_inch * 2
        row_height = self.inches(2)
        padding_vert = self.inches(2.5)
        font = ImageFont.truetype("Yagora.ttf", font_size)
                
        for i, row in enumerate(rows):
            x = self.X * .1
            if position == "top":
                y = padding_vert + i * row_height
            else:
                y = self.Y - len(rows) * row_height - padding_vert + i * row_height
            print("Adding text {0}".format(row))
            self.draw.text((x, y),row,(0,0,0),font=font)


    def inches(self, value):
        return value * self.config.pixels_per_inch

    def render_grid(self):
        if not self.draw:
            raise Exception("You must instantiate self.draw as an instance of Image.draw()")
        delta_x = 12.0 * self.config.pixels_per_inch
        delta_y = delta_x
        font = ImageFont.truetype("Yagora.ttf", int(self.config.pixels_per_inch * 1.5))
        while delta_x < self.X:
            label = delta_x / 12.0 / self.config.pixels_per_inch
            self.draw.line([(delta_x, 0), (delta_x, self.Y)], fill='grey', width=LINE_WIDTH_THIN)
            self.draw.text((delta_x + 20, delta_y * 0.05), f"{label:.0f} (ft)", (0,0,0), font=font)
            delta_x = delta_x + 12.0 * self.config.pixels_per_inch

        while delta_y < self.Y:
            label = (self.Y - delta_y) / 12.0 / self.config.pixels_per_inch
            self.draw.line([(0, delta_y), (self.X, delta_y)], fill='grey', width=LINE_WIDTH_THIN)
            self.draw.text((20, delta_y), f"{label:.0f} (ft)", (0,0,0), font=font)
            delta_y = delta_y + 12.0 * self.config.pixels_per_inch

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


    def add_rungs(self) -> int:
        """
        Start at the left bottom of the curve.
        Loop until the next point is greater than the rung width, then end rung.
        Continue looping until you are past the gap_width, then start a new rung.


        """
        rung_count = 0
        p1 = (self.x[0], self.y[0])
        in_gap = False
        for i in range(self.X):
            p2 = (self.x[i], self.y[i])
            if in_gap:
                if dist(p1, p2) > self.inches(1.5):
                    in_gap = False
                    p1 = p2
            
            # Not in the gap, check if I am the end of a rung. 
            elif dist(p1, p2) > self.inches(self.config.rung_width):
                in_gap = True
                self.draw.line([p1, p2], fill='red', width=50)
                rung_count = rung_count + 1
                print(f"i = {i}, x = {self.x[i] / self.config.pixels_per_inch}")
                p1 = p2

        self.stats.update({"rung_count": rung_count}) 
        return rung_count
