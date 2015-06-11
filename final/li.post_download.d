FD=ddc_500
COMPLETE_FILE=complete.chk

; Produce a fixed output result
steps/10.fix_status/$[COMPLETE_FILE] <- output/$[FD]_daas_output.csv [shell]
  mkdir -p steps/10.fix_status && rm -rf tmp.cmds && rm -rf steps/10.fix_status/$[FD]* steps/10.fix_status/$[COMPLETE_FILE]
  cat $[INPUT] | scripts/fix_status.py > steps/10.fix_status/$[FD]_fixed_output_file.csv && touch steps/10.fix_status/$[COMPLETE_FILE]

; Clean fixed output file and replace some lable
steps/11.clean_fixed_output/$[COMPLETE_FILE] <- steps/10.fix_status/$[COMPLETE_FILE]  [shell]
  mkdir -p steps/11.clean_fixed_output && rm -rf tmp.cmds && rm -rf steps/11.clean_fixed_output/$[FD]* steps/11.clean_fixed_output/$[COMPLETE_FILE]
  cat steps/10.fix_status/$[FD]_fixed_output_file.csv | sed 's/Invalidated/Unavailable/g' | sed 's/Not Covered//g' | sed 's/Filtered/Matched/g' | csvfix order -f 1:3,5:7,9:18,20:22,23:26,28:30,32:42 > $[FD]_analysis.csv && touch steps/11.clean_fixed_output/$[COMPLETE_FILE]

; Store results
steps/12.store_results/$[COMPLETE_FILE] <- steps/11.clean_fixed_output/$[COMPLETE_FILE] [shell]
  mkdir -p steps/12.store_results && rm -rf tmp.cmds && rm -rf steps/12.store_results/$[FD]* steps/12.store_results/$[COMPLETE_FILE]
  scripts/produce_report.py $[FD]_analysis.csv > output/$[FD]_Waterfall_Results.csv && touch steps/12.store_results/$[COMPLETE_FILE]
