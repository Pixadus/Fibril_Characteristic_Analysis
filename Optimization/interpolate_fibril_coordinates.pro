
; This IDL script will take a table of coordinate positions for fibrils, typically
;     a set of manually selected ("clicked") fibril positions, with sparse sampling,
;     and interpolate a series of positions along the fibril with a spacing of
;     one pixel between points. This is comparable to the output of the OCCULT-2 code
;     and sufficient for proximity measures.
;
; The code will also, while it's at it, determine the corresponding values at the 
;     derived pixel positions, and return those along with the pixel coordinates.
;     Note: this isn't strictly related to the interpolation process, but is done as a 
;           convenience for future use. Could be split out into a separate function for consistency
;
; The program generates a single large array (fib_combo_1pix_all), which is [N, 6], and 
;     contains the fibril ID (index counter), x and y coordinates, and the derived values
;     for the line width, core intensity, and velocity
;

; The program can optionally overplot the original or the interpolated fibrils onto the 
;     current display, as well as label each fibril trace with it's ID number
;

FUNCTION interpolate_fibril_coordinates, fibril_coords_file, colors=colors

IF N_ELEMENTS(colors) NE 2 THEN BEGIN
    colfib = cgColor('Red6')
    coltxt = cgColor('Red3')
ENDIF ELSE BEGIN
    colfib = cgColor(colors[0])
    coltxt = cgColor(colors[1])
ENDELSE
plot_fibrils  = 1
label_fibrils = 1
plot_fitted   = 1

if N_ELEMENTS(halpha_coreint_mfbd_m300) LE 1 then $
    restore,/ve,'data/images/sav/Halpha.6563.line.params.mfbd_300modes.ser171853.seq00.hmi_aligned.sav'
coreint_map = halpha_coreint_mfbd_m300
width_map   = halpha_width_mfbd_m300
vel_map     = halpha_vel_mfbd_m300

; choose which fibril file to read and assign it a unique color for the plotting
; this has now been superceded by the ability to provide the filename as an input parameter
; fibril_coords_file = 'coordinates.gc.20210625.csv'                 & colfib = cgColor('Red6') & coltxt = cgColor('Red3')
; fibril_coords_file = 'coordinates-benoit-2021-06-25.csv'          & colfib = cgColor('Blu5') & coltxt = cgColor('Blu3')
; fibril_coords_file = 'coordinates-parker-2021-06-25-11_06_30.csv' & colfib = cgColor('Grn4') & coltxt = cgColor('Grn3')

; read in fibril file and store information on individual fibrils
print,"Reading fibril file : ", fibril_coords_file
coords_manual      = read_csv(fibril_coords_file)
fibrils_manual_ids = coords_manual.field1[uniq(coords_manual.field1, sort(coords_manual.field1))]
fibrils_manual_num = N_ELEMENTS(fibrils_manual_ids)
fibrils_manual_pts = FLTARR(2, fibrils_manual_num)

; loop through each fibril
for fib_id_cnt = 0,fibrils_manual_num-1 do begin

    fib_id = fibrils_manual_ids[fib_id_cnt]

    ; extract selected (sparse) coordinate positions for each fibril
    fib_idx = where(FIX(coords_manual.field1) EQ fib_id, fibril_points)
    fibrils_manual_pts[*, fib_id_cnt] = [fib_id, fibril_points]

    if N_ELEMENTS(fib_idx) GT 1 then begin

        fib_xc_orig = coords_manual.field2[fib_idx]
        fib_yc_orig = coords_manual.field3[fib_idx]
        fib_xc_num  = N_Elements(fib_xc_orig)
        fib_yc_num  = N_Elements(fib_yc_orig)

        if plot_fibrils then plots, fib_xc_orig, fib_yc_orig, col=colfib,/dev,psym=-1,th=2
        if label_fibrils then xyouts, fib_xc_orig[0], fib_yc_orig[0],strtrim(fib_id,2),col= coltxt,charsi=1.2,charth=0.8,/dev,align=0.5
    
        ; determine the pixel offset in the x and y directions between each clicked point in the fibril trace
        fib_xc_step = fib_xc_orig[1:-1] - fib_xc_orig[0:-2]
        fib_yc_step = fib_yc_orig[1:-1] - fib_yc_orig[0:-2]

        ; compute the total length between each clicked point in the fibril trace
        fib_segment_lengths = round(sqrt(fib_xc_step^2 + fib_yc_step^2))

        ; for each segment, generate an array with the number of steps equal to the total segment length
        ; then generate an array of x and y coordinate positions with step size appropriate step sizes
        ; such that the total length between pixel positions is one pixel
        ;
        ; for the first segment we do this outside of the loop, then for subsequent segments, if any, it is 
        ; done within the loop and concatenated to the values of the initial segment
        fib_xc_1pix      = findgen(fib_segment_lengths[0]) * fib_xc_step[0]/fib_segment_lengths[0] + fib_xc_orig[0]
        fib_yc_1pix      = findgen(fib_segment_lengths[0]) * fib_yc_step[0]/fib_segment_lengths[0] + fib_yc_orig[0]

        for nn=1, fib_xc_num-2 do begin

            fib_xc_1pix = [fib_xc_1pix, findgen(fib_segment_lengths[nn]) * fib_xc_step[nn]/fib_segment_lengths[nn] + fib_xc_orig[nn]]
            fib_yc_1pix = [fib_yc_1pix, findgen(fib_segment_lengths[nn]) * fib_yc_step[nn]/fib_segment_lengths[nn] + fib_yc_orig[nn]]

        endfor

        ; extract map values for each interpolated coordinate position
        fib_width_1pix   = interpolate(width_map,   fib_xc_1pix, fib_yc_1pix, cubic=-0.5)
        fib_coreint_1pix = interpolate(coreint_map, fib_xc_1pix, fib_yc_1pix, cubic=-0.5)
        fib_vel_1pix     = interpolate(vel_map,     fib_xc_1pix, fib_yc_1pix, cubic=-0.5)

        if plot_fitted then plots, fib_xc_1pix, fib_yc_1pix, psym=3,col=5e4, /dev

        ; create an array that contains
        ;     0: fibril id
        ;     1: interpolated x postions
        ;     2: interpolated y postions
        ;     3: width values at interpolated coordinate positions
        ;     4: intensity values at interpolated coordinate positions
        ;     5: velocity values at interpolated coordinate positions
        ;     
        fib_combo_1pix = [[intarr(N_ELEMENTS(fib_xc_1pix)) + fib_id], [fib_xc_1pix], [fib_yc_1pix], $
                          [fib_width_1pix], [fib_coreint_1pix], [fib_vel_1pix]]

        ; combine all interpolate fibril locations into one large array
        ;     individual fibril information can be extracted from array by
        ;     selecting on the fibril id
        if fib_id EQ 0 then begin
            fib_combo_1pix_all = fib_combo_1pix
        endif else begin
            fib_combo_1pix_all = [fib_combo_1pix_all, fib_combo_1pix]
        endelse

    endif

endfor

return, fib_combo_1pix_all

end