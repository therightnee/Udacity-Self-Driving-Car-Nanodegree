
#include "PID.h"
#include <cmath>
#include <iostream>

PID::PID() {}

PID::~PID() {}

void PID::Init(double Kp, double Ki, double Kd) {
    mKp = Kp; //store the proportional gain
    mKi = Ki; //store the integral gain
    mKd = Kd; //store the derivative gain
    mPro_err = 0.0; //initialize the propotional error
    mInt_err = 0.0; //initialize the integral error
    mDer_err = 0.0; //initialize the derivative error
    mBest_err = 1000.0; //best error
    mSecond_case = false ; //switch variable 
    
}

void PID::UpdateError(double cte) {
    //update derivative error first - mPro_err is previous cte
    mDer_err = cte - mPro_err;
    mPro_err = cte; //update propotional error
    mInt_err += cte; //update integral error

}

double PID::TotalError() {
    return (-mKp * mPro_err) - (mKi * mInt_err) - (mKd * mDer_err);
}

bool PID::TwiddleTuner(double cte, double steer_value, int step_count, int cur_gain) {
    int mSteps = step_count;
    int mGain_Pos = cur_gain;
    bool tol_check = false; 
    double dp_sum = 0.0;
    double mTol = 0.0001;
    double mError = 0.0;
    double mCurr_err = 0.0;
    double p[3] = {mKp, mKi, mKd}; //default gain array
    double dp[3] = {0.01, 0.0001, 0.1}; //Twiddle gain array modifier

    //error calculation as given
    mError += pow(cte,2);
    mCurr_err = mError/mSteps;

    //algorithm to modify each gain
    std::cout << "Current gain position: " << mGain_Pos << std::endl;

    p[mGain_Pos] += dp[mGain_Pos];

    if (mCurr_err < mBest_err && mSecond_case == false){
        std::cout << "First conditional" << std::endl;
        mBest_err = mCurr_err;
        mKp = p[0];
        mKi = p[1];
        mKd = p[2];
        dp[mGain_Pos] *= 1.1;
    } else if (mSecond_case) {
        std::cout << "Second conditional" << std::endl;
        mSecond_case = false;
        if (mCurr_err < mBest_err){
            std::cout << "Second conditional - First option" << std::endl;
            mBest_err = mCurr_err;
            mKp = p[0];
            mKi = p[1];
            mKd = p[2];
            dp[mGain_Pos] *= 1.1;
        } else {
            std::cout << "Second conditional - Second option" << std::endl;
            p[mGain_Pos] += dp[mGain_Pos];
            dp[mGain_Pos] *= 0.9;
        }

    } else {
        std::cout << "Third conditional" << std::endl;
        p[mGain_Pos] -= 2*dp[mGain_Pos];
        mSecond_case = true;
    }

    //sum the array
    for (int i=0; i < 3; i++) {
        dp_sum += dp[i];
    }

    //exit
    if (dp_sum < mTol) {
        tol_check = true;
        std::cout << "Current [K_p, K_i, K_d]: " << mKp << "," 
          << mKi << "," << mKd << "," << std::endl;
    } else {
        std::cout << "Current [K_p, K_i, K_d]: " << mKp << "," 
          << mKi << "," << mKd << "," << std::endl;
        std::cout << "Current Error:" << mCurr_err << " "<< "Best Error: " << mBest_err << std::endl;
        std::cout << "Current sum:" << dp_sum << std::endl;
        std::cout << "Moving to next iteration." << std::endl;
    }

    return tol_check;
}