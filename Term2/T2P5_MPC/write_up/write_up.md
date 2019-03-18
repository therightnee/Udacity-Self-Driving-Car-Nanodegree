# Model Predictive Control Project Write Up

This project implemented a MPC based controller to develop a plan for the car, and update that plan at each time step. 

Performance of the final MPC based controller:

![alt text](Localization_Success.png "No hands with MPC.")

### The Model

When run, `main.cpp` takes the following from the simulator:

- ptsx - x-coordinate of the waypoint
- ptsy - y-coordinate of the waypoint
- px - x-coodinate of the
- py - y-coodrinate of the
- psi - 
- speed - 

These 6 inputs are bundled and sent to MPC::LatencyInjetor() which attempts to predict where the car will be in the near future, essentially integrating current values to return a likely future state. Steering angle, cross track error, and angle offset is similarly calculated, using the current steering angle, coupled with the turning radius of the car to help translate velocity to rate of change in the yaw axis. 

After the latency is implemented, the output vector is fed into the MPC solver. This solver is identical to the one presented in the course. 

The major difference is that the output contains the steering angle delta, acceleration delta, and then the x, and y positions for N future states, as set at the start of MPC.cpp. 

### Steering Tuning Explored

Test with a scalar of 100

Test with a scalar of 500

### Varying Number of Steps

N = 25

N = 10

N = 5

### Varying dt

N = 10, dt = 0.5

N = 25, dt = 1.0

N = 25, dt = 0.5

