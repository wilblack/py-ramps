
import io
import json
import os
import uuid
from math import atan, cos, floor, pi, sin, sqrt
from typing import List, Tuple

import boto3
from boto3.dynamodb.types import TypeSerializer

serializer = TypeSerializer()

from PIL import Image, ImageDraw, ImageFont

LINE_WIDTH = 100
LINE_WIDTH_THIN = 5
TO_DEGREES = 180.0 / pi
TO_RADIANS = pi / 180.0




def format_float(f: float):
    if isinstance(f, float):
        return float(f"{f:.2}")
    else:
        return f


def dist(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def radian_to_degree(rads: float) -> float:
    return rads * TO_DEGREES


def degree_to_radian(degrees: float) -> float:
    return degrees * TO_RADIANS


BUCKET_NAME = "mtb-ramps"


class BaseConfig():
    def __init__(self, filename: str, output_dir: str = "output", pixels_per_inch=100, mode='RGB', show_frame=True, add_text=True, rung_width: float = 5.5, debug=False):
        self.output_dir = output_dir
        self.filename = filename

        self.rung_width = rung_width
        self.pixels_per_inch = pixels_per_inch
        self.mode = mode
        self.show_frame = show_frame
        self.add_text = add_text
        self.debug = debug

class RampBase():

    def __init__(self, config: BaseConfig):
        self.env = os.getenv("ENV")
        self.config = config
        self.stats = {}
        self.out_path = "output"

        # Absolute size of canvas in pixels
        self.X = 0
        self.Y = 0

        # The pixels of the curve
        self.curve_x = [0]
        self.curve_y = [0]
        self.curve_points = []

        # The image object, will be instantiated by the subclass
        self.image = Image.new(mode="RGB", size=(1, 1))
        self.draw = ImageDraw.Draw(self.image)

    def draw_image(self):
        raise NotImplemented("Must be implemented by subclass.")

    def draw_frame(self, width_inches: float = 11.0):
        """
        Draws a 2x frame based on the midpoint of the curve

        """
        raise NotImplemented()

    def compute_curve(self) -> Tuple[List[Tuple[float, float]], List[float], List[float]]:
        raise NotImplemented("Must be implemented by subclass.")

    def add_text(self, rows: List[str], position: str = "top"):
        if not self.draw:
            raise Exception(
                "You must instantiate self.draw as an instance of Image.draw()")
        font_size = self.config.pixels_per_inch * 2
        row_height = self.inches(2)
        padding_vert = self.inches(2.5)
        font = ImageFont.truetype("Yagora.ttf", font_size)

        for i, row in enumerate(rows):
            x = self.X * .1
            if position == "top":
                y = padding_vert + i * row_height
            else:
                y = self.Y - len(rows) * row_height - \
                    padding_vert + i * row_height
            print("Adding text {0}".format(row))
            self.draw.text((x, y), row, (0, 0, 0), font=font)

    def inches(self, inches: float):
        """
        Converts value in inches to pixels
        """
        return inches * self.config.pixels_per_inch

    def pixel_to_inch(self, pixels: float) -> float:
        return pixels / self.config.pixels_per_inch / 12.0

    def render_grid(self):
        if not self.draw:
            raise Exception(
                "You must instantiate self.draw as an instance of Image.draw()")
        delta_x = 12.0 * self.config.pixels_per_inch
        delta_y = delta_x
        font = ImageFont.truetype("Yagora.ttf", int(
            self.config.pixels_per_inch * 1.5))
        while delta_x < self.X:
            label_ft = delta_x / 12.0 / self.config.pixels_per_inch
            label = f"{label_ft:.0f} (ft) [{delta_x}]"
            self.draw.line([(delta_x, 0), (delta_x, self.Y)],
                           fill='grey', width=LINE_WIDTH_THIN)
            self.draw.text((delta_x + 20, delta_y * 0.05),
                           label, (0, 0, 0), font=font)
            delta_x = delta_x + 12.0 * self.config.pixels_per_inch

        while delta_y < self.Y:
            label_ft = (self.Y - delta_y) / 12.0 / self.config.pixels_per_inch
            label = f"{label_ft:.0f} (ft) [{delta_y}]"
            self.draw.line([(0, delta_y), (self.X, delta_y)],
                           fill='grey', width=LINE_WIDTH_THIN)
            self.draw.text((20, delta_y), label, (0, 0, 0), font=font)
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

    def render_beam(self, anchor: Tuple[float, float], length_pixels: float, width_pixels: float, angle_radians: float):
        """_summary_
        All coordinates are in pixels

        Args:
            anchor (Tuple[float, float]): _description_ Top left corner of the beam
            length_pixels (float): _description_
            width_pixels (float): _description_
            angle_radians (float): _description_
        """
        length_pixels = length_pixels  # self.inches(length_pixels)
        width_pixels = width_pixels  # self.inches(width_pixels)

        points = [
            (0, 0),
            (length_pixels, 0),
            (length_pixels, width_pixels),
            (0, width_pixels)
        ]

        print(f"X: {self.X}, Y: {self.Y}")
        # rotate
        points = [self.rotate(p, angle_radians) for p in points]

        # translate
        points = [self.translate(p, anchor) for p in points]

        self.draw.line([points[0], points[1]],
                       fill='red', width=LINE_WIDTH_THIN)
        self.draw.line([points[1], points[2]],
                       fill='red', width=LINE_WIDTH_THIN)
        self.draw.line([points[2], points[3]],
                       fill='red', width=LINE_WIDTH_THIN)
        self.draw.line([points[3], points[0]],
                       fill='red', width=LINE_WIDTH_THIN)

    def add_rungs(self) -> int:
        """
        Start at the left bottom of the curve.
        Loop until the next point is greater than the rung width, then end rung.
        Continue looping until you are past the gap_width, then start a new rung.


        """
        rung_count = 0
        p1 = (self.curve_x[0], self.curve_y[0])
        in_gap = False
        for i in range(self.X):
            p2 = (self.curve_x[i], self.curve_y[i])
            if in_gap:
                if dist(p1, p2) > self.inches(1.5):
                    in_gap = False
                    p1 = p2

            # Not in the gap, check if I am the end of a rung.
            elif dist(p1, p2) > self.inches(self.config.rung_width):
                in_gap = True
                self.draw.line([p1, p2], fill='red', width=50)
                rung_count = rung_count + 1
                p1 = p2

        self.stats.update({"rung_count": rung_count})
        return rung_count

    def _create(self, table: str, stats) -> str:
        if self.env == "local":
            print("Env is local so doing nothing.")
            return ""

        db = boto3.resource(
            'dynamodb',
            region_name="us-west-2"
        )
        table = db.Table(table)  # type: ignore
        payload = {**stats, "id": str(uuid.uuid4())}
        response = table.put_item(  # type: ignore
            TableName=table,
            Item=payload
        )

        print(response)
        return payload["id"]

    def save_image(self):
        return self._save_image_s3()
        # if self.env == "local":
        #     return self._save_image_local()
        # else:
        #     return self._save_image_s3

    def _save_image_s3(self):
        s3 = boto3.client('s3')
        io_stream = io.BytesIO()
        self.image.save(io_stream, format="PNG")
        io_stream.seek(0)

        s3.upload_fileobj(
            io_stream,  # This is what i am trying to upload
            BUCKET_NAME,
            self.out_path,
            ExtraArgs={
                'ACL': 'public-read'
            }
        )
        url = f"https://{BUCKET_NAME}.s3.us-west-2.amazonaws.com/{self.out_path}"
        self.stats.update({"url": url})

        return url

    def _save_image_local(self):
        if not os.path.exists(self.config.output_dir):
            # Create path
            os.makedirs(self.config.output_dir)
        self.image.save(self.out_path)
        return self.out_path

    def get_midpoint(self):
        if len(self.curve_x) < 3 or len(self.curve_y) < 3:
            raise Exception(
                "curve_x or curve_y is not long enough to compute midpoint.")
        index = floor(len(self.curve_x) / 2)
        rise = self.curve_y[index + 1] - self.curve_y[index - 1]
        run = self.curve_x[index + 1] - self.curve_x[index - 1]
        slope = rise / run
        angle_radian = atan(slope)
        angle_degree = radian_to_degree(angle_radian)
        
        out = {
            "x": self.curve_x[index],
            "y": self.curve_y[index],
            "slope": slope,
            "radians": angle_radian,
            "angle_degree": angle_degree
        }
        if self.config.debug:
            print(f"[get_midpoint] {json.dumps(out, indent=2)}")


        return out
