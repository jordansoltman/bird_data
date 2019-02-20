import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import math
import csv
import numpy as np
import time

colorSets = ['blue', 'orange', 'purple', 'magenta', 'brown', 'gold', 'lightskyblue', 'gray', 'blueviolet', 'olive']

class DataPlot:

    def __init__(self, doneCallback, skipCallback, dumpCallback, exitCallback, prevCallback, background, MAX_PROMINENCE=6.0, FALSE_MAXIMUM_ROW_DISTANCE = 30):

        self.MAX_PROMINENCE = MAX_PROMINENCE
        self.FALSE_MAXIMUM_ROW_DISTANCE = FALSE_MAXIMUM_ROW_DISTANCE

        self.doneCallback = doneCallback
        self.skipCallback = skipCallback
        self.dumpCallback = dumpCallback
        self.exitCallback = exitCallback
        self.prevCallback = prevCallback

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

        self.background = background

        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Voltage")

        self.titleColor = 'black'

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

        self.doneButtonTitle = 'Done'

        doneButtonAxes = plt.axes([0.80, 0.05, 0.1, 0.045])
        self.doneButton = plt.Button(doneButtonAxes, self.doneButtonTitle)
        self.doneButton.on_clicked(self.done)

        resetBtn = plt.axes([0.69, 0.05, 0.1, 0.045])
        self.resetButton = plt.Button(resetBtn, 'Auto')
        self.resetButton.on_clicked(self.reset)

        skipButtonAxes = plt.axes([0.58, 0.05, 0.1, 0.045])
        self.skipButton = plt.Button(skipButtonAxes, 'Skip')
        self.skipButton.on_clicked(self.skip)

        dumpButtonAxes = plt.axes([0.47, 0.05, 0.1, 0.045])
        self.dumpButton = plt.Button(dumpButtonAxes, 'Dump')
        self.dumpButton.on_clicked(self.dump)

        clearButtonAxes = plt.axes([0.36, 0.05, 0.1, 0.045])
        self.clearButton = plt.Button(clearButtonAxes, 'Clear')
        self.clearButton.on_clicked(self.clear)

        prevButtonAxes = plt.axes([0.25, 0.05, 0.1, 0.045])
        self.prevButton = plt.Button(prevButtonAxes, 'Prev')
        self.prevButton.on_clicked(self.prev)

        exitButtonAxes = plt.axes([0.14, 0.05, 0.1, 0.045])
        self.exitButton = plt.Button(exitButtonAxes, 'Exit')
        self.exitButton.on_clicked(self.exit)

        self.fig.canvas.mpl_connect('button_press_event', self.onclick)


    def initializePlot(self, column, xData, yData, saved, forced, doneButtonTitle='Done'):

        self.yData = yData
        self.xData = xData

        self.minimums = np.array([], dtype=np.int_)
        self.maximums = np.array([], dtype=np.int_)

        self.column = column

        parts = column.lower().split("_")
        if len(parts) != 3:
            # should error here
            return

        color, intensity, fps = parts

        if color == 'b':
            self.color = 'Blue'
        elif color == 'uv':
            self.color = 'Ultra Violet'
        elif color == 'bw':
            self.color = 'White'

        self.intensity = int(intensity)


        self.fps = int(fps[:-1] if self.background else fps)

        self.min_prominence = 0
        self.max_prominence = 0

        self.doneButtonTitle = doneButtonTitle
        self.doneButton.label.set_text(doneButtonTitle)

        self.determineMaxProminence()
        self.determineMinProminence()

        self.attemptAutomaticDataInterpretation()

        if forced:
            self.titleColor = 'red'
        elif saved:
            self.titleColor = 'green'
        else:
            self.titleColor = 'black'

        self.plotData()

        plt.show() # I don't know why but this has to be here

    # This function assumes well formatted minimums and maximums
    def getMaximumMinimumPairs(self):
        minimums, maximums = self.getOrderedMaximumAndMinimum(self.minimums, self.maximums)
        results = []
        dataLength = max(len(maximums), len(minimums))
        for i in range(0, dataLength):
            if i < len(minimums):
                _min = minimums[i]
                minX = self.xData[_min]
                minY = self.yData[_min]
            else:
                minX = '-'
                minY = '-'

            if i < len(maximums):
                _max = maximums[i]
                maxX = self.xData[_max]
                maxY = self.yData[_max]
            else:
                maxX = '-'
                maxY = '-'
            results.append(((minX, minY), (maxX, maxY)))
        return results

    def minMaxAreOffset(self, minimums, maximums):
        return sorted(minimums)[0] > sorted(maximums)[0]

    # This function assumes well formatted minimums and maximums of the same length
    def determineAveragePeakHeightWidth(self):

        minimums, maximums = self.getOrderedMaximumAndMinimum(self.minimums, self.maximums)

        dataLength = len(self.minimums)

        widths = []
        heights = []

        for i in range(0, dataLength):
            min = minimums[i]
            max = maximums[i]
            minX = self.xData[min]
            minY = self.yData[min]
            maxX = self.xData[max]
            maxY = self.yData[max]

            # we discard offset data
            if i != 0 or not self.minMaxAreOffset(self.minimums, self.maximums):
                widths.append(maxX - minX)

            heights.append(maxY - minY)

        # this is wrong, average width might not be correct
        averageHeight = np.mean(heights)
        averageWidth = np.mean(widths)
        heightStdDev = np.std(heights)
        widthStdDev = np.std(widths)

        # We can't calculate the offset for a single value
        if self.minMaxAreOffset(self.minimums, self.maximums) and dataLength == 1:
            averageWidth = 'N/A'

        return (averageHeight, averageWidth, heightStdDev, widthStdDev)

    def validateMinMax(self, verbose=False):

        minimums, maximums = self.getOrderedMaximumAndMinimum(self.minimums, self.maximums)

        minLength = min(len(maximums), len(minimums))

        if len(minimums) == 0 or len(maximums) == 0:
            if verbose:
                print("ERROR: Minimums or maximums array length is zero.")
            return (False, -1, 'zero_length')

        # check that the data is in proper order
        offset = self.minMaxAreOffset(minimums, maximums)
        if (offset and minimums[0] < maximums[0]) or (not offset and minimums[0] > maximums[0]):
            if verbose:
                print("ERROR: minimums/maximums not in proper order")
            return (False, 0, 'improper_order')

        interwoven = []
        # first interweave the min/max pairs
        for i in range(1, minLength):
            interwoven.append(minimums[i])
            interwoven.append(maximums[i])

        for i in range(0, len(interwoven) - 1):
            val1 = interwoven[i]
            val2 = interwoven[i + 1]
            if val1 > val2:
                if verbose:
                    print("ERROR: minimums/maximums not in proper order")
                return (False, int(i / 2) + 1, 'improper_order')

        if len(minimums) != len(maximums):
            if verbose:
                print("ERROR: Different number of minimums (" + str(len(minimums)) + ") than maximums (" + str(len(maximums)) + ")!")
            return (False, minLength, 'len_min_max_different')

        reqPeaks = self.requiredPeaks()
        if reqPeaks != len(minimums) or reqPeaks != len(maximums):
            if verbose:
                print("ERROR: Expected " + str(reqPeaks) + " peaks but have " + str(len(minimums)) + ".")
            return (False, -1, 'wrong_peak_count')

        return (True, -1, None)

    def reset(self, val):
        self.determineMaxProminence()
        self.determineMinProminence()
        self.attemptAutomaticDataInterpretation()
        self.plotData()

    def skip(self, val):
        self.skipCallback()

    def exit(self, val):
        self.exitCallback()

    def dump(self, val):
        self.dumpCallback()

    def prev(self, val):
        self.prevCallback()

    def clear(self, val):
        self.minimums = np.array([], dtype=np.int_)
        self.maximums = np.array([], dtype=np.int_)
        self.plotData()

    # holding f key while clicking done overrides validation for better or for worse
    def done(self, event):
        valid, _, error = self.validateMinMax(verbose=event.key != 't')
        if event.key == 't' and not valid:
            print("Forcing output!")
        if not valid and event.key != 't':
            print("Hold t key while pressing " + self.doneButtonTitle + " to force data output (not recommended).")
            return
        # We can't calculate the average height and average duration if it's forced
        if valid or error == 'wrong_peak_count':
            averageHeight, averageDuration, stdDevHeight, stdDevDuration = self.determineAveragePeakHeightWidth()
        else:
            averageHeight = averageDuration = 'N/A'
        minMaxPairs = self.getMaximumMinimumPairs()
        self.doneCallback(self.column, not valid and event.key == 't', minMaxPairs, averageHeight, averageDuration, stdDevHeight, stdDevDuration, plt)

    def title(self):
        return self.color + ", Intensity " + str(self.intensity) + " @ " + str(self.fps) + " fps (" + self.column + ") Expecting " + str(self.requiredPeaks()) + " pairs"

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
        minPeaks = list(self.findMinPeaks())
        maxPeaks = list(self.findMaxPeaks())

        offset = self.minMaxAreOffset(minPeaks, maxPeaks)

        # this code does some fancy tricks to find places where
        # two or more max peaks or two or more min peaks sit between two max/min peaks respectively
        for i in range(0, len(minPeaks) - 1):
            peak1 = minPeaks[i]
            peak2 = minPeaks[i+1]
            midPeaks = [(self.yData[x], i) for i, x in enumerate(maxPeaks) if x > peak1 and x < peak2]
            if len(midPeaks) > 1:
                # find the max value of the mid peaks
                maxValue = max(midPeaks, key=lambda item: item[0])
                midPeaks.remove(maxValue)
                valuesToRemove = list(map(lambda val: maxPeaks[val[1]], midPeaks))
                for val in valuesToRemove:
                    maxPeaks.remove(val)

        for i in range(0, len(maxPeaks) - 1):
            peak1 = maxPeaks[i]
            peak2 = maxPeaks[i+1]
            midPeaks = [(self.yData[x], i) for i, x in enumerate(minPeaks) if x > peak1 and x < peak2]
            if len(midPeaks) > 1:
                # find the max value of the mid peaks
                minValue = min(midPeaks, key=lambda item: item[0])
                midPeaks.remove(minValue)
                valuesToRemove = list(map(lambda val: minPeaks[val[1]], midPeaks))
                for val in valuesToRemove:
                    minPeaks.remove(val)

        # make smarter b_1_75

        self.minimums = np.array(minPeaks)
        self.maximums = np.array(maxPeaks)

    def plotData(self):
        maxima, minima = self.findPeaks()

        validated, idx, error = self.validateMinMax()

        if validated:
            self.doneButton.color = 'green'
            self.doneButton.hovercolor = 'darkgreen'
        elif error == 'wrong_peak_count':
            self.doneButton.color = 'yellow'
            self.doneButton.hovercolor = 'gold'
        else:
            self.doneButton.color = 'red'
            self.doneButton.hovercolor = 'darkred'

        self.ax.clear()
        self.ax.plot(self.xData, self.yData)

        if len(maxima) > 0:
            self.ax.plot(self.xData[maxima], self.yData[maxima], "o", alpha=0.7, color='darkgreen')
        if len(minima) > 0:
            self.ax.plot(self.xData[minima], self.yData[minima], "o", alpha=0.7, color='darkred')

        minimums, maximiums = self.getOrderedMaximumAndMinimum(self.minimums, self.maximums)

        valid, brokenIdx, _ = self.validateMinMax()

        for idx, val in enumerate(minimums):
            error = not valid and brokenIdx == idx
            color = 'red' if error else colorSets[idx % len(colorSets)]
            style = 'italic' if error else 'normal'
            self.ax.annotate(str(idx + 1) + " min", (self.xData[val], self.yData[val]), textcoords='offset pixels', xytext=(15, -15), fontweight='bold', style=style,
                    fontsize=8, color=color, arrowprops={'arrowstyle': '->'})

        for idx, val in enumerate(maximiums):
            error = not valid and brokenIdx == idx
            color = 'red' if error else colorSets[idx % len(colorSets)]
            style = 'italic' if error else 'normal'
            self.ax.annotate(str(idx + 1) + " max", (self.xData[val], self.yData[val]), textcoords='offset pixels',
                             xytext=(15, 15), fontweight='bold', style=style,
                             fontsize=8, color=color, arrowprops={'arrowstyle': '->'})


        self.ax.set_title(self.title(), color=self.titleColor)

        plt.show(block=False)
        plt.draw()
        # self.fig.canvas.flush_events()

    # orders the minimums and maximums taking account for any offsets that may be in place
    def getOrderedMaximumAndMinimum(self, mins, maxs):

        maximums = sorted(maxs)
        minimums = sorted(mins)

        if len(maximums) == 0 or len(minimums) == 0:
            return (minimums, maximums)

        if self.minMaxAreOffset(minimums, maximums):
            minArray = [minimums[-1]]
            minArray.extend(minimums[:-1])
            return (minArray, maximums)
        else:
            return (minimums, maximums)

    def addSpecificMinMax(self, clickX, minOrMax):
        dataMaxX = self.xData[-1]
        dataMinX = self.xData[0]

        if minOrMax == 'min':
            action = self.insertRemoveMin
        else:
            action = self.insertRemoveMax

        if clickX < dataMinX:
            action(0, 'insert')
        elif clickX > dataMaxX:
            action(len(self.xData) - 1, 'insert')
        else:
            for i in range(0, len(self.xData)):
                val = self.xData[i]
                if clickX < val:
                    action(i, 'insert')
                    break

    def addRemoveMinMax(self, clickX, clickY, action):

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
            self.insertRemoveMin(val, action)
        else:
            idx = maxPeakDistances.index(closestMaxPeak)
            val = maxList[idx]
            self.insertRemoveMax(val, action)

    def insertRemoveMax(self, val, action):
        if action == 'remove':
            self.maximums = self.maximums[self.maximums != val]
        elif action == 'insert' and not val in self.maximums:
            self.maximums = np.append(self.maximums, int(val))

    def insertRemoveMin(self, val, action):
        if action == 'remove':
            self.minimums = self.minimums[self.minimums != val]
        elif action == 'insert' and not val in self.minimums:
            self.minimums = np.append(self.minimums, int(val))

    def onclick(self, event):
        # only do something if we are over the graph
        if event.inaxes == None or event.inaxes.name != 'main':
            return

        if event.key == 'w':
            self.addSpecificMinMax(event.xdata, 'max')
        elif event.key == 'x':
            self.addSpecificMinMax(event.xdata, 'min')
        elif event.key == 'a':
            self.addRemoveMinMax(event.xdata, event.ydata, 'insert')
        elif event.key == 'd':
            self.addRemoveMinMax(event.xdata, event.ydata, 'remove')
        else:
            return

        self.plotData()
