;+
; Project     : SOHO, TRACE, STEREO, HINODE, SDO
;
; Name        : LOOPTRACING_AUTO4 - CUSTOM
;
; Category    : Automated 2D Pattern Recognition
;
; Explanation : An input image (IMAGE1) is highpass-filtered (IMAGE2)
;		and automatically traced for curvi-linear structures,
;		whose [x,y] coordinates in solar radii are stored in LOOPFILE.
;		The algorithm iteratively starts to trace a loop from
;		the position of the absolute flux maximum in the image,
;		tracks in a bi-directional way by oriented directivity,
;		based on the direction of the ridge with maximum flux.
;
; Reference   : Aschwanden,M.J. (2010), Solar Physics 262, 399-423,
;		"A code for automated tracing of coronal Loops
;               approaching visual perception"
;               describes earlier version of OCCULT code.
;               This routine computes a newer version of the OCCULT-2 code 
;
; Syntax      : IDL> looptracing_auto3,image1,image2,para2,output,test
;
; Inputs      : image1 - input image 
;               para2 - [nsm1,nstruc,lmin,....]
;                       contains algorithm control parameters, such as:
;                       nsm1  = lowpass filter [pixels]
;                       nstruc= maximum number of analyzed structures
;                       lmin  = minimum length of loop segments
;			nloopw= maximum number of loop per (wavelength) image 
;               ngap =  number of pixels in loop below flux threshold
;                       significance levels with respect to the
;                       the median flux in loop profile
;                       Recommended values for loop detection in AIA/SDO images:
;			(nsm1=3, nstruc=1000, lmin=25, nloopw=100,ngap=3) 
;               test -  flag for no test (0) or interactive test output (1)
;
; Outputs     : image2	 - output image of highpass-filtered image
;
; History     : 22-Oct-2009, Version 1 written by Markus J. Aschwanden
;		26-Apr-2013, new version of code OCCULT-2
;		 4-May-2013, new version of code OCCULT-3
;		18-May-2013, final version of OCCULT-3     ;looptracing_auto3
;		20-Jun-2013, if (iloop ge nloopmax) then stop
;               20-Jun-2014, add parameter ngap to PARA2[6]
;               26-Jul-2014, update documentation on new parameters in PARA2
;		19-Mar-2015; statistic,image2,zavg,zsig
;		19-Jan-2015, if (zstart le zsig*thresh2) then goto,end_trace
;		24-Nov-2015, automated calculation of thresh
;		 8-Dec-2015, no subtraction of median, image1 = image1 > zmed
;		12-Dec-2021, custom modifications	
;
; Contact     : aschwanden@sag.lmsal.com
;-

function looptracing_auto4_custom,image1,image2,para2,output,test

fibList = List()

;UNPACK CONTROL PARAMETERS__________________________________________
	;para2=[nsm1,rmin,lmin,nstruc,nloopw,ngap,qthresh1,qthresh2]
nsm1      =long(para2(0))
rmin      =long(para2(1))
lmin      =long(para2(2))
nstruc    =long(para2(3))
nloop	    =long(para2(4))
ngap	    =long(para2(5))            
qthresh1  =para2(6)
qthresh2  =para2(7)
reso      =1
step	    =1
nloopmax  =10000
npmax	    =2000
nsm2	    =nsm1+2
nlen	    =rmin
na	      =180
nb	      =30
s_loop	  =step*findgen(nlen)
s0_loop	  =step*(findgen(nlen)-nlen/2)
wid	      =(nsm2/2-1) > 1
looplen	  =0.

;BASE LEVEL______________________________________________________________
zmed	=median(image1)
ind_pos =where(image1 gt 0,nind)
if (nind le 1) then zmed=median(image1)
if (nind ge 2) then zmed=median(image1(ind_pos))
image1	=image1 > (zmed*qthresh1)		;CHANGE DEC 8, 2015

;HIGHPASS FILTER__________________________________________________________
if (nsm1 le 2) then image2=image1-smooth(image1,nsm2)
if (nsm1 ge 3) then image2=smooth(image1,nsm1)-smooth(image1,nsm2)
dim	=size(image1)
nx	=dim(1)
ny	=dim(2)

