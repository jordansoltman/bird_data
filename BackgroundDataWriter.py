import datetime
import os
import csv

class BackgroundDataWriter:
    def __init__(self):
        self.data = {}

    def writeLine(self, column, average):
        self.data[column] = average

    def writeToFile(self, outputFilename):
        fieldnames = ['Series', 'Average']

        if outputFilename != None:
            output = outputFilename
        else:
            baseDir = os.path.dirname(os.path.realpath(__file__))
            directory = os.path.join(baseDir, 'output')
            if not os.path.exists(directory):
                os.makedirs(directory)
            output = os.path.join(directory, 'background_'+str(datetime.datetime.now())+'.csv')
        try:
            with open(output, mode='w') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(fieldnames)

                for row in self.data:
                    writer.writerow([row, self.data[row]])

                csv_file.close()
        except:
            print("There was an error outputing to " + output)