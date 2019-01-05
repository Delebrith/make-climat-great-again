import pandas
import numpy as np


class Point:
    def __init__(self, latitude, longitude, regression=0, label=""):
        self.latitude = _geo_coord_str_to_float(latitude, 'N', 'S') if type(latitude) is str else float(latitude)
        self.longitude = _geo_coord_str_to_float(longitude, 'W', 'E') if type(longitude) is str else float(longitude)

        self.regression = float(regression)
        self.label = label

    def get_cartesian_coordinates(self, center, radius):
        x = center[0] + radius * np.cos(self.latitude * np.pi / 180) * np.sin(self.longitude * np.pi / 180)
        y = center[1] + radius * np.cos(self.latitude * np.pi / 180) * np.cos(self.longitude * np.pi / 180)
        z = center[2] + radius * np.sin(self.latitude * np.pi / 180)

        return x, y, z

    def __str__(self):
        return "{}\t{}\t{}".format(
            self.label,
            _geo_coord_float_to_str(self.latitude, 'N', 'S'),
            _geo_coord_float_to_str(self.longitude, 'W', 'E'))


def _geo_coord_str_to_float(str_, positive, negative):
    if str_.endswith(positive):
        return float(str_[:-len(positive)])
    elif str_.endswith(negative):
        return -float(str_[:-len(negative)])
    else:
        return float(str_)


def _geo_coord_float_to_str(coord, positive, negative):
    return str(coord) + (positive if coord >= 0 else negative)


def load_from_csv(filename):
    dataframe = pandas.read_csv(filename)

    return [Point(row['Latitude'], row['Longitude'], row['Regression'], row['City']) for _, row in dataframe.iterrows()]
