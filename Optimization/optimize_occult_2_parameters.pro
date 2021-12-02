;+
; :Description:
;   Works in conjunction with calculate_fibril_proximity.pro to optimize OCCULT-2 parameters. 
;
; :Params:
;    none
;
; :Keywords:
;    none
;
; :Author: Parker Lamb, December 2021
;-

; Our reference set of fibrils
;fibrils_manual = READ_CSV("../data/manual_results/coordinates-parker-2021-06-25-11.csv")
;fibrils_manual = READ_CSV("/Users/aethio/Documents/Projects/fibril_tracing/data/manual_results/coordinates-parker-2021-06-25-11.csv")
fibrils_manual_struct = READ_CSV("/Users/aethio/Documents/Projects/fibril_tracing/data/manual_results/coordinates-parker-2021-06-25-11.csv")
fibrils_manual = fltarr(size(fibrils_manual_struct.(0),/N_ELEMENTS),3)
fibrils_manual[*,0] = fibrils_manual_struct.(0)
fibrils_manual[*,1] = fibrils_manual_struct.(1)
fibrils_manual[*,2] = fibrils_manual_struct.(2)

; Our test set of fibrils
fibrils_occult_struct = READ_CSV("/Users/aethio/Documents/Projects/fibril_tracing/data/occult_results/Halpha-N5R30L25G2.csv")
fibrils_occult = fltarr(size(fibrils_occult_struct.(0),/N_ELEMENTS),3)
fibrils_occult[*,0] = fibrils_occult_struct.(0)
fibrils_occult[*,1] = fibrils_occult_struct.(1)
fibrils_occult[*,2] = fibrils_occult_struct.(2)

; The matching script
fibril_proximity = calculate_fibril_proximity(fibrils_manual, fibrils_occult)

end