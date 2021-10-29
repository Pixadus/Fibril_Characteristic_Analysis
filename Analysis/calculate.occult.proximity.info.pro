plot_fibrils  = 0
label_fibrils = 0

; restore,/ve,'Halpha.6563.line.params.mfbd_300modes.ser171853.seq00.hmi_aligned.sav'
;coreint_map = halpha_coreint_mfbd_m300
;width_map   = halpha_width_mfbd_m300
;vel_map     = halpha_vel_mfbd_m300

; this is the output table from OCCULT
fibrils = read_csv('Halpha-N3R45L45G3.dat')
; the total number of pixel coordinates for all identified fibrils
numpts  = N_ELEMENTS(fibrils.field1)
; these are fibrils that are close to edge of field of view, mostly edge artifacts
bad_fibrils = [0,1,2,5,7,8,10,12, 78,43,50, 49, 89, 246, 127, 226, 455, 289]

; convert CSV table into an array of fibril parameters
fibrils_oclt = FLTARR(numpts,5)
for nn=0,numpts-1 do begin & $
    fibrils_oclt[nn,*] = float(strsplit(fibrils.field1[nn],/extract)) & $
endfor

; find numbers of individual fibrils in the OCCULT file
fibrils_oclt_uniq_idx = UNIQ(fibrils_oclt[*,0], SORT(fibrils_oclt[*,0]))
fibrils_oclt_uniq     = (fibrils_oclt[*,0])[fibrils_oclt_uniq_idx]
fibrils_oclt_num      = N_ELEMENTS(fibrils_oclt_uniq)

; make a binary 0/1 array to flag bad fibrils
fibrils_oclt_valid    = BYTARR(fibrils_oclt_num) + 1
fibrils_oclt_valid[bad_fibrils] = 0
fibrils_oclt_aspect   = FLTARR(fibrils_oclt_num)

for fib_id = 0, fibrils_oclt_num-1 do begin
    ; select all points matching each individual fibril index
    fib_oclt_matchidx = WHERE(fibrils_oclt[*,0] EQ fib_id, fib_oclt_matchcnt)
    ; and now extract the fibril coordinated for each fibril index
    fibrils_oclt_pts  = fibrils_oclt[fib_oclt_matchidx,*]

    ; bad edge fibrils were identified already (see "bad_fibrils" above), so we don't need to do it again
    ;IF MAX(fibrils_oclt_pts[*,1]) LE 50  THEN fibrils_oclt_valid[fib_id] = 0
    ;IF MIN(fibrils_oclt_pts[*,1]) GE 950 THEN fibrils_oclt_valid[fib_id] = 0
    ;IF MAX(fibrils_oclt_pts[*,2]) LE 50  THEN fibrils_oclt_valid[fib_id] = 0

    ; plot all fibrils
    If fibrils_oclt_valid[fib_id] EQ 1 then begin
        if plot_fibrils then plots, fibrils_oclt[fib_oclt_matchidx,1], fibrils_oclt[fib_oclt_matchidx,2], $
            col=cgColor('YGB6'),/dev,psym=-3,th=2
        if label_fibrils then xyouts, fibrils_oclt[fib_oclt_matchidx[0],1], fibrils_oclt[fib_oclt_matchidx[0],2]-1,$
            strtrim(fib_id,2),col=cgColor('YGB4'),charsi=2,charth=1,/dev,align=0.5
    endif
endfor

fibrils_oclt_values = FLTARR(numpts,3)

; using various maps, calculate the values at each identified fibril coordinate 
fib_oclt_width   = interpolate(width_map,   fibrils_oclt[*,1], fibrils_oclt[*,2], cubic=-0.5)
fib_oclt_coreint = interpolate(coreint_map, fibrils_oclt[*,1], fibrils_oclt[*,2], cubic=-0.5)
fib_oclt_vel     = interpolate(vel_map,     fibrils_oclt[*,1], fibrils_oclt[*,2], cubic=-0.5)

; select the identified fibrils to use a reference in calculating proximity below.
; we use the manually selected fibrils which have been interpolated to have coordinate points 
; at a spacing of one pixel. This allows for a better calculation of proximity.
;fibril_reference = fib_combo_1pix_all

; the combined coordinate information for all manually selected fibrils is generating by running 
;     the interpolate.fibril.coordinate.pro for each manually selected dataset and combing them
;     into a single superset (adding an offset to the fibril id numbers to make sure each fibril dataset
;     covers a different interval)
; .r interpolate_fibril_coordinates.pro
; fib_combo_1pix_gianna = interpolate_fibril_coordinates('coordinates.gc.20210625.csv',                 colors=['Red6', 'Red3'])
; fib_combo_1pix_benoit = interpolate_fibril_coordinates('coordinates-benoit-2021-06-25.csv' ,          colors=['Blu5', 'Blu3'])
; fib_combo_1pix_parker = interpolate_fibril_coordinates('coordinates-parker-2021-06-25-11_06_30.csv' , colors=['Grn4', 'Grn3'])
; fib_combo_1pix_parker[*,0] += 1000
; fib_combo_1pix_benoit[*,0] += 2000
; fib_combo_1pix_manual = [fib_combo_1pix_gianna,fib_combo_1pix_parker,fib_combo_1pix_benoit]

fibril_reference = fib_combo_1pix_manual
fibril_reference_num = N_ELEMENTS(fibril_reference[*,0])

