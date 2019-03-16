#include "kalman_filter.h"
#include "math.h"

using Eigen::MatrixXd;
using Eigen::VectorXd;

/* 
 * Please note that the Eigen library does not initialize 
 *   VectorXd or MatrixXd objects with zeros upon creation.
 */

KalmanFilter::KalmanFilter() {}

KalmanFilter::~KalmanFilter() {}

void KalmanFilter::Init(VectorXd &x_in, MatrixXd &P_in, MatrixXd &F_in,
                        MatrixXd &H_in, MatrixXd &R_in, MatrixXd &Q_in) {
  x_ = x_in;
  P_ = P_in;
  F_ = F_in;
  H_ = H_in;
  R_ = R_in;
  Q_ = Q_in;
}

void KalmanFilter::Predict() {
  //State Transition Function
  x_ = F_ * x_;

  //Linear Motion Model
  MatrixXd Ft = F_.transpose();
	P_ = F_ * P_ * Ft + Q_;
}

void KalmanFilter::Update(const VectorXd &z) {

		VectorXd y = z - H * x;
		MatrixXd Ht = H.transpose();
		MatrixXd S = H * P * Ht + R;
		MatrixXd Si = S.inverse();
		MatrixXd K =  P * Ht * Si;

		//Update Estimate and Uncertainty
		x_ = x_ + (K * y);
    I = MatrixXd::Identity(x_.size(), x_.size());
		P_ = (I - K * H) * P_;

}

void KalmanFilter::UpdateEKF(const VectorXd &z) {
    float rho = sqrt(pow(x_(0), 2) + pow(x_(1), 2));
    float phi = atan(x_(1)/x_(0));
    float rho_dot = (x_(0)*x_(2) + (x(1)*x(3))/rho);
		
    VectorXd H_j(3)
    H_j << rho, phi, rho_dot 
    VectorXd y = z - H_j;
		MatrixXd Ht = H.transpose();
		MatrixXd S = H * P * Ht + R;
		MatrixXd Si = S.inverse();
		MatrixXd K =  P * Ht * Si;

		//Update Estimate and Uncertainty
		x_ = x_ + (K * y);
    I = MatrixXd::Identity(x_.size(), x_.size());
		P_ = (I - K * H) * P_;
