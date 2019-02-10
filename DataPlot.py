import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import math
import csv
import numpy as np
import time

colorSets = ['blue', 'orange', 'purple', 'greenyellow', 'brown', 'gold', 'lightskyblue', 'gray', 'blueviolet', 'olive']

plt.interactive(False)

class DataPlot:

    def __init__(self, column, xData, yData, doneCallback, skipCallback, dumpCallback, exitCallback, doneButtonTitle='Done', MAX_PROMINENCE=6.0, FALSE_MAXIMUM_ROW_DISTANCE = 30):

        self.MAX_PROMINENCE = MAX_PROMINENCE
        self.FALSE_MAXIMUM_ROW_DISTANCE = FALSE_MAXIMUM_ROW_DISTANCE

        self.yData = yData
        self.xData = xData

        self.doneCallback = doneCallback
        self.skipCallback = skipCallback
        self.dumpCallback = dumpCallback
        self.exitCallback = exitCallback

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

        self.fig.subplots_adjust(bottom=0.27, top=0.92, left=0.08, right=0.94)

        # Define an axes area and draw a slider in it
        min_prom_slider_ax = self.fig.add_axes([0.25, 0.17, 0.65, 0.03])
        self.min_prom_slider = plt.Slider(min_prom_slider_ax, 'Min. Prom.', 0.0, MAX_PROMINENCE, valinit=MAX_PROMINENCE)

        # Draw another slider
        max_prom_slider_ax = self.fig.add_axes([0.25, 0.12, 0.65, 0.03])
        self.max_prom_slider = plt.Slider(max_prom_slider_ax, 'Max. Prom.', 0.0, MAX_PROMINENCE, valinit=MAX_PROMINENCE)

        self.min_prom_slider.on_changed(self.updateProminence)
        self.max_prom_slider.on_changed(self.updateProminence)

        # axprev =
        doneButtonAxes = plt.axes([0.80, 0.05, 0.1, 0.045])
        self.doneButton = plt.Button(doneButtonAxes, doneButtonTitle)
        self.doneButton.on_clicked(self.done)

        resetBtn = plt.axes([0.70, 0.05, 0.1, 0.045])
        self.resetButton = plt.Button(resetBtn, 'Reset')
        self.resetButton.on_clicked(self.reset)

        skipButtonAxes = plt.axes([0.60, 0.05, 0.1, 0.045])
        self.skipButton = plt.Button(skipButtonAxes, 'Skip')
        self.skipButton.on_clicked(self.skip)

        dumpButtonAxes = plt.axes([0.50, 0.05, 0.1, 0.045])
        dumpButton = plt.Button(dumpButtonAxes, 'Dump')
        dumpButton.on_clicked(self.dump)

        exitButtonAxes = plt.axes([0.40, 0.05, 0.1, 0.045])
        exitButton = plt.Button(exitButtonAxes, 'Exit')
        exitButton.on_clicked(self.exit)

        self.fig.canvas.mpl_connect('button_press_event', self.onclick)

        self.determineMaxProminence()
        self.determineMinProminence()

        self.attemptAutomaticDataInterpretation()

        self.plotData()
        plt.show()
        plt.clf()
        plt.cla()
        plt.close()

    # This function assumes well formatted minimums and maximums
    def getMaximumMinimumPairs(self):
        minimums, maximums = self.getOrderedMaximumAndMinimum()
        results = []
        dataLength = max(len(maximums), len(minimums))
        for i in range(0, dataLength):
            if i < len(minimums):
                _min = self.minimums[i]
                minX = self.xData[_min]
                minY = self.yData[_min]
            else:
                minX = '-'
                minY = '-'

            if i < len(maximums):
                _max = self.maximums[i]
                maxX = self.xData[_max]
                maxY = self.xData[_max]
            else:
                maxX = '-'
                maxY = '-'
            results.append(((minX, minY), (maxX, maxY)))
        return results

    def minMaxAreOffset(self):
        return sorted(self.minimums)[0] > sorted(self.maximums)[0]

    # This function assumes well formatted minimums and maximums of the same length
    def determineAveragePeakHeightWidth(self):

        minimums, maximums = self.getOrderedMaximumAndMinimum()

        dataLength = len(self.minimums)
        dataMaxX = self.xData[-1]
        dataMinX = self.xData[0]
        totalWidth = 0
        totalHeight = 0

        for i in range(0, dataLength):
            min = minimums[i]
            max = maximums[i]
            minX = self.xData[min]
            minY = self.yData[min]
            maxX = self.xData[max]
            maxY = self.yData[max]

            # we discard offset data
            if i != 0 or not self.minMaxAreOffset():
                totalWidth += maxX - minX

            totalHeight += maxY - minY

        averageHeight = totalHeight / dataLength
        averageWidth = totalWidth / dataLength

        # We can't calculate the offset for a single vale
        if self.minMaxAreOffset() and dataLength == 1:
            averageWidth = 'N/A'

        return (averageHeight, averageWidth)

    def validateMinMaxCorrectLength(self):
        minimums, maximums = self.getOrderedMaximumAndMinimum()
        reqPeaks = self.requiredPeaks()
        return reqPeaks == len(minimums) and reqPeaks == len(maximums)

    def validateMinMax(self, verbose=False):

        minimums, maximums = self.getOrderedMaximumAndMinimum()

        if len(minimums) != len(maximums):
            if verbose:
                print("ERROR: Different number of minimums than maximums!")
            return False
        if len(minimums) == 0 or len(maximums) == 0:
            if verbose:
                print("ERROR: Minimums or maximums array length is zero.")
            return False

        # check that the data is in proper order
        offset = self.minMaxAreOffset()
        if (offset and minimums[0] < maximums[0]) or (not offset and minimums[0] > maximums[0]):
            if verbose:
                print("ERROR: minimums/maximums not in proper order")
            return False

        for i in range(1, len(minimums)):
            if (minimums[i] > maximums[i]):
                if verbose:
                    print("ERROR: minimums/maximums not in proper order")
                return False
        return True

    def reset(self, val):
        self.determineMaxProminence()
        self.determineMinProminence()
        self.attemptAutomaticDataInterpretation()
        self.plotData()

    def skip(self, val):
        self.skipCallback()
        plt.close()

    def exit(self, val):
        self.exitCallback()

    def dump(self, val):
        self.dumpCallback()

    # holding f key while clicking done overrides validation for better or for worse
    def done(self, event):
        if event.key != 'f' and not self.validateMinMax(verbose=True):
            return
        # We can't calculate the average height and average duration if it's forced
        if event.key != 'f':
            averageHeight, averageDuration = self.determineAveragePeakHeightWidth()
        else:
            averageHeight = averageDuration = 'N/A'
        minMaxPairs = self.getMaximumMinimumPairs()
        self.doneCallback(self.column, minMaxPairs, averageHeight, averageDuration)
        plt.show(block=True)
        plt.clf()
        plt.cla()
        plt.close()

    def title(self):
        return self.color + ", Intensity " + str(self.intensity) + " @ " + str(self.fps) + " fps (" + self.column + ") Expecting " + str(self.requiredPeaks()) + " peaks"

    def determineMaxProminence(self):
        maxAndMin = self.requiredPeaks()
        self.max_prominence = self.MAX_PROMINENCE

        while self.max_prominence > 0.0:
            self.max_prominence -= .1
            max_peaks = self.findMaxPeaks()
            if len(max_peaks) >= maxAndMin:
                break

        time.sleep(.2)
        self.max_prom_slider.set_val(self.max_prominence)

    def determineMinProminence(self):
        # determine how many peaks we are looking for
        maxAndMin = self.requiredPeaks()
        self.min_prominence = self.MAX_PROMINENCE

        while self.min_prominence > 0.0:
            self.min_prominence -= .1
            if len(self.findMinPeaks()) >= maxAndMin:
                break

        time.sleep(.2)
        self.min_prom_slider.set_val(self.min_prominence)

    def requiredPeaks(self):
        return math.ceil(self.fps / 5.0)

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
                    abs(peaks[idx] - peaks[idx + 1]) > self.FALSE_MAXIMUM_ROW_DISTANCE or \
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

        # make smarter b_1_40

        self.minimums = minPeaks
        self.maximums = maxPeaks

    def plotData(self):
        maxima, minima = self.findPeaks()

        validated = self.validateMinMax()
        correctLength = self.validateMinMaxCorrectLength()

        if validated and correctLength:
            self.doneButton.color = 'green'
            self.doneButton.hovercolor = 'darkgreen'
        elif validated and not correctLength:
            self.doneButton.color = 'yellow'
            self.doneButton.hovercolor = 'gold'
        else:
            self.doneButton.color = 'red'
            self.doneButton.hovercolor = 'darkred'

        self.ax.clear()
        self.ax.set_title(self.title())
        self.ax.plot(self.xData, self.yData)
        if len(maxima) > 0:
            self.ax.plot(self.xData[maxima], self.yData[maxima], "o", alpha=0.7, color='darkgreen')
        if len(minima) > 0:
            self.ax.plot(self.xData[minima], self.yData[minima], "o", alpha=0.7, color='darkred')

        minimums, maximiums = self.getOrderedMaximumAndMinimum()

        for idx, val in enumerate(minimums):
            self.ax.annotate(str(idx + 1) + " min", (self.xData[val], self.yData[val]), textcoords='offset pixels', xytext=(15, -15), fontweight='bold',
                    fontsize=8, color=colorSets[idx % len(colorSets)], arrowprops={'arrowstyle': '->'})

        for idx, val in enumerate(maximiums):
            self.ax.annotate(str(idx + 1) + " max", (self.xData[val], self.yData[val]), textcoords='offset pixels',
                             xytext=(15, 15), fontweight='bold',
                             fontsize=8, color=colorSets[idx % len(colorSets)], arrowprops={'arrowstyle': '->'})

        plt.show(block=False)
        plt.draw()
        self.fig.canvas.flush_events()

    # orders the minimums and maximums taking account for any offsets that may be in place
    def getOrderedMaximumAndMinimum(self):

        maximums = sorted(self.maximums)
        minimums = sorted(self.minimums)

        if len(maximums) == 0 or len(minimums) == 0:
            return (minimums, maximums)

        if self.minMaxAreOffset():
            minArray = [minimums[-1]]
            minArray.extend(minimums[:-1])
            return (minArray, maximums)
        else:
            return (minimums, maximums)

    def addRemoveMinMax(self, clickX, clickY):

        # we create sets here so we only get the unique values
        minSet = set(self.findMinPeaks())
        minSet.update(self.minimums)

        maxSet = set(self.findMaxPeaks())
        maxSet.update(self.maximums)

        minPeakDistances = []
        maxPeakDistances = []

        minList = list(minSet)
        maxList = list(maxSet)


        # Since the x/y scales are different we get the aspect ratio to better
        # determine which point was closest to being clicked
        yb, yt = self.ax.get_ylim()
        xl, xr = self.ax.get_xlim()

        aspect = abs(yt - yb) / abs(xl - xr)

        for val in minList:
            peakX = self.xData[val]
            peakY = self.yData[val]
            distance = math.hypot(aspect * (clickX - peakX), clickY - peakY)
            minPeakDistances.append(distance)

        for val in maxList:
            peakX = self.xData[val]
            peakY = self.yData[val]
            distance = math.hypot(aspect * (clickX - peakX), clickY - peakY)
            maxPeakDistances.append(distance)

        closestMinPeak = min(minPeakDistances)
        closestMaxPeak = min(maxPeakDistances)

        if closestMinPeak < closestMaxPeak:
            idx = minPeakDistances.index(closestMinPeak)
            val = minList[idx]
            self.insertRemoveMin(val)
        else:
            idx = maxPeakDistances.index(closestMaxPeak)
            val = maxList[idx]
            self.insertRemoveMax(val)

    def insertRemoveMax(self, val):
        if val in self.maximums:
            self.maximums = self.maximums[self.maximums != val]
        else:
            self.maximums = np.append(self.maximums, val)

    def insertRemoveMin(self, val):
        if val in self.minimums:
            self.minimums = self.minimums[self.minimums != val]
        else:
            self.minimums = np.append(self.minimums, val)

    def onclick(self, event):
        # only do something if we are over the graph
        if event.inaxes == None or event.inaxes.name != 'main':
            return

        self.addRemoveMinMax(event.xdata, event.ydata)
        self.plotData()
