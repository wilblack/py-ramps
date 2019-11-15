from math import sin, pi, sqrt
from PIL import Image, ImageDraw


PIXELS_PER_INCH = 100
X = 8 * 12 * PIXELS_PER_INCH
Y = 4 * 12 * PIXELS_PER_INCH

def inches(value):
    return value * PIXELS_PER_INCH

def rung(p1, p2):
    draw.line([p1, p2], fill=black, width=30)

def dist(p1, p2):
    return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


size = (X, Y)
filename = 'output/roller.png'
mode = 'RGB'
color = 'white'
width = 10
img = Image.new(mode, size, color)
draw = ImageDraw.Draw(img)

A = inches(9)
w = 2 * pi / X
H = A
Y_OFFSET = inches(1.5)
phase = pi / 2
points = []
x = []
y = []
for i in range(X):
    _y = A * sin(w * i + phase) + (Y - H) - Y_OFFSET
    points.append((i ,_y))
    x.append(i)
    y.append(_y)


p1 = (x[0], y[0])
in_gap = False
for i in range(X):
    p2 = (x[i], y[i])
    if in_gap:
        if dist(p1, p2) > inches(1.5):
            print("leaving gap")
            in_gap = False
            p1 = p2

    if not in_gap and dist(p1, p2) > inches(3.5):
        print("entering gap", dist(p1, p2))
        in_gap = True
        print(p1)
        print(p2)
        print ([p1, p2])
        draw.line([p1, p2], fill='red', width=100)
        p1 = p2


draw.line(points, fill='black', width=width)
img.save(filename)
