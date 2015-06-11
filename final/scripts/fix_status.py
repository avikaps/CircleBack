#! /usr/bin/env python

from __future__ import print_function
import csv, sys

# Column indexes 0-indexed
COMPANY_IDX = 19
COMPANY_CB_IDX = 20
DIFF_COMPANY = 21

TITLE_IDX = 15
TITLE_CB_IDX = 16
DIFF_TITLE = 17

if __name__ == "__main__":

    reader = csv.reader( sys.stdin, quoting = csv.QUOTE_MINIMAL )   
    writer = csv.writer( sys.stdout, quoting = csv.QUOTE_MINIMAL, doublequote = True, lineterminator = '\n')

    # header = reader.next()
    # writer.writerow(header)

    for row in reader:

        if row[DIFF_COMPANY] == "Updated" or row[DIFF_COMPANY] == "Replaced":
            normalized_company_str = row[COMPANY_IDX].lower().replace("the", "").replace("+", "").replace("&", "").replace(",", "").replace(".", "").replace(" ","").strip()
            normalized_cb_company_str = row[COMPANY_CB_IDX].lower().replace("the", "").replace("+", "").replace("&", "").replace(",", "").replace(".", "").replace(" ","").strip()
            # print("AFTER NORMALIZATION:  Source org: %s -- Updated Org: %s" % (normalized_company_str, normalized_cb_company_str))
            if normalized_company_str[:3] == normalized_cb_company_str[:3]:
                row[DIFF_COMPANY] = "Validated"

        if row[DIFF_TITLE] == "Updated" or row[DIFF_TITLE] == "Replaced":
            normalized_title_str = row[TITLE_IDX].lower().replace("the", "").replace("+", "").replace("&", "").replace(",", "").replace(".", "").replace(" ","").strip()
            normalized_cb_title_str = row[TITLE_CB_IDX].lower().replace("the", "").replace("+", "").replace("&", "").replace(",", "").replace(".", "").replace(" ","").strip()
            # print("AFTER NORMALIZATION:  Source org: %s -- Updated Org: %s" % (normalized_company_str, normalized_cb_company_str))
            if normalized_title_str[:3] == normalized_cb_title_str[:3]:
                row[DIFF_TITLE] = "Validated"
        
        writer.writerow(row)
