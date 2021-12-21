from flask import Flask, render_template, request
from flask import jsonify
from werkzeug.utils import secure_filename

from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from IPython import get_ipython

from os import listdir

import detect_image
# import miscellaneous modules
import matplotlib.pyplot as plt
import cv2
import os
import numpy as np
import time

# set tf backend to allow memory to grow, instead of claiming everything
#import tensorflow as tf

app = Flask(__name__, template_folder='template')
app.config['UPLOAD_FOLDER'] = './static/uploads'
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route('/')
def index():
    models = [f for f in listdir('./static/models')]

    return render_template('index.html', models=models)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    global filename
    if request.method == 'POST':
        f = request.files['file']
        save_dir = os.path.join(
            app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
        filename = f.filename
        f.save(save_dir)
        return jsonify({"result": save_dir})

model = ""
filename = ""

@app.route('/get_model', methods=['GET', 'POST'])
def get_model():
    global model
    model_name = request.args.get("model_name")
    model_path = './static/models/'+model_name
    model = detect_image.get_model(model_path)
    return jsonify({"result": model_name})

@app.route('/detect')
def detect_object():
    image_path = request.args.get('image_path')
    mobil_conf = float(request.args.get('mobil_conf'))
    motor_conf = float(request.args.get('motor_conf'))
    sedan_conf = float(request.args.get('sedan_conf'))
    truk_conf = float(request.args.get('truk_conf'))
    bus_conf = float(request.args.get('bus_conf'))
    confidence_cutoff = {'mobil': mobil_conf, 'motor': motor_conf, 'sedan': sedan_conf, 'bus': bus_conf, 'truk': truk_conf}
    print(image_path, mobil_conf, motor_conf, sedan_conf)
    result = detect_image.detect(
        image_path, model, filename, confidence_cutoff)

    return jsonify(result)


if __name__ == '__main__':
    detect_image.init_tf()

    app.run(host='0.0.0.0', port='80')
