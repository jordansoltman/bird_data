import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import csv
import numpy as np
import DataPlot

plt.interactive(False)
# b - blue
# uv - ultraviolet
# bw - white


def extractData(xFieldname, yFieldname, data):
    xData = []
    yData = []
    for row in data:
        xData.append(float(row[xFieldname]))
        yData.append(float(row[yFieldname]))
    return (np.array(xData), np.array(yData))

def openFile(filename):
    try:
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            # First we need to determine the columns that are available
            # and we can assume that the first column is the time series
            fieldnames = list(reader.fieldnames)
            dataFieldNames = []

            for fieldname in fieldnames:
                if fieldname != '' and not fieldname.lower().startswith('time'):
                    dataFieldNames.append(fieldname)
            rows = list(reader)
            return (fieldnames[0], dataFieldNames, rows)
    except:
        print("There was an error opening ", filename)

def done(column, data):
    print(column, data)

rawData = openFile('/Users/jordansoltman/Desktop/sample_data.csv')
timeField = rawData[0]
fields = rawData[1]
data = rawData = rawData[2]

# axis = plt.axes()
# plt.Slider(axis, 'test', 1, 10)



xData, yData = extractData(timeField, 'B_1_10', data)


dataPlot = DataPlot.DataPlot('B_1_10', xData, yData, done)
dataPlot.plotData()