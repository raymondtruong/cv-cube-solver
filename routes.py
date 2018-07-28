from app import app
from flask import render_template, request
import json
import matplotlib.pyplot as plt
import base64
from PIL import Image
from io import BytesIO
import numpy as np
import cv2



@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", test="Home")


@app.route("/solve", methods=["POST"])
def solve():
    test = "Test"
    json_images = request.form["images"]
    images = json.loads(json_images)
    new_images = [None] * 6

    for i in range(6):
        img = base64.b64decode(images[0][21:])
        npimg = np.fromstring(img, dtype=np.uint8)

        source = cv2.imdecode(npimg, 1)
        edges = cv2.Canny(source,100,200)

        (_, x) = cv2.imencode(".png", edges)
        y = "data:image/png;base64," + str(base64.b64encode(x))[2:-1]


        # cv2.imshow("some window", edges)
        new_images[i] = y

    return render_template("solve.html", test=y, old_images=images, new_images=new_images)
