# **Behavioral Cloning Writeup** 

## James Nee
---

**Behavioral Cloning Project**

The goals / steps of this project are the following:
* Use the simulator to collect data of good driving behavior
* Build, a convolution neural network in Keras that predicts steering angles from images
* Train and validate the model with a training and validation set
* Test that the model successfully drives around track one without leaving the road
* Summarize the results with a written report


[//]: # (Image References)

[image1]: ./WriteUp_Images/model.png "Model Architecture"
[image2]: ./WriteUp_Images/placeholder.png "Grayscaling"
[image3]: ./WriteUp_Images/placeholder_small.png "Recovery Image"
[image4]: ./WriteUp_Images/placeholder_small.png "Recovery Image"
[image5]: ./WriteUp_Images/placeholder_small.png "Recovery Image"
[image6]: ./WriteUp_Images/placeholder_small.png "Normal Image"
[image7]: ./WriteUp_Images/placeholder_small.png "Flipped Image"

## Rubric Points
### Here I will consider the [rubric points](https://review.udacity.com/#!/rubrics/432/view) individually and describe how I addressed each point in my implementation.  

---
### Files Submitted & Code Quality

#### 1. Submission includes all required files and can be used to run the simulator in autonomous mode

My project includes the following files:
* model.py containing the script to create and train the model
* drive.py for driving the car in autonomous mode
* FinalModel.h5 containing a trained convolution neural network 
* NeeJames_WriteUp.md summarizing the results

#### 2. Submission includes functional code
I did not modify the drive.py file to run the full course. To start the autonomous control run the following commmand:

```sh
python drive.py FinalModel.h5
```

#### 3. Submission code is usable and readable

The model.py file contains the code for training and saving the convolution neural network. The file shows the pipeline I used for training and validating the model, and it contains comments to explain how the code works.

### Model Architecture and Training Strategy

#### 1. An appropriate model architecture has been employed

I attempted to employ the same convolution neural network as described in ["End to End Learning for Self-Driving Cars"](https://images.nvidia.com/content/tegra/automotive/images/2016/solutions/pdf/end-to-end-dl-using-px.pdf,) a research paper sponsored by the NVIDIA, which trained the convolution neural network to map pixel inputs to steering commands.

XX 5x5 filters with depths of XXX, then XXX 3x3 filters with depths of XXXX. Then the layers are flattened, and subsequently condensed down to XXXXX nodes, until reaching a single output. Each of the convolution layers were activated using a RELU, and each of the dense layers etc. etc.

The input frames were normalized and cropped to remove extraneous visual information.

#### 2. Attempts to reduce overfitting in the model

Overfitting was done primarily through introducing droupout in in the dense layers.

Originally, I included a high amount of dropout in order to prevent overfitting, but when my validation loss was not converging, I began to dial back the dropout rate, and in the end eliminating it all together.

#### 3. Model parameter tuning

The model used an adam optimizer with a user defined learning and decay rate. In earlier iterations of the model the optimizer was not tuned, but I found that the validation losses were not converging. When I looked at the default optimizer values, I guessed that it may have been too high and was jumping past the optimal weights.

#### 4. Appropriate training data

First, I took data going in both clockwise and counterclockwise directions, on both tracks, and changing the centerline of the road. The idea was to generate enough disparate data that will teach the model to ignore the scenery, focus on the road ahead, and also give it enough direction that it will be able to recover if the vehicle drifts too far to the left or right.

To further increase the range of available data, I used all three camera angles with a fixed angle correction on the steering angle to adjust for the camera position.

### Model Architecture and Training Strategy

#### 1. Solution Design Approach

Used the NVIDIA end-to-end model. Powerful training model for behavioral cloning, came recommmended via the class, and easy to implement via Keras.

Validation and test split, plotted error on training set and validation set. 

I implemented the exact same CNN as described, because it was easy to do with Keras and the paper indicated it was particularly powerful for behavioral cloning.

Initially set the dropout incredibly high, at 50 percent of the input set. The model was not getting sufficient data to be properly trained.

Even reducing the dropout resulted in erratic behavior, training vs. validation loss was never stabilizing.

Eliminating dropout allowed for at least either a stable and consistent loss, or a slight downward trend. Epochs limited to 5 max, because I never saw decreasing loss after 5 epochs.

This training allowed me to get around the first bend and across the bridge quiet well, but when the car came to the fork, the car would not turn away from the dirt path and would continue straight, either hitting the barriers and getting stuck, or piloting down the dirt path until it rejoined the circuit, but be unable to cross back onto the track.

My attempts to tune the system using dropouts, specialized datasets focused on course correction and returning to the track from the margins, and tuning the cropping function did not result in noticeable benefits.

Ultimately what worked best was training the model using clockwise center driving data twice. I am uncertain what this means for overfitting.

#### 2. Final Model Architecture

The final model architecture (model.py lines 18-24) consisted of a convolution neural network with the following layers and layer sizes ...

Here is a visualization of the architecture (note: visualizing the architecture is optional according to the project rubric)

![alt text][image1]

#### 3. Creation of the Training Set & Training Process

To capture good driving behavior, I first recorded fivce laps on track one using center lane driving. Here is an example image of center lane driving:

![alt text][image2]

I then recorded the vehicle recovering from the left side and right sides of the road back to center so that the vehicle would learn to .... These images show what a recovery looks like starting from ... :

![alt text][image3]
![alt text][image4]
![alt text][image5]

Then I repeated this process on track two in order to get more data points.

Furthermore I took data of the vehicle driving in the opposite direction on the track, as well as keeping the car on the appropriate lane, per US driving standards. I took data in this way from both tracks.

![alt text][image6]
![alt text][image7]


After the collection process, I had X number of data points. I then preprocessed this data purely in the model by normalizing and cropping the images.

I wanted to be able to control what image sets I fed into the system, so I wrote an error handler to catch if a pre-trained model existed, and if it did, would load that model instead of building one. It would then continue training with whatever data source I had indicated.

This was key to my eventual success because I was able to track the progress of the model incrementally, as opposed to needing to fully train the model and then run a test.

I found that starting with the 5 CW lane agnostic laps data set, then training with the 3 laps CW and 3 laps CC lane centered data gave me decent results. The issue was that when the simulated car passed the bridge and reach the fork with the dirt path and paved road it would always choose to go down the dirt path.

Then when I added the driving data from the second track, both lane centered, 2 laps each, the car self-corrected faster, and while it still chose to drive down the dirt path, would be able to navigate through the dirt path, almost rejoining the road at the end.

What worked in the end was to then feed the original data set of 5 CW lane agnostic laps. I had some concerns about this overfitting the model, but the validation errors weren't much different.

For each data set, I randomly shuffled the data set and put Y% of the data into a validation set. 

I used this training data for training the model. The validation set helped determine if the model was over or under fitting. Though there was not much variation in the validation loss even after the first epoch, there was clearly no benefit after 5 epochs across the range training sets I ran. 

I used an adam optimizer so that manually training the learning rate wasn't necessary, but I did tune the parameters so that the learning rate would decay at a more controlled rate. Based on the fluctuations in validation loss I was concerned the learning rate was not decaying fast enough and was skipping over the optimal weights.
