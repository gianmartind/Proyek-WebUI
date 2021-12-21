from re import L
import keras

# import keras_retinanet
from keras_retinanet import models
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color

# import miscellaneous modules
import cv2
import numpy as np
import time

# set tf backend to allow memory to grow, instead of claiming everything
import tensorflow as tf

from PIL import Image
import string
import random

import plotly.express as px
import plotly.offline

def get_session():
    config = tf.compat.v1.ConfigProto()
    config.gpu_options.allow_growth = True
    return tf.compat.v1.Session(config=config)


def init_tf():
    tf.compat.v1.keras.backend.set_session(get_session())


def get_model(model_path):
    print("Loading Model: {}".format(model_path))
    model = models.load_model(model_path, backbone_name='resnet50')

    # Check that it's been converted to an inference model
    try:
        model = models.convert_model(model)
    except:
        print("Model is likely already an inference model")

    return model


def draw_text(img, text,
              font=cv2.FONT_HERSHEY_COMPLEX_SMALL,
              pos=(0, 0),
              font_scale=1,
              font_thickness=1,
              text_color=(255, 255, 255),
              text_color_bg=(0, 0, 0)
              ):

    x, y = pos
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size
    cv2.rectangle(img, pos, (x + text_w, y + text_h), text_color_bg, -1)
    cv2.putText(img, text, (x, y + text_h + font_scale - 1),
                font, font_scale, text_color, font_thickness)

    return text_size


def compute_iou(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # compute the area of intersection rectangle
    interArea = abs(max((xB - xA, 0)) * max((yB - yA), 0))
    if interArea == 0:
        return 0
    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = abs((boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    boxBArea = abs((boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)

    # return the intersection over union value
    return iou

def id_generator(size=12, chars=string.ascii_letters + string.digits):
   return ''.join(random.choice(chars) for _ in range(size))

def detect(image_path, model, filename, confidence_cutoff):
    image = np.asarray(Image.open(image_path).convert('RGB'))
    image = image[:, :, ::-1].copy()
    labels_to_names = {0: 'motor', 1: 'mobil', 2: 'sedan', 3: 'truk', 4: 'bus'}

    # copy to draw on
    draw = image.copy()
    draw = cv2.cvtColor(draw, cv2.COLOR_BGR2RGB)

    # Image formatting specific to Retinanet
    image2 = preprocess_image(image)
    image2, scale = resize_image(image2)

    # Run the inference
    start = time.time()

    boxes, scores, labels = model.predict_on_batch(
        np.expand_dims(image2, axis=0))
    print("processing time: ", time.time() - start)

    # correct for image scale
    boxes /= scale

    detect_result = {"mobil": 0, "motor": 0, "sedan": 0, "truk": 0, "bus": 0}

    cutoff_motor = confidence_cutoff['motor']
    cutoff_mobil = confidence_cutoff['mobil']
    cutoff_sedan = confidence_cutoff['sedan']
    cutoff_truk = confidence_cutoff['truk']
    cutoff_bus = confidence_cutoff['bus']


    i = 0
    # visualize detections
    for box, score, label in zip(boxes[0], scores[0], labels[0]):
        # if overlap break

        # scores are sorted so we can break
        if label == 0 and score < cutoff_motor:
            continue
        elif label == 1 and score < cutoff_mobil:
            continue
        elif label == 2 and score < cutoff_sedan:
            continue
        elif label == 3 and score < cutoff_truk:
            continue
        elif label == 4 and score < cutoff_bus:
            continue
        elif label == -1:
            continue
        i += 1
        # Add boxes and captions
        color = (255, 255, 255)
        thickness = 2
        b = np.array(box).astype(int)
        cv2.rectangle(draw, (b[0], b[1]), (b[2], b[3]),
                      color, thickness, cv2.LINE_AA)

        if(label > len(labels_to_names)):
            print("WARNING: Got unknown label, using 'detection' instead")
            caption = "Detection {:.3f}".format(score)
        else:
            caption = "{} {:.3f}".format(labels_to_names[label], score)

        detect_result[labels_to_names[label]] = detect_result[labels_to_names[label]] + 1

        #cv2.putText(draw, caption, (b[0], b[1] - 10), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 3)
        #cv2.putText(draw, caption, (b[0], b[1] - 10), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        draw_text(draw, caption, pos=(b[0], b[1] - 10))

    # Write out image
    draw = Image.fromarray(draw)
    detected_image_path = './static/uploads/detection/' + id_generator() + filename
    draw = draw.save(detected_image_path)

    result = dict()
    result['path'] = detected_image_path
    result['count'] = detect_result

    return result
