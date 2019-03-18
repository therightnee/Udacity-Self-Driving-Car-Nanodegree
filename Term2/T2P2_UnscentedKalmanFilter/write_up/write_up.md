# Unscented Kalman Filter Project Write Up

This project implemeented an Extended Kalman Filter to estimate the state of a moving object of interest with noisy lidar and radar measurements. The "unscented" aspect of the Kalman filter was that it used signma values to transform non-linear results from one coordinate space to another.

The filter was able to achieve an px, py, vx, vy RMSE of [0.0760, 0.0832, 0.3169, 0.2014] which is lower than the values required in the project rubric. 

![alt text](UKF_out.png "Sample Output from Dataset 1 Run with UKF Implementation")


## Top Points of Discussion

### General Unscented Kalman Filter Methodology

The Unscented Kalman filter is different from the Extended Kalman Filter implemented previously in that both the LiDAR and RADAR are processed in the same fashion.

### Setting Sigma Points and Linearizing the Output

### Processing RADAR & LiDAR with Sigma Points
