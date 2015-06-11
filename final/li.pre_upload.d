FD=ddc_498
ORIG=ddc_498_list_ingestion.csv
COMPLETE_FILE=complete.chk
INPUT_ENCODING=ISO-8859-1
MAPPING_FILE=mapping_ddc_498.txt
PART_SIZE=100000
PARALLEL_DEGREE=16
LIST_ID=0

; Convert to UTF-8
steps/01.convert_to_utf8/$[COMPLETE_FILE] <- input/$[ORIG] [shell]
  mkdir -p steps/01.convert_to_utf8 && rm -rf tmp.cmds && rm -rf steps/01.convert_to_utf8/$[FD]* steps/01.convert_to_utf8/$[COMPLETE_FILE]
  scripts/utf_converter.py $[INPUT] $[INPUT_ENCODING] steps/01.convert_to_utf8/$[FD]_utf8.csv && touch steps/01.convert_to_utf8/$[COMPLETE_FILE]

; Clean newline character from fields
steps/02.filter_level_01/$[COMPLETE_FILE] <- steps/01.convert_to_utf8/$[COMPLETE_FILE] [shell]
  mkdir -p steps/02.filter_level_01 && rm -rf tmp.cmds && rm -rf steps/02.filter_level_01/$[FD]* steps/02.filter_level_01/$[COMPLETE_FILE]
  cat steps/01.convert_to_utf8/$[FD]_utf8.csv | scripts/clean_newlines.py > steps/02.filter_level_01/$[FD]_filter_level1.csv && contact_records=$(cat steps/02.filter_level_01/$[FD]_filter_level1.csv | wc -l) 
  echo "Total number of records are $contact_records" && touch steps/02.filter_level_01/$[COMPLETE_FILE]

; Re-order csv wrt DAAS format
steps/03.reorder/$[COMPLETE_FILE] <- steps/02.filter_level_01/$[COMPLETE_FILE] [shell]
  mkdir -p steps/03.reorder && rm -rf tmp.cmds && rm -rf steps/03.reorder/$[FD]* steps/03.reorder/$[COMPLETE_FILE]
  scripts/reorder_script.py steps/02.filter_level_01/$[FD]_filter_level1.csv mapping/$[MAPPING_FILE] steps/03.reorder/ && touch steps/03.reorder/$[COMPLETE_FILE] 

; Additional Step - Check file format of the output file 
steps/04.fileformat/$[COMPLETE_FILE] <- steps/03.reorder/$[COMPLETE_FILE] [shell]
  mkdir -p steps/04.fileformat && rm -rf tmp.cmds && rm -rf steps/04.fileformat/$[FD]* steps/04.fileformat/$[COMPLETE_FILE]
  awk '{ sub("\r$", ""); print }' steps/03.reorder/Reordered_$[FD]_filter_level1.csv > steps/04.fileformat/Reordered_$[FD]_unix.csv && touch steps/04.fileformat/$[COMPLETE_FILE]

; Normalize first pass
steps/06.normalized/$[COMPLETE_FILE] <- steps/04.fileformat/$[COMPLETE_FILE] [shell]
  export CA_DATA=/mnt/data2/siq-data/experian/data/Data/
  export CA_DATA_CANADA=/mnt/data2/siq-data/experian/data/DataCanada/
  mkdir -p steps/06.normalized && rm -rf tmp.cmds && rm -rf steps/06.normalized/$[FD]* steps/06.normalized/$[COMPLETE_FILE]
  cat steps/04.fileformat/Reordered_$[FD]_unix.csv | normalize_address | normalize_names 'First Name' 'Last Name' | normalize_csv maps/csv_header.map | csvfix rmnew > steps/06.normalized/$[FD]_normalized.csv && touch steps/06.normalized/$[COMPLETE_FILE]

output/$[COMPLETE_FILE] <- steps/06.normalized/$[COMPLETE_FILE] [shell]
  cat steps/06.normalized/$[FD]_normalized.csv | csvfix order -f 1:13 > output/$[FD]_normalized_input.csv

; Remove null_ characters from the file
steps/07.remove_null_char/$[COMPLETE_FILE] <- steps/06.normalized/$[COMPLETE_FILE] [shell]
  mkdir -p steps/07.remove_null_char/ && rm -rf tmp.cmds && rm -rf steps/07.remove_null_char/$[FD]* steps/07.remove_null_char/$[COMPLETE_FILE]
  cat output/$[FD]_normalized_input.csv | scripts/clean_file.py > steps/07.remove_null_char/$[FD]_removed_null.csv
  usable_records=$(cat steps/07.remove_null_char/$[FD]_removed_null.csv | wc -l) && echo "Total number of Usable records are $usable_records" && touch steps/07.remove_null_char/$[COMPLETE_FILE]

; Clean newline character from fields
steps/08.remove_duplicate_emails/$[COMPLETE_FILE] <- steps/07.remove_null_char/$[COMPLETE_FILE] [shell]
  mkdir -p steps/08.remove_duplicate_emails && rm -rf tmp.cmds && rm -rf steps/08.remove_duplicate_emails/$[FD]* steps/08.remove_duplicate_emails/$[COMPLETE_FILE]
  cat steps/07.remove_null_char/$[FD]_removed_null.csv | csvfix remove -f 2 -e '^$' | csvfix unique -f 2 > output/$[FD]_daas_input.csv
  cat steps/07.remove_null_char/$[FD]_removed_null.csv | csvfix find -f 2 -e '^$' >> output/$[FD]_daas_input.csv
  unique_records=$(cat output/$[FD]_daas_input.csv | wc -l) && echo "Total number of Usable records are $unique_records" && touch steps/08.remove_duplicate_emails/$[COMPLETE_FILE]

; DAAS Data processing
steps/09.upload_to_daas/$[COMPLETE_FILE] <- steps/08.remove_duplicate_emails/$[COMPLETE_FILE] [shell]
  mkdir -p steps/09.upload_to_daas && rm -rf tmp.cmds && rm -rf steps/09.upload_to_daas/$[FD]* steps/09.upload_to_daas/$[COMPLETE_FILE]
  curl --basic -u "avi.kapoor@circleback.com:Password@123!" -F "name=$[FD]" -F "description=$[FD] List Ingestion" -F "file=@output/$[FD]_daas_input.csv" https://daas.circleback.com/api/contactlist/upload
  while [[ $LIST_ID -le 0 ]];
  do
     echo "List ID is : $LIST_ID"
     sleep 60
     curl --basic -u "avi.kapoor@circleback.com:Password@123!" https://daas.circleback.com/api/contactlist/ > steps/contact_list.txt
     LIST_ID=$(awk -v k="text" '{n=split($0,a,"{"); for (i=1; i<=n; i++) print a[i]}' steps/contact_list.txt | tail -1 | awk -F, '{if ($4 == "\"status\"\:\"Ready\"" && $5 == "\"name\"\:\"$[FD]\"") print $1}' | awk -F\: '{print $2}')
  done
  relink=$(curl --basic -u "avi.kapoor@circleback.com:Password@123!" https://daas.circleback.com/api/contactlist/$[LIST_ID]/download | awk -F\"\:\" '{print $2}' | awk -F\" '{print $1}')
  wget $relink -o ./output/$[FD]_daas_output.csv
  mv /output/$[FD]_daas_output.csv /input/$[FD]_daas_output.csv && touch steps/09.upload_to_daas/$[COMPLETE_FILE]

