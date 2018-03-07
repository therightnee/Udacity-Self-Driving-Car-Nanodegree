import csv
import cv2
import numpy as np
from tqdm import tqdm
import glob
import time

from keras.utils import plot_model
from keras.models import Sequential, Model, load_model
from keras.layers import Flatten, Dense, Lambda, Cropping2D, Conv2D, Dropout
from keras import optimizers

model_list = glob.glob('*.h5')
model = load_model(model_list[0])
print("LOADED " + model_list[0])


plot_model(model, to_file='model.png')