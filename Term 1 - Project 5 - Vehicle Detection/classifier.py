import cv2
#CV2 loads everythings as BGR
import glob
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from skimage.feature import hog
from sklearn.svm import LinearSVC
from sklearn.datasets import make_classification
from sklearn.preprocessing import StandardScaler
from sklearn.cross_validation import train_test_split
from scipy.ndimage.measurements import label
from tqdm import tqdm

#Train Classifier to look for HOG and Color Spaces


#HOG Feature Extractor
def patch_analyzer(image, size=(16,16), nbins=16, bins_range=(0,256)):
    grey_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    fd, hog_image = hog(grey_img, orientations=8, pixels_per_cell=(8, 8),
                        cells_per_block=(1, 1), visualise=True)

    #Color Space Extraction

    #conv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    conv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)

    #Downsample 0.25x from original
    #Original patch is 64px
    # Use cv2.resize().ravel() to create the feature vector
    scale_feature = cv2.resize(conv_img, size).ravel() 


    #Create Histograms from scaled image
    c1_hist = np.histogram(image[:,:,0], bins=nbins, range=bins_range)
    c2_hist = np.histogram(image[:,:,1], bins=nbins, range=bins_range)
    c3_hist = np.histogram(image[:,:,2], bins=nbins, range=bins_range)
    # Concatenate the histograms into a single feature vector
    hist_features = np.concatenate((c1_hist[0], c2_hist[0], c3_hist[0]))


    #Combine and Normalized Data
    feature_list = [fd, scale_feature, hist_features]
    # Create an array stack, NOTE: StandardScaler() expects np.float64
    tmp_x = np.concatenate(feature_list).astype(np.float64)

    return tmp_x, image, hog_image

#Train the classifier using patch_analyzer
vehicles = glob.glob('vehicles/*/*.png')
non_vehicles = glob.glob('non-vehicles/*/*.png')
image_loc_list = non_vehicles + vehicles

features_array = np.asarray([patch_analyzer(cv2.imread(image))[0] for image in tqdm(image_loc_list)])

np.save('LinearSVC_GTI_KTTT', features_array)



#Number of non-cars are represented by zeros
#Number of cars are represented by ones
img_labels = np.concatenate([np.zeros(8968), np.ones(8792)])


features_array = np.load('LinearSVC_GTI_KTTT.npy')

X_train, X_test, y_train, y_test= train_test_split(features_array, img_labels, test_size=0.35)

# Fit a per-column scaler
X_scaler = StandardScaler().fit(X_train)
# Apply the scaler to X
scaled_X_train = X_scaler.transform(X_train)
scaled_X_test = X_scaler.transform(X_test)

print("LinearSVC Reached")

#Implement Linear SVM Classifier
clf = LinearSVC(C=0.001,verbose=1, random_state=0)
clf.fit(scaled_X_train, y_train)

#Run trained classifier on test image

print(clf.score(scaled_X_train, y_train)*100)

print(clf.score(scaled_X_test, y_test)*100)



#HOG Sub-Sampling on search in the band below the horizon, above the hood

## Return a list of image patches
test_image = cv2.imread(test_image_list[0])

def sliding_window(img, y_start=360, y_stop=720, patch_size=64, stride=16, scale=1):
    #Convert to float-32 value and normalize
    image = img.astype(np.float32)/255
    trans_img = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
    imshape = trans_img.shape
    if scale != 1:
        print("trans")
        trans_img = cv2.resize(trans_img, (np.int(imshape[1]/scale), np.int(imshape[0]/scale)))
    y_stop = np.int(imshape[0]/scale)
    x_stop = np.int(imshape[1]/scale)
    
    patch_list = []
    
    for x in range(0, x_stop-patch_size, stride):
        for y in range(y_start, y_stop-patch_size, stride):
            ypos_end = y+patch_size
            xpos_end = x+patch_size
            cur_patch = trans_img[y:ypos_end, x:xpos_end]
            print((x, y), (xpos_end, ypos_end))
            # Extract HOG for this patch
            patch_list.append([cur_patch, (x, y), (xpos_end, ypos_end)])
    return patch_list, trans_img