fibrils_occult_match = fltarr(numpts, 8)                                                                  
for fib_oclt_idx=0LL, numpts-1 do begin
    ; loop through each point in all the identified fibrils 
    fiboclt = fibrils_oclt[fib_oclt_idx,*]
    ; calculate the distance from all pixel positions in the reference fibrils to the OCCULT fibril pixel coordinate                       
    dists_all = sqrt((fibril_reference[*,1]-fiboclt[1])^2 + (fibril_reference[*,2]-fiboclt[2])^2)
    ; find the reference pixel location that is closest to the OCCULT fibril pixel 
    mindist = MIN(dists_all,mindist_idx)
    ; store the OCCULT pixel coordinate and closest reference fibril pixel
    fibrils_occult_match[fib_oclt_idx,*] = [fiboclt[0:2],reform(fibril_reference[mindist_idx,0:3]),mindist]
endfor                                   

; find all pixel positions where the distance between OCCULT and reference fibrils is less than 10 pixels
mindist_match = WHERE(fibrils_occult_match[*,7] LE 10) 

match_dist_ave  = FLTARR(fibrils_oclt_num)
match_dist_min  = FLTARR(fibrils_oclt_num)
match_dist_max  = FLTARR(fibrils_oclt_num)
match_dist_rms  = FLTARR(fibrils_oclt_num)
match_id_median = FLTARR(fibrils_oclt_num)
match_id_rms    = FLTARR(fibrils_oclt_num)
match_id_num    = FLTARR(fibrils_oclt_num)
width_ave       = FLTARR(fibrils_oclt_num)
coreint_ave     = FLTARR(fibrils_oclt_num)
vel_ave         = FLTARR(fibrils_oclt_num)
length          = FLTARR(fibrils_oclt_num)

fib_first = 1
valid_fibrils_mask = BYTARR(fibrils_oclt_num)

for fib_id = 0, fibrils_oclt_num-1 do begin

    ; select pixel coordinates for each unique OCCULT fibril
    fib_oclt_matchidx = WHERE(fibrils_oclt[*,0] EQ fib_id, fib_oclt_matchcnt)

    ; if the fibril consists of more than three points then start processing
    if (fib_oclt_matchcnt GE 3) AND (fibrils_oclt_valid[fib_id] EQ 1) then begin
        valid_fibrils_mask[fib_id] = 1

        ; select pixel coordinates and distances for matching fibrils
        fib_oclt_info      = fibrils_occult_match[fib_oclt_matchidx,*]
        fib_oclt_info_dist = fibrils_occult_match[fib_oclt_matchidx,7]

        ; generate statistics about distance measurements for each fibril
        match_dist_ave[fib_id] = MEAN(fib_oclt_info_dist)
        match_dist_min[fib_id] = MIN(fib_oclt_info_dist)
        match_dist_max[fib_id] = MAX(fib_oclt_info_dist)
        match_dist_rms[fib_id] = STDDEV(fib_oclt_info_dist)

        ; general statistics on how many reference fibrils match a given OCCULT fibril 
        fib_oclt_info_id = fibrils_occult_match[fib_oclt_matchidx,3]
        match_id_median[fib_id] = MEDIAN(fib_oclt_info_id)
        match_id_rms[fib_id]    = STDDEV(fib_oclt_info_id)
        ; determine the number of different reference fibrils that are "closest" to the selected OCCULT fibril
        fib_oclt_info_id_uniq   = fib_oclt_info_id[UNIQ(fib_oclt_info_id,SORT(fib_oclt_info_id))]
        match_id_num[fib_id]    = N_ELEMENTS(fib_oclt_info_id_uniq)
    
        ; calculate mean information on map parameters for each OCCULT fibril 
        ;    -- this actually doesn't have anything to do with the fibril matching process
        width_ave[fib_id]   = MEAN(fib_oclt_width[fib_oclt_matchidx])
        coreint_ave[fib_id] = MEAN(fib_oclt_coreint[fib_oclt_matchidx])
        vel_ave[fib_id]     = MEAN(fib_oclt_vel[fib_oclt_matchidx])
        fibril_distance     = sqrt((fib_oclt_info[*,1] - fib_oclt_info[0,1])^2 + (fib_oclt_info[*,2] - fib_oclt_info[0,2])^2)
        length[fib_id]      = MAX(fibril_distance)

        fib_widths          = fib_oclt_width[fib_oclt_matchidx]
        fib_coreints        = fib_oclt_coreint[fib_oclt_matchidx]
        fib_vels            = fib_oclt_vel[fib_oclt_matchidx]
        fib_widths_id       = FLTARR(fib_oclt_matchcnt) + fib_id
        fib_info_combo      = [[fib_widths_id], [fibril_distance], [fib_widths], [fib_coreints], [fib_vels]]

        if fib_first EQ 1 then begin 
            fib_params_all  = fib_info_combo
            fib_first       = 0
        endif else begin
            fib_params_all  = [fib_params_all, fib_info_combo]
        endelse

    endif

endfor

valid_fibrils_idx = WHERE(valid_fibrils_mask)

; save the information on the matching fibrils
fib_oclt_match_info = CREATE_STRUCT('dist_ave',  match_dist_ave[valid_fibrils_idx], $
                                    'dist_min',  match_dist_min[valid_fibrils_idx], $
                                    'dist_max',  match_dist_max[valid_fibrils_idx], $
                                    'dist_rms',  match_dist_rms[valid_fibrils_idx], $
                                    'id_median', match_id_median[valid_fibrils_idx], $
                                    'id_rms',    match_id_rms[valid_fibrils_idx], $
                                    'id_num',    match_id_num[valid_fibrils_idx], $
                                    'width_ave',       width_ave[valid_fibrils_idx], $
                                    'coreint_ave',     coreint_ave[valid_fibrils_idx], $
                                    'vel_ave',         vel_ave[valid_fibrils_idx], $
                                    'length',         length[valid_fibrils_idx], $
                                    'fib_params_all', fib_params_all)

end