class KalmanFilter:
    def __init__(self, process_variance, measurement_variance, initial_estimate=0, initial_estimate_uncertainty=1):
        self.process_variance = process_variance  # Q: Process noise variance
        self.measurement_variance = measurement_variance  # R: Measurement noise variance
        self.estimate = initial_estimate  # Initial estimate
        self.estimate_uncertainty = initial_estimate_uncertainty  # P: Initial estimate uncertainty

    def update(self, measurement):
        # Kalman Gain
        kalman_gain = self.estimate_uncertainty / (self.estimate_uncertainty + self.measurement_variance)

        # Update estimate with measurement
        self.estimate = self.estimate + kalman_gain * (measurement - self.estimate)

        # Update estimate uncertainty
        self.estimate_uncertainty = (1 - kalman_gain) * self.estimate_uncertainty + self.process_variance

        return self.estimate
