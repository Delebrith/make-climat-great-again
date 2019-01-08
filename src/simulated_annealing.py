from src.points_set import PointsSet

import random
import math
import signal


class SimulatedAnnealing:
    def __init__(self, points_set: PointsSet, temperature=1.0, max_iterations=100000, seed=1):
        self._points_set = points_set
        self._temperature = temperature
        self._t0 = temperature

        self._max_iterations = max_iterations
        self._iterations = 0
        self._time_to_stop = False
        signal.signal(signal.SIGINT, self.__signal_handler)

        self._max_value = 0

        random.seed(a=seed)

    def __signal_handler(self, signal, frame):
        print('Algorithm manually stopped.')
        self._time_to_stop = True

    def _annealing_rate(self, old_value, new_value):
        return math.exp(-abs(new_value - old_value) / self._temperature)

    def _next_iteration(self):
        self._iterations += 1
        # decide whether to add a point or remove it
        adding_probability = len(self._points_set.points_to_add) / (len(self._points_set.points_to_add)
                                                                    + len(self._points_set.points_to_remove))

        if random.random() <= adding_probability:
            # select point to add
            point = random.sample(self._points_set.points_to_add, 1)[0]
            old_value = self._points_set.value
            new_value = self._points_set.value_with_added(point)

            if new_value > old_value:
                self._points_set.add_point(point)
            elif random.random() < self._annealing_rate(old_value, new_value):
                self._points_set.add_point(point)

        else:
            # select point to remove
            point = random.sample(self._points_set.points_to_remove, 1)[0]
            old_value = self._points_set.value
            new_value = self._points_set.value_with_removed(point)

            if new_value > old_value:
                self._points_set.remove_point(point)
            elif random.random() < self._annealing_rate(old_value, new_value):
                self._points_set.remove_point(point)

        # similar to built-in mathlab way for simulated annealing
        self._temperature = self._t0 * math.pow(0.95, self._iterations)

    def calculate(self):
        best_points = set()
        self.log()
        while self._iterations < self._max_iterations and not self._time_to_stop:
            self._next_iteration()
            if self._points_set.has_minimal_density and self._points_set.value > self._max_value:
                self._max_value = self._points_set.value
                best_points = set(self._points_set.points)
            self.log()
        return self._points_set, best_points

    def log(self):
        print("{}/{}:\tArea\t{}\tValue\t{}\tMax Value\t{}\tMinimal Density\t{}\tDensity\t{}"
              .format(self._iterations, self._max_iterations, self._points_set.area,
                      self._points_set.value, self._max_value, self._points_set._minimal_point_density,
                      len(self._points_set.points) / self._points_set.area if self._points_set.area > 0 else 0))
