import argparse
import BirdData

parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument("source", type=str, help="Source file to get data from.")
parser.add_argument("-o", "--output", type=str, help="Directory to output to. Defaults to source input file name in the current directory.")
parser.add_argument('-b', help="Process background columns only.", action='store_true')
parser.add_argument("-c", '--columns', nargs='+', default=None, help="Supply specific columns instead of iterating through all available columns.")
parser.add_argument('-s', "--start", type=str, default=None, help="Column to start at.")
parser.add_argument('-n', action='store_true', default=False, help="Don't save graph image output.")
args = vars(parser.parse_args())

BirdData.BirdData(args['source'], columns=args['columns'], outputDirectory=args['output'], backgroundOnly=args['b'], startColumn = args['start'], saveImages = not args['n'])