import sys
from datetime import datetime

import pandas
from scipy.stats import linregress

import src.point as point


def main():
    if len(sys.argv) not in (3, 4):
        exit("Invalid number of arguments. Input and output .csv files' names required, may be followed by cities csv")

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    data_frame = pandas.read_csv(input_file, usecols=["dt", "AverageTemperature", "City", "Latitude", "Longitude"])
    data_by_location = data_frame.groupby(by=["City", "Latitude", "Longitude"], as_index=False)
    data_by_location = data_by_location.apply(temperature_series_to_regression)
    data_by_location = data_by_location.reset_index()

    if len(sys.argv) == 4:
        cities_file = sys.argv[3]
        cities_data_frame = pandas.read_csv(cities_file, usecols=["AccentCity", "Latitude", "Longitude"])
        data_by_location = data_by_location.apply(cities_location, axis=1, cities_data_frame=cities_data_frame)

    data_by_location.drop_duplicates(subset=["Latitude", "Longitude"])
    data_by_location.to_csv(output_file, header=True)

    points = point.load_from_csv(output_file)
    locations = [(p.longitude, p.latitude) for p in points]
    unique_locations = set(locations)

    print("Points: {}, Unique points: {}".format(len(locations), len(unique_locations)))


def temperature_series_to_regression(temperatures: pandas.Series):
    temperatures = temperatures.dropna()
    regression = linregress(temperatures["dt"].map(map_date), temperatures["AverageTemperature"])[0]
    print("{}: {}".format(list(temperatures["City"])[0], regression))
    return pandas.Series(regression, index=["Regression"])


def cities_location(data_by_location, cities_data_frame):
    results = cities_data_frame.loc[cities_data_frame['AccentCity'].str.lower() == data_by_location['City'].lower()]
    if results.shape[0] > 0:
        if results.shape[0] != 1:
            print("{}: {} results".format(data_by_location['City'], results.shape[0]))
            orig = point.Point(data_by_location['Latitude'], data_by_location['Longitude'])
            results = results\
                .assign(f=lambda r: [orig.dist(point.Point(lat, lon)) for lat, lon in zip(r.Latitude, r.Longitude)])\
                .sort_values('f')\
                .drop('f', axis=1)

            print("Changed location from {}, {} to {}, {}".format(
                data_by_location['Latitude'], data_by_location['Longitude'],
                results.iloc[0]['Latitude'], results.iloc[0]['Longitude']))

        data_by_location['Latitude'] = results.iloc[0]['Latitude']
        data_by_location['Longitude'] = results.iloc[0]['Longitude']
    else:
        print("{}: no results".format(data_by_location['City']))

    return data_by_location


def dist(data1, data2):
    lat1 = data1['Latitude']
    lon1 = data1['Longitude']
    lat2 = data2['Latitude']
    lon2 = data2['Longitude']


def map_date(date_string):
    return datetime.strptime(date_string, "%Y-%M-%d").year


if __name__ == '__main__':
    main()
