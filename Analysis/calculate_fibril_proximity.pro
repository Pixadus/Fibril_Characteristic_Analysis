;+
; :Description:
;    Calculates the minimum distance between each fibril in an input set of test fibrils
;    and a set of reference fibrils, indentifying the "closest match" fibril from the reference set 
;
; :Params:
;    fibrils_reference = set of reference fibrils
;    fibrils_tested    = set of fibrils to be tested
;
; :Keywords:
;    plot_fibrils      = plot test fibrils onto current window
;    label_fibrils     = output test fibril ID at head of each fibril plot
;    
;  :Note:
;    fibril datasets are expected to be in form of fltarr(m,n), 
;        where m is the number of distinct fibril coordinate points 
;        and the first three columns are:
;    fibril_set[m, 0] = fibril ID - unique identifier for set of connected fibril coordinate points
;    fibril_set[m, 1] = fibril x-coordinate [pixels]
;    fibril_set[m, 2] = fibril y-coordinate [pixels]
;    
;
; :Author: Kevin Reardon, November 2021
;-

FUNCTION calculate_fibril_proximity, fibrils_reference, fibrils_tested, $
    plot_fibrils=plot_fibrils, label_fibrils=label_fibrils, fibril_colors=fibril_colors

IF N_ELEMENTS(plot_fibrils)  EQ 0 THEN plot_fibrils  = 0
IF N_ELEMENTS(label_fibrils) EQ 0 THEN label_fibrils = 0
IF N_ELEMENTS(fibril_colors) NE 2 THEN fibril_colors=['YGB6', 'Yellow']

; find numbers of individual fibrils in the fibrils being tested

fibrils_numpts          = n_elements(fibrils_tested[*,0])
fibrils_tested_uniq_idx = UNIQ(fibrils_tested[*,0], SORT(fibrils_tested[*,0]))
fibrils_tested_uniq     = (fibrils_tested[*,0])[fibrils_tested_uniq_idx]
fibrils_tested_num      = N_ELEMENTS(fibrils_tested_uniq)

fibrils_reference_num   = N_ELEMENTS(fibrils_reference[*,0])
fibrils_ref_uniq_idx    = UNIQ(fibrils_reference[*,0], SORT(fibrils_reference[*,0]))
fibrils_reference_uniq  = (fibrils_reference[*,0])[fibrils_ref_uniq_idx]

; we will first loop through each fibril coordinate, ignoring which "fibril" they belong to.
fibrils_tested_match = fltarr(fibrils_numpts, 8)
for fib_test_idx=0LL, fibrils_numpts-1 do begin
  ; loop through each point in all the identified fibrils
  fibtestpnt = fibrils_tested[fib_test_idx,*]
  
  ; calculate the distance from all pixel positions in the reference fibrils to the tested fibril pixel coordinate
  dists_all = sqrt((fibrils_reference[*,1]-fibtestpnt[1])^2 + (fibrils_reference[*,2]-fibtestpnt[2])^2)

  ; find the reference pixel location that is closest to the tested fibril pixel
  mindist = MIN(dists_all,mindist_idx)

  ; store the tested pixel coordinate and closest reference fibril pixel
  ; fibrils_tested_match[0,nn] = test fibril ID
  ; fibrils_tested_match[1,nn] = test fibril x-coordinate
  ; fibrils_tested_match[2,nn] = test fibril y-coordinate
  ; fibrils_tested_match[3,nn] = reference fibril ID
  ; fibrils_tested_match[4,nn] = reference fibril x-coordinate
  ; fibrils_tested_match[5,nn] = reference fibril y-coordinate
  ; fibrils_tested_match[6,nn] = reference fibril width value
  ; fibrils_tested_match[7,nn] = distance between test and reference fibril coordinates   
  fibrils_tested_match[fib_test_idx,*] = [fibtestpnt[0:2],reform(fibrils_reference[mindist_idx,0:3]),mindist]
endfor

match_dist_ave   = FLTARR(fibrils_tested_num)
match_dist_min   = FLTARR(fibrils_tested_num)
match_dist_max   = FLTARR(fibrils_tested_num)
match_dist_rms   = FLTARR(fibrils_tested_num)
match_id_primary = FLTARR(fibrils_tested_num)
match_id_num     = FLTARR(fibrils_tested_num)
length           = FLTARR(fibrils_tested_num)
distance         = FLTARR(fibrils_tested_num)
candidate_match_best = FLTARR(fibrils_tested_num, 9)

