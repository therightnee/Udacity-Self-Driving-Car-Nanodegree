/*
 * particle_filter.cpp
 *
 *  Created on: Dec 12, 2016
 *      Author: Tiffany Huang
 */

#include <random>
#include <algorithm>
#include <iostream>
#include <math.h> 
#include <iostream>
#include <sstream>
#include <string>
#include <iterator>

#include "particle_filter.h"

using namespace std;

// declare a random engine to be used across multiple and various method calls
static default_random_engine gen;

void ParticleFilter::init(double x, double y, double theta, double std[]) {
	// TODO: Set the number of particles. Initialize all particles to first position (based on estimates of 
	//   x, y, theta and their uncertainties from GPS) and all weights to 1. 
	// Add random Gaussian noise to each particle.
	// NOTE: Consult particle_filter.h for more information about this method (and others in this file).

	if(is_initialized) {
		return;
	} 

	//Number of particles
	num_particles = 1000;

	//Create normal distributions
	normal_distribution<double> gauss_x(x, std[0]);
	normal_distribution<double> gauss_y(y, std[1]);
	normal_distribution<double> gauss_t(theta, std[2]);

	//Generate particles with normal distribution with mean on GPS values.
	for(int i = 0; i < num_particles; i++) {
		Particle p;
		p.id = i;
		p.x = gauss_x(gen);
		p.y = gauss_y(gen);
		p.theta = gauss_t(gen);
		p.weight = 1.0;
		particles.push_back(p);
	}

	is_initialized = true;

}

void ParticleFilter::prediction(double delta_t, double std_pos[], double velocity, double yaw_rate) {
	// TODO: Add measurements to each particle and add random Gaussian noise.
	// NOTE: When adding noise you may find std::normal_distribution and std::default_random_engine useful.
	//  http://en.cppreference.com/w/cpp/numeric/random/normal_distribution
	//  http://www.cplusplus.com/reference/random/default_random_engine/

	//Normal distributions for sensor noise
	normal_distribution<double> gauss_x(0, std_pos[0]);
	normal_distribution<double> gauss_y(0, std_pos[1]);
	normal_distribution<double> gauss_t(0, std_pos[2]);

	for(int p = 0; p < num_particles; p++) {
		//ensure no division by zero
		if(fabs(yaw_rate) > 0.001) { 
			particles[p].x += velocity / yaw_rate * (sin(particles[p].theta + yaw_rate*delta_t) - sin(particles[p].theta));
			particles[p].y += velocity / yaw_rate * (cos(particles[p].theta) - cos(particles[p].theta + yaw_rate*delta_t));
			particles[p].theta += yaw_rate * delta_t; 
		} 
		else{
			particles[p].x += velocity * delta_t * cos(particles[p].theta);
			particles[p].y += velocity * delta_t * sin(particles[p].theta);
		}

		//After particles have been set add noise
		particles[p].x += gauss_x(gen);
		particles[p].y += gauss_y(gen);
		particles[p].theta += gauss_t(gen);
	}

}

void ParticleFilter::dataAssociation(std::vector<LandmarkObs> predicted, std::vector<LandmarkObs>& observations) {
	// TODO: Find the predicted measurement that is closest to each observed measurement and assign the 
	//   observed measurement to this particular landmark.
	// NOTE: this method will NOT be called by the grading code. But you will probably find it useful to 
	//   implement this method and use it as a helper during the updateWeights phase.

	//each observation will be paired with a prediction
	for( unsigned int i = 0; i < observations.size(); i++) { 
		double minDist = 1000000;
		int mapId = -1;
		for(unsigned int j = 0; j < predicted.size(); j++ ) {
			double xDist = observations[i].x - predicted[j].x;
			double yDist = observations[i].y - predicted[j].y;
			double distance = xDist * xDist + yDist * yDist;
			if(distance < minDist) {
				minDist = distance;
				mapId = predicted[j].id;
			}
			observations[i].id = mapId;
		}
	}

}

