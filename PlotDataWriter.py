import csv
import os
import datetime

class PlotDataWriter:

    def __init__(self):
        self.data = {}

    def addLine(self, column, forced, minMaxPairs, averageHeight, averageDuration, stdDevHeight, stdDevDuration):
        self.data[column] = {
            'forced': forced,
            'minMaxPairs': minMaxPairs,
            'averageHeight': averageHeight,
            'averageDuration': averageDuration,
            'stdDevHeight': stdDevHeight,
            'stdDevDuration': stdDevDuration
        }

    # returns the data status of the column
    # (Saved, Forced)
    def getColumnStatus(self, column):
        if column in self.data:
            return (True, self.data[column]['forced'])
        else:
            return (False, False)

    def writeToFile(self, outputDirectory):
        # find max number of min/max pairs
        maxPairs = 0
        for column in self.data:
            row = self.data[column]
            if len(row['minMaxPairs']) > maxPairs:
                maxPairs = len(row['minMaxPairs'])

        fieldnames = ['Series', 'Forced', 'Avg. Duration', 'Avg. Height', 'Std Dev. Duration', 'Std Dev. Height']
        for i in range(0, maxPairs):
            fieldnames.append(str(i + 1) + ' Min X,Y')
            fieldnames.append(str(i + 1) + ' Max X,Y')

        output = os.path.join(outputDirectory, 'plot_data.csv')

        try:
            with open(output, mode='w') as csv_file:
                writer = csv.writer(csv_file, lineterminator='\n')
                writer.writerow(fieldnames)

                for column in self.data:
                    data = self.data[column]
                    row = [column, str(data['forced']).lower(), data['averageDuration'], data['averageHeight'], data['stdDevDuration'], data['stdDevHeight']]
                    for pair in data['minMaxPairs']:
                        _min, _max = pair
                        minX, minY = _min
                        maxX, maxY = _max
                        row.append(str(minX) + ', ' + str(minY))
                        row.append(str(maxX) + ', ' + str(maxY))
                    writer.writerow(row)

                csv_file.close()
        except Exception as e:
            print("ERROR: There was an error outputing to ", output)
            print(e)