import time

class PerformanceData:
    def __init__(self):
        #todo performance stats
        self.average_iteration_time : float = 0
        self.min_iteration_time : float = 0
        self.max_iteration_time : float = 0
        self.total_iterations : int = 0
        self.successful_iterations : int = 0

    def measure_model_iteration_performance(self, model_predict):
        start = time.time()
        model_predict() #todo actual model prediction function call
        end = time.time()
        delta = end - start
        self.average_iteration_time = (self.average_iteration_time * self.total_iterations + delta) / (self.total_iterations + 1)
        self.total_iterations += 1
        self.min_iteration_time = min(self.min_iteration_time, delta)
        self.max_iteration_time = max(self.max_iteration_time, delta)