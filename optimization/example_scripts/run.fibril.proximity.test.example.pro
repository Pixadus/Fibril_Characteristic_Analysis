; load OCCULT-identified fibrils
fibrils = read_csv('Halpha-N3R45L45G3.dat')
numpts  = N_ELEMENTS(fibrils.field1)

; go loaded table and construct array of fibril parameters
fibrils_oclt = FLTARR(numpts,6)
for nn=0,numpts-1 do begin & $
    fibrils_oclt[nn,0:4] = float(strsplit(fibrils.field1[nn],/extract)) & $
    IF (max(bad_fibrils EQ fibrils_oclt[nn,0]) ne 1) then fibrils_oclt[nn,5] = 1 & $
endfor

; a manually identified list of spurious fibrils (mostly picking up edges of field)
bad_fibrils = [0,1,2,5,7,8,10,12, 78,43,50, 49, 89, 246, 127, 226, 455, 289]
; construct fibril array excluding bad fibrils
fibrils_oclt_valid = fibrils_oclt[WHERE(fibrils_oclt[*,5] EQ 1),*]

; now load in different sets of manually selected fibrils
fib_combo_1pix_gianna = interpolate_fibril_coordinates('coordinates.gc.20210625.csv', colors=['Red6', 'Red3'])
;Reading fibril file : coordinates.gc.20210625.csv
fib_combo_1pix_benoit = interpolate_fibril_coordinates('coordinates-benoit-2021-06-25.csv', colors=['Blu5', 'Blu3'])
;Reading fibril file : coordinates-benoit-2021-06-25.csv
fib_combo_1pix_parker = interpolate_fibril_coordinates('coordinates-parker-2021-06-25-11_06_30.csv', colors=['Grn4', 'Grn3'])
;Reading fibril file : coordinates-parker-2021-06-25-11_06_30.csv
; convert fibril identifiers into unique values by adding in an offset
; (assumes no more than 1000 fibrils in any one fibril set
fib_combo_1pix_parker[*,0] += 1000
fib_combo_1pix_benoit[*,0] += 2000
; construct joint set of manually selected fibrils
; this is a set of discrete pixel positions, with an identifier value for each fibril
fib_combo_1pix_manual = [fib_combo_1pix_gianna,fib_combo_1pix_parker,fib_combo_1pix_benoit]

; now run calculate_fibril_proximity to quantify correspondence between manual and OCCULT fibrils
fibril_match_info = calculate_fibril_proximity(fib_combo_1pix_manual,fibrils_oclt_valid,plot=0,label=0)

do_display = 1
if do_display EQ 1 then begin
    ; display the original map of H-alpha profile widths and overplot matching fibrils
    restore,/ve,'Halpha.6563.line.params.mfbd_300modes.ser171853.seq00.hmi_aligned.sav'
    tvscl,halpha_width_mfbd_m300
    ; construct a list of each unique fibril identifiers in the manually selected fibrils
    ref_ids = fib_combo_1pix_manual[uniq(fib_combo_1pix_manual[*,0], sort(fib_combo_1pix_manual[*,0])),0]
    ; loop through each unique fibril and plot
    for nn=0,n_elements(ref_ids)-1 do begin & matchidx = where(fib_combo_1pix_manual[*,0] EQ ref_ids[nn]) & $
        plots,fib_combo_1pix_manual[matchidx,1],fib_combo_1pix_manual[matchidx,2],col=cgcolor('grn6'),/dev,th=5
    fibril_match_info = calculate_fibril_proximity(fib_combo_1pix_manual,fibrils_oclt_valid,plot=0,label=0)

    ; now run calculate_fibril_proximity to quantify correspondence between manual and OCCULT fibrils (with plotting)
    fibril_match_info = calculate_fibril_proximity(fib_combo_1pix_manual,fibrils_oclt_valid,/plot,/label)
endif