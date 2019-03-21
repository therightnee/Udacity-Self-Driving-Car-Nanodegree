# PID Controller Project Write Up

This project implemented a PID controller to control the steering input to drive a car safely around a track.

Final PID parameters were: {0.08,0.0006,2}

Performance of the final PID parameters is decent, though there is a point on second to last turn where the front left tire contacts the painted section which could be improved.

[Full run with the final parameters](Tuned_Run_Full.mp4)

### PID Tuning Explored

The effect of only propotional control is that the car will swing widely to the right and left of the centerline, with increasing amplitude. With only propotional gain, there is nothing to dampen the oscillations around the target, so the car will constantly overshoot the centerline, with increasing error, which in turn further increases the overshoot, resulting in a positive feedback loop that leads to instability.

[Run with Propotional gain set to 1](P_1.mp4)

Integral only control, without any other factors, is not particularly useful. The integral gain is based on the sum of all previous errors, which means there is little effect in the beginning, and when the car encounters an externality, like hitting the curb forcing the wheels to turn right, the system becomes unstable and all corrective actions are ineffective. The integral term is meant to adjust for issues with the propotional term by adding a "memory" of what the error has been. Used on its own, without the driving force of the proportional gain, it is unable to have a significant affect on the vehicle.

[Run with Integral gain set to 1](I_1.mp4)

The derivative only gain does very little, until the cross track error becomes significant. From the clip below it is clear that the effect of the derivative only gain pulls the car more strongly as the car deviates further from the centerline. This is in line with the intended use of the derivative gain. Whereas the integral term is a "memory" of what has happened previously, the derivative gain allows the system insight into possible future actions. By building a trendline of the delta between the current error and the previous error, the derivative term attempts to increase the efficacy of that trendline. If the system is settling, the settling time should improve, and with less oscillation. If the system is ramping, it should ramp faster, with smoother rise and less overshoot.

[Run with Derivative gain set to 1](D_1.mp4)

### Twiddle Tuning Algorithm

The PID parameters were manually tuned to get the simulated car to roughly pass around the track. Then the `tuned` flag was turned on and the Twiddle algorithm began tuning.

While the algorithm will stop after the sum of the delta gain array is less than the threshold, there was no rigorous methodology on how the threshold value itself should be determined.

Instead, the thershold was set very low, and the algorithm run continuously until the results looked reasonable. This was roughl 200 iterations.

Psuedocode of the Twiddle Algorithm presented in class

```python
def twiddle(tol=0.2): 
    p = [0, 0, 0] #this is the gain array
    dp = [1, 0.001, 0.1] #this is the delta gain array

    while sum(dp) > tol: 
    """
    run as long as the sum of the delta gain array > the tolerance threshold
    """
        for i in range(len(p)):
            p[i] += dp[i]
            #add the delta gain to the respective gain and gather data
            robot = make_robot()
            x_trajectory, y_trajectory, err = run(robot, p)

            if err < best_err:
            #after sufficient data has been gathered check for improvement
                best_err = err
                dp[i] *= 1.1
            else:
            #if there is no improvement run this heuristic and gather more data
                p[i] -= 2 * dp[i]
                robot = make_robot()
                x_trajectory, y_trajectory, err = run(robot, p)

                if err < best_err:
                #after the second run, run the check again
                    best_err = err
                    dp[i] *= 1.1
                else:
                #if there is still no improvement, run this heuristic and loop
                    p[i] += dp[i]
                    dp[i] *= 0.9
        it += 1
    return p
```

In the implementation, the Twiddle algorithm runs a full lap on the initialized PID values to get a baseline error. Then it will run through three possible options. The decision tree is first if the error has improved or not; if it has not, a switch flag is set which will first trigger the `else` heuristic (`p[i] -= 2 * dp[i]`), do another run, and then evaluate again. If the switch flag is set and there is still no improvement, then the third conditional (`dp[i] *= 0.9`), is exectued and the loop repeats. It is important to loop through each of the gain values, P, I, and D. This is achieved by dividing the number iterations run by 3, and shifting the gain being adjusted.

### Future work
There is plenty of further work that can be explored. First and foremost the tuning could be further optimized, as evidenced by the one corner where the front left wheel touches the concrete. Additionally, the throttle value is fixed at 0.5, but it could also be placed in a PID loop and optimized.