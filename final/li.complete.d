FD=ddc_474
ORIG=ddc_474_bb_list_ingestion.csv
COMPLETE_FILE=complete.chk
INPUT_ENCODING=ISO-8859-1
MAPPING_FILE=ddc_474_bb_mapping.txt
PART_SIZE=100000
PARALLEL_DEGREE=16
LIST_ID=0
USERNAME="@circleback.com"
PASSWORD=""

; Convert to UTF-8
steps/01.convert_to_utf/$[COMPLETE_FILE] <- input/$[ORIG] [shell]
  mkdir -p steps/01.convert_to_utf && rm -rf tmp.cmds && rm -rf steps/01.convert_to_utf/$[FD]* steps/01.convert_to_utf/$[COMPLETE_FILE]
  scripts/utf_converter.py $[INPUT] $[INPUT_ENCODING] steps/01.convert_to_utf/$[FD]_utf.csv && touch steps/01.convert_to_utf/$[COMPLETE_FILE]

; Clean newline character from fields
steps/02.remove_new_lines/$[COMPLETE_FILE] <- steps/01.convert_to_utf/$[COMPLETE_FILE] [shell]
  mkdir -p steps/02.remove_new_lines && rm -rf tmp.cmds && rm -rf steps/02.remove_new_lines/$[FD]* steps/02.remove_new_lines/$[COMPLETE_FILE]
  cat steps/01.convert_to_utf/$[FD]_utf.csv | scripts/clean_newlines.py > steps/02.remove_new_lines/$[FD]_rmnew.csv && contact_records=$(cat steps/02.remove_new_lines/$[FD]_rmnew.csv | wc -l) 
  echo " *NOTE* - - - Total number of Contact Records are : $contact_records" && touch steps/02.remove_new_lines/$[COMPLETE_FILE]

; Re-order csv wrt DAAS format
steps/03.reorder/$[COMPLETE_FILE] <- steps/02.remove_new_lines/$[COMPLETE_FILE] [shell]
  mkdir -p steps/03.reorder && rm -rf tmp.cmds && rm -rf steps/03.reorder/$[FD]* steps/03.reorder/$[COMPLETE_FILE]
  scripts/reorder_script.py steps/02.remove_new_lines/$[FD]_rmnew.csv mapping/$[MAPPING_FILE] steps/03.reorder/ && touch steps/03.reorder/$[COMPLETE_FILE] 

; Additional Step - Check file format of the output file 
steps/04.fileformat/$[COMPLETE_FILE] <- steps/03.reorder/$[COMPLETE_FILE] [shell]
  mkdir -p steps/04.fileformat && rm -rf tmp.cmds && rm -rf steps/04.fileformat/$[FD]* steps/04.fileformat/$[COMPLETE_FILE]
  awk '{ sub("\r$", ""); print }' steps/03.reorder/Reordered_$[FD]_rmnew.csv > steps/04.fileformat/Reordered_$[FD]_unix.csv && touch steps/04.fileformat/$[COMPLETE_FILE]

; Normalize first pass
steps/06.normalized/$[COMPLETE_FILE] <- steps/04.fileformat/$[COMPLETE_FILE] [shell]
  export CA_DATA=/mnt/data2/siq-data/experian/data/Data/
  export CA_DATA_CANADA=/mnt/data2/siq-data/experian/data/DataCanada/
  mkdir -p steps/06.normalized && rm -rf tmp.cmds && rm -rf steps/06.normalized/$[FD]* steps/06.normalized/$[COMPLETE_FILE]
  cat steps/04.fileformat/Reordered_$[FD]_unix.csv | normalize_address | normalize_names 'First Name' 'Last Name' | normalize_csv maps/csv_header.map | csvfix rmnew > steps/06.normalized/$[FD]_normalized.csv 
  cat steps/06.normalized/$[FD]_normalized.csv | csvfix order -f 1:13 > output/$[FD]_normalized_input.csv && touch steps/06.normalized/$[COMPLETE_FILE]

; Remove null_ characters from the file
steps/07.usable_input/$[COMPLETE_FILE] <- steps/06.normalized/$[COMPLETE_FILE] [shell]
  mkdir -p steps/07.usable_input/ && rm -rf tmp.cmds && rm -rf steps/07.usable_input/$[FD]* steps/07.usable_input/$[COMPLETE_FILE]
  cat output/$[FD]_normalized_input.csv | scripts/clean_file.py > steps/07.usable_input/$[FD]_usable_input.csv
  usable_records=$(cat steps/07.usable_input/$[FD]_usable_input.csv | wc -l)
  echo " *NOTE* - - - Total number of Usable records are : $usable_records" && touch steps/07.usable_input/$[COMPLETE_FILE]

