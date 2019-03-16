import csv
import cv2
import numpy as np
from tqdm import tqdm
import glob
import time

#Initialize Variables
car_images = []
steering_angles = []
data_sources = glob.glob('./starting_data')

#Define Functions

#Fix the filepath
def path_fix(org_path, folder_loc):
    filename = org_path.split('/')[-1]
    new_path = folder_loc + '/IMG/' + filename
    return new_path
#Prepare the set of images for training
def training_set_prep(source_folder):
    new_source = []
    with open (source_folder + '/driving_log.csv') as csvfile:
        reader = csv.reader(csvfile)
        for line in reader:
            new_source.append(line)
            
    for line in tqdm(new_source):
        #Grab Steering Angle Measurements
        center_steering_ang = float(line[3])
        #Add in side images (potentially calculate optimal correction factor)
        #create adjusted steering measurements for the side camera images
        correction = 0.2 # this is a parameter to tune
        steering_left = center_steering_ang + correction
        steering_right = center_steering_ang - correction
        #read in images from center, left and right cameras
        #Convert image paths to new locations
        center_path = path_fix(line[0], source_folder)
        left_path = path_fix(line[1], source_folder)
        right_path = path_fix(line[2], source_folder)
        img_center = cv2.imread(center_path)
        img_left = cv2.imread(left_path)
        img_right = cv2.imread(right_path)
        #add images and angles to data set
        car_images.extend([img_center, img_left, img_right])
        steering_angles.extend([center_steering_ang, steering_left, steering_right])

#Build Training Sets
for source in data_sources:
    print(source)
    training_set_prep(source)

#Hardcoded test for initial dataset - only use to verify location
#training_set_prep('./starting_data')

#Set tf variables for input and labels
X_train = np.array(car_images)
print(len(car_images))
y_train = np.array(steering_angles)

#Load necessary Keras modules
from keras.models import Sequential, Model, load_model
from keras.layers import Flatten, Dense, Lambda, Cropping2D, Conv2D, Dropout
from keras import optimizers

#See if a model already exists - load that existing model and continue training it
try:
    #Reload model
    model_list = glob.glob('*.h5')
    #print(model_list)
    model = load_model(model_list[0])
    print("LOADED " + model_list[0])
#If no valid model exists, the follow code defines the model architecture and trains it
except:
    #CNN MODEL HERE
    model = Sequential()
    model.add(Lambda(lambda x: x/(255.0-0.5), input_shape=(160,320,3)))
    model.add(Cropping2D(cropping=((50,20), (0,0))))

    #5x5 Convolve 1
    model.add(Conv2D(24, (5, 5), strides=(2, 2), activation='relu'))
    #5x5 Convolve 2
    model.add(Conv2D(36, (5, 5), strides=(2, 2), activation='relu'))
    #5x5 Convolve 3
    model.add(Conv2D(48, (5, 5), strides=(2, 2), activation='relu'))
    #3x3 Convolve 1
    model.add(Conv2D(64, (3, 3), strides=(1, 1), activation='relu'))
    #3x3 Convolve 2
    model.add(Conv2D(64, (3, 3), strides=(1, 1), activation='relu'))

    #Flatten
    model.add(Flatten())

    # #3X Fully Connected layers
    #model.add(Dense(1164, activation='sigmoid'))
    model.add(Dense(100, activation='sigmoid'))
    #model.add(Dropout(0.2))
    model.add(Dense(50, activation='sigmoid'))
    model.add(Dense(10, activation='softmax'))
    model.add(Dense(1))
    adam_mod = optimizers.Adam(lr=0.0005, decay=0.001)
    model.compile(loss='mse', optimizer=adam_mod)

#Track calculation time
t0 = time.time()

#model.fit(X_train, y_train, validation_split=0.3, shuffle=True, nb_epoch=5, verbose=2)

#Following section used to generate training loss vs. validation loss graphs
#Import Agg to prevent Invalid DISPLAY variable
import matplotlib
matplotlib.use('Agg') # Must be before importing matplotlib.pyplot or pylab!

import matplotlib.pyplot as plt

#Run the model with a validation set 30% of the input set
history_object = model.fit(X_train, y_train, 
    validation_split=0.3, shuffle=True, nb_epoch=3, verbose=1)


#plotting code inspired by darienmt - https://github.com/darienmt/CarND-Behavioral-Cloning-P3/blob/master/model.py
# print the keys contained in the history object
print(history_object.history.keys())
t1 = time.time()
print(t1-t0)
cur_time = str(int(t1))

# plot the training and validation loss for each epoch
fig = plt.figure(1)
plt.plot(history_object.history['loss'])
plt.plot(history_object.history['val_loss'])
plt.title('model mean squared error loss')
plt.ylabel('mean squared error loss')
plt.xlabel('epoch')
plt.legend(['training set', 'validation set'], loc='upper right')
fig.savefig(cur_time + 'error_tracking.png', dpi=400)

#Save the model to a unique name that can be loaded or downloaded
model.save(cur_time + '-model' + '.h5')

print(cur_time)