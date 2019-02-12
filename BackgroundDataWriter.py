import datetime
import os
import csv

class BackgroundDataWriter:
    def __init__(self):
        self.data = {}

    def writeLine(self, column, average, variance):
        self.data[column] = {
            'average': average,
            'variance': variance
        }

    def writeToFile(self, directory):
        fieldnames = ['Series', 'Average', 'Variance']
        output = os.path.join(directory, 'background_data.csv')
        try:
            with open(output, mode='w') as csv_file:
                writer = csv.writer(csv_file, lineterminator='\n')
                writer.writerow(fieldnames)

                for row in self.data:
                    writer.writerow([row, self.data[row]['average'], self.data[row]['variance']])

                csv_file.close()
        except Exception as e:
            print("There was an error outputing background data to " + output)
            print(e)