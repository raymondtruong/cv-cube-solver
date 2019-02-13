from flask import Flask, render_template, request
import kociemba    # TODO: install via pip
import json
import base64
import cv2
import numpy as np
import colorsys
import math


app = Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/preview", methods=["POST"])
def preview():
    colour_scheme = {}
    colours = [[[None, None, None], [None, None, None], [None, None, None]],
               [[None, None, None], [None, None, None], [None, None, None]],
               [[None, None, None], [None, None, None], [None, None, None]],
               [[None, None, None], [None, None, None], [None, None, None]],
               [[None, None, None], [None, None, None], [None, None, None]],
               [[None, None, None], [None, None, None], [None, None, None]]]

    raw_images = json.loads(request.form["images"])

    # first, we can standarize a colour scheme
    for face in range(6):
        image = decode_image(raw_images[face])

        # do this by looking at the center piece of each face
        center_piece = image[48:96, 48:96]
        standardize_colour_scheme(face, colour_scheme, center_piece)

    # then, we can use it to determine each piece's colour
    for face in range(6):
        image = decode_image(raw_images[face])

        for row in range(3):
            for column in range(3):

                # cut each face into 48x48 squares and identify their colour
                square = image[(row * 48):((row + 1) * 48), (column * 48):((column + 1) * 48)]
                colours[face][row][column] = identify_colour(square, colour_scheme)

    # generate a "net" of the cube for use with our algorithm, and also make a
    # second slightly modified version compatible with the visualization library
    net = generate_net(colours)
    visualization_net = visualize_net(net)

    return render_template("preview.html", net=net, visualization_net=visualization_net)


@app.route("/solve", methods=["POST"])
def solve():
    net = request.form["net"]

    # convert net to kociemba-compatible string notation
    state = kociemba_state(net)

    # solve!
    try:
        solution = kociemba.solve(state)
        success = True

    except ValueError as e:
        solution = ""
        success = False

    return render_template("solve.html", solution=solution, success=success)


def decode_image(b64):
    """
    This function takes a base64-encoded string and decodes it as an image,
    converts it to the appropriate colour space (CIELAB) for colour
    recognition, and returns a cropped version of it so that individual pieces
    can later be extracted.
    """
    # ignore the first 21 characters of b64 data
    encoded_image = np.fromstring(base64.b64decode(b64[21:]), dtype=np.uint8)
    decoded_image = cv2.imdecode(encoded_image, 1)
    converted_image = cv2.cvtColor(decoded_image, cv2.COLOR_BGR2LAB)

    # crop to 144x144 (so we can have 3 48x48 rows/columns)
    cropped_image = converted_image[17:161, 45:189]

    return cropped_image


def standardize_colour_scheme(face, colour_scheme, center_piece):
    """
    This function takes the given colour scheme dictionary and maps the colour
    of the given center piece with the colour that it is supposed to represent.
    """
    # take the midpoint of the piece and determine its L, a, and b values
    # according to the CIELAB standard
    center_midpoint = center_piece[24, 24]
    center_midpoint = (center_midpoint[0] / 2.55,
                       center_midpoint[1] - 128,
                       center_midpoint[2] - 128)

    face_order = ["g", "o", "b", "r", "y", "w"]
    colour_scheme[face_order[face]] = center_midpoint


def identify_colour(square, colour_scheme):
    """
    This function takes pixel values in CIELAB format from a specific square
    and compares it to the preestablished colour scheme, determining which of
    the six colours it is closest to.

    source: http://colormine.org/delta-e-calculator
    """
    closest_colour = ""
    best_delta = math.inf

    square_midpoint = square[24, 24]
    square_midpoint = (square_midpoint[0] / 2.55,
                       square_midpoint[1] - 128,
                       square_midpoint[2] - 128)

    # apply colour difference algorithm against all 6 known colours and keep
    # the closest
    for colour in colour_scheme:
        known_lab = colour_scheme[colour]
        delta = math.sqrt(((known_lab[0] - square_midpoint[0]) ** 2) +
                          ((known_lab[1] - square_midpoint[1]) ** 2) +
                          ((known_lab[2] - square_midpoint[2]) ** 2))

        if delta < best_delta:
            best_delta = delta
            closest_colour = colour

    return closest_colour


def generate_net(c):
    """
    This function takes a large array c of the colour of every piece on every
    face of the Rubik's cube as determined by the program, and returns one
    single string representation of the current state of the cube, according to
    the following diagram:

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

    The string takes the form U1U2U3...R1R2R3...F1...D1...L1...B1..., as
    dictated by this implementation of Kociemba's algorithm.
    """
    u = [c[4][0][2], c[4][1][2], c[4][2][2], c[4][0][1], c[4][1][1], c[4][2][1], c[4][0][0], c[4][1][0], c[4][2][0]]
    r = [c[3][0][0], c[3][0][1], c[3][0][2], c[3][1][0], c[3][1][1], c[3][1][2], c[3][2][0], c[3][2][1], c[3][2][2]]
    f = [c[2][0][0], c[2][0][1], c[2][0][2], c[2][1][0], c[2][1][1], c[2][1][2], c[2][2][0], c[2][2][1], c[2][2][2]]
    d = [c[5][2][0], c[5][1][0], c[5][0][0], c[5][2][1], c[5][1][1], c[5][0][1], c[5][2][2], c[5][1][2], c[5][0][2]]
    l = [c[1][0][0], c[1][0][1], c[1][0][2], c[1][1][0], c[1][1][1], c[1][1][2], c[1][2][0], c[1][2][1], c[1][2][2]]
    b = [c[0][0][0], c[0][0][1], c[0][0][2], c[0][1][0], c[0][1][1], c[0][1][2], c[0][2][0], c[0][2][1], c[0][2][2]]
    net = u + r + f + d + l + b

    state = ''.join(net)
    return state


def visualize_net(net):
    """
    This function takes a large string net of the colour of every piece on
    every face of the Rubik's cube as determined by the generate_net()
    function, and rearranges the pieces in a way that the visualization library
    can properly display.
    """
    # rearrange faces
    new_net = net[33:36] + net[30:33] + net[27:30]
    new_net += net[15:18] + net[12:15] + net[9:12]
    new_net += net[24:27] + net[21:24] + net[18:21]
    new_net += net[6:9] + net[3:6] + net[0:3]
    new_net += net[42:45] + net[39:42] + net[36:39]
    new_net += net[51:54] + net[48:51] + net[45:48]

    return new_net


def kociemba_state(net):
    """
    This function takes a large string net of the colour of every piece on
    every face of the Rubik's cube as determined by the generate_net()
    function, and replaces the individual colour identifiers with a broader
    positional notation to create a new state that can be accepted by
    Kociemba's algorithm.
    """
    net = net.replace('y', 'U')
    net = net.replace('r', 'R')
    net = net.replace('b', 'F')
    net = net.replace('w', 'D')
    net = net.replace('o', 'L')
    net = net.replace('g', 'B')

    return net


if __name__ == "__main__":
    app.run(debug=True)
