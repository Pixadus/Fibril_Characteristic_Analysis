# -*- coding: utf-8 -*-
"""
Created on Thur July 15 2021

@author: Parker Lamb
@description: Maps OCCULT-2 measurements to original image, and determines intensity and
              width on a per-pixel basis.
"""
import sys
import re
from astropy.io import fits
import scipy.io as sio
import numpy as np

# 0. Specify OCCULT-2 data file and original picture file

occult2_path = sys.argv[1]
picture_path = sys.argv[2]

f = None
data_dict = {}
# Storing our data as as dict of loops, with each loop associated with a list of dicts, with each dict
# containing per-pixel characteristics. 
# {loop1: [{"x":x,"y":y,"length":length,"intensity": intensity, "width":width},{x,y,length,intensity,width}, ... ]}

# 1. Open OCCULT-2 data file, original picture file

# -- Open original picture file. Either a FITS file or a SAV file. 
if ".fits" in picture_path:
    f = fits.open(picture_path, ignore_missing_end=True)
elif ".sav" in picture_path:
    f = sio.readsav(picture_path)
    if len(f) > 1:
        n = 0
        print("Multiple images available in save. Choose the number that corresponds with the image you want.")
        for im_name in f.keys():
            print("{}: {}".format(n,im_name))
            n+=1
        opt = input("> ")
        f = f[list(f.keys())[int(opt)]]
        
        # OCCULT-2 flips the array output vertically. We match that here. 
        f = np.flipud(f)
    else:
        f = f[list(f.keys())[0]]
        f = np.flipud(f) # Flip array. See above. 
else:
    print("Input file not specified, or invalid. Exiting.")
    sys.exit(0)

# -- Open OCCULT-2 data file
datafile = open(occult2_path,newline='')

# 2. Read in OCCULT-2 x and y. 

for row in datafile:
    # Remove extra whitespace, and replace with commas. 
    row = re.sub('\s+',',',row)
    row = row.split(",")
    row.pop(0)
    loop = int(round(float(row[0])))
    x = float(row[1])
    y = float(row[2])
    coord_set = {"x": x, "y": y, "length": 0, "intensity": 0, "width": 0}
    if row[1] == '' or row[2] == '':
        continue
     # Check if the loop exists in the dictionary. If so, just append to it.
    try:
        data_dict[loop]
        data_dict[loop].append(coord_set)
    # If not, initialize the list containing loop coordinate details
    except KeyError: 
        data_dict[loop] = [coord_set]

# Calculate the lengths of each curve
# Iterate through all loops
for key in data_dict.keys():
    length = 0
    prevcoord=np.array([])
    # Iterate through each coordinate list here
    for coord_set in data_dict[key]:
        coord = np.array([coord_set["x"],coord_set["y"]])
        if prevcoord.size == 0:
            prevcoord = coord
        else:
            length+=np.abs(np.linalg.norm(coord-prevcoord))
            prevcoord = coord
        coord_set["length"] = length

# 3. Get original picture intensity value at coordinates.
 
for key in data_dict.keys():
    for coord_set in data_dict[key]:
        coord_set["intensity"] = f[int(np.floor(coord_set["x"])),int(np.floor(coord_set["y"]))]

# 4. Calculate width of the fibril at this point

# -- a. Determine dx, dy
# -- b. Get 90 degree rotation dx, dy. A(x,y) -> A(-y,x)
# -- c. Divide by absolute value (magnitude) of self to get unit direction in both dx and dy
# -- d. Determine min threshhold automatically. Try looking at threshold values of all lines, 
#       find average line threshhold, subtract some value to get a min threshold. 
# -- e. Continue along perpendicular line until min threshold reached. 
# 
# NOTE: for now, we're assuming max intensity is the center of the fibril, and just doubling the measured width above. 
#       Problems exist with this method - may be unequal observed widths but equal physical widths, or equal observed
#       widths and unequal physical widths.

for key in data_dict.keys():
    length = 0
    prevcoord=np.array([])
    # Iterate through each coordinate list here
    for coord_set in data_dict[key]:
        coord = np.array([coord_set["x"],coord_set["y"]])
        if prevcoord.size == 0:
            prevcoord = coord
        else:
            dx = coord[0]-prevcoord[0]
            dy = coord[1]-prevcoord[1]
            prevcoord = coord
            # Get perpendicular dx/dy
            dxp = -dy
            dyp = dx
            # Get perpendicular coordinate
            perp_x = coord + dxp
            perp_y = coord + dyp

            # LEFTOFF: We need to determine how far to continue along dxp/dyp. Get lowest detected structure intensity,
            #          then find all pixels along line that are lowest-somevalue 
            # NOTE: lowest is still a max intensity. Goal is to find all values < lowest but still > avg back intensity.


# 5. Get intensity values along this perpendicular line. For every intensity value greater than background threshhold
#    in both directions, increment width and continue along line