#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import pigpio

from crypt import crypt
from hmac import compare_digest

from functools import wraps
from flask import Flask, Response, request, render_template, redirect, url_for


# Basic configuration
img_file = '/tmp/pulicam-raspistill.jpg'
frame_time = 2.5
pan_gpio = 23
tilt_gpio = 24
reverse_cam = True

# User dict: key = user, value = password
# Password must be the result of crypt.crypt('password'). Example using python3:
# python -c "import crypt; print(crypt.crypt('password'))"
userlist = {
    'admin': '$6$6I2vyM9D9d5DoNTe$xvPKCM5J6FOKzhpKUm3Tv22QwXZiSp7czuymyBO2HaD2/JIPDEFN2IaWCeI1NNY9blClFDXzHIr8mBwcoOrl5.'
}

# Shortcuts
memories = {
    'comida': {'name': 'Comida', 'pan': 1300, 'tilt': 1200},
    'mueble': {'name': 'Mueble', 'pan': 1200, 'tilt': 1350},
    'rascador': {'name': 'Rascador', 'pan': 1450, 'tilt': 1400},
    'centrado': {'name': 'Centrado', 'pan': 1350, 'tilt': 1250},
    'salon': {'name': 'Salón', 'pan': 1850, 'tilt': 1300}
}

# Expert configuration
boundary = 'pulicam'

max_pulse = 2000
cen_pulse = 1500
min_pulse = 1000

# GPIO
pigpio.exceptions = False
pig = pigpio.pi('localhost', 8888)


def move_servo(servo, direction):
    new_pulse = cen_pulse

    sgpio = pan_gpio
    if servo == 'tilt':
        sgpio = tilt_gpio

    if direction is not 'center':
        step = 50
        if direction in ['right', 'up']:
            step = -50

        if reverse_cam:
            step = -step

        try:
            pulse = pig.get_servo_pulsewidth(sgpio)
        except:
            pulse = 0

        if min_pulse > pulse or max_pulse < pulse:
            pulse = new_pulse

        new_pulse = pulse + step
        if not min_pulse <= new_pulse <= max_pulse:
            new_pulse = pulse

    pig.set_servo_pulsewidth(sgpio, new_pulse)

    return new_pulse


def memory_servos(memory):
    if memory in memories.keys():
        pig.set_servo_pulsewidth(pan_gpio, memories[memory]['pan'])
        pig.set_servo_pulsewidth(tilt_gpio, memories[memory]['tilt'])


# Flask app
app = Flask(__name__)


# HTTP Auth
def check_auth(username, password):
    if username in userlist:
        return compare_digest(userlist[username],
                              crypt(password, userlist[username]))

    else:
        return False


def authenticate():
    return Response(
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


# Routes
@app.route('/')
@requires_auth
def index():
    return render_template('index.html', memories=memories)


@app.route('/stream')
@requires_auth
def stream():
    def mjpeg_stream():
        while True:
            with open(img_file, 'rb') as f:
                img = f.read()

                hdr = '--{}\r\n'.format(boundary)
                hdr += 'Content-Type: image/jpeg\r\n'
                # hdr += 'Content-Length: {}\r\n'.format(len(img))
                hdr += '\r\n'

                yield(bytes(hdr, 'utf-8') + img + b'\r\n\r\n')

            time.sleep(frame_time)

    return Response(mjpeg_stream(),
                    mimetype='multipart/x-mixed-replace; '
                    'boundary={}'.format(boundary))


@app.route('/servo/pan')
@requires_auth
def servo_pan():
    move_servo('pan', 'center')
    return redirect(url_for('index'))


@app.route('/servo/pan/left')
@requires_auth
def servo_pan_left():
    move_servo('pan', 'left')
    return redirect(url_for('index'))


@app.route('/servo/pan/right')
@requires_auth
def servo_pan_right():
    move_servo('pan', 'right')
    return redirect(url_for('index'))


@app.route('/servo/tilt')
@requires_auth
def servo_tilt():
    move_servo('tilt', 'center')
    return redirect(url_for('index'))


@app.route('/servo/tilt/down')
@requires_auth
def servo_tilt_down():
    move_servo('tilt', 'down')
    return redirect(url_for('index'))


@app.route('/servo/tilt/up')
@requires_auth
def servo_tilt_up():
    move_servo('tilt', 'up')
    return redirect(url_for('index'))


@app.route('/servo/memory/<memo>')
@requires_auth
def servo_memory(memo):
    memory_servos(memo)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True, debug=True)