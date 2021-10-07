from re import L
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

from PIL import Image

def get_session():
    config = tf.compat.v1.ConfigProto()
    config.gpu_options.allow_growth = True
    return tf.compat.v1.Session(config=config)

def init_tf():
    tf.compat.v1.keras.backend.set_session(get_session())

def get_model(model_path):
    print("Loading Model: {}".format(model_path))
    model = models.load_model(model_path, backbone_name='resnet50')

    #Check that it's been converted to an inference model
    try:
        model = models.convert_model(model)
    except:
        print("Model is likely already an inference model")
    
    return model

def detect(image_path, model, filename, confidence_cutoff):
    image = np.asarray(Image.open(image_path).convert('RGB'))
    image = image[:, :, ::-1].copy()
    labels_to_names = {0: 'motor', 1: 'mobil'}

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

    detect_result = dict()

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

        if labels_to_names[label] in detect_result:
            detect_result[labels_to_names[label]] = detect_result[labels_to_names[label]] + 1
        else:
            detect_result[labels_to_names[label]] = 1

        #cv2.putText(draw, caption, (b[0], b[1] - 10), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 3)
        cv2.putText(draw, caption, (b[0], b[1] - 10), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

    #Write out image
    draw = Image.fromarray(draw)
    detected_image_path = './static/uploads/detection/' + filename
    draw = draw.save(detected_image_path)

    detect_result['path'] = detected_image_path

    return detect_result