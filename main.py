import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import csv
import numpy as np

plt.interactive(False)
# b - blue
# uv - ultraviolet
# bw - white

min_prominence = 1
max_prominence = 1

fig = plt.figure()
ax = fig.add_subplot(111)

ax.set_xlabel("Time")
ax.set_ylabel("Speed")

ax.name = 'main'

fig.subplots_adjust(bottom=0.3)

# Define an axes area and draw a slider in it
min_prom_slider_ax  = fig.add_axes([0.25, 0.15, 0.65, 0.03])
min_prom_slider = plt.Slider(min_prom_slider_ax, 'Min. Prom.', 1.0, 10.0, valinit=1)

# Draw another slider
max_prom_slider_ax = fig.add_axes([0.25, 0.1, 0.65, 0.03])
max_prom_slider = plt.Slider(max_prom_slider_ax, 'Max. Prom.', 1.0, 10.0, valinit=1)

def updateProminence(val):
    min_prominence = min_prom_slider.val
    max_prominence = max_prom_slider.val
    plotData()

min_prom_slider.on_changed(updateProminence)
max_prom_slider.on_changed(updateProminence)

def findPeaks(yData):
    maxima, _ = find_peaks(yData, prominence=max_prominence)
    minima, _ = find_peaks(-yData, prominence=min_prominence)
    return (maxima, minima)

def plotData(xData, yData):
    maxima, minima = findPeaks(yData)
    ax.plot(xData, yData)
    ax.plot(xData[maxima], yData[maxima], "x")
    ax.plot(xData[minima], yData[minima], "o")
    plt.show(block=False)


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


rawData = openFile('/Users/jordansoltman/Desktop/sample_data.csv')
timeField = rawData[0]
fields = rawData[1]
data = rawData = rawData[2]

# axis = plt.axes()
# plt.Slider(axis, 'test', 1, 10)


def onclick(event):
    if event.inaxes.name != 'main':
        return
    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata))

    ax.annotate("1 min", (event.xdata, event.ydata), textcoords='offset pixels', xytext=(10, 10), fontweight='bold', fontsize=8, color='darkred')
    plt.draw()

cid = fig.canvas.mpl_connect('button_press_event', onclick)




data = extractData(timeField, 'B_1_2', data)
plotData(data[0], data[1])

plt.show()