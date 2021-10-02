# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

# %%
import os
from PIL import Image

import string
import random


# %%
THRES_SCORE = 0.8

# show images inline
get_ipython().run_line_magic('matplotlib', 'inline')

# automatically reload modules when they have changed
get_ipython().run_line_magic('reload_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')

# import keras
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

def get_session():
    config = tf.compat.v1.ConfigProto()
    config.gpu_options.allow_growth = True
    return tf.compat.v1.Session(config=config)

tf.compat.v1.keras.backend.set_session(get_session())


# %%
model_path = r'E:\Kuliah\Proyek Data Science\#_PROYEK\Retinanet-Tutorial\keras-retinanet\Dataset_1\snapshots\resnet50_pascal_14.h5'

# load retinanet model
print("Loading Model: {}".format(model_path))
model = models.load_model(model_path, backbone_name='resnet50')

#Check that it's been converted to an inference model
try:
    model = models.convert_model(model)
except:
    print("Model is likely already an inference model")


# %%
#from url
def id_generator(size=12, chars=string.ascii_letters + string.digits):
   return ''.join(random.choice(chars) for _ in range(size))

image_url = "https://www.mercurynews.com/wp-content/uploads/2019/07/EBT-L-CHEATERS-06XX-1.jpg?w=1020"
image_path = tf.keras.utils.get_file('img-{}'.format(id_generator()), origin=image_url)


# %%
#from local
image_path = r'E:\Kuliah\Proyek Data Science\#_PROYEK\Retinanet-Tutorial\keras-retinanet\images\51.jpg'


# %%
print("Loading image from {}".format(image_path))
image = np.asarray(Image.open(image_path).convert('RGB'))
image = image[:, :, ::-1].copy()


# %%
confidence_cutoff = 0.2


# %%
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
plt.figure(figsize=(50, 50))
plt.axis('off')
plt.imshow(draw)
plt.show()

