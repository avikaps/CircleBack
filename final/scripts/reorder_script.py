#!/usr/bin/python

import os
import csv
import time
import sys

#Creating empty list of both the headers
actual_header = []
expected_header = []

#----------------------------------------------------------------------
#Function writes the list of headers
def create_headers(mapping_file):
    """
    This function creates a list of elements to the expected and actual
    headers after reading through the 'mapping.txt' file.
    """
    with open(mapping_file, 'r') as map_file:
        for each_line in map_file:
            expected_header.append(tuple(each_line.strip().split(":"))[0])
            actual_header.append(tuple(each_line.strip().split(":"))[1])
            #print actual_header
            #print expected_header

#----------------------------------------------------------------------
#Reads the CSV file (row-wise)
def csv_row_reader(INPUTFILE_PATH):
    """
    Read a CSV file using csv.Reader and returns a list of all rows in
    the read CSV file. 
    """
    input_data = []
    #print INPUTFILE_PATH
    with open(INPUTFILE_PATH, 'rU') as input_file:
        read_file = csv.reader(input_file)
        for each_row in read_file:
            #print each_row
            input_data.append(each_row)
        return input_data

#----------------------------------------------------------------------
#Writes dictionary to the CSV file   
def csv_dict_writer(path, fieldnames, data):
    """
    Writes a CSV file using DictWriter
    """
    with open(path, "wb") as out_file:
        writer = csv.DictWriter(out_file, delimiter=',', fieldnames=fieldnames)
        writer.writeheader()
        #print type(data)
        for row in data:
            #print row
            writer.writerow(row)
            
#----------------------------------------------------------------------
#Process the CSV information and producing a relevant output.            
def csv_processing(INPUTFILE_PATH, MAPPINGFILE_PATH, OUTPUTFILE_PATH):
    """
    Does all the processing in the Input file and produces the releavnt output
    based on the data written in the mapping file.
    """
    #print INPUTFILE_PATH
    #print MAPPINGFILE_PATH
    #print OUTPUTFILE_PATH
    input_data = csv_row_reader(INPUTFILE_PATH)
    #Create an empty list of the data to be written on output file
    write_data = []
    input_file_header = input_data[0]
    #print input_file_header
    #print actual_header
    ignore_keys = [item for item in input_file_header if item not in actual_header]
    #print ignore_keys
    for each_values in input_data[1:]:
        refined_dict = dict(zip(input_file_header, each_values))
        #print refined_dict
        for item in ignore_keys:
            #print item
            refined_dict.pop(item, None)
        #print refined_dict
        write_data.append(refined_dict)
    #print write_data
    temp_file_name = "Temp_"+ os.path.basename(INPUTFILE_PATH)
    temp_file_path = os.path.join(os.path.dirname(OUTPUTFILE_PATH), temp_file_name)
    csv_dict_writer(temp_file_path, actual_header, write_data)
    newLine = ','.join(expected_header) + '\n'
    outputfile_name = "Reordered_" + os.path.basename(INPUTFILE_PATH)
    outputfile_path = os.path.join(os.path.dirname(OUTPUTFILE_PATH), outputfile_name)
    replace_header(newLine, temp_file_path, outputfile_path)
    os.remove(temp_file_path)
    
#----------------------------------------------------------------------
#Replace the old header with the new header in the final output file.    
def replace_header(newLine, temp_file_path, outputfile_path):
    """
    Changes the header of the freshly written csv.
    """   
    with open(temp_file_path, 'r') as temp_file:
        with open(outputfile_path, 'wb') as write_file:
            temp_file.next()
            write_file.write(newLine)
            #print actual_header
            if actual_header[0] is not '':
                for line in temp_file:
                    write_file.write(line)
            else:
                for line, count in zip(temp_file, range(1,5000000)):
                    modLine = str(count) + line
                    write_file.write(modLine)


#----------------------------------------------------------------------
#Main function        
if __name__ == "__main__":
    start_time = time.time()
    try :
        INPUTFILE_PATH = sys.argv[1]
        MAPPINGFILE_PATH = sys.argv[2]
        OUTPUTFILE_PATH = sys.argv[3]
    except IndexError:
        print "\nUsage of the script is as shown below :"
        print "\n<script_name> <input_file_path> <mapping_file_path> <output_directory>"
        print "\npython reoder_script.py ~/Downloads/tsm-leads-report-test.csv ~/Downloads/mapping_tsm-leads.txt"
    if not os.path.exists(INPUTFILE_PATH):
        print os.path.basename(INPUTFILE_PATH), "- File not found !"
        sys.exit("File not found")
    if not os.path.exists(MAPPINGFILE_PATH):
        print os.path.basename(MAPPINGFILE_PATH), "- File not found !"
        sys.exit("File not found")
    if not os.path.exists(OUTPUTFILE_PATH):
        print os.path.dirname(OUTPUTFILE_PATH), "- Directory not found !"
        sys.exit("Directory not found")
    create_headers(MAPPINGFILE_PATH)
    csv_processing(INPUTFILE_PATH, MAPPINGFILE_PATH, OUTPUTFILE_PATH)
    print("Time spent in complete activity : %s seconds" % (time.time() - start_time))
