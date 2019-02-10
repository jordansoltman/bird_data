import csv
import os
import datetime

class PlotDataWriter:

    def __init__(self):
        self.data = {}

    def addLine(self, column, minMaxPairs, averageHeight, averageDuration):
        self.data[column] = {
            'minMaxPairs': minMaxPairs,
            'averageHeight': averageHeight,
            'averageDuration': averageDuration
        }

    def writeToFile(self, outputFilename):
        # find max number of min/max pairs
        maxPairs = 0
        for column in self.data:
            row = self.data[column]
            if len(row['minMaxPairs']) > maxPairs:
                maxPairs = len(row['minMaxPairs'])

        fieldnames = ['Series', 'Avg. Duration', 'Avg. Height']
        for i in range(0, maxPairs):
            fieldnames.append(str(i + 1) + ' Min X,Y')
            fieldnames.append(str(i + 1) + ' Max X,Y')

        if outputFilename != None:
            output = outputFilename
        else:
            baseDir = os.path.dirname(os.path.realpath(__file__))
            directory = os.path.join(baseDir, 'output')
            if not os.path.exists(directory):
                os.makedirs(directory)
            output = os.path.join(directory, 'plot_' + str(datetime.datetime.now()) + '.csv')

        try:
            with open(output, mode='w') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(fieldnames)

                for column in self.data:
                    data = self.data[column]
                    row = [column, data['averageDuration'], data['averageHeight']]
                    for pair in data['minMaxPairs']:
                        _min, _max = pair
                        minX, minY = _min
                        maxX, maxY = _max
                        row.append(str(minX) + ', ' + str(minY))
                        row.append(str(maxX) + ', ' + str(maxY))
                    writer.writerow(row)

                csv_file.close()
        except:
            print("ERROR: There was an error outputing to ", output)