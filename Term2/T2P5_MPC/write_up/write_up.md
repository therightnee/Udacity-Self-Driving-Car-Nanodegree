# Model Predictive Control Project Write Up

This project implemented a MPC based controller to develop a plan for the car, and update that plan at each time step. 

Performance of the final MPC based controller with N  = 10, and dt = 0.05

![alt text](mpc_run.mp4 "No hands with MPC.")

### The Model

This model is based on the solution provided in "Mind the Line", with some changes to adapt to a more complicated track.

The waypoints are fitted to a third order polynomial, instead of a line. 

I really liked the way the cost function was implemented in the solution code. Breaking up each of the equations into sections and specifying the effect each group had on the aggregate cost was particularly helpful in tuning the system.

The actual vehicle model was also copied from the solution code, though f0 and psides0 had to be adjusted for the third order polynomial. Thankfully this was a straightforward as expanding f(x) to include x0^3, with the appropriately indexed coefficient, and then setting psides0 to be atan(f'(x)).

MPC::Solve is essentially identical to the function in MPC.cpp from the quizzes. I simply copied over the methods used to set the limits and start both the lower and upper bounds at the current value for that given variable. The output vector needed some modifcation as it need to scale depending on the size of N. Given that the first two entries are always the same, the vector is initialized with those values and then stuffed with the x/y values for the N points.


###Latency

These 6 inputs are bundled and sent to MPC::LatencyInjetor() which attempts to predict where the car will be in the near future, essentially integrating current values to return a likely future state. Steering angle, cross track error, and angle offset is similarly calculated, using the current steering angle, coupled with the turning radius of the car to help translate velocity to rate of change in the yaw axis. 

After the latency is implemented, the output vector is fed into the MPC solver. This solver is identical to the one presented in the course. 

The major difference is that the output contains the steering angle delta, acceleration delta, and then the x, and y positions for N future states, as set at the start of MPC.cpp. 

### Varying Number of Steps

I first started with N = 25 and dt = 0.06 based on the quiz in the MPC lesson. Discovered that 25 was unnecessary, especially at the starting reference velocity of 40 MPH. 

Increased the reference velocity to 80, and kept the responsiveness of the acceleration change rate equation relatively high by not multiplying it with a large scalar factor.

The heuristic I developed by trying N=5, N=10, N=20, and N=25 is that the larger N is the more computationally expensive the model is to run, but if N is too small the predicted path easily deviates from the waypoints, which is extra problematic at higher speeds. At a reference velocity of 80, I found N=10 a good balance where the prediction tracked closely to the waypoints, and there did not seem to be excess predictions. In cases where N was large (20+), I noticed the predicted path would often curl to the right, likely indicating a limitation of the model in predicting points that far out.

### Varying dt

The other lever to adjust in implementing an model predictive controller is the time step between each prediction. I experimented with dt = 0.05, dt = 1, and dt = 0.01. 

At first, I thought that dt = 0.01 would improve performance, but in fact performance was far worse than dt = 0.05. My intuition here is that smaller time steps mean that more iterations of the prediction are being cycled, since only the first actuation state is implemented, and then a new state is calculated. This means there is less time for the system to stabilize, and the car is constantly attempting to adjust, resulting in rapid and large steering angle changes. 

With dt = 0.1 performance was better than dt =  0.01, but I found that the vehicle respond slowly to turns. This makes sense as the the larger time delta means breaking up the path into larger steps relative to a dt =0.05 or dt = 0.01. Ultimately, I used N = 10, dt = 0.05. It is important to couple N with dt, having a larger N with smaller dt is significantly different than a small N with a small dt.

### Cost Function Tuning 

I tuned each of the cost functions with a scalar value, taking the heuristic presented in the MPC lesson that the larger the value, the smoother the transition.

WHen I changed the reference velocity to 80, I noticed steering instability was a major problem, resulting in the large (2*10^7) scalar on the steering cost function.
