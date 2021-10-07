from flask import Flask, render_template, request
from flask import jsonify
from werkzeug.utils import secure_filename

from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from IPython import get_ipython

import string
import random
'''
import keras

# import keras_retinanet
from keras_retinanet import models
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color
'''
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
    return render_template('index.html')

@app.route('/upload', methods = ['GET', 'POST'])
def upload_file():
    global filename
    if request.method == 'POST':
        f = request.files['file']
        save_dir = os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename))
        filename = f.filename
        f.save(save_dir)
        return jsonify({"result":save_dir})

model = ""
filename = ""

@app.route('/detect')
def detect_object():
    image_path = request.args.get('image_path')
    confidence_cutoff = 0.7
    print(image_path)
    detected_result = detect_image.detect(image_path, model, filename, confidence_cutoff)

    return jsonify(detected_result)

if __name__ == '__main__':
    detect_image.init_tf()

    # load retinanet model
    model_path = r'E:\Kuliah\Proyek Data Science\#_PROYEK\Retinanet-Tutorial\keras-retinanet\Dataset_2\snapshots\resnet50_pascal_15.h5'
    model = detect_image.get_model(model_path)

    app.run(host='0.0.0.0', port='80')