first_fibril = 1
valid_fibrils_mask = BYTARR(fibrils_tested_num)

; Now we walk through each test fibril and find it's closest match

for fib_id_idx = 0, fibrils_tested_num-1 do begin
  fib_id = fibrils_tested_uniq[fib_id_idx]

  ; select pixel coordinates for each unique test fibril
  fib_test_matchidx = WHERE(fibrils_tested[*,0] EQ fib_id, fib_test_matchcnt)

  ; if the fibril consists of more than three points then start processing
  if (fib_test_matchcnt GE 3) then begin
    valid_fibrils_mask[fib_id_idx] = 1

    ; select pixel coordinates and distances for matching fibrils
    fib_test_info        = fibrils_tested_match[fib_test_matchidx,*]
    fib_test_info_dist   = fibrils_tested_match[fib_test_matchidx,7]
    fib_test_numcoord    = N_ELEMENTS(fib_test_info[*,0])

    ; generate statistics about distance measurements for each fibril
    match_dist_ave[fib_id_idx] = MEAN(fib_test_info_dist)
    match_dist_min[fib_id_idx] = MIN(fib_test_info_dist)
    match_dist_max[fib_id_idx] = MAX(fib_test_info_dist)
    match_dist_rms[fib_id_idx] = STDDEV(fib_test_info_dist)

    ; calculate the distance of from each fibril coordinate to the starting coordinate
    ; from this we can calculate the "straight-line length" - 
    ; that is, the greatest distance between the starting point and another coordinate in
    ; the fibril definition - should typically be the end point of the fibril if it is close to a straight line.
    fibril_distance              = sqrt((fib_test_info[*,1] - fib_test_info[0,1])^2 + (fib_test_info[*,2] - fib_test_info[0,2])^2)
    distance[fib_id_idx]         = MAX(fibril_distance)

    ; now we compute the full path length of the fibril, by calculating the distance between 
    ;   adjacent points and summing up all those distances
    fibril_length                = sqrt((fib_test_info[1:*,1] - fib_test_info[0:-2,1])^2 + (fib_test_info[1:*,2] - fib_test_info[0:-2,2])^2)
    length[fib_id_idx]           = TOTAL(fibril_length)

    ; create an array of information about the fibril distance/length 
    fib_widths_id                = FLTARR(fib_test_matchcnt) + fib_id
    fib_info_combo               = [[fib_widths_id], [fibril_distance], [0,fibril_length]]

    ; general statistics on how many reference fibrils match a given test fibril
    fib_test_info_id             = fibrils_tested_match[fib_test_matchidx,3]
    ; find the most common matching fibril
    histmax                      = max(histogram(fib_test_info_id,loc=xscl),histmaxpos)
    match_id_primary[fib_id_idx] = xscl[histmaxpos]

    ; determine the number of different reference fibrils that have a "closest" point to the selected test fibril
    ; we will use this collection of "sometimes close" fibrils to look for a best match fibril
    ; these are the "candidate" best-match fibrils
    ;fib_test_info_id_uniq    = fib_test_info_id[UNIQ(fib_test_info_id,SORT(fib_test_info_id))]
    
    ; or just use the list of all reference fibrils to test *every* reference fibril against *every* test fibril
    ; Hooray for brute force!
    fib_test_info_id_uniq    = fibrils_reference_uniq

    match_id_num[fib_id_idx] = N_ELEMENTS(fib_test_info_id_uniq)

    candidate_match_info     = FLTARR(match_id_num[fib_id_idx],9)

    ; now loop through each candidate fibril
    for candidate_idx = 0,match_id_num[fib_id_idx]-1 do begin
        ; extract information (coordinates, number of coordinate points, fibril length) on
        ; each candidate fibril
        candidate_id         = fib_test_info_id_uniq[candidate_idx]
        candidate_fibril_pts = WHERE(fibrils_reference[*,0] EQ candidate_id, candidate_fibril_len)
        candidate_fibril     = fibrils_reference[candidate_fibril_pts, *]
        candidate_length     = TOTAL(SQRT((candidate_fibril[1:*,1] - candidate_fibril[0:-2,1])^2 + $
                                          (candidate_fibril[1:*,1] - candidate_fibril[0:-2,1])^2 ))

        candidate_dists      = FLTARR(fib_test_numcoord)
        
        ; now loop through each point in the test fibril and calculate the 
        ; distance from that point to the closest point in the candidate fibril being evaluated
        ; this results in an array of distances to nearest point in candidate fibril
        for fib_test_idx = 0,fib_test_numcoord-1 do begin
            fibtestpnt = fib_test_info[fib_test_idx,0:2]
            candidate_dists[fib_test_idx] = min(sqrt((candidate_fibril[*,1]-fibtestpnt[1])^2 + $
                                                       (candidate_fibril[*,2]-fibtestpnt[2])^2))
        endfor

        ; now order the array of distances 
        candidate_dists_sort = candidate_dists[SORT(candidate_dists)]
        ; find the comparison length - whichever is the shorter of length of test and reference fibril
        ; we want to define a fibril overlap interval
        length_limit         = MIN([candidate_fibril_len, fib_test_numcoord])
        ; now extract the number of points equal to the comparison length - we want to compare fibrils over a joint length
        candidate_dists_trim = candidate_dists_sort[0:length_limit-1]
        ; now compute the statistics of the distances over that joint fibril overlap
        candidate_dists_mean = MEAN(candidate_dists_trim)
        candidate_dists_min  = MIN(candidate_dists_trim)
        candidate_dists_max  = MAX(candidate_dists_trim)
        ; create an array witn information on:
        ; candidate_match_info[nn, 0:2] = test fibril [ID, number of coordinate points, geometrical path length]
        ; candidate_match_info[nn, 3:5] = reference fibril [ID, number of coordinate points, geometrical path length]
        ; candidate_match_info[nn, 6]   = mean distance to reference fibril
        ; candidate_match_info[nn, 7:8] = min/max distance to reference fibril
        candidate_match_info[candidate_idx, *] = [fib_id, fib_test_numcoord, length[fib_id_idx], $
                                                  candidate_id, candidate_fibril_len, candidate_length, $
                                                  candidate_dists_mean, candidate_dists_min, candidate_dists_max]
        ;print,reform(candidate_match_info[candidate_idx, *])
    endfor
    
    ; select reference fibril that has smallest mean distance to test fibril
    best_fibril_dist = MIN(candidate_match_info[*,6], best_fibril_pos)
    candidate_match_best[fib_id_idx,*] = candidate_match_info[best_fibril_pos, *]
    

    if first_fibril EQ 1 then begin
      fib_params_all  = fib_info_combo
      first_fibril       = 0
    endif else begin
      fib_params_all  = [fib_params_all, fib_info_combo]
    endelse
  endif

  ; if requested, plot fibrils on screen
  if plot_fibrils then begin
    match_limit_lower = 10
    match_limit_upper = 200
    if (candidate_match_best[fib_id_idx,6] GT match_limit_lower) and $
       (candidate_match_best[fib_id_idx,6] LE match_limit_upper) then begin
      plots, fibrils_tested[fib_test_matchidx,1], fibrils_tested[fib_test_matchidx,2], $
          col=cgColor(fibril_colors[0]),/dev,psym=-3,th=3
      candidate_fibril_pts = WHERE(fibrils_reference[*,0] EQ candidate_match_best[fib_id_idx,3], candidate_fibril_len)
      candidate_fibril     = fibrils_reference[candidate_fibril_pts, *]

      plots, candidate_fibril[*,1], candidate_fibril[*,2], $
          col=cgColor(fibril_colors[1]),/dev,psym=-3,th=1

      if label_fibrils then xyouts, fibrils_tested[fib_test_matchidx[0],1], fibrils_tested[fib_test_matchidx[0],2]-1,$
          strtrim(ROUND(fib_id),2),col=cgColor(fibril_colors[0]),charsi=1,charth=1,/dev,align=0.5
    endif
  endif

endfor

valid_fibrils_idx = WHERE(valid_fibrils_mask)

; save the information on the matching fibrils
fib_test_match_info = CREATE_STRUCT($
  'best_match', candidate_match_best, $
  'dist_ave',   match_dist_ave[valid_fibrils_idx], $
  'dist_min',   match_dist_min[valid_fibrils_idx], $
  'dist_max',   match_dist_max[valid_fibrils_idx], $
  'dist_rms',   match_dist_rms[valid_fibrils_idx], $
  'id_primary', match_id_primary[valid_fibrils_idx], $
  'id_num',     match_id_num[valid_fibrils_idx], $
  'length',         length[valid_fibrils_idx], $
  'distance',       distance[valid_fibrils_idx], $
  'fib_params_all', fib_params_all)

return,fib_test_match_info

end
