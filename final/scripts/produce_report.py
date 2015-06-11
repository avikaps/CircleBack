#! /usr/bin/env python

from __future__ import print_function
import csv, sys

LIST_INGESTION_RESULTS = str(sys.argv[1])

def read_funding_data(path):
    with open(path, 'rU') as data:
        reader = csv.DictReader(data)
        for row in reader:
            yield row

if __name__ == "__main__":
    
    email_count_dict = { 'Added':0, 'Validated':0, 'Unavailable':0, 'Normalized':0, 'blank':0, 'Replaced':0 }
    phone_count_dict = { 'Added':0, 'Validated':0, 'Unavailable':0, 'Normalized':0, 'blank':0, 'Replaced':0 }
    mobile_count_dict = { 'Added':0, 'Validated':0, 'Unavailable':0, 'Normalized':0, 'blank':0, 'Replaced':0 }
    org_count_dict = { 'Added':0, 'Validated':0, 'Unavailable':0, 'Normalized':0, 'blank':0, 'Replaced':0 }
    title_count_dict = { 'Added':0, 'Validated':0, 'Unavailable':0, 'Normalized':0, 'blank':0, 'Replaced':0 }
    updated_count = 0
    filtered_count = 0    

    for idx, row in enumerate(read_funding_data(LIST_INGESTION_RESULTS)):
	
        if row['CB TopCard'] == 'Updated': 
            updated_count = updated_count + 1

            email_status = 'blank' if row['DIFF email'] == '' else row['DIFF email']
            title_status = 'blank' if row['DIFF title'] == '' else row['DIFF title']
            org_status = 'blank' if row['DIFF company'] == '' else row['DIFF company']
            phone_status = 'blank' if row['DIFF work phone'] == '' else row['DIFF work phone']
            mobile_status = 'blank' if row['DIFF mobile phone'] == '' else row['DIFF mobile phone']

            email_count_dict[email_status] = email_count_dict[email_status] + 1
            title_count_dict[title_status] = title_count_dict[title_status] + 1
            org_count_dict[org_status] = org_count_dict[org_status] + 1
            phone_count_dict[phone_status] = phone_count_dict[phone_status] + 1
            mobile_count_dict[mobile_status] = mobile_count_dict[mobile_status] + 1


        elif row['CB TopCard'] == 'Matched': 
            filtered_count = filtered_count + 1

    print("Email\n\tUpdated\t%s\n\tFilled In\t%s\n\tValidated\t%s\n" % (email_count_dict['Replaced'], email_count_dict['Added'], email_count_dict['Validated']))
    print("Phone\n\tUpdated\t%s\n\tFilled In\t%s\n\tValidated\t%s\n" % (phone_count_dict['Replaced'], phone_count_dict['Added'], phone_count_dict['Validated']))
    print("Mobile\n\tUpdated\t%s\n\tFilled In\t%s\n\tValidated\t%s\n" % (mobile_count_dict['Replaced'], mobile_count_dict['Added'], mobile_count_dict['Validated']))
    print("Org:\n\tUpdated\t%s\n\tFilled In\t%s\n\tValidated\t%s\n" % (org_count_dict['Replaced'], org_count_dict['Added'], org_count_dict['Validated']))
    print("Title:\n\tUpdated\t%s\n\tFilled In\t%s\n\tValidated\t%s\n" % (title_count_dict['Replaced'], title_count_dict['Added'], title_count_dict['Validated']))

    print(email_count_dict)
    print(phone_count_dict)
    print(mobile_count_dict)
    print(org_count_dict)
    print(title_count_dict)

    print("Matched %s contacts." % (updated_count + filtered_count))
    print("Updated %s contacts." % updated_count)