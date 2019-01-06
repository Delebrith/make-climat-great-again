import sys

import matplotlib.pyplot as plt
import numpy as np
from scipy.misc import imread

from src.point import load_from_csv


def add_sphere(subplot, center, radius, color):
    # based on https://stackoverflow.com/a/31775938/7108762
    radius *= 0.99
    phi, theta = np.mgrid[0.0:2.0 * np.pi:100j, 0.0:2.0 * np.pi:100j]
    x = center[0] + radius * np.cos(phi) * np.cos(theta)
    y = center[1] + radius * np.cos(phi) * np.sin(theta)
    z = center[2] + radius * np.sin(phi)

    subplot.plot_surface(
        x, y, z,  rstride=1, cstride=1, color=color, alpha=0.4, linewidth=0)


def _visualise_on_sphere(points, colors):
    center = 0.5, 0.5, 0.5
    radius = 0.5

    coords = [point.get_cartesian_coordinates(center, radius) for point in points]
    xx, yy, zz = zip(*coords)

    fig = plt.figure()
    subplot = fig.add_subplot(1, 1, 1, projection="3d")

    add_sphere(subplot, center, radius, "green")

    subplot.scatter(xx, yy, zz, color=colors, s=20)

    subplot.set_xlim([0, 1])
    subplot.set_ylim([0, 1])
    subplot.set_zlim([0, 1])
    subplot.set_aspect("equal")

    plt.tight_layout()
    plt.show()


def _visualise_as_map(points, colors):
    xx = [p.longitude / 180 for p in points]
    yy = [0.5 + p.latitude / 180 for p in points]

    img = imread("src/resource/equidstant-projection.jpg")
    plt.imshow(img, zorder=0, extent=[-1., 1., 0., 1.])

    plt.scatter(xx, yy, c=colors)
    plt.show()


def visualise(points, color_mapper, as_map=False):
    """

    :param points: iterable collection of points
    :param color_mapper: function that as an argument takes point and returns it's color
    :param as_map:
    :return: None
    """
    colors = [color_mapper(point) for point in points]

    if not as_map:
        _visualise_on_sphere(points, colors)
    else:
        _visualise_as_map(points, colors)


def main():
    if len(sys.argv) != 2:
        exit("Invalid argument number. Required: .csv file name with points")

    points = load_from_csv(sys.argv[1])

    min_regression = min(points, key=lambda p: p.regression).regression
    max_regression = max(points, key=lambda p: p.regression).regression
    avg_regression = sum([p.regression for p in points]) / len(points)

    print("Minimal regression coefficent in data: {}".format(min_regression))
    print("Maximal regression coefficent in data: {}".format(max_regression))
    print("Average regression coefficent in data: {}".format(avg_regression))
    print("Number of data points: {}".format(len(points)))

    def regression_color_mapper(point):
        range_ = max_regression - min_regression

        regression_normalized = (point.regression - min_regression) / range_

        blue_val = 1 if regression_normalized < 0.5 else 2 * (1 - regression_normalized)
        red_val = 1 if regression_normalized > 0.5 else 2 * regression_normalized

        return red_val, 0, blue_val

    visualise(points, regression_color_mapper, as_map=True)


if __name__ == '__main__':
    main()