void ParticleFilter::updateWeights(double sensor_range, double std_landmark[], 
		const std::vector<LandmarkObs> &observations, const Map &map_landmarks) {
	// TODO: Update the weights of each particle using a mult-variate Gaussian distribution. You can read
	//   more about this distribution here: https://en.wikipedia.org/wiki/Multivariate_normal_distribution
	// NOTE: The observations are given in the VEHICLE'S coordinate system. Your particles are located
	//   according to the MAP'S coordinate system. You will need to transform between the two systems.
	//   Keep in mind that this transformation requires both rotation AND translation (but no scaling).
	//   The following is a good resource for the theory:
	//   https://www.willamette.edu/~gorr/classes/GeneralGraphics/Transforms/transforms2d.htm
	//   and the following is a good resource for the actual equation to implement (look at equation 
	//   3.33
	//   http://planning.cs.uiuc.edu/node99.html

	//Each particle for loop
	for(int i = 0; i < num_particles; i++) {
		double p_x = particles[i].x;
		double p_y = particles[i].y;
		double p_theta = particles[i].theta;

		//Create a vector to hold the map landmark locations predicted to be within sensor range of the particle
		vector<LandmarkObs> predictions;

		//Each map landmark for loop
		for( unsigned int j = 0; j < map_landmarks.landmark_list.size(); j++) {

			//Get id and x,y coordinates
			float lm_x = map_landmarks.landmark_list[j].x_f;
			float lm_y = map_landmarks.landmark_list[j].y_f;
			int   lm_id = map_landmarks.landmark_list[j].id_i;

			float search_radius = sqrt( pow((lm_x - p_x), 2) + pow((lm_y - p_y),2));
			
			//Only consider landmarks within sensor range of the particle 
			if(search_radius <= sensor_range ) {
				predictions.push_back(LandmarkObs{ lm_id, lm_x, lm_y });
			}
		}

		/*
        Create and populate a copy of the list of observations transformed from 
        vehicle coordinates to map coordinates
        */
		vector<LandmarkObs> remap;
		for(unsigned int j = 0; j < observations.size(); j++) {
			double t_x = cos(p_theta)*observations[j].x - sin(p_theta)*observations[j].y + p_x;
			double t_y = sin(p_theta)*observations[j].x + cos(p_theta)*observations[j].y + p_y;
			remap.push_back(LandmarkObs{ observations[j].id, t_x, t_y });
		}

		/*
        Data association for the predictions and transformed 
        observations on current particle
        */
		dataAssociation(predictions, remap);

		for(unsigned int j = 0; j < remap.size(); j++) {
			double obs_x, obs_y, pred_x, pred_y;
			obs_x = remap[j].x;
			obs_y = remap[j].y;

			//x,y coordinates of the prediction associated with the current observation
			for(unsigned int k = 0; k < predictions.size(); k++) {
				if(predictions[k].id == remap[j].id) {
					pred_x = predictions[k].x;
					pred_y = predictions[k].y;
				}
			}

			//Weight for this observation with multivariate Gaussian
			double s_x = std_landmark[0];
			double s_y = std_landmark[1];
			double obs_w = ( 1/(2*M_PI*s_x*s_y)) * exp( -( pow(pred_x-obs_x,2)/(2*pow(s_x, 2)) + (pow(pred_y-obs_y,2)/(2*pow(s_y, 2))) ) );

			//Product of this obersvation weight with total observations weight
			particles[i].weight = obs_w;
		}
	}
}

void ParticleFilter::resample() {
	// TODO: Resample particles with replacement with probability proportional to their weight. 
	// NOTE: You may find std::discrete_distribution helpful here.
	//   http://en.cppreference.com/w/cpp/numeric/random/discrete_distribution

	//Get weights and max weight.
	vector<double> weights;
	double maxWeight = -1000000;
	for(int i = 0; i < num_particles; i++) {
		weights.push_back(particles[i].weight);
		if(particles[i].weight > maxWeight) {
			maxWeight = particles[i].weight;
		}
	}

	uniform_real_distribution<double> distDouble(0.0, maxWeight);
	uniform_int_distribution<int> distInt(0, num_particles - 1);
	int index = distInt(gen);
	double beta = 0.0;
	vector<Particle> resampledParticles;
	for(int i = 0; i < num_particles; i++) {
		beta += distDouble(gen) * 2.0;
		while(beta > weights[index]) {
			beta -= weights[index];
			index = (index + 1) % num_particles;
		}
		resampledParticles.push_back(particles[index]);
	}

	particles = resampledParticles;

}

void ParticleFilter::SetAssociations(Particle& particle, const std::vector<int>& associations, 
                                     const std::vector<double>& sense_x, const std::vector<double>& sense_y)
{
    //particle: the particle to assign each listed association, and association's (x,y) world coordinates mapping to
    // associations: The landmark id that goes along with each listed association
    // sense_x: the associations x mapping already converted to world coordinates
    // sense_y: the associations y mapping already converted to world coordinates
	
    particle.associations= associations;
    particle.sense_x = sense_x;
    particle.sense_y = sense_y;
}

string ParticleFilter::getAssociations(Particle best)
{
	vector<int> v = best.associations;
	stringstream ss;
    copy( v.begin(), v.end(), ostream_iterator<int>(ss, " "));
    string s = ss.str();
    s = s.substr(0, s.length()-1);  // get rid of the trailing space
    return s;
}
string ParticleFilter::getSenseCoord(Particle best, string coord)
{
	vector<double> v;
  	if (coord == "X") {
		v = best.sense_x;
	} else if (coord == "Y") {
		v = best.sense_y;
	} else {
		std::cout << "Coordinat Selector not set " << endl;
	}
	stringstream ss;
    copy( v.begin(), v.end(), ostream_iterator<float>(ss, " "));
    string s = ss.str();
    s = s.substr(0, s.length()-1);  // get rid of the trailing space
    return s;
}
