import DataPlot
import DataExtractor
import PlotDataWriter
import BackgroundDataWriter
import sys

class BirdData:
    def __init__(self, filename, columns=None, background=False, output=None, startColumn=None):
        self.dataExtractor = DataExtractor.DataExtractor(filename)
        self.plotDataWriter = PlotDataWriter.PlotDataWriter()
        self.ouputFilename = output
        availableColumns = self.dataExtractor.getAvailableColumns(background)

        #Ensure that the column names are valid
        if columns != None:
            errorColumns = []
            for column in columns:
                if not column in availableColumns:
                    errorColumns.append(column)
            if len(errorColumns) != 0:
                print("Fatal Error! these column(s) do not exist for this mode: " + ', '.join(x for x in errorColumns))
                return
            self.columnsToPlot = columns
        elif startColumn != None:
            try:
                idx = availableColumns.index(startColumn)
                self.columnsToPlot = availableColumns[idx:]
            except:
                print("Start column: " + startColumn + " was not found.")
        else:
            self.columnsToPlot = availableColumns

        if not background:
            self.plotNext()
        else:
            backgroundDataWriter = BackgroundDataWriter.BackgroundDataWriter()
            for column in self.columnsToPlot:
                _, yData = self.dataExtractor.extractData(column)
                backgroundDataWriter.writeLine(column, sum(yData)/len(yData))
            backgroundDataWriter.writeToFile(self.ouputFilename)

    def plotNext(self):
        if len(self.columnsToPlot) > 0:
            column = self.columnsToPlot.pop(0)
            xData, yData = self.dataExtractor.extractData(column)
            title = 'Finish' if len(self.columnsToPlot) == 0 else 'Next'
            self.current = DataPlot.DataPlot(column, xData, yData, self.done, self.skip, self.dump, self.exit, doneButtonTitle=title)
        else:
            self.plotDataWriter.writeToFile(self.ouputFilename)
            sys.exit()

    def done(self, column, minMaxPairs, averageHeight, averageDuration):
        self.plotDataWriter.addLine(column, minMaxPairs, averageHeight, averageDuration)
        self.plotNext()

    def skip(self):
        self.plotNext()

    def dump(self):
        self.plotDataWriter.writeToFile(self.ouputFilename)

    def exit(self):
        self.plotDataWriter.writeToFile(self.ouputFilename)
        sys.exit()