#! /usr/bin/env python

from __future__ import print_function
import csv, sys, xlwt

LIST_INGESTION_RESULTS =  str(sys.argv[1])
FILE_NAME = str(sys.argv[2])
CONTACT_RECORDS = str(sys.argv[3])
USABLE_RECORDS = str(sys.argv[4])
UNIQUE_RECORDS = str(sys.argv[5])
UNIQUE_COMPANIES = str(sys.argv[6])

style0 = xlwt.easyxf('font: name Arial, color-index black, bold on',
                     num_format_str='#,##0.00')
style1 = xlwt.easyxf('font: name Arial, color-index black, bold off',
                     num_format_str='#,##0')
style2 = xlwt.easyxf('font: name Arial, color-index black, bold off',
                     num_format_str='0.00%')
style3 = xlwt.easyxf('pattern: pattern solid, fore_colour pale_blue;'
                              'font: colour white, bold True;')
style4 = xlwt.easyxf('pattern: pattern solid, fore_colour gray40;'
                              'font: colour white, bold True;')


def read_funding_data(path):
    with open(path, 'rU') as data:
        reader = csv.DictReader(data)
        for row in reader:
            yield row


if __name__ == "__main__":
    
    email_count_dict = { 'Added':0, 'Validated':0, 'Invalidated':0, 'Normalized':0, 'blank':0, 'Replaced':0 }
    phone_count_dict = { 'Added':0, 'Validated':0, 'Invalidated':0, 'Normalized':0, 'blank':0, 'Replaced':0 }
    mobile_count_dict = { 'Added':0, 'Validated':0, 'Invalidated':0, 'Normalized':0, 'blank':0, 'Replaced':0 }
    org_count_dict = { 'Added':0, 'Validated':0, 'Invalidated':0, 'Normalized':0, 'blank':0, 'Replaced':0 }
    title_count_dict = { 'Added':0, 'Validated':0, 'Invalidated':0, 'Normalized':0, 'blank':0, 'Replaced':0 }
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
    #
    matched_count = updated_count + filtered_count
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Standard_Waterfall_Report')
    ws.write(0, 0, ' ', style3) 
    ws.write(0, 1, ' ', style3)
    ws.write(0, 2, ' ', style3)
    #ws.set_column('A:A', 36)
    ws.row(0).height = 0x4ba
    ws.col(0).width = 0x147f
    ws.row(0).height_mismatch = True
    ws.col(3).width = 0x40f
    ws.col(4).width = 0x40f
    ws.insert_bitmap('./CB_logo.bmp', 0, 0, 0, 0, 0.878, 0.222)
    #ws.insert_image('A1', '/media/avi/Data/Projects/Common Scripts/CB_logo.png')
    ws.write(1, 0, 'Detailed Analysis Report', style0)
    ws.write(1, 2, 'Contacts', style0)
    ws.write(2, 0, ' ', style3)
    ws.write(2, 1, ' ', style3)
    ws.write(2, 2, ' ', style3)
    ws.write(3, 0, 'Contact Records', style0)
    ws.write(3, 2, CONTACT_RECORDS, style1)
    ws.write(4, 0, ' ', style4)
    ws.write(4, 1, ' ', style4)
    ws.write(4, 2, ' ', style4)
    ws.write(5, 0, 'Unusable Records', style0)
    ws.write(5, 2, xlwt.Formula("C4-C7"), style1)
    ws.write(6, 0, 'Usable Records', style0)
    ws.write(6, 2, USABLE_RECORDS, style1)
    ws.write(7, 0, ' ', style4)
    ws.write(7, 1, ' ', style4)
    ws.write(7, 2, ' ', style4)
    ws.write(8, 0, 'Duplicates (Email)', style0)
    ws.write(8, 2, xlwt.Formula("C7-C10"), style1)
    ws.write(9, 0, 'Unique Records', style0)
    ws.write(9, 2, UNIQUE_RECORDS, style1)
    ws.write(10, 0, ' ', style4)
    ws.write(10, 1, ' ', style4)
    ws.write(10, 2, ' ', style4)
    ws.write(11, 0, 'Unique Companies', style0)
    ws.write(11, 2, UNIQUE_COMPANIES, style1)
    ws.write(12, 0, ' ', style4)
    ws.write(12, 1, ' ', style4)
    ws.write(12, 2, ' ', style4)
    
    ws.write(13, 0, 'Number of Contacts Matched', style0)
    ws.write(13, 2, matched_count, style1)

    ws.write(14, 0, 'Match %', style0)
    ws.write(14, 2, xlwt.Formula("(C14/C10)"), style2)

    ws.write(15, 0, 'Number of Contacts Updated', style0)
    ws.write(15, 2, updated_count, style1)

    ws.write(16, 0, 'Updated %', style0)
    ws.write(16, 2, xlwt.Formula("(C16/C10)"), style2)
    #
    ws.write(17, 0, ' ', style3)
    ws.write(17, 1, ' ', style3)
    ws.write(17, 2, ' ', style3)   
    #
    ws.write(18, 0, 'Email :', style0)

    ws.write(19, 1, 'Updated', style1)
    ws.write(19, 2, email_count_dict['Replaced'], style1)

    ws.write(20, 1, 'Filled In', style1)
    ws.write(20, 2, email_count_dict['Added'], style1)

    ws.write(21, 1, 'Validated', style1)
    ws.write(21, 2, (email_count_dict ['Validated'] + email_count_dict ['Normalized']), style1)
    #
    ws.write(22, 0, 'Phone :', style0)

    ws.write(23, 1, 'Updated', style1)
    ws.write(23, 2, phone_count_dict['Replaced'], style1)

    ws.write(24, 1, 'Filled In', style1)
    ws.write(24, 2, phone_count_dict['Added'], style1)

    ws.write(25, 1, 'Validated', style1)
    ws.write(25, 2, (phone_count_dict ['Validated'] + phone_count_dict ['Normalized']), style1)
    #
    ws.write(26, 0, 'Mobile :', style0)
    ws.write(27, 1, 'Updated', style1)
    ws.write(27, 2, mobile_count_dict['Replaced'], style1)
    ws.write(28, 1, 'Filled In', style1)
    ws.write(28, 2, mobile_count_dict['Added'], style1)
    ws.write(29, 1, 'Validated', style1)
    ws.write(29, 2, (mobile_count_dict['Validated'] + mobile_count_dict ['Normalized']), style1)
    #
    ws.write(30, 0, 'Organization :', style0)
    ws.write(31, 1, 'Updated', style1)
    ws.write(31, 2, org_count_dict['Replaced'], style1)
    ws.write(32, 1, 'Filled In', style1)
    ws.write(32, 2, org_count_dict['Added'], style1)
    ws.write(33, 1, 'Validated', style1)
    ws.write(33, 2, (org_count_dict['Validated'] + org_count_dict ['Normalized']), style1)
    #
    ws.write(34, 0, 'Title :', style0)
    ws.write(35, 1, 'Updated', style1)
    ws.write(35, 2, title_count_dict['Replaced'], style1)
    ws.write(36, 1, 'Filled In', style1)
    ws.write(36, 2, title_count_dict['Added'], style1)
    ws.write(37, 1, 'Validated', style1)
    ws.write(37, 2, (title_count_dict['Validated'] + title_count_dict ['Normalized']), style1)
    #
    ws.write(38, 0, ' ', style3)
    ws.write(38, 1, ' ', style3)
    ws.write(38, 2, ' ', style3)
    #
    ws.write(39, 0, ' ', style3)
    ws.write(39, 1, ' ', style3)
    ws.write(39, 2, ' ', style3)
    #
    ws.write(0, 3, ' ', style3)
    ws.write(0, 4, ' ', style3)
    ws.write(1, 3, ' ', style3)
    ws.write(1, 4, ' ', style3)
    ws.write(2, 3, ' ', style3)
    ws.write(2, 4, ' ', style3)
    ws.write(3, 3, ' ', style3)
    ws.write(3, 4, ' ', style3)
    ws.write(4, 3, ' ', style3)
    ws.write(4, 4, ' ', style3)
    ws.write(5, 3, ' ', style3)
    ws.write(5, 4, ' ', style3)
    ws.write(6, 3, ' ', style3)
    ws.write(6, 4, ' ', style3)
    ws.write(7, 3, ' ', style3)
    ws.write(7, 4, ' ', style3)
    ws.write(8, 3, ' ', style3)
    ws.write(8, 4, ' ', style3)
    ws.write(9, 3, ' ', style3)
    ws.write(9, 4, ' ', style3)
    ws.write(10, 3, ' ', style3)
    ws.write(10, 4, ' ', style3)
    ws.write(11, 3, ' ', style3)
    ws.write(11, 4, ' ', style3)
    ws.write(12, 3, ' ', style3)
    ws.write(12, 4, ' ', style3)
    ws.write(13, 3, ' ', style3)
    ws.write(13, 4, ' ', style3)
    ws.write(14, 3, ' ', style3)
    ws.write(14, 4, ' ', style3)
    ws.write(15, 3, ' ', style3)
    ws.write(15, 4, ' ', style3)
    ws.write(16, 3, ' ', style3)
    ws.write(16, 4, ' ', style3)
    ws.write(17, 3, ' ', style3)
    ws.write(17, 4, ' ', style3)
    ws.write(18, 3, ' ', style3)
    ws.write(18, 4, ' ', style3)
    ws.write(19, 3, ' ', style3)
    ws.write(19, 4, ' ', style3)
    ws.write(20, 3, ' ', style3)
    ws.write(20, 4, ' ', style3)
    ws.write(21, 3, ' ', style3)
    ws.write(21, 4, ' ', style3)
    ws.write(22, 3, ' ', style3)
    ws.write(22, 4, ' ', style3)
    ws.write(23, 3, ' ', style3)
    ws.write(23, 4, ' ', style3)
    ws.write(24, 3, ' ', style3)
    ws.write(24, 4, ' ', style3)
    ws.write(25, 3, ' ', style3)
    ws.write(25, 4, ' ', style3)
    ws.write(26, 3, ' ', style3)
    ws.write(26, 4, ' ', style3)
    ws.write(27, 3, ' ', style3)
    ws.write(27, 4, ' ', style3)
    ws.write(28, 3, ' ', style3)
    ws.write(28, 4, ' ', style3)
    ws.write(29, 3, ' ', style3)
    ws.write(29, 4, ' ', style3)
    ws.write(30, 3, ' ', style3)
    ws.write(30, 4, ' ', style3)
    ws.write(31, 3, ' ', style3)
    ws.write(31, 4, ' ', style3)
    ws.write(32, 3, ' ', style3)
    ws.write(32, 4, ' ', style3)
    ws.write(33, 3, ' ', style3)
    ws.write(33, 4, ' ', style3)
    ws.write(34, 3, ' ', style3)
    ws.write(34, 4, ' ', style3)
    ws.write(35, 3, ' ', style3)
    ws.write(35, 4, ' ', style3)
    ws.write(36, 3, ' ', style3)
    ws.write(36, 4, ' ', style3)
    ws.write(37, 3, ' ', style3)
    ws.write(37, 4, ' ', style3)
    ws.write(38, 3, ' ', style3)
    ws.write(38, 4, ' ', style3)
    ws.write(39, 3, ' ', style3)
    ws.write(39, 4, ' ', style3)
    #
    wb.save(FILE_NAME)
