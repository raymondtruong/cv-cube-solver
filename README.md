# CV Cube Solver

## Live Demo
[Try me!](https://raymondtruong.pythonanywhere.com/)

## About
A computer vision Rubik's cube solver implementing Kociemba's two-phase algorithm.

Created as a Python web application utilizing the OpenCV library for image recognition, the [TwistySim](http://cube.crider.co.uk/twistysim.html) JavaScript API for puzzle visualizations, and [Maxim Tsoy's Python port of Kociemba's algorithm](https://github.com/muodov/kociemba).

## Dependencies
(see [requirements.txt](/requirements.txt))

## Usage
```
$ git clone https://github.com/raymondtruong/cv-cube-solver.git
$ cd cv-cube-solver
$ python3 -m venv env && . env/bin/activate
(env) $ pip3 install -r requirements.txt
(env) $ python3 main.py
```
The app can then be accessed at 127.0.0.1:5000.

## Screenshots
![Capture](https://user-images.githubusercontent.com/11844501/45581376-d71f5880-b86a-11e8-93c3-5387c478c6e1.jpg)
![Preview](https://user-images.githubusercontent.com/11844501/45581379-f1f1cd00-b86a-11e8-91b5-f0bf6a8608d0.jpg)
![Solve](https://user-images.githubusercontent.com/11844501/45581381-f322fa00-b86a-11e8-9032-f6c429c87d45.jpg)
