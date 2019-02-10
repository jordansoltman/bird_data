import csv
import numpy as np

class DataExtractor:
    def __init__(self, filename):
        self.timeField, self.availableColumnNames, self.data = self.openFile(filename)

    def extractData(self, yFieldname):
        xData = []
        yData = []
        for row in self.data:
            xData.append(float(row[self.timeField]))
            yData.append(float(row[yFieldname]))
        return (np.array(xData), np.array(yData))

    def getAvailableColumns(self, background=False):
        if background:
            return list(filter(lambda val: val.endswith('B'), self.availableColumnNames))
        else:
            return list(filter(lambda val: not val.endswith('B'), self.availableColumnNames))

    def openFile(self, filename):
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
            print("ERROR: There was an error opening ", filename)