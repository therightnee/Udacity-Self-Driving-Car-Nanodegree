## Writeup Template
### You can use this file as a template for your writeup if you want to submit it as a markdown file, but feel free to use some other method and submit a pdf if you prefer.

---

**Vehicle Detection Project**

The goals / steps of this project are the following:

* Perform a Histogram of Oriented Gradients (HOG) feature extraction on a labeled training set of images and train a classifier Linear SVM classifier
* Optionally, you can also apply a color transform and append binned color features, as well as histograms of color, to your HOG feature vector. 
* Note: for those first two steps don't forget to normalize your features and randomize a selection for training and testing.
* Implement a sliding-window technique and use your trained classifier to search for vehicles in images.
* Run your pipeline on a video stream (start with the test_video.mp4 and later implement on full project_video.mp4) and create a heat map of recurring detections frame by frame to reject outliers and follow detected vehicles.
* Estimate a bounding box for vehicles detected.

[//]: # (Image References)
[image1]: ./examples/car_not_car.png
[image2]: ./examples/HOG_example.jpg
[image3]: ./examples/sliding_windows.jpg
[image4]: ./examples/sliding_window.jpg
[image5]: ./examples/bboxes_and_heat.png
[image6]: ./examples/labels_map.png
[image7]: ./examples/output_bboxes.png
[video1]: ./project_video.mp4

## [Rubric](https://review.udacity.com/#!/rubrics/513/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  [Here](https://github.com/udacity/CarND-Vehicle-Detection/blob/master/writeup_template.md) is a template writeup for this project you can use as a guide and a starting point.  

Here you go!

### Histogram of Oriented Gradients (HOG)

#### 1. Explain how (and identify where in your code) you extracted HOG features from the training images.

In the second cell of the "Vehicle_Detection.ipynb" notebook, I wrote a method that does both HOG feature extraction and pre-processing for colorspace detection.

Instead of converting the 3-layer image through a single gradient colorspace, I ran HOG feature extraction on each layer, after converting the image into the desired colorspace.

Here is the input image:

Here is the normalized HLS converted image:

This is what 'ch1' which is fed into the HOG extraction looks like:

![alt text][image2]

#### 2. Explain how you settled on your final choice of HOG parameters.

***RUN CODE WITH VARIOUS ORIENTATIONS, PIXELS PER CELL, CELLS PER BLOCK ETC***

In the sub-sampling version there was greater value to modifying the cells per block and pixels per cell, but given that I know the input patch would only be 64x64, that gave me a more narrow range of effective values.


#### 3. Describe how (and identify where in your code) you trained a classifier using your selected HOG features (and color features if you used them).

Based on the advanced lane finding project I knew I wanted to use the HLS color space, since I saw that it was powerful in detecting lane lines, and would help my classifier detect road features and detect them. I was a little concerned how this colorspace might work with the vehicle and non-vehicle training set because the images were not particularly variant in terms of lighting

### Sliding Window Search

#### 1. Describe how (and identify where in your code) you implemented a sliding window search.  How did you decide what scales to search and how much to overlap windows?

I created a list of various scales and scaled the images to search over various window sizes. A render of what that the various scales looked like are below.

![alt text][image3]

#### 2. Show some examples of test images to demonstrate how your pipeline is working.  What did you do to optimize the performance of your classifier?

I leaned heavily on the test images to track how changes to my parameters affected my detection rates.

![alt text][image4]
---

### Video Implementation

#### 1. Provide a link to your final video output.  Your pipeline should perform reasonably well on the entire project video (somewhat wobbly or unstable bounding boxes are ok as long as you are identifying the vehicles most of the time with minimal false positives.)

Here's a [link to my video result](./Bounded_Output.mp4)


#### 2. Describe how (and identify where in your code) you implemented some kind of filter for false positives and some method for combining overlapping bounding boxes.

Heatmaps were implemented, and the threshold value tuned to eliminate some false positives.

Also, in addition to heatmaps, I implemented a physically based check that looked at the height and width of the box being drawn and rejected it if it was too small. This is relatively crude, but was able to eliminate a good deal of mis-classified noise that was had a high enough heatmap value to qualify as an object, but was too small to possibly be a vehicle.

### Here are six frames and their corresponding heatmaps:

![alt text][image5]

### Here is the output of `scipy.ndimage.measurements.label()` on the integrated heatmap from all six frames:
![alt text][image6]

### Here the resulting bounding boxes are drawn onto the last frame in the series:
![alt text][image7]



---

### Discussion

#### 1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

I attempted to implement sub-sampling both to improve detection rates and also increase the scale range that I could cycle through.  My current method calculates the HOG for every patch fed into the classifier, which is computationally intensive. If I could just calculate the HOG features once and extract that information it would be much more efficient, and possibly more capable.

Another issue that is apparent in the output video is that I chose poorly regarding the colorspace. The classifier easily detects dark colored vehicles, but largely ignores the white one. It is able to pick up some features like the headlights, tires, and rear window, but is unable to piece these elements together into one holistic object.
