#! /usr/bin/env python

import csv, sys

reader = csv.reader( sys.stdin, quoting = csv.QUOTE_MINIMAL )
writer = csv.writer( sys.stdout, quoting = csv.QUOTE_MINIMAL, doublequote = True, lineterminator = '\n')

for line in reader:
	
	output_line = []
	
	for field in line:

		output_line.append( field.replace('\n',' ') )

	writer.writerow(output_line)
