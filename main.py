from flask import Flask, render_template, request
from flask import jsonify
from werkzeug.utils import secure_filename

from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from IPython import get_ipython

from PIL import Image

import string
import random

import keras

# import keras_retinanet
from keras_retinanet import models
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color

# import miscellaneous modules
import matplotlib.pyplot as plt
import cv2
import os
import numpy as np
import time

# set tf backend to allow memory to grow, instead of claiming everything
import tensorflow as tf

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
def detect_object(confidence_cutoff=0.3):
    image_path = request.args.get('image_path')
    print(image_path)
    #image_path = r'E:\Kuliah\Proyek Data Science\#_PROYEK\Retinanet-Tutorial\keras-retinanet\images\51.jpg'
    image = np.asarray(Image.open(image_path).convert('RGB'))
    image = image[:, :, ::-1].copy()
    labels_to_names = {0: 'mobil', 1: 'motor'}

    # copy to draw on
    draw = image.copy()
    draw = cv2.cvtColor(draw, cv2.COLOR_BGR2RGB)

    # Image formatting specific to Retinanet
    image2 = preprocess_image(image)
    image2, scale = resize_image(image2)

    # Run the inference
    start = time.time()

    boxes, scores, labels = model.predict_on_batch(np.expand_dims(image2, axis=0))
    print("processing time: ", time.time() - start)

    # correct for image scale
    boxes /= scale

    # visualize detections
    for box, score, label in zip(boxes[0], scores[0], labels[0]):
        # scores are sorted so we can break
        if score < confidence_cutoff:
            break

        #Add boxes and captions
        color = (255, 255, 255)
        thickness = 2
        b = np.array(box).astype(int)
        cv2.rectangle(draw, (b[0], b[1]), (b[2], b[3]), color, thickness, cv2.LINE_AA)

        if(label > len(labels_to_names)):
            print("WARNING: Got unknown label, using 'detection' instead")
            caption = "Detection {:.3f}".format(score)
        else:
            caption = "{} {:.3f}".format(labels_to_names[label], score)

        #cv2.putText(draw, caption, (b[0], b[1] - 10), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 3)
        cv2.putText(draw, caption, (b[0], b[1] - 10), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

    #Write out image
    draw = Image.fromarray(draw)
    detected_image_path = './static/uploads/detection/' + filename
    draw = draw.save(detected_image_path)
    #plt.figure(figsize=(50, 50))
    #plt.axis('off')
    #plt.imshow(draw)
    #plt.show()
    return jsonify({"result":detected_image_path})

if __name__ == '__main__':
    def get_session():
        config = tf.compat.v1.ConfigProto()
        config.gpu_options.allow_growth = True
        return tf.compat.v1.Session(config=config)

    tf.compat.v1.keras.backend.set_session(get_session())

    model_path = r'E:\Kuliah\Proyek Data Science\#_PROYEK\Retinanet-Tutorial\keras-retinanet\Dataset_1\snapshots\resnet50_pascal_14.h5'

    # load retinanet model
    print("Loading Model: {}".format(model_path))
    model = models.load_model(model_path, backbone_name='resnet50')

    #Check that it's been converted to an inference model
    try:
        model = models.convert_model(model)
    except:
        print("Model is likely already an inference model")


    app.run(host='0.0.0.0', port='80')