;ERASE BOUNDARIES ZONES (SMOOTHING EFFECTS)_______________________________
image2(0:nsm2-1,*)      =0.
image2(nx-nsm2:nx-1,*)  =0.
image2(*,0:nsm2-1,*)    =0.
image2(*,ny-nsm2:ny-1,*)=0.

;NOISE THRESHOLD__________________________________________________________
zmed	=median(image2)
ind_pos	=where(image2 gt 0,nind)	;half positive, half negative diff
if (nind ge 1) then zmed=median(image2(ind_pos))
thresh 	=zmed*qthresh2 		

;LOOP TRACING START AT MAXIMUM FLUX POSITION______________________________
iloop=0
residual=image2	> 0.	
iloop_nstruc=fltarr(nstruc)
loop_len=fltarr(nloopmax)
for istruc=0,nstruc-1 do begin
 zstart =max(residual,im) 
 if (zstart le thresh) then goto,end_trace
 if (istruc mod 100) eq 0 then begin
  ipix	=where(residual gt 0.,npix)
  qpix	=float(npix)/(float(nx)*float(ny))
; flux_sigma=zstart/thresh	
  flux_sigma=zstart/zmed	;thresh	
  print,'Struc#'+string(istruc,'(I7)')+'  Loop#'+string(iloop,'(I5)')+$
        '  Signal/noise='+string(flux_sigma,'(f9.2)') 
 endif
 jstart	=long(im/nx)
 istart	=long(im mod nx)

;TRACING LOOP STRUCTURE STEPWISE_____________________________________________
 ip	=0
 ndir	=2
 for idir=0,ndir-1 do begin
  xl	=fltarr(npmax+1)
  yl	=fltarr(npmax+1)
  zl	=fltarr(npmax+1)
  al	=fltarr(npmax+1)
  ir	=fltarr(npmax+1)
  if (idir eq 0) then sign_dir=+1
  if (idir eq 1) then sign_dir=-1

;INITIAL DIRECTION FINDING___________________________________________________ 
  xl(0) =istart
  yl(0) =jstart
  zl(0) =zstart
  alpha  =!pi*findgen(na)/float(na)
  flux_max=0.
  for ia=0,na-1 do begin
   x_   =xl(0)+s0_loop*cos(alpha(ia))
   y_   =yl(0)+s0_loop*sin(alpha(ia))
   ix    =long(x_+0.5)
   iy    =long(y_+0.5)
   flux_ =residual(ix,iy)  	                ;residual image
   flux  =total(flux_>0.)/float(nlen)
   if (flux gt flux_max) then begin
    flux_max=flux
    al(0)=alpha(ia)				;initial direction angle 
    x_lin=x_
    y_lin=y_
   endif
  endfor

