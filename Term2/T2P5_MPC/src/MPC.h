#ifndef MPC_H
#define MPC_H

#include <vector>
#include "Eigen-3.3/Eigen/Core"

using namespace std;
using Eigen::VectorXd;

class MPC {
 public:
  MPC();

  virtual ~MPC();

  // Solve the model given an initial state and polynomial coefficients.
  // Return the first actuatotions.
  std::vector<double> Solve( VectorXd &state, VectorXd &coeffs);

  const Eigen::VectorXd Latency( double v, double steering_input, 
                    double throttle_input, double cte, double psi_error);
};

#endif /* MPC_H */
