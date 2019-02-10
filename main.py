import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import argparse
import BirdData

parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument("source", type=str, help="Source file to get data from.")
parser.add_argument("-o", "--output", type=str, help="Output file.")
parser.add_argument('-b', help="Process background columns.", action='store_true')
parser.add_argument("-c", '--columns', nargs='+', default=None, help="Supply specific columns instead of iterating through all available columns.")
parser.add_argument('-s', "--start", type=str, default=None, help="Column to start at.")
args = vars(parser.parse_args())

BirdData.BirdData(args['source'], columns=args['columns'], output=args['output'], background=args['b'], startColumn = args['start'])