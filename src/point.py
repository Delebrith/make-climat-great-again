import pandas
import numpy as np


class Point:
    def __init__(self, latitude, longitude, regression=0, label=""):
        self.latitude = _geo_coord_str_to_float(latitude, 'N', 'S') if type(latitude) is str else float(latitude)
        self.longitude = _geo_coord_str_to_float(longitude, 'E', 'W') if type(longitude) is str else float(longitude)

        self.regression = float(regression)
        self.label = label

    def get_cartesian_coordinates(self, center, radius):
        x = center[0] + radius * np.cos(self.latitude * np.pi / 180) * np.sin(self.longitude * np.pi / 180)
        y = center[1] + radius * np.cos(self.latitude * np.pi / 180) * np.cos(self.longitude * np.pi / 180)
        z = center[2] + radius * np.sin(self.latitude * np.pi / 180)

        return x, y, z

    def dist(self, point):
        """
        :param point: a Point
        :return: a Haversine distance between points in radians
        """
        lat1 = self.latitude * np.pi / 180
        lon1 = self.longitude * np.pi / 180
        lat2 = point.latitude * np.pi / 180
        lon2 = point.longitude * np.pi / 180

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        return 2 * np.arcsin(np.sqrt(a))

    def __str__(self):
        return "{}\t{}\t{}".format(
            self.label,
            _geo_coord_float_to_str(self.latitude, 'N', 'S'),
            _geo_coord_float_to_str(self.longitude, 'E', 'W'))

    def __hash__(self):
        return hash(self.label) ^ hash(self.latitude) ^ hash(self.longitude)

def _geo_coord_str_to_float(str_, positive, negative):
    if str_.endswith(positive):
        return float(str_[:-len(positive)])
    elif str_.endswith(negative):
        return -float(str_[:-len(negative)])
    else:
        return float(str_)


def _geo_coord_float_to_str(coord, positive, negative):
    return str(abs(coord)) + (positive if coord >= 0 else negative)


def load_from_csv(filename):
    dataframe = pandas.read_csv(filename)

    return [Point(row['Latitude'], row['Longitude'], row['Regression'], row['City']) for _, row in dataframe.iterrows()]

