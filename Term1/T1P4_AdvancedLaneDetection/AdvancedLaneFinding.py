
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import glob


cal_img = glob.glob("cal_img/*")

3D_points = []
2D_points = []

obj_ideal = np.zeros((6*8,3),np.float32)
obj_ideal[:,:2] = np.grid[0:8,0:6].T.reshape(-1,2)


def point_setup(img_list):
	for image in img_list:
		img = cv2.imread(image)
		gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		ret, corners = cv2.findChessboardCorners(gray, (8,6), None)
		if ret == True:
			2D_points.append(corners)
			3D_points.append(obj_ideal)

def camera_cal(input_img, objpoints, imgpoints):
	dist_img = cv2.imread(input_img)
    ret1, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    fix_img = cv2.undistort(dist_img, mtx, dist, None, mtx)
    plt.imshow(fix_img)


#Gradient and Thresholding Corrected Image - Only really needed for curvature detection
def threshold_trans(raw_img):
	# Convert to HLS color space and separate the S channel
	# Note: img is the undistorted image
	hls = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
	s_channel = hls[:,:,2]

	# Grayscale image
	# NOTE: we already saw that standard grayscaling lost color information for the lane lines
	# Explore gradients in other colors spaces / color channels to see what might work better
	gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

	# Sobel x
	sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0) # Take the derivative in x
	abs_sobelx = np.absolute(sobelx) # Absolute x derivative to accentuate lines away from horizontal
	scaled_sobel = np.uint8(255*abs_sobelx/np.max(abs_sobelx))

	# Threshold x gradient
	thresh_min = 20
	thresh_max = 100
	sxbinary = np.zeros_like(scaled_sobel)
	sxbinary[(scaled_sobel >= thresh_min) & (scaled_sobel <= thresh_max)] = 1

	# Threshold color channel
	s_thresh_min = 170
	s_thresh_max = 255
	s_binary = np.zeros_like(s_channel)
	s_binary[(s_channel >= s_thresh_min) & (s_channel <= s_thresh_max)] = 1

	# Stack each channel to view their individual contributions in green and blue respectively
	# This returns a stack of the two binary images, whose components you can see as different colors
	color_binary = np.dstack(( np.zeros_like(sxbinary), sxbinary, s_binary)) * 255

	# Combine the two binary thresholds
	combined_binary = np.zeros_like(sxbinary)
	combined_binary[(s_binary == 1) | (sxbinary == 1)] = 1

	# Plotting thresholded images
	f, (ax1, ax2) = plt.subplots(1, 2, figsize=(20,10))
	ax1.set_title('Stacked thresholds')
	ax1.imshow(color_binary)

	ax2.set_title('Combined S channel and gradient thresholds')
	ax2.imshow(combined_binary, cmap='gray')

def perspective_trans(undist_img):
	img_size = (undist_img.shape[1], undist_img.shape[0])

	#Source Coordinates - SE, NE, NW, SE
	src = np.float32(
		[[500,500],
		 [500,500],
		 [500,500],
		 [500,500]])

	#Desired Coordinates - SE, NE, NW, SE
	dst = np.float32(
		[[100,0],
		 [100, 500],
		 [0,500],
		 [0,0]])

	#Generate perspective transform
	M = cv2.getPerspectiveTransform(src,dst)

	#Inverse transform
	M_inv = cv2.getPerspectiveTransform(dst,src)

	#Transform Image
	flattened = cv2.warpPerspective(undist_img, M, img_size, flags=cv2.INTER_LINEAR)

#Caclulate Radius of curvature for both lanes - expects input points from top to bottom, sorted using the y-axis
def radii_calc(l_lane_pts, r_lane_pts):
	# Fit a second order polynomial to pixel positions in each fake lane line
	left_fit = np.polyfit(ploty, leftx, 2)
	left_fitx = left_fit[0]*ploty**2 + left_fit[1]*ploty + left_fit[2]
	right_fit = np.polyfit(ploty, rightx, 2)
	right_fitx = right_fit[0]*ploty**2 + right_fit[1]*ploty + right_fit[2]
	# Define y-value where we want radius of curvature
	# I'll choose the maximum y-value, corresponding to the bottom of the image
	y_eval = np.max(ploty)
	left_curverad = ((1 + (2*left_fit[0]*y_eval + left_fit[1])**2)**1.5) / np.absolute(2*left_fit[0])
	right_curverad = ((1 + (2*right_fit[0]*y_eval + right_fit[1])**2)**1.5) / np.absolute(2*right_fit[0])
	print(left_curverad, right_curverad)
	# Example values: 1926.74 1908.48
	# Define conversions in x and y from pixels space to meters
	ym_per_pix = 30/720 # meters per pixel in y dimension
	xm_per_pix = 3.7/700 # meters per pixel in x dimension
	# Fit new polynomials to x,y in world space
	left_fit_cr = np.polyfit(ploty*ym_per_pix, leftx*xm_per_pix, 2)
	right_fit_cr = np.polyfit(ploty*ym_per_pix, rightx*xm_per_pix, 2)
	# Calculate the new radii of curvature
	left_curverad = ((1 + (2*left_fit_cr[0]*y_eval*ym_per_pix + left_fit_cr[1])**2)**1.5) / np.absolute(2*left_fit_cr[0])
	right_curverad = ((1 + (2*right_fit_cr[0]*y_eval*ym_per_pix + right_fit_cr[1])**2)**1.5) / np.absolute(2*right_fit_cr[0])
	# Now our radius of curvature is in meters
	print(left_curverad, 'm', right_curverad, 'm')
	# Example values: 632.1 m    626.2 m

#Highway should never be lower than 180 m, should be seeing something in the 450 m to 850 m range

#Perspective Test
plt.imshow("lane_image")
plt.plot(500, 500, '*') #point 1
plt.plot(500, 500, '*') #point 1
plt.plot(500, 500, '*') #point 1
plt.plot(500, 500, '*') #point 1