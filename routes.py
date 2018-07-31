from app import app
from flask import render_template, request
import json
import matplotlib.pyplot as plt
import base64
from PIL import Image
from io import BytesIO
import numpy as np
import cv2
import colorsys
import sys


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", test="Home")


@app.route("/solve", methods=["POST"])
def solve():

    b64_raw_images = json.loads(request.form["images"])
    b64_squares = [[[None, None, None], [None, None, None], [None, None, None]],
                  [[None, None, None], [None, None, None], [None, None, None]],
                  [[None, None, None], [None, None, None], [None, None, None]],
                  [[None, None, None], [None, None, None], [None, None, None]],
                  [[None, None, None], [None, None, None], [None, None, None]],
                  [[None, None, None], [None, None, None], [None, None, None]]]
    colours = [[[None, None, None], [None, None, None], [None, None, None]],
              [[None, None, None], [None, None, None], [None, None, None]],
              [[None, None, None], [None, None, None], [None, None, None]],
              [[None, None, None], [None, None, None], [None, None, None]],
              [[None, None, None], [None, None, None], [None, None, None]],
              [[None, None, None], [None, None, None], [None, None, None]]]

    for i in range(6):
        # decode image
        encoded_image = np.fromstring(base64.b64decode(b64_raw_images[i][21:]), dtype=np.uint8)
        source = cv2.imdecode(encoded_image, 1)

        # crop
        cropped_source = source[17:161, 45:189]     # 144x144 crop

        # individual squares
        for row in range(3):
            for column in range(3):

                # slice square
                square = cropped_source[(row * 48):((row + 1) * 48), (column * 48):((column + 1) * 48)]

                # extract colour
                pixel_colour = square[24, 24]     # midpoint
                rgb = (pixel_colour[2], pixel_colour[1], pixel_colour[0])
                colours[i][row][column] = identify_colour(rgb)

                # encode square
                ret, x = cv2.imencode(".png", square)
                b64_squares[i][row][column] = "data:image/png;base64," + str(base64.b64encode(x))[2:-1]

        print()

    return render_template("solve.html", test="Test", squares=b64_squares, colours=colours)


def identify_colour(rgb):
    colour = "indeterminate"

    hex = "#%02x%02x%02x" % rgb
    hue, saturation, value = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)

    # colour logic
    if (saturation < 0.25):
        colour = "white"
    elif (hue > 0.15 and hue < 0.32):
        colour = "yellow"
    elif (hue >= 0.32 and hue < 0.45):
        colour = "green"
    elif (hue >= 0.45 and hue < 0.7):
        colour = "blue"
    else:
        if (value <= 0.77):
            colour = "red"
        else:
            colour = "orange"

    print("{} - ({}, {}, {})".format(hex, hue, saturation, value), file=sys.stderr)
    return colour
