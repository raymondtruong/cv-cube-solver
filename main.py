from flask import Flask, render_template, request
import kociemba    # TODO: install via pip
import json
import base64
import cv2
import numpy as np
import colorsys


app = Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/solve", methods=["POST"])
def solve():

    raw_images = json.loads(request.form["images"])
    colours = [[[None, None, None], [None, None, None], [None, None, None]],
              [[None, None, None], [None, None, None], [None, None, None]],
              [[None, None, None], [None, None, None], [None, None, None]],
              [[None, None, None], [None, None, None], [None, None, None]],
              [[None, None, None], [None, None, None], [None, None, None]],
              [[None, None, None], [None, None, None], [None, None, None]]]

    for face in range(6):
        # decode image
        encoded_image = np.fromstring(base64.b64decode(raw_images[face][21:]), dtype=np.uint8)
        source_image = cv2.imdecode(encoded_image, 1)

        # crop to 144x144 (48x48 individual pieces)
        cropped_source = source_image[17:161, 45:189]

        # determine individual pieces
        for row in range(3):
            for column in range(3):

                # slice into 48x48 piece
                square = cropped_source[(row * 48):((row + 1) * 48), (column * 48):((column + 1) * 48)]

                # extract colour
                pixel_colour = square[24, 24]     # midpoint
                rgb = (pixel_colour[2], pixel_colour[1], pixel_colour[0])
                colours[face][row][column] = identify_colour(rgb)

    # manually override each center piece
    colours[0][1][1] = "g"
    colours[1][1][1] = "o"
    colours[2][1][1] = "b"
    colours[3][1][1] = "r"
    colours[4][1][1] = "y"
    colours[5][1][1] = "w"

    # generate net
    net = generate_net(colours)

    # convert net to kociemba-compatible string notation
    state = kociemba_state(net)

    # solve!
    try:
        solution = kociemba.solve(state)
    except ValueError as e:
        solution = e

    return render_template("solve.html", solution=solution)


"""
This function takes an tuple rgb of three values (red, blue, and green pixel
intensity values) and returns one character corresponding to any of the six
colours on a standard Rubik's cube, depending on which is the best match.
"""
def identify_colour(rgb):
    colour = ""

    (hue, saturation, value) = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)

    # colour identification logic
    if (saturation < 0.2):
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

    return colour


"""
This function takes a large array c of the colour of every piece on every face
of the Rubik's cube as determined by the program, and returns one single string
representation of the current state of the cube, according to the following
diagram:

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

The string takes the form U1U2U3...R1R2R3...F1...D1...L1...B1, as dictated
by this implementation of Kociemba's algorithm.
"""
def generate_net(c):
    u = [c[4][0][2], c[4][1][2], c[4][2][2], c[4][0][1], c[4][1][1], c[4][2][1], c[4][0][0], c[4][1][0], c[4][2][0]]
    r = [c[3][0][0], c[3][0][1], c[3][0][2], c[3][1][0], c[3][1][1], c[3][1][2], c[3][2][0], c[3][2][1], c[3][2][2]]
    f = [c[2][0][0], c[2][0][1], c[2][0][2], c[2][1][0], c[2][1][1], c[2][1][2], c[2][2][0], c[2][2][1], c[2][2][2]]
    d = [c[5][2][0], c[5][1][0], c[5][0][0], c[5][2][1], c[5][1][1], c[5][0][1], c[5][2][2], c[5][1][2], c[5][0][2]]
    l = [c[1][0][0], c[1][0][1], c[1][0][2], c[1][1][0], c[1][1][1], c[1][1][2], c[1][2][0], c[1][2][1], c[1][2][2]]
    b = [c[0][0][0], c[0][0][1], c[0][0][2], c[0][1][0], c[0][1][1], c[0][1][2], c[0][2][0], c[0][2][1], c[0][2][2]]
    net = u + r + f + d + l + b

    state = ''.join(net)
    return state


"""
This function takes a large string c of the colour of every piece on every face
of the Rubik's cube as determined by the generate_net() function, and replaces
the individual colour identifiers with a broader positional notation to create
a new state that can be accepted by Kociemba's algorithm.
"""
def kociemba_state(c):
    c = c.replace('y', 'U')
    c = c.replace('r', 'R')
    c = c.replace('b', 'F')
    c = c.replace('w', 'D')
    c = c.replace('o', 'L')
    c = c.replace('g', 'B')

    return c


if __name__ == "__main__":
    app.run(debug=True)
