# -*- coding: utf-8 -*-
"""
Created on Thur July 15 2021

@author: Parker Lamb
@description: Maps OCCULT-2 measurements to original image, and determines intensity and
              width on a per-pixel basis.
"""
import sys
import re
import csv
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
from astropy.io import fits
from collections import OrderedDict
from scipy.signal import argrelextrema
from intensity_limits import get_intensity_limit

# 0. Specify OCCULT-2 data file and original picture file

# We're storing our data as as dict of loops, with each loop associated with a list of dicts, with each dict
# containing per-pixel characteristics. 
# {loop1: [{"x":x,"y":y,"length":length,"intensity": intensity, "width":width},{x,y,length,intensity,width}, ... ]}

occult2_path = sys.argv[1]
picture_path = sys.argv[2]

# 1. Open OCCULT-2 data file, original picture file

f = None
data_dict = {}

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
        
        # OCCULT-2 flips the array output vertically. We do the same here. 
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
    # -- Remove extra whitespace, and replace with commas. 
    row = re.sub('\s+',',',row)
    row = row.split(",")
    row.pop(0)
    loop = int(round(float(row[0])))
    x = float(row[1])
    y = float(row[2])
    coord_set = {"x": x, "y": y, "length": 0, "intensity": 0, "width": 0}
    if row[1] == '' or row[2] == '':
        continue
     # -- Check if the loop exists in the dictionary. If so, just append to it.
    try:
        data_dict[loop]
        data_dict[loop].append(coord_set)
    # -- If not, initialize the list containing loop coordinate details
    except KeyError: 
        data_dict[loop] = [coord_set]

# -- Calculate the lengths of each curve
for key in data_dict.keys(): # Loop iteration
    length = 0
    prevcoord=np.array([])
    # Coordinate iteration
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
        # -- Coordinates are rounded to nearest coordinate
        coord_set["intensity"] = f[int(np.round(coord_set["x"])),int(np.round(coord_set["y"]))]
        
# 4. Calculate width of the fibril at this point

# -- a. Determine dx, dy
# -- b. Get 90 degree rotation dx, dy. A(x,y) -> A(-y,x)
# -- c. Determine min threshhold automatically. Try looking at threshold values of all lines, 
#       find average line threshhold, subtract some value to get a min threshold. 
# -- d. Width extension if:
# ---- 1. Located perpendicular to line pixel's slope
# ---- 2. Intensity > get_intensity_limit

# Get the image average difference between maxima and minima
intensity_limit_frac = get_intensity_limit(picture_path)

for key in data_dict.keys():
    length = 0
    prevcoord=np.array([])
    intensities = []
    for coord_set in data_dict[key]:
        intensities.append(coord_set["intensity"])
    median_loop_intensity = np.median(intensities)

    # -- Iterate through each coordinate list here
    for coord_set in data_dict[key]:
        # Round coordinate to nearest whole coordinate
        coord = np.array([int(np.round(coord_set["x"])),int(np.round(coord_set["y"]))])

        # If this coordinate is the first entry in the list, continue past it
        if prevcoord.size == 0:
            prevcoord = coord
            continue

        else:
            # Get the x and y slopes from the last coordinate to this coordinate
            dx = coord[0]-prevcoord[0]
            dy = coord[1]-prevcoord[1]
            prevcoord = coord

            # Get perpendicular dx/dy (90 degree rotation)
            dxp = -dy
            dyp = dx

            # Width will always be at least 1 pixel
            width = 1

            # Define intensity list
            orig_intensity = f[coord[0],coord[1]]
            intensities = []

            # Get intensities of 5 coordinates in direction 1
            for n in range(1,6,1):
                perp_coord = coord+np.array([dxp*n,dyp*n])
                # Skip tested coordinates outside of the image
                if perp_coord[0] >= 1000 or perp_coord[1] >= 1000:
                    continue
                # Skip coordinates inside a "gray region" surrounding the image
                if np.round(f[perp_coord[0],perp_coord[1]],decimals=8) == 1.1016595:
                    continue
                intensities.append(f[perp_coord[0],perp_coord[1]])

            # Get local minima along direction 1
            # We want to increase if the intensities are less than the original intensity, but are greater than 
            # the median_loop intensity * intensity_limit. See intensity_limits.py
            local_minima = argrelextrema(np.array(intensities), np.less)[0]
            if local_minima.size == 0: # this can happen if the minima are at the list extrema
                # If the 0th extrema intensity is less than the following element, and also less than 
                # the origin point intensity (maximum intensity), increase width
                if intensities[0] < intensities[1] and intensities[0] < orig_intensity:
                    width += 1

            # Otherwise, increase width if intensity is both greater than the origin intensity and greater than
            # the median_intensity*intensity_limit (see intensity_limits.py)
            else:
                if intensities[local_minima[0]] < orig_intensity and intensities[local_minima[0]] > median_loop_intensity*intensity_limit_frac:
                    width += local_minima[0]+1

            intensities = []
            for n in range(-1,-6,-1):
                perp_coord = coord+np.array([dxp*n,dyp*n])
                # Skip tested coordinates outside of the image
                if perp_coord[0] >= 1000 or perp_coord[1] >= 1000:
                    continue
                # Skip coordinates inside a "gray region" surrounding the image
                if np.round(f[perp_coord[0],perp_coord[1]],decimals=8) == 1.1016595:
                    continue
                intensities.append(f[perp_coord[0],perp_coord[1]])

            # Get local minima along direction 2
            # We want to increase if the intensities are less than the original intensity, but are greater than 
            # the median_loop intensity * intensity_limit. See intensity_limits.py
            local_minima = argrelextrema(np.array(intensities), np.less)[0]
            if local_minima.size == 0: # this can happen if the minima are at the list extrema
                # If the 0th extrema intensity is less than the following element, and also less than 
                # the origin point intensity (maximum intensity), increase width
                if intensities[0] < intensities[1] and intensities[0] < orig_intensity:
                    width += 1

            # Otherwise, increase width if intensity is both greater than the origin intensity and greater than
            # the median_intensity*intensity_limit (see intensity_limits.py)
            else:
                if intensities[local_minima[0]] < orig_intensity and intensities[local_minima[0]] > median_loop_intensity*intensity_limit_frac:
                    width += local_minima[0]+1

        coord_set["width"] = width

# Calculate global averages here
total_widths = []
total_lengths = []
total_intensities = []
for key in data_dict.keys():
    widths = []
    length = 0
    intensities = []
    for coord_set in data_dict[key]:
        widths.append(coord_set["width"])
        length = coord_set["length"] # Last length is the only one we care about in each coord set
        intensities.append(coord_set["intensity"])
    total_widths.append(np.mean(widths))
    total_lengths.append(length)
    total_intensities.append(np.mean(intensities))

print("Average width: {} pixels".format(np.mean(total_widths)))
print("Average length: {} pixels".format(np.mean(total_lengths)))
print("Average loop intensity: {}".format(np.mean(total_intensities)))

# 5. Export to CSV (results/results.csv)
file_path = 'results/mapping_results.csv'

# Python dictionaries are unordered by default; sort it here.
ordered_data = OrderedDict(sorted(data_dict.items()))

with open(file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Loop', 'x', 'y', 'Length', 'Intensity', 'Width'])
    for loop in ordered_data.keys():
        for coord_set in data_dict[loop]:
            writer.writerow([loop, coord_set['x'], coord_set['y'], coord_set['length'], coord_set['intensity'], coord_set['width']])

print("Results written to {}".format(file_path))