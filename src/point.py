import pandas
import numpy as np


class Point:
    def __init__(self, latitude, longitude, regression=0, label=""):
        self.latitude = _geo_coord_str_to_float(latitude, 'N', 'S') if type(latitude) is str else float(latitude)
        self.longitude = _geo_coord_str_to_float(longitude, 'W', 'E') if type(longitude) is str else float(longitude)

        self.regression = float(regression)
        self.label = label

    def get_cartesian_coordinates(self, center, radius):
        x = center[0] + radius * np.cos(self.latitude) * np.sin(self.longitude)
        y = center[1] + radius * np.cos(self.latitude) * np.cos(self.longitude)
        z = center[2] + radius * np.sin(self.latitude)

        return x, y, z


def _geo_coord_str_to_float(str_, positive, negative):
    if str_.endswith(positive):
        return float(str_[:-len(positive)])
    elif str_.endswith(negative):
        return -float(str_[:len(negative)])
    else:
        return float(str_)


def load_from_csv(filename):
    dataframe = pandas.read_csv(filename)

    return [Point(row['Latitude'], row['Longitude'], row['Regression'], row['City']) for _, row in dataframe.iterrows()]
