import sys
from datetime import datetime

import pandas
from scipy.stats import linregress


def main():
    if len(sys.argv) != 3:
        exit("Invalid number of arguments. Input and output .csv files' names required")

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    data_frame = pandas.read_csv(input_file, usecols=["dt", "AverageTemperature", "City", "Latitude", "Longitude"])
    data_by_location = data_frame.groupby(by=["City", "Latitude", "Longitude"])
    data_by_location = data_by_location.apply(temperature_series_to_regression)
    data_by_location.to_csv(output_file, header=True)


def temperature_series_to_regression(temperatures: pandas.Series):
    temperatures = temperatures.dropna()
    regression = linregress(temperatures["dt"].map(map_date), temperatures["AverageTemperature"])[0]
    print("{}: {}".format(list(temperatures["City"])[0], regression))
    return pandas.Series(regression, index=["Regression"])


def map_date(date_string):
    return datetime.strptime(date_string, "%Y-%M-%d").year


if __name__ == '__main__':
    main()