;CURVATURE RADIUS________________________________________________________
  xx_curv=fltarr(nlen,nb,npmax)
  yy_curv=fltarr(nlen,nb,npmax)
  for ip=0,npmax-1 do begin          		;maximum loop length
   if (ip eq 0) then begin 
    ib1	=0 
    ib2	=nb-1 					;large range of curv radii
   endif 					
   if (ip ge 1) then begin 
    ib1=(ir(ip)-1)>0
    ib2=(ir(ip)+1)<(nb-1) 			;small range of curv radii
   endif 					
   beta0=al(ip)+!pi/2.				;angle at curvature center 
   xcen	=xl(ip)+rmin*cos(beta0)			
   ycen	=yl(ip)+rmin*sin(beta0)
   flux_max=0.
   for ib=ib1,ib2 do begin			;curvature radii array
    rad_i =rmin/(-1.+2.*float(ib)/float(nb-1))  
    xcen_i=xl(ip)+(xcen-xl(ip))*(rad_i/rmin)	;curvature center position
    ycen_i=yl(ip)+(ycen-yl(ip))*(rad_i/rmin)
    beta_i=beta0+sign_dir*s_loop/rad_i		;angle at curvature center
    x_    =xcen_i-rad_i*cos(beta_i)		;x-coord of curved segment
    y_    =ycen_i-rad_i*sin(beta_i)
    ix    =long(x_+0.5)				;x-pixel or curved segment
    iy    =long(y_+0.5)
    flux_ =residual(ix,iy) > 0.	         	;resdiual image
    flux  =total(flux_)/float(nlen)
    if (idir eq 1) then begin &xx_curv(*,ib,ip)=x_ &yy_curv(*,ib,ip)=y_ &endif
    if (flux gt flux_max) then begin
     flux_max=flux
     al(ip+1)=al(ip)+sign_dir*(step/rad_i)
     ir(ip+1)=ib 				;curvature radius index
     al_mid  =(al(ip)+al(ip+1))/2.
     xl(ip+1)=xl(ip)+step*cos(al_mid+!pi*idir)
     yl(ip+1)=yl(ip)+step*sin(al_mid+!pi*idir)
     ix_ip   =(long(xl(ip+1)+0.5)>0)<(nx-1)
     iy_ip   =(long(yl(ip+1)+0.5)>0)<(ny-1)
     zl(ip+1)=residual(ix_ip,iy_ip)
     if (ip eq 0) then begin &x_curv=x_ &y_curv=y_ &endif
    endif
   endfor
   iz1	=(ip+1-ngap)>0
   if (max(zl(iz1:ip+1)) le 0) then begin
    ip=(iz1-1) > 0
    goto,endsegm 
   endif
  endfor		;for ip=0,npmax		;loop points
  ENDSEGM:

;RE-ORDERING LOOP COORDINATES______________________________________ 
  if (idir eq 0) then begin			;first half of loop
   xloop	=reverse(xl(0:ip))
   yloop	=reverse(yl(0:ip))
   zloop	=reverse(zl(0:ip))
  endif
  if (idir eq 1) and (ip ge 1) then begin	;second half of loop 
   xloop	=[xloop,xl(1:ip)]
   yloop	=[yloop,yl(1:ip)]
   zloop	=[zloop,zl(1:ip)]
  endif
 endfor						;for idir=0,1 do 
 ind	=where((xloop ne 0) and (yloop ne 0),nind)
 looplen=0
 if (nind le 1) then goto,skip_struct
 xloop	=xloop(ind)
 yloop	=yloop(ind)
 zloop	=zloop(ind)
 if (iloop ge nloopmax) then goto,end_trace

;LOOP COMPLETED - LOOP LENGTH_________________________________________
 np	=n_elements(xloop)
 s	=fltarr(np)			;loop length coordinate
 looplen=0
 if (np ge 2) then for ip=1,np-1 do s(ip)=s(ip-1)+$
   sqrt((xloop(ip)-xloop(ip-1))^2+(yloop(ip)-yloop(ip-1))^2)
 looplen=s(np-1) 			;number of pixels for full loop length 
 ns	=long(looplen)>3		
 ss	=findgen(ns)

SKIP_STRUCT:
;STORE LOOP COORDINATES_______________________________________________
 if (looplen ge lmin) then begin
  nn	=long(ns/reso+0.5)
  ii	=findgen(nn)*reso
  xx	=interpol(xloop,s,ii)				;interpolate
  yy	=interpol(yloop,s,ii)
  ff	=interpol(zloop,s,ii)				;flux average
  x_rsun=xx
  y_rsun=yy
  s_rsun=ii						;loop length
  ;if (iloop eq 0) then openw,2,loopfile
  ;if (iloop ge 1) then openw,2,loopfile,/append
  for ip=0,nn-1 do fibList.Add,[iloop,xx(ip),yy(ip),ff(ip),ii(ip)]
  iloop_nstruc(istruc)=iloop
  loop_len(iloop)=looplen
  iloop=iloop+1
 endif

