from math import cos, pi, sin

from PIL import ImageFont

LINE_WIDTH = 100
LINE_WIDTH_THIN = 20
TO_DEGREES = 180.0 / pi
TO_RADIANS = pi / 180.0



class BaseConfig():
    def __init__(self, filename:str, output_dir: str=None, pixels_per_inch=100, mode='RGB', show_frame=True, add_text=True):
        self.output_dir = output_dir if output_dir else "output"
        self.filename = filename

        self.pixels_per_inch = pixels_per_inch
        self.mode = mode
        self.show_frame = show_frame
        self.add_text = add_text

class RampBase():

    def init(self, config: BaseConfig):
        self.config = config
        self.draw = None


    def draw_image(self):
        raise NotImplemented("Must be implemented by subclass.") 

    def compute_curve(self) -> tuple[list[tuple[float, float]], list[float], list[float]]:
        raise NotImplemented("Must be implemented by subclass.") 

    def add_text(self, rows):
        if not self.draw:
            raise Exception("You must instantiate self.draw as an instance of Image.draw()")
        font_size = 100
        row_height = self.inches(1.2)
        padding_bottom = self.inches(2)
        font = ImageFont.truetype("Helvetica.ttc", font_size)
        for i, row in enumerate(rows):
            x = self.inches(36)
            y = self.Y - len(rows) * row_height - padding_bottom + i * row_height
            print("Adding text {0}".format(row))
            self.draw.text((x, y),row,(0,0,0),font=font)


    def inches(self, value):
        return value * self.config.pixels_per_inch

    def render_grid(self):
        delta_x = 12.0 * self.config.pixels_per_inch
        delta_y = delta_x
        while delta_x < self.X:
            self.draw.line([(delta_x, 0), (delta_x, self.Y)], fill='grey', width=LINE_WIDTH_THIN)
            delta_x = delta_x + 12.0 * self.config.pixels_per_inch

        while delta_y < self.Y:
            self.draw.line([(0, delta_y), (self.X, delta_y)], fill='grey', width=LINE_WIDTH_THIN)
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
