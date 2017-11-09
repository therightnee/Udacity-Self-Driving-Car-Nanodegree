# **Finding Lane Lines on the Road** 

**Finding Lane Lines on the Road**

The goals / steps of this project are the following:
* Make a pipeline that finds lane lines on the road
* Reflect on your work in a written report


[//]: # (Image References)

[image1]: ./examples/grayscale.jpg "Grayscale"

---

### Reflection

### 1. Describe your pipeline. As part of the description, explain how you modified the draw_lines() function.

My pipeline is as follows:

* Greyscale Conversion
* Gaussian Blur
* Canny Transform
* Region Masking
* Hough Line Transform

Each step was tuned to minimize artifacts and maximize the amount of lane line recognized. The Hough Line transform was the most difficult for me to conceptualize, but certainly offered the most flexibility and precision in lane detection.

I found the instructions on the `draw_line` function vague and difficult to understand. It was incredibly helpful to look through previous students' work and see how they approached the problem. I found the work done by [Raymond U Chen](https://github.com/raymonduchen/CarND-P1-Finding-Lane-Line) and [Ashish Rana](https://github.com/Ashish-Rana/Simple-Lane-Detection/blob/master/P1.ipynb) particularly helpful. My final approach follows the same method Raymond outlines, although I reduced the y-axis length to avoid artifcats generated at the horizon, and increased the upper bound of the right lane slope, in the attempt to adjust the final line's slope to be steeper.

The approach can be broken up into two major elements. First determing the lines in the image.

```
    for line in lines:
        for x1,y1,x2,y2 in line:
            m=((y1-y2)/(x1-x2))
            #Determine if the line is on the left or right side
            if (m < -0.6 and m > -0.9):
                left_m_array.append(m)
                left_x_sum.append(x1, x2)
                left_y_sum.append(y1,y2)
            elif (m > 0.45 and m < 2):
                right_m_array.append(m)
                right_x_sum.append(x1, x2)
                right_y_sum.append(y1, y2)
```

Here each of the lines in the image is looped through and its slope claculated. If the slope is positive it is a designated as a right side line, and if it is negative a left side line. The number of lines in that set is increment, and the total sum of the x and y values calculated. This sum will be used in the average in the next section.

```
    #Caclulate the start and end-points of the line
    #uses hardcoded y values based on the known size of the image to caluclate x values
    if len(left_m_array) != 0 :
        left_m = np.mean(left_m_array)
        left_x_avg = int(np.mean(left_x_sum))
        left_y_avg = int(np.mean(left_y_sum))
        left_y1 = 330
        left_x1 = int( (left_y1 - left_y_avg)/left_m + left_x_avg )
        left_y2 = 960
        left_x2 = int( (left_y2 - left_y_avg)/left_m + left_x_avg )
        cv2.line(img, (left_x1, left_y1), (left_x2, left_y2), color=(255,255,0), thickness=3)
        
    if len(right_m_array) != 0 :
        right_m = np.mean(right_m_array)
        right_x_avg = int(np.mean(right_x_sum))
        right_y_avg = int(np.mean(right_y_sum))
        right_y1 = 330
        right_x1 = int( (right_y1 - right_y_avg)/right_m + right_x_avg )
        right_y2 = 960
        right_x2 = int( (right_y2 - right_y_avg)/right_m + right_x_avg )
        cv2.line(img, (right_x1, right_y1), (right_x2, right_y2), color=(255,255,255), thickness=3) 
```

Next the two conditional statements return the starting and ending points for the left and right lane lines. Those start and end y-axis coordinates are hardcoded based on the image size, and used to determine the x-axis values.


### 2. Identify potential shortcomings with your current pipeline

The first improvement I would make is to improve the `draw_lines` function. Currently it maps continuous line markers well, but when extrapolating from dashed lines there is a noticeable deviation.

Second is that my current pipeline is limited with respect to lighting conditions, lane marker hue and brightness, as well as curvature. Much of the tuning I did through the region masking and Hough Transform focuses on eliminating artifacts, but is designed for small set of cases. 
### 3. Suggest possible improvements to your pipeline

My current thinking on how to fix this would be to change the approach of the fuction from an average of all points to averaging points within a given area and then mapping the curve that contains those points using a best fit polynomial. 

Regarding the lighting conditions, I would first tune the Canny and Hough transforms to be more robust in eliminating artifacts, and then expand my region of interest to increase the length of lane visible in the region. To address color issues, such as changing light conditions or faded lane marker. I would first need to expand the Canny thresholds to account for a lower range of acceptable values, but also modify the greyscale image to more clearly separate the lane in shadow from equally dark but non-lane itmes.

#### License

The contents of this repository are covered under the MIT License.

Copyright (c) 2017 James Matthew Nee

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
