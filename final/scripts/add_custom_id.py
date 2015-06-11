#! /usr/bin/env python

import csv, sys

reader = csv.reader( sys.stdin, quoting = csv.QUOTE_MINIMAL )
writer = csv.writer( sys.stdout, quoting = csv.QUOTE_MINIMAL, doublequote = True, lineterminator = '\n')

header = reader.next()
writer.writerow(header)

custom_id = 1
for line in reader:

	line[0] = custom_id
	line[1] = line[1].lower()
	custom_id = custom_id + 1
	writer.writerow(line)
	
