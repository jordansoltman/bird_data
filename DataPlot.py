import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import math
import csv
import numpy as np
import time

MAX_PROMINENCE = 6.0
FALSE_MAXIMUM_ROW_DISTANCE = 10

class DataPlot:

    def __init__(self, column, xData, yData, doneCallback):

        self.yData = yData
        self.xData = xData

        self.doneCallback = doneCallback

        self.offset = False
        self.minimums = []
        self.maximums = []
        self.automaticallyInterpretedData = False

        parts = column.lower().split("_")
        if len(parts) != 3:
            return

        color, intensity, fps = parts

        if color == 'b':
            self.color = 'Blue'
        elif color == 'uv':
            self.color = 'Ultra Violet'
        elif color == 'bw':
            self.color = 'White'

        self.intensity = int(intensity)

        self.fps = int(fps)

        self.column = column

        self.min_prominence = 1
        self.max_prominence = 1

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Voltage")

        self.ax.name = 'main'

        self.fig.subplots_adjust(bottom=0.27)

        # Define an axes area and draw a slider in it
        min_prom_slider_ax = self.fig.add_axes([0.25, 0.17, 0.65, 0.03])
        self.min_prom_slider = plt.Slider(min_prom_slider_ax, 'Min. Prom.', 0.0, MAX_PROMINENCE, valinit=MAX_PROMINENCE)

        # Draw another slider
        max_prom_slider_ax = self.fig.add_axes([0.25, 0.12, 0.65, 0.03])
        self.max_prom_slider = plt.Slider(max_prom_slider_ax, 'Max. Prom.', 0.0, MAX_PROMINENCE, valinit=MAX_PROMINENCE)

        self.min_prom_slider.on_changed(self.updateProminence)
        self.max_prom_slider.on_changed(self.updateProminence)

        # axprev = plt.axes([0.7, 0.05, 0.1, 0.075])
        doneBtn = plt.axes([0.81, 0.05, 0.1, 0.045])

        bnext = plt.Button(doneBtn, 'Done')
        bnext.on_clicked(self.done)

        self.fig.canvas.mpl_connect('button_press_event', self.onclick)

        self.determineMaxProminence()
        self.determineMinProminence()

        self.attemptAutomaticDataInterpretation()

        self.plotData()
        plt.show()

    # This function assumes well formatted minimums and maximums
    def getMaximumMinimumValues(self):
        dataLength = len(self.minimums)
        for i in range(0, dataLength):
            

    # This function assumes well formatted minimums and maximums
    def determineAveragePeakHeightWidth(self):

        dataLength = len(self.minimums)
        dataMaxX = self.xData[-1]
        dataMinX = self.xData[0]
        totalWidth = 0
        totalHeight = 0

        for i in range(0, dataLength):
            min = self.minimums[i]
            max = self.maximums[i]
            minX = self.xData[min]
            minY = self.yData[min]
            maxX = self.xData[max]
            maxY = self.yData[max]

            # special case for offset graphs because they wrap around
            if i == 0 and self.offset:
                totalWidth += (dataMaxX - minX) + (maxX - dataMinX)
            else:
                totalWidth += maxX - minX

            totalHeight += maxY - minY

        averageHeight = totalHeight / dataLength
        averageWidth = totalWidth / dataLength

        return (averageHeight, averageWidth)

    def done(self, val):
        if len(self.minimums) != len(self.maximums):
            print("ERROR: Different number of minimums than maximums!")
            return
        averageHeight, averageWidth = self.determineAveragePeakHeightWidth()
        print(averageHeight, averageWidth)
        self.doneCallback(self.column, (self.minimums, self.maximums))
        plt.close()
        print("EXPORT")

    def title(self):
        return self.color + ", Intensity " + str(self.intensity) + " @ " + str(self.fps) + " fps (" + self.column + ")"

    def determineMaxProminence(self):
        maxAndMin = math.ceil(self.fps / 5.0)
        self.max_prominence = MAX_PROMINENCE

        while self.max_prominence > 0.0:
            self.max_prominence -= .1
            max_peaks = self.findMaxPeaks()
            if len(max_peaks) >= maxAndMin:
                break

        time.sleep(.2)
        self.max_prom_slider.set_val(self.max_prominence)

    def determineMinProminence(self):
        # determine how many peaks we are looking for
        maxAndMin = math.ceil(self.fps / 5.0)
        self.min_prominence = MAX_PROMINENCE

        while self.min_prominence > 0.0:
            self.min_prominence -= .1
            if len(self.findMinPeaks()) >= maxAndMin:
                break

        time.sleep(.2)
        self.min_prom_slider.set_val(self.min_prominence)

    def updateProminence(self, val):
        self.min_prominence = self.min_prom_slider.val
        self.max_prominence = self.max_prom_slider.val
        self.plotData()

    def filterClosePeaks(self, peaks):
        # if there are two peaks of equal height right next to each other
        # we want to filter that out...
        result = []
        for idx, val in enumerate(peaks):
            if idx == len(peaks) - 1 or \
                    abs(peaks[idx] - peaks[idx + 1]) > FALSE_MAXIMUM_ROW_DISTANCE or \
                    self.yData[peaks[idx]] != self.yData[peaks[idx + 1]]:
                result.append(val)
        return np.array(result)

    def findMaxPeaks(self):
        maxima, _ = find_peaks(self.yData, prominence=self.max_prominence)
        return self.filterClosePeaks(maxima)

    def findMinPeaks(self):
        minima, _ = find_peaks(-self.yData, prominence=self.min_prominence)
        return self.filterClosePeaks(minima)

    def findPeaks(self):
        return (self.findMaxPeaks(), self.findMinPeaks())

    def attemptAutomaticDataInterpretation(self):
        minPeaks = self.findMinPeaks()
        maxPeaks = self.findMaxPeaks()

        numPeaks = len(maxPeaks)

        # we must have the same number of peaks
        if len(maxPeaks) != len(minPeaks) or numPeaks == 0:
            return

        # offset means that a max comes before a min, in which case we compensate
        if minPeaks[0] > maxPeaks[0]:
            self.offset = True

        # ensure that all of the data points are in order
        for i in range(0, numPeaks):
            if  (self.offset and maxPeaks[i] > minPeaks[i]) or \
                (not self.offset and minPeaks[i] > maxPeaks[i]):
                return

        #if we get here we know that the data must be formatted well
        self.automaticallyInterpretedData = True

        if not self.offset:
            self.minimums = minPeaks
            self.maximums = maxPeaks

        if self.offset:
            self.maximums = maxPeaks
            self.minimums = np.append(minPeaks[1:],minPeaks[0])




    def plotData(self):
        maxima, minima = self.findPeaks()
        self.ax.clear()
        self.ax.set_title(self.title())
        self.ax.plot(self.xData, self.yData)
        if len(maxima) > 0:
            self.ax.plot(self.xData[maxima], self.yData[maxima], "o", alpha=0.7, color='darkgreen')
        if len(minima) > 0:
            self.ax.plot(self.xData[minima], self.yData[minima], "o", alpha=0.7, color='darkred')

        for idx, val in enumerate(self.minimums):
            self.ax.annotate(str(idx + 1) + " min", (self.xData[val], self.yData[val]), textcoords='offset pixels', xytext=(10, -15), fontweight='bold',
                    fontsize=8, color='darkred')

        for idx, val in enumerate(self.maximums):
            self.ax.annotate(str(idx + 1) + " max", (self.xData[val], self.yData[val]), textcoords='offset pixels',
                             xytext=(10, 10), fontweight='bold',
                             fontsize=8, color='darkgreen')

        plt.show(block=False)

    def onclick(self, event):
        if event.inaxes == None or event.inaxes.name != 'main':
            return
        print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              ('double' if event.dblclick else 'single', event.button,
               event.x, event.y, event.xdata, event.ydata))

        self.ax.annotate("1 min", (event.xdata, event.ydata), textcoords='offset pixels', xytext=(10, -10), fontweight='bold',
                    fontsize=8, color='darkred')
        plt.draw()
