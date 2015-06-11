#! /usr/bin/env python
import os, sys

input_file = sys.argv[1]
input_codec = sys.argv[2]
output_file = sys.argv[3]

with open(input_file, 'r') as f, open(output_file, 'w') as f_out:

    for line in f:

    	unicode_line = line.decode(input_codec)

    	utf8_line = unicode_line.encode("utf-8")

    	f_out.write(utf8_line)