; Clean newline character from fields
steps/08.remove_duplicate_emails/$[COMPLETE_FILE] <- steps/07.usable_input/$[COMPLETE_FILE] [shell]
  mkdir -p steps/08.remove_duplicate_emails && rm -rf tmp.cmds && rm -rf steps/08.remove_duplicate_emails/$[FD]* steps/08.remove_duplicate_emails/$[COMPLETE_FILE]
  cat steps/07.usable_input/$[FD]_usable_input.csv | csvfix remove -f 2 -e '^$' | csvfix unique -f 2 > output/$[FD]_daas_input.csv
  cat steps/07.usable_input/$[FD]_usable_input.csv | csvfix find -f 2 -e '^$' >> output/$[FD]_daas_input.csv
  unique_records=$(cat output/$[FD]_daas_input.csv | wc -l)
  echo " *NOTE* - - - Total number of Unique records are : $unique_records" && touch steps/08.remove_duplicate_emails/$[COMPLETE_FILE]

; DAAS Data processing
steps/09.upload_to_daas/$[COMPLETE_FILE] <- steps/08.remove_duplicate_emails/$[COMPLETE_FILE] [shell]
  mkdir -p steps/09.upload_to_daas && rm -rf tmp.cmds && rm -rf steps/09.upload_to_daas/$[FD]* steps/09.upload_to_daas/$[COMPLETE_FILE]
  curl --basic -u $USERNAME:$PASSWORD -F "name=$[FD]" -F "description=$[FD] List Ingestion" -F "file=@output/$[FD]_daas_input.csv" https://daas.circleback.com/api/contactlist/upload
  while [[ $LIST_ID -le 0 ]];
  do
     sleep 50
     curl --basic -u $USERNAME:$PASSWORD https://daas.circleback.com/api/contactlist/ > steps/contact_list.txt
     LIST_ID=$(awk -v k="text" '{n=split($0,a,"{"); for (i=1; i<=n; i++) print a[i]}' steps/contact_list.txt | tail -1 | awk -F, '{if ($4 == "\"status\"\:\"Ready\"" && $5 == "\"name\"\:\"$[FD]\"") print $1}' | awk -F\: '{print $2}')
     sleep 10
     printf "\nWaiting until uploaded file get analysed . . .\n\n"
  done
  relink=$(curl --basic -u $USERNAME:$PASSWORD https://daas.circleback.com/api/contactlist/462/download | awk -F\" '{print $4}') 
  sleep 2
  wget $relink -O output/$[FD]_daas_output.csv 
  touch steps/09.upload_to_daas/$[COMPLETE_FILE]

; Produce a fixed output result
steps/10.fix_status/$[COMPLETE_FILE] <- steps/09.upload_to_daas/$[COMPLETE_FILE] [shell]
  mkdir -p steps/10.fix_status && rm -rf tmp.cmds && rm -rf steps/10.fix_status/$[FD]* steps/10.fix_status/$[COMPLETE_FILE]
  cat output/$[FD]_daas_output.csv | scripts/fix_status.py > steps/10.fix_status/$[FD]_fixed_output_file.csv && touch steps/10.fix_status/$[COMPLETE_FILE]

; Clean fixed output file and replace some lable
steps/11.clean_fixed_output/$[COMPLETE_FILE] <- steps/10.fix_status/$[COMPLETE_FILE]  [shell]
  mkdir -p steps/11.clean_fixed_output && rm -rf tmp.cmds && rm -rf steps/11.clean_fixed_output/$[FD]* steps/11.clean_fixed_output/$[COMPLETE_FILE]
  cat steps/10.fix_status/$[FD]_fixed_output_file.csv | sed 's/Invalidated/Unavailable/g' | sed 's/Not Covered//g' | sed 's/Filtered/Matched/g' | csvfix order -f 1:3,5:7,9:18,20:22,23:26,28:30,32:42 > steps/11.clean_fixed_output/$[FD]_analysis.csv && touch steps/11.clean_fixed_output/$[COMPLETE_FILE]

; Store results
steps/12.store_results/$[COMPLETE_FILE] <- steps/11.clean_fixed_output/$[COMPLETE_FILE] [shell]
  mkdir -p steps/12.store_results && rm -rf tmp.cmds && rm -rf steps/12.store_results/$[FD]* steps/12.store_results/$[COMPLETE_FILE]
  scripts/produce_report.py steps/11.clean_fixed_output/$[FD]_analysis.csv > output/$[FD]_Waterfall_Results.csv && touch steps/12.store_results/$[COMPLETE_FILE]
