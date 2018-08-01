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
from app import kociemba # temp
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

                # encode square image
                ret, x = cv2.imencode(".png", square)
                b64_squares[i][row][column] = "data:image/png;base64," + str(base64.b64encode(x))[2:-1]

        print()

    colours[5][1][1] = "w" # manually override white center
    state = generate_cube_state(colours)
    try:
        solution = kociemba.solve(state)
    except ValueError as e:
        solution = e

    return render_template("solve.html", test="Test", squares=b64_squares, colours=colours, solution=solution)


def identify_colour(rgb):
    colour = "indeterminate"

    hex = "#%02x%02x%02x" % rgb
    hue, saturation, value = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)

    # colour logic
    if (saturation < 0.25):
        colour = "w"
    elif (hue < 0.11):
        colour = "o"
    elif (hue >= 0.11 and hue < 0.32):
        colour = "y"
    elif (hue >= 0.32 and hue < 0.45):
        colour = "g"
    elif (hue >= 0.45 and hue < 0.8):
        colour = "b"
    else:
        colour = "r"

    print("{} - ({}, {}, {})".format(hex, hue, saturation, value), file=sys.stderr)
    return colour


def generate_cube_state(c):
    """
                 |------------|
                 | U1  U2  U3 |
                 |            |
                 | U4  U5  U6 |
                 |            |
                 | U7  U8  U9 |
    |------------|------------|------------|------------|
    | L1  L2  L3 | F1  F2  F3 | R1  R2  R3 | B1  B2  B3 |
    |            |            |            |            |
    | L4  L5  L6 | F4  F5  F6 | R4  R5  R6 | B4  B5  B6 |
    |            |            |            |            |
    | L7  L8  L9 | F7  F8  F9 | R7  R8  R9 | B7  B8  B9 |
    |------------|------------|------------|------------|
                 | D1  D2  D3 |
                 |            |
                 | D4  D5  D6 |
                 |            |
                 | D7  D8  D9 |
                 |------------|

    URFDLB
    """
    mappings = {"u": 4, "r": 3, "f": 2, "d": 5, "l": 1, "b": 0}

    u = [c[4][0][2], c[4][1][2], c[4][2][2], c[4][0][1], c[4][1][1], c[4][2][1], c[4][0][0], c[4][1][0], c[4][2][0]]
    r = [c[3][0][0], c[3][0][1], c[3][0][2], c[3][1][0], c[3][1][1], c[3][1][2], c[3][2][0], c[3][2][1], c[3][2][2]]
    f = [c[2][0][0], c[2][0][1], c[2][0][2], c[2][1][0], c[2][1][1], c[2][1][2], c[2][2][0], c[2][2][1], c[2][2][2]]
    d = [c[5][2][0], c[5][1][0], c[5][0][0], c[5][2][1], c[5][1][1], c[5][0][1], c[5][2][2], c[5][1][2], c[5][0][2]]
    l = [c[1][0][0], c[1][0][1], c[1][0][2], c[1][1][0], c[1][1][1], c[1][1][2], c[1][2][0], c[1][2][1], c[1][2][2]]
    b = [c[0][0][0], c[0][0][1], c[0][0][2], c[0][1][0], c[0][1][1], c[0][1][2], c[0][2][0], c[0][2][1], c[0][2][2]]
    net = u + r + f + d + l + b

    state = ''.join(net)

    # replace colours
    state = state.replace('y', 'U')
    state = state.replace('g', 'R')
    state = state.replace('r', 'F')
    state = state.replace('w', 'D')
    state = state.replace('b', 'L')
    state = state.replace('o', 'B')

    print(state, file=sys.stderr)
    return state
