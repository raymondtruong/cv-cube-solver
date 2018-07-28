from app import app
from flask import render_template, request
import json

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", test="Home")

@app.route("/solve", methods=["POST"])
def solve():
    test = "Test"
    json_images = request.form["images"]
    images = json.loads(json_images)
    return render_template("solve.html", test=len(images), images=images)
