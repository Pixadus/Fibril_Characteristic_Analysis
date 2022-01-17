;+
; :Description:
;    Script to optimize OCCULT-2 parameters. Given a parameter space, run OCCULT-2 for all parameters.
;    Generate array of match percentages for each. An optimized parameter set will be chosen from an array 
;    of runs, with the distinguishing factors:
;    1. Maximize percentage of matched OCCULT fibrils
;    2. Maximize percentage of matched manual fibrils
;    
; :Params:
;    none
;
; :Keywords:
;    none
;
; :Author: Parker Lamb, December 2021 with code from Kevin Reardon. 
;-

; Change directory to script folder
cd, file_dirname(routine_filepath(/Either))

; Variable defintions
;restore,/ve,'data/images/sav/Halpha.6563.line.params.mfbd_300modes.ser171853.seq00.hmi_aligned.sav'
;width_map   = halpha_width_mfbd_m300
width_map = READFITS('data/images/fits/Ha_cropped.fits')

; rotate manual array by 0.42 degrees

;output_img  = "data/images/sav/Ha-occult-result.sav"
; TODO add gaussian smoothed width map?
gianna_results = 'data/manual_results/coords_gianna.csv'
benoit_results = 'data/manual_results/coords_benoit.csv'
parker_results = 'data/manual_results/coords_parker.csv'
parameters_set = List()

; Read in manual fibrils
print,"Reading in manual fibril files"
manual_gianna = interpolate_fibril_coordinates(gianna_results, colors=['Red6', 'Red3'])
manual_benoit = interpolate_fibril_coordinates(benoit_results, colors=['Blu5', 'Blu3'])
manual_parker = interpolate_fibril_coordinates(parker_results, colors=['Grn4', 'Grn3'])
; Make benoit and parker fibrils have unique ids
manual_parker[*,0] += 1000
manual_benoit[*,0] += 2000
; Combined manual data
manual_combined = [manual_gianna,manual_benoit,manual_parker]

; Define parameter set here
nnsm1_range   = [4]           ; NSM 3-7
rmin_range    = [45]       ; RMIN 35:55 (:5)
lmin_range    = [35]      ; LMIN 35:45 (:10)
nstruc        = 2000            ; NSTRUC 2000
nloopmax      = 2000            ; NLOOPMAX 2000
ngap_range    = [1]           ; NGAP 1-3
thresh1_range = [0.0]           ; THRESH1 0.0 (no effect)
thresh2_range = [3]             ; THRESH2 3 (no effect)

for nsm1=0, N_ELEMENTS(nsm1_range)-1 do begin
  for rmin=0, N_ELEMENTS(rmin_range)-1 do begin
    for lmin=0, N_ELEMENTS(lmin_range)-1 do begin
      for ngap=0, N_ELEMENTS(ngap_range)-1 do begin
        for thresh1=0, N_ELEMENTS(thresh1_range)-1 do begin
          for thresh2=0, N_ELEMENTS(thresh2_range)-1 do begin
             
            params = [$
              nsm1_range[nsm1],       $
              rmin_range[rmin],       $
              lmin_range[lmin],       $ 
              nstruc,                 $
              nloopmax,               $
              ngap_range[ngap],       $
              thresh1_range[thresh1], $
              thresh2_range[thresh2] ]
            print,"nsm1=", params[0], " rmin=", params[1], " lmin=", params[2], " nstruc=", params[3], " nloopmax=", params[4], " ngap=", params[5], " thresh1=", params[6], " thresh2=", params[7]
              
            ; Run OCCULT-2, get data on fibrils
            print,"Getting OCCULT fibril data"
            occult_results_valid = looptracing_auto4_custom(width_map,output_img,params,output, 2001)
            write_csv,"data/optimization_results/occult_results_valid.csv",transpose(occult_results_valid)
            
;            ; REMOVE Using temporary test data for now
;            occult_fibrils_raw = read_csv('data/occult_results/Halpha-N3R45L45G3.dat')
;            ; a manually identified list of spurious fibrils (mostly picking up edges of field)
;            bad_fibrils = [0,1,2,5,7,8,10,12, 78,43,50, 49, 89, 246, 127, 226, 455, 289]
;            numpts  = N_ELEMENTS(occult_fibrils_raw.field1)
;            ; go loaded table and construct array of fibril parameters
;            occult_fibrils_arr = FLTARR(numpts,6)
;            for nn=0,N_ELEMENTS(occult_fibrils_raw.field1)-1 do begin & $
;              occult_fibrils_arr[nn,0:4] = float(strsplit(occult_fibrils_raw.field1[nn],/extract)) & $
;              IF (max(bad_fibrils EQ occult_fibrils_arr[nn,0]) ne 1) then occult_fibrils_arr[nn,5] = 1 & $
;            endfor
;            
;            ; construct fibril array excluding bad fibrils
;            occult_fibrils_valid = occult_fibrils_arr[WHERE(occult_fibrils_arr[*,5] EQ 1),*]
;            
;            write_csv,"data/occult_results.csv",transpose(occult_results)
;            write_csv,"data/occult_old_results.csv",transpose(occult_fibrils_valid)
              
            ; Run calculate_fibridl_proximity on occult fibrils
            print,"Calculating proximity of occult fibrils"
            occult_fibril_match_info = calculate_fibril_proximity(manual_combined,occult_results_valid,plot=0,label=0)
            occult_best_matches = occult_fibril_match_info.BEST_MATCH
  
            ; Run calculate_fibril_proximity on manual fibrils
            print,"Calculating proximity of manual fibrils"
            manual_fibril_match_info = calculate_fibril_proximity(occult_results_valid,manual_combined,plot=0,label=0)
            manual_best_matches = manual_fibril_match_info.BEST_MATCH
  
            ; Find number of OCCULT fibrils with minimum distance from nearest manual neighbor > 10 px. These are considered "invalid" fibrils.
            ; We could also use mean distance, which would be more harsh (more nomatch occult fibrils)
            print,"Filtering fibrils"
            occult_fibril_num = size(occult_best_matches)
            occult_fibril_num = occult_fibril_num[1]
            occult_nomatch = occult_best_matches[WHERE(occult_best_matches[*,7] GT 10.0),*]
            occult_nomatch_num = size(occult_nomatch)
            occult_nomatch_num = occult_nomatch_num[1]
            ; REMOVE, info only
            ;write_csv,"data/optimization_results/occult_match_info.csv", transpose(occult_nomatch)
  
            ; Find number of manual fibrils with minimum distance from nearest occult neighbor > 10 px. Considered "invalid" manual fibrils.
            manual_fibril_num = size(manual_best_matches)
            manual_fibril_num = manual_fibril_num[1]
            manual_nomatch = manual_best_matches[WHERE(manual_best_matches[*,7] GT 10.0),*]
            manual_nomatch_num = size(manual_nomatch)
            manual_nomatch_num = manual_nomatch_num[1]
            ; REMOVE, info only
            ;write_csv,"data/optimization_results/manual_match_info.csv", transpose(manual_nomatch)
  
            occult_percent = 1.0-(float(occult_nomatch_num)/float(occult_fibril_num))
            manual_percent = 1.0-(float(manual_nomatch_num)/float(manual_fibril_num))
            
            ; Add in occult_percent and manual_percent to params
            params = [params, [occult_percent], [manual_percent]]
            parameters_set.Add,params
            
            parameters_set_arr = parameters_set.ToArray()
                        
            print,"Writing CSV"
            write_csv,"data/optimization_results/optimization.csv",transpose(parameters_set_arr)

          endfor
        endfor
      endfor
    endfor
  endfor
endfor

end