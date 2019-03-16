#ifndef PID_H
#define PID_H
#include <vector>


class PID {
public:
  /*
  * Errors
  */
  double mPro_err;
  double mInt_err;
  double mDer_err;

  /*
  * Coefficients
  */ 
  double mKp;
  double mKi;
  double mKd;

  /*
  * Twiddle Persistent
  */
  double mBest_err;
  bool mSecond_case;
    

  /*
  * Constructor
  */
  PID();

  /*
  * Destructor.
  */
  virtual ~PID();

  /*
  * Initialize PID.
  */
  void Init(double Kp, double Ki, double Kd);

  /*
  * Update the PID error variables given cross track error.
  */
  void UpdateError(double cte);

  /*
  * Calculate the total PID error.
  */
  double TotalError();

  /*
  * Invoke the Twiddle PID tuning algorithm
  */

  bool TwiddleTuner(double cte, double steer_value, int step_count, int cur_gain);
};

#endif /* PID_H */