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

[image1]: ./WriteUp_Images/HOG_Feature_Mods/8O_8x8_1x1CELL_HOGwHSV.png

[image2]: ./WriteUp_Images/HOG_Feature_Mods/8O_8x8_1x1CELL_HOGwLAB.png
[image3]: ./WriteUp_Images/HOG_Feature_Mods/8O_8x8_1x1CELL_HOGwYCrCb.png

[image4]: ./WriteUp_Images/HOG_Feature_Mods/12O_4x4_2x2CELL_HOGwHSV.png
[image5]: ./WriteUp_Images/HOG_Feature_Mods/12O_4x4_HOGwHSV.png

[image6]: ./WriteUp_Images/Sliding_Window.png

[image7]: ./WriteUp_Images/TestImage/Test_Image_Bounded.png
[image8]: ./WriteUp_Images/TestImage/Test_Image_Heatmap.png

[image9]: ./WriteUp_Images/TestFrame/Test_Frame_Bounded.png
[image10]: ./WriteUp_Images/TestFrame/Test_Frame_Heatmap.png
[image11]: ./WriteUp_Images/TestFrame/Test_Frame_Original.png

[image12]: ./WriteUp_Images/Bounded_Image&HeatMaps/225.png
[image13]: ./WriteUp_Images/Bounded_Image&HeatMaps/225-heat.png
[image14]: ./WriteUp_Images/Bounded_Image&HeatMaps/255.png
[image15]: ./WriteUp_Images/Bounded_Image&HeatMaps/255-heat.png
[image16]: ./WriteUp_Images/Bounded_Image&HeatMaps/287.png
[image17]: ./WriteUp_Images/Bounded_Image&HeatMaps/287-heat.png
[image18]: ./WriteUp_Images/Bounded_Image&HeatMaps/412.png
[image19]: ./WriteUp_Images/Bounded_Image&HeatMaps/412-heat.png
[image20]: ./WriteUp_Images/Bounded_Image&HeatMaps/450.png
[image21]: ./WriteUp_Images/Bounded_Image&HeatMaps/450-heat.png
[image22]: ./WriteUp_Images/Bounded_Image&HeatMaps/503.png
[image23]: ./WriteUp_Images/Bounded_Image&HeatMaps/503-heat.png
[image24]: ./WriteUp_Images/450_2.png
[image25]: ./WriteUp_Images/450-heat2.png

[video1]: ./Bounded_Output.mp4

## [Rubric](https://review.udacity.com/#!/rubrics/513/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  [Here](https://github.com/udacity/CarND-Vehicle-Detection/blob/master/writeup_template.md) is a template writeup for this project you can use as a guide and a starting point.  

Here you go!

### Histogram of Oriented Gradients (HOG)

#### 1. Explain how (and identify where in your code) you extracted HOG features from the training images.

In the second cell of the "Vehicle_Detection.ipynb" notebook, I wrote a method titled 'patch_analyzer' that does both HOG feature extraction and pre-processing for colorspace detection.

Instead of converting the 3-channel RGB image through a single gradient colorspace, I ran HOG feature extraction on each channel, after converting the image into the desired colorspace.

===UPDATE===

Per the feedback on the last submission, I increased the orientations to 11, pixesl to 16x16, and 2x2 cells per block. The HOG features were calculated on top of a YUV image, and the color space extraction done an an HLS image.

When I compared the HOG images to my previous tunings, it actually seemed that the suggested parameters would be worse, but after continuing to the SVM training I found that I was able to get higher validation percentages with even stricter C values, so I continued onward to the object recognition.

#### 2. Explain how you settled on your final choice of HOG parameters.

To my detriment, I actually did not tune the HOG parameters before running the classifier. I took what had been presented in the lessons and implemented that right away.

After I had already created the output video, I decided to experiment with different HOG parameters, and believe that I should have increased the orientation count, and decreased the pixel area per cell. The cells per block didn't seem to have much effect, even with the decreased pixel area, but had I been tracking computation time the increased block size likely would have made processing faster.

Additionally, I was a little disappointed to see how ineffective CH2 and CH3 were across all colorspaces. The output video took nearly seven hours to compute at 10 FPS, and if most of the classification was from a single channel then I could have cut the compute time in half. Lessons learned.

Final HOG Parameters:

![alt text][image1]

12 Orientation, 4x4 Pixel Area, 1 Cell Per Block:

![alt text][image4]

12 Orientation, 4x4 Pixel Area, 2 Cells Per Block:

![alt text][image5]

#### 3. Describe how (and identify where in your code) you trained a classifier using your selected HOG features (and color features if you used them).

Based on the advanced lane finding project I knew I wanted to use the HLS color space, since I saw that it was powerful in detecting lane lines, and would help my classifier detect road features and detect them. This was further verified through my parameter tuning when I cycled through the available color spaces and evaluated which colorspace would generate the most features. I was a little concerned how this colorspace might work with the vehicle and non-vehicle training set because the images were not particularly variant in terms of lighting, but HSV did seem to be the best choice.

Cells 3-5 of 'VehicleDetection.ipynb', I load the non-vehicle and vehicle images from the GTI and KITTI sets, run all the images through the patch analyzer, which normalizes the images as part of the function, then the outputs and their labels, are split into training and test sets, and scale the two sets independently to prevent information crossover.
After the transform, a linear SVC is trained. I chose to set a low C value, allowing for more error in the system. This becomes apparent in the output video that the C value may have been too low. I did not modify the default Gamma value.

