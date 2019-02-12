import DataPlot
import DataExtractor
import PlotDataWriter
import BackgroundDataWriter
import sys, os, time
from pathlib import Path
import numpy as np

class BirdData:
    def __init__(self, filename, columns=None, backgroundOnly=False, outputDirectory=None, startColumn=None, saveImages=True):
        self.dataExtractor = DataExtractor.DataExtractor(filename)
        self.plotDataWriter = PlotDataWriter.PlotDataWriter()
        self.saveImages = saveImages
        self.dataPlot = DataPlot.DataPlot(self.done, self.skip, self.dump, self.exit, self.prev)
        availablePlotColumns = self.dataExtractor.getAvailableColumns('plot')


        try:
            if outputDirectory == None:
                self.outputDirectory = os.path.join(os.getcwd(), str(Path(filename).with_suffix('')) + '_results_'  + str(int(time.time())))
            else:
                self.outputDirectory = outputDirectory

            # don't allow overwriting of directories
            if os.path.exists(self.outputDirectory):
                print("ERROR: Output directory already exists. Choose another directory or remove the exisiting output directory before continuing.")
                sys.exit()

            # attempt to make the output directory if it doesn't exist
            if not os.path.exists(self.outputDirectory):
                os.makedirs(self.outputDirectory)
            # attempt to add the image directory if it's required
            if saveImages and not backgroundOnly:
                self.imageDirectory = os.path.join(outputDirectory, 'plots')
                if not os.path.exists(self.imageDirectory):
                    os.makedirs(self.imageDirectory)

            print("Files will be output to: " + self.outputDirectory)
        except Exception as e:
            print("There was a problem creating the output directories.")
            print(e)
            sys.exit()

        availableBackgroundcolumns = self.dataExtractor.getAvailableColumns('background')

        backgroundDataWriter = BackgroundDataWriter.BackgroundDataWriter()
        for column in availableBackgroundcolumns:
            _, yData = self.dataExtractor.extractData(column)
            backgroundDataWriter.writeLine(column, sum(yData) / len(yData), np.var(yData))
        backgroundDataWriter.writeToFile(self.outputDirectory)
        print("Background data processing completed.")

        if backgroundOnly:
            sys.exit()

        #Ensure that the column names are valid
        if columns != None:
            errorColumns = []
            for column in columns:
                if not column in availablePlotColumns:
                    errorColumns.append(column)
            if len(errorColumns) != 0:
                print("Fatal Error! these column(s) do not exist for this mode: " + ', '.join(x for x in errorColumns))
                sys.exit()
            self.columnsToPlot = columns
        elif startColumn != None:
            try:
                idx = availablePlotColumns.index(startColumn)
                self.columnsToPlot = availablePlotColumns[idx:]
            except:
                print("Start column: " + startColumn + " was not found.")
        else:
            self.columnsToPlot = availablePlotColumns

        if len(self.columnsToPlot) == 0:
            print("No columns to plot. Exiting.")
            sys.exit()

        self.currentPlotIndex = 0

        self.printGuide()

        self.plotNext()

    def printGuide(self):
        print("Usage Guide:")
        print("While clicking on the plot, use the following keys:")
        print("a - add point at nearest minima/maxima")
        print("d - remove point nearest to cursor")
        print("w - add maxima point at current cursor x position")
        print("x - add minima point at current cursor x position")
        print()
        print("To force output of a row, hold 't' while clicking on 'Next'")


    def plotNext(self):
        if self.currentPlotIndex < len(self.columnsToPlot):
            column = self.columnsToPlot[self.currentPlotIndex]
            xData, yData = self.dataExtractor.extractData(column)
            title = 'Finish' if len(self.columnsToPlot) - 1 == self.currentPlotIndex else 'Next'
            saved, forced = self.plotDataWriter.getColumnStatus(column)
            self.dataPlot.initializePlot(column, xData, yData, saved, forced, doneButtonTitle=title)
        else:
            self.plotDataWriter.writeToFile(self.outputDirectory)
            sys.exit()

    def done(self, column, forced, minMaxPairs, averageHeight, averageDuration, plt):
        try:
            if self.saveImages:
                plt.savefig(os.path.join(self.imageDirectory, column+'.png'))
        except Exception as e:
            print("Could not save " + column + " plot!")
            print(e)
        self.plotDataWriter.addLine(column, forced, minMaxPairs, averageHeight, averageDuration)
        self.currentPlotIndex += 1
        self.plotNext()

    def skip(self):
        self.currentPlotIndex += 1
        self.plotNext()

    def prev(self):
        if self.currentPlotIndex > 0:
            self.currentPlotIndex -= 1
            self.plotNext()

    def dump(self):
        self.plotDataWriter.writeToFile(self.outputDirectory)

    def exit(self):
        self.plotDataWriter.writeToFile(self.outputDirectory)
        sys.exit()
