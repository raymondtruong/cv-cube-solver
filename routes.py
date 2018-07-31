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
                colour = square[24, 24]
                rgb = (colour[2], colour[1], colour[0])
                print("{} = {}".format(i, identify_colour(rgb)), file=sys.stderr)

                # encode square
                ret, x = cv2.imencode(".png", square)
                b64_squares[i][row][column] = "data:image/png;base64," + str(base64.b64encode(x))[2:-1]


    return render_template("solve.html", test="Test", squares=b64_squares)


def identify_colour(rgb):
    # todo
    hex = "#%02x%02x%02x" % rgb
    hsv = colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2])
    print(hsv, file=sys.stderr)

    return hex
