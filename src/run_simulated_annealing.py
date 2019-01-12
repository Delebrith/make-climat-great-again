from src.point import Point
from src.delaunay_diagram import DelaunayDiagram
from src.points_set import PointsSet
from src.simulated_annealing import SimulatedAnnealing

import pandas as pd
import argparse

import random


parser = argparse.ArgumentParser(description='Process parameters of simulated annealing')
parser.add_argument('--data')
parser.add_argument('--max_iterations')
parser.add_argument('--temperature')
parser.add_argument('--seed')
parser.add_argument('--minimal_density')
parser.add_argument('--minimal_regression')
args = parser.parse_args()


def main():
    points_df = pd.read_csv(args.data)
    points = [Point(p[1]['Latitude'], p[1]['Longitude'], p[1]['Regression'], p[1]['City'])
              for p in points_df.iterrows()]

    delaunay_diagram = DelaunayDiagram(points=points)
    starting_point = initiate(points, args.seed, args.minimal_regression)
    points_set = PointsSet(delaunay_diagram=delaunay_diagram, initial_point=starting_point,
                           minimal_point_density=float(args.minimal_density),
                           minimal_regression=float(args.minimal_regression))
    simulated_annealing = SimulatedAnnealing(points_set=points_set, temperature=float(args.temperature),
                                             max_iterations=int(args.max_iterations), seed=int(args.seed))
    result, best = simulated_annealing.calculate()
    simulated_annealing.save_history()

    print()
    print("Final result ({}) points:".format(len(result.points)))
    print(*result.points, sep=",\n")
    print()
    print("Best result ({}) points:".format(len(best)))
    print(*best, sep=",\n")


def initiate(points, seed, minimal_regression):
    random.seed(a=seed)
    while True:
        point = random.choice(points)
        if point.regression > float(minimal_regression):
            return point


if __name__ == '__main__':
   main()
