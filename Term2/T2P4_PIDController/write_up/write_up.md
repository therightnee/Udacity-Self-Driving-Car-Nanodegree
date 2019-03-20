# PID Controller Project Write Up

This project implemented a PID controller to control the steering input to drive a car safely around a track.

Final PID parameters were:

Performance of the final PID parameters: {0.08,0.0006,2}

![alt text](Localization_Success.png "No hands.")

### PID Tuning Explored

Effect of only propotional control

Effect of only integral control

Effect of only derivative control

### Twiddle Tuning Algorithm

### Future work
There is plenty of further work that can be explored. First and foremost the tuning could be further optimized, as evidenced by the one corner where the front left wheel touches the concrete. Additionally, the throttle value is fixed at 0.5, but it could also be placed in a PID loop and optimized.