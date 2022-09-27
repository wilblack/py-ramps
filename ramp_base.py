from math import pi

from PIL import ImageFont

LINE_WIDTH = 100
LINE_WIDTH_THIN = 20
TO_DEGREES = 180.0 / pi
TO_RADIANS = pi / 180.0


class RampBase():

    def add_text(self, rows):
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