# Here is your draw_boxes function from the previous exercise
def draw_boxes(img, bboxes, color=(0, 0, 255), thick=6):
    # Make a copy of the image
    imcopy = np.copy(img)
    # Iterate through the bounding boxes
    for bbox in bboxes:
        # Draw a rectangle given bbox coordinates
        cv2.rectangle(imcopy, bbox[1], bbox[2], color, thick)
    # Return the image copy with boxes drawn
    return imcopy

#Iterate through three different scales
scale_list = [0.5, 1, 1.5, 2]

for scale in scale_list:
    print(scale)
    windows = sliding_window(test_image, y_start=0, y_stop=720, patch_size = 64, scale=scale)
    window_img = draw_boxes(windows[1], windows[0], color=(0, 0, 255), thick=1)
    plt.imshow(window_img)
    plt.show()

#Iterate through three different scales
scale_list = [0.5, 1, 1.5]

for scale in scale_list:
    sliding_window(test_image, y_stop = 500)

#Feed function trained LinearSVC classifier and list of patches to predict locations
def search_windows(img_list):
    positives_list = []
    for entry in img_list:
        prediction = clf.predict(X_scaler.transform(patch_analyzer(entry[0])[0]))
        if prediction == 1:
            positives_list.append(entry[1:])
    return positives_list
    
box_list = search_windows(test_image)

#Draw bounding boxes around potential cars
draw_image = np.copy(test_image)

# Define a function to draw bounding boxes
def draw_boxes(img, bboxes, color=(0, 0, 255), thick=6):
    # Make a copy of the image
    imcopy = np.copy(img)
    # Iterate through the bounding boxes
    for bbox in bboxes:
        # Draw a rectangle given bbox coordinates
        cv2.rectangle(imcopy, bbox[0], bbox[1], color, thick)
    # Return the image copy with boxes drawn
    return imcopy


#Overlay outputs into heatmap, generate heatmap image + bounding box cluster images

def heat_map(img, box_list, threshold=0):
    heat = np.zeros_like(image[:,:,0]).astype(np.float)
    #Iterate through all the positively identified windows
    for entry in box_list:
        # Add += 1 for all pixels inside each bbox
        # Assuming each "box" takes the form ((x1, y1), (x2, y2))
        img[entry[0][1]:entry[1][1], entry[0][0]:box[1][0]] += 1
    #Zero out pixels below the threshold
    img[img <= threshold] = 0
    return img

#Labeled box code same as lesson function
def draw_labeled_bboxes(img, labels):
    # Iterate through all detected cars
    for car_number in range(1, labels[1]+1):
        # Find pixels with each car_number label value
        nonzero = (labels[0] == car_number).nonzero()
        # Identify x and y values of those pixels
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])
        # Define a bounding box based on min/max x and y
        bbox = ((np.min(nonzerox), np.min(nonzeroy)), (np.max(nonzerox), np.max(nonzeroy)))
        # Draw the box on the image
        cv2.rectangle(img, bbox[0], bbox[1], (0,0,255), 6)
    # Return the image
    return img

# Add heat to each box in box list and threshold the image for false positives
heat = heat_map(heat,box_list, 2)

# Visualize the heatmap when displaying    
heatmap = np.clip(heat, 0, 255)

# Find final boxes from heatmap using label function
labels = label(heatmap)
draw_img = draw_labeled_bboxes(np.copy(image), labels)

fig = plt.figure()
plt.subplot(121)
plt.imshow(draw_img)
plt.title('Car Positions')
plt.subplot(122)
plt.imshow(heatmap, cmap='hot')
plt.title('Heat Map')
fig.tight_layout()

"""
print(cv2.__version__)
vidcap = cv2.VideoCapture('')
success,image = vidcap.read()
count = 0
success = True
while success:
  success,image = vidcap.read()
  print 'Read a new frame: ', success
  box_list = search_windows(image)
  # Add heat to each box in box list and threshold the image for false positives
  heatmap = np.clip(heat_map(heat,box_list, 2), 0, 255)
  #Merge the pixels
  merged_cars = label(heatmap)
  draw_labeled_bboxes(merged_cars)
  cv2.imwrite("frame%d.png" % count, image)     # save frame as PNG file
  count += 1
"""