#! /usr/bin/env python

import csv, sys

reader = csv.reader( sys.stdin, quoting = csv.QUOTE_MINIMAL )
writer = csv.writer( sys.stdout, quoting = csv.QUOTE_ALL, doublequote = True, lineterminator = '\n')

for line in reader:

    if len(line[3].strip()) == 0 or line[3].lower() == 'null':
        continue

    # if len(line[1].strip()) == 0 and len(line[6].strip()) == 0:
    #     continue

    writer.writerow(line)