Final Color Space (HSV):

![alt text][image1]

LAB Color Space:

![alt text][image2]

YCrCb Color Space:

![alt text][image3]

### Sliding Window Search

#### 1. Describe how (and identify where in your code) you implemented a sliding window search.  How did you decide what scales to search and how much to overlap windows?

In the seventh cell of the "Vehicle_Detection.ipynb" notebook, I wrote titled 'sliding_window' that takes the input image, a start and stop input, and a scalar value. The scalar will scale the image accordingly, doubling or halving as commanded. This in effect creates a sliding window search. The patches are still the same size, but the effect is that they are searching over an different area, because the image itself has changed. The start and stop inputs allows the search to be more efficient; if I already know that a certain region will be mostly sky or irrelevant lanes, then I do not need the calsifier to search in that region.


===UPDATE===

The scale for the windows were also changed based on feedback from the previous submission. I chose to use 0.5, 0.75, 1, and 2. The feedback mentioned using 2-3 instead of 4, but I found that having the half-sized window search was useful, and maintained it. To speed up my processing time I launched a compute optimized AWS instance, and when coupled with the other speed improvements to my pipeline, I was able to process the video in half the time.

![alt text][image6]

===UPDATE 2===


I added an additional axis of control to the sliding window search so I could focus searching only on lanes that had traffic flows in the same direction.

#### 2. Show some examples of test images to demonstrate how your pipeline is working.  What did you do to optimize the performance of your classifier?

I leaned heavily on the test images to track how changes to my parameters affected my detection rates.

![alt text][image7]

![alt text][image8]

Then I pulled a single frame from the short, one second video to develop a time reference for how long it would take to go through the project video.

This is where I realized that visualizing the HOG images was severely impeding my iteration rate, and set them all to 'False'.

![alt text][image9]

![alt text][image10]

![alt text][image11]

---

### Video Implementation

#### 1. Provide a link to your final video output.  Your pipeline should perform reasonably well on the entire project video (somewhat wobbly or unstable bounding boxes are ok as long as you are identifying the vehicles most of the time with minimal false positives.)

===UPDATE===

New link - https://www.dropbox.com/s/2vyeue6bp4v9x6c/VehicleDetection_Take3.mp4?dl=0

#### 2. Describe how (and identify where in your code) you implemented some kind of filter for false positives and some method for combining overlapping bounding boxes.

Heatmaps were implemented, and the threshold value tuned to eliminate some false positives.

Also, in addition to heatmaps, I implemented a physically based check that looked at the height and width of the box being drawn and rejected it if it was too small. This is relatively crude, but was able to eliminate a good deal of mis-classified noise that was had a high enough heatmap value to qualify as an object, but was too small to possibly be a vehicle.

===UPDATE===


Based on the feedback of the last submission, I spent a lot of time tuning and adding features to the pipeline to improve perforamnce. I used the `collections.deque` to create a trailing average to influence the heatmap in hopes of reducing splitting of the boxes, and the LinearSVC `decision_function` method to only return patches that had a high confidence of being a car.

Despite this, I was unable to eliminate all false positives, the highway exit sign being the most difficult, without losing track of the white car, so I preferenced tracking the white car all the way through the clip and accepting a few frames of tracking the highway sign.

### Here are six frames and their corresponding heatmaps:
Note: I multiplied all the values in the image by 5 so that the highlighted regions would be more apparent. Without this gain, the heated areas were of low intensity and difficult to see.

Frane 225

![alt text][image12]

![alt text][image13]

Frame 255

![alt text][image14]

![alt text][image15]

Frame 287

![alt text][image16]

![alt text][image17]

Frame 412

![alt text][image18]

![alt text][image19]

Frame 450

![alt text][image20]

![alt text][image21]

===UPDATE==

The following is Frame 450 of the second video. I was able to get the cmap functionality working and also the noise reduction is rather good.

![alt text][image24]

![alt text][image25]

### Here the resulting bounding boxes are drawn onto the last frame in the series:

I particularly like this frame because even though the black Mercedes is not fully in the frame, the classifier is still able to discern that it is a car and bound it.

![alt text][image22]

![alt text][image23]

---

### Discussion

#### 1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

I attempted to implement sub-sampling both to improve detection rates and also increase the scale range that I could cycle through.  My current method calculates the HOG for every patch fed into the classifier, which is computationally intensive. If I could just calculate the HOG features once and extract that information it would be much more efficient, and possibly more capable.

Another issue that is apparent in the output video is that I chose poorly regarding the colorspace implementation, either in training or the channel separation. The classifier easily detects dark colored vehicles, but largely ignores the white one. It is able to pick up some features like the headlights, tires, and rear window, but is unable to piece these elements together into one holistic object.

Finally, one of the most persistent, and frustrating, issues was poor classification. I believe I needed to trian my classifier on a greater set of images than just the GTI and KITTI sets, because it was recognizing road elements as vehicles.

===UPDATE===

After the modifications were made to the HOG parameters, the new pipeline performs much better, recognizing more vehicles and rejecting more false-positives. I noticed that the object detection is weak around shadows, and has the most fals positives when driving through an overcast section of the freeway. Additionally, the classifier recognizes part of the hood as another "car", as well as some billboards. Going forward, I can further reduce the search window to preclude the entirety of the hood, and add more billboards to the SVM training data. Regarding shadows, that will likely be a combination of tuning my colorspace parameters and training.