;TEST DISPLAY_________________________________________________________
if (test eq 2) and (looplen ge lmin) then begin 
 for io=0,0 do begin
 form	=1
 char	=0.7
 fignr =strtrim(string(iloop,'(I4)'),2)
 plotname='tracing'
 ref	=''
 unit	=1
 fig_open,io,form,char,fignr,plotname,unit
 loadct,5
 x0     =(max(xloop)+min(xloop))/2.
 y0     =(max(yloop)+min(yloop))/2.
 dx     =(max(xloop)-min(xloop))/2.
 dy     =(max(yloop)-min(yloop))/2.
 dd     =(dx>dy)>(step/2)
 i1     =long(x0-dd*2.5)>0
 i2     =long(x0+dd*2.5)<(nx-1)
 j1     =long(y0-dd*2.5)>0
 j2     =long(y0+dd*2.5)<(ny-1)
 subimage=image2(i1:i2,j1:j2)			;original display
 subimage2=residual(i1:i2,j1:j2)		;residual display
 z0     =max(subimage)>1.
 xfov   =i1+findgen(i2-i1+1)
 yfov   =j1+findgen(j2-j1+1)
 !p.position=[0.05,0.05,0.95,0.7]
 !x.range=[i1,i2]
 !y.range=[j1,j2]
 !x.style=1
 !y.style=1
 !p.title='Structure #'+string(istruc,'(i4)')+' Loop #'+string(iloop,'(I4)')
 plot,[i1,i1],[j1,j1]
 level  =max(zloop)*(0.1+findgen(28))/28.
 contour,subimage,xfov,yfov,level=level,/overplot
 contour,subimage-subimage2,xfov,yfov,level=level,color=128,/overplot
 for ip=10,npmax-1,10 do for ib=0,nb-1 do $
  oplot,xx_curv(*,ib,ip),yy_curv(*,ib,ip)
 oplot,istart*[1,1],jstart*[1,1],psym=4,symsize=4,color=200,thick=4
 dip	=5 < (np-1)
 for ip=0,np-1,dip do $
  xyouts,xloop(ip),yloop(ip),string(ip,'(i3)'),size=1,color=150
;oplot,x_lin,y_lin,thick=6,linestyle=2,color=200
;oplot,x_curv,y_curv,thick=6,color=200
 oplot,xloop,yloop,thick=3,color=50,psym=-1,symsize=2
 fig_close,io,fignr,ref
 read,'continue?',yes
 if (yes eq 0) then stop
 endfor
endif

;ERASE LOOP IN RESIDUAL IMAGE________________________________________
 i3	=(istart-wid)>0
 i4	=(istart+wid)<(nx-1)
 j3	=(jstart-wid)>0
 j4	=(jstart+wid)<(ny-1)
 residual(i3:i4,j3:j4)=0.		;in case of no valid loop
 nn	=n_elements(xloop)
 for is=0,nn-1 do begin
  i0	=(long(xloop(is))>0)<(nx-1)
  i3	=long(i0-wid)>0
  i4	=long(i0+wid)<(nx-1)
  j0	=(long(yloop(is))>0)<(ny-1)
  j3	=long(j0-wid)>0
  j4	=long(j0+wid)<(ny-1)
  residual(i3:i4,j3:j4)=0.
 endfor

 endloop:
endfor	;for istruc=0,nstruc-1 do begin
END_TRACE:
fluxmin =min(image1)
fluxmax =max(image1)
output  =[wid,fluxmin,fluxmax,nsm2,nlen,na,nb]
  
;;SELECT LONGEST LOOPS_______________________________________________
;ind_det	=where(loop_len gt 0,ndet)
;if (ndet ge 1) then begin
; isort	=sort(-loop_len)
; readcol,loopfile,iloop_,xx_,yy_,ff_,ii_
;
; openw,2,loopfile
; nlist	=(nloop < ndet) 		;minimum is 1 loop at least
; print,'nloop,ndet,nlist=',nloop,ndet,nlist 
; for iloop=0,nlist-1 do begin
;  ind	=where(iloop_ eq isort(iloop),np)
;  if (np ge 3) then begin
;   for ip=0,np-1 do begin
;    ii	=ind(ip)
;    printf,2,iloop_(ii),xx_(ii),yy_(ii),ff_(ii),ii_(ii)
;   endfor
;  endif
; endfor
; close,2
;endif
;end

print,"List size: ",fibList.Count()
fibArr = fibList.ToArray()
return,fibArr

end
