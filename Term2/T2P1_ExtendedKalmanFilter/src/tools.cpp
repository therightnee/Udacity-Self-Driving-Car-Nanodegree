#include <iostream>
#include "tools.h"

using Eigen::VectorXd;
using Eigen::MatrixXd;
using std::vector;

Tools::Tools() {}

Tools::~Tools() {}

VectorXd Tools::CalculateRMSE(const vector<VectorXd> &estimations,
                              const vector<VectorXd> &ground_truth) {
  /**
  TODO:
    * Calculate the RMSE here.
  */
  VectorXd rmse(4);
  rmse << 0, 0, 0, 0;

  // check the validity of the following inputs:
  //  * the estimation vector size should not be zero
  //  * the estimation vector size should equal ground truth vector size
  if (estimations.size() != ground_truth.size()
      || estimations.size() == 0){
      std::cout << "Invalid estimation or ground_truth data" << std::endl;
      return rmse;
  }

  //accumulate squared residuals
  for (unsigned int i = 0; i < estimations.size(); ++i){

      VectorXd cur_delta = estimations[i] - ground_truth[i];

      //coefficient-wise multiplication
      cur_delta = cur_delta.array()*cur_delta.array();
      rmse += cur_delta;
  }

  //calculate the mean
  rmse = rmse / estimations.size();

  //calculate the squared root
  rmse = rmse.array().sqrt();

  //return the result
  return rmse;
}

MatrixXd Tools::CalculateJacobian(const VectorXd& x_state) {
  /**
  TODO:
    * Calculate a Jacobian here.
  */
  MatrixXd Hj(3, 4);
  //recover state parameters
  float px = x_state(0);
  float py = x_state(1);
  float vx = x_state(2);
  float vy = x_state(3);

  //pre-compute a set of terms to avoid repeated calculation
  float d1 = pow(px, 2) + pow(py, 2);
  float d2 = sqrt(d1);
  float d3 = d1*d2;

  //compute the Jacobian matrix
  if (fabs(d1) > 0.0001) {
  Hj << (px / d2), (py / d2), 0, 0,
      -(py / d1), (px / d1), 0, 0,
      py*(vx*py - vy*px) / d3, px*(vy*px - vx*py) / d3, px / d2, py / d2;
  } else {
    std::cout << "CalculateJacobian () - Error - Division by Zero" << std::endl;
    return Hj;
  }

  return Hj;
}