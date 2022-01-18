#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Fri 12.31.21
@title: Characterization
@author: Parker Lamb
@description: Script used to characterize OCCULT-2 identified fibrils, including core intensity,
breadth and velocity values for each coordinate point on each fibril. 
@usage: "python characterization.py <occult-coordinates-file> <Ha.sav file>"
"""

import argparse
from contextlib import suppress
import sys
import numpy as np
import csv
import cv2
from scipy.__config__ import show
from scipy.io import readsav
from matplotlib import pyplot as plt
from collections import OrderedDict
from os.path import exists

# Modify numpy print options
np.set_printoptions(suppress=True)

# Disable if you don't want to visualize width calculations
show_width_calculations = True

# Parse command line arguments
parser = argparse.ArgumentParser(description="Characterize fibrils on a coordinate-by-coordinate basis. ")
parser.add_argument('coordinate_file', help='OCCULT-2 coordinates file')
parser.add_argument('sav_file', help='ha sav file')
parser.add_argument('output_file', help='where to store characteristic info')
args = parser.parse_args()

# Test validity of command line arguments
if not exists(args.coordinate_file):
    sys.exit("Coordinate file not found")
if not exists(args.sav_file):
    sys.exit("Save file not found")

# Read in the sav file
sav = readsav(args.sav_file)
core_map = sav['halpha_coreint']
width_map = sav['halpha_width']
vel_map = sav['halpha_vel']

# Numpy array indices are [y,x]. No further transformations necessary.

# Convert OCCULT-2 coordinates file to an OrderedDict
coords = OrderedDict()
with open(args.coordinate_file, newline='') as csvfile:
    for line in csvfile.readlines():
        line = ' '.join(line.split())
        line = line.split(" ")
        num = int(float(line[0]))
        x = float(line[1])
        y = float(line[2])
        try:
            coords[num]
        except KeyError:
            coords[num] = np.array([])
        if np.size(coords[num]) == 0:
            coords[num] = np.array([[x,y]])
        else:
            coords[num] = np.append(coords[num], [np.array([x,y])], axis=0)
        # Structure of coords is: {fibril_id: np.array([x,y],[x,y], ...)}

# Get intensity and velocity on a per-coordinate basis
for key in coords.keys():
    coord_info = []
    for coordpair in coords[key]:
        x = int(coordpair[0])
        y = int(coordpair[1])
        intensity = core_map[y,x]
        velocity = vel_map[y,x]
        coord_info.append([coordpair[0],coordpair[1],intensity,velocity])
    coords[key] = np.array(coord_info)

# Getting the breadth of each fibril. 
## This technique will sharpen the image, slightly smooth out noise, then run cv2.Canny
## on the result to identify edges.

def unsharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
    """Return a sharpened version of the image, using an unsharp mask."""
    # From https://codingdeekshi.com/python-3-opencv-script-to-smoothen-or-sharpen-input-image-using-numpy-library/
    blurred = cv2.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred
    sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
    sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
    sharpened = sharpened.round().astype(np.uint8)
    if threshold > 0:
        low_contrast_mask = np.absolute(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)
    return sharpened

width_map_cv2 = width_map*325
width_map_cv2 = width_map_cv2.astype(np.uint8)

# Create a sharpened image, then blur it a bit to get rid of noise
wm_sharp = unsharp_mask(width_map_cv2, amount=10.0)
wm_sharp_gauss = cv2.GaussianBlur(wm_sharp, (5,5), 8.0)

edges = cv2.Canny(wm_sharp_gauss, threshold1=260, threshold2=280, apertureSize=7)

# Test if Canny boundaries match OCCULT-identified fibrils
# overlay = cv2.addWeighted(width_map_cv2, 0.7, edges, 0.4,0)
# fig, ax = plt.subplots()
# plt.imshow(overlay, origin='lower')
# for key in coords.keys():
#     x = coords[key][:,0]
#     y = coords[key][:,1]
#     plt.plot(x,y,markersize=1,linewidth=1, color='#ff0000')
# plt.show()

# REMOVE Set up test --
overlay = cv2.addWeighted(width_map_cv2, 0.7, edges, 0.4,0)
plt.imshow(overlay, origin='lower')
for key in coords.keys():
    x = coords[key][:,0]
    y = coords[key][:,1]
    plt.plot(x,y,markersize=1,linewidth=1, color='#ff0000')
# --

# Calculate breadth of fibril
keys = list(coords)
for key in coords.keys():
    # Get a list of all coordinates in the fibril
    coordinfo = list(coords[key])
    coordinfo_new = list()
    # Counter to display every nth width segment
    wctr = 0
    for coord in coordinfo:
        wctr +=1
        # Get next and previous coordinates
        nextcoord = next((i for i, val in enumerate(coordinfo) if np.all(val == coord)), -1)+1
        prevcoord = next((i for i, val in enumerate(coordinfo) if np.all(val == coord)), -1)-1
        if nextcoord > len(coordinfo)-1:
            nextcoord = len(coordinfo)-1
        if prevcoord < 0:
            prevcoord = 0
        nextcoord = coordinfo[nextcoord]
        prevcoord = coordinfo[prevcoord]
        # Calculate the slope at the coordinate
        dx = nextcoord[1]-prevcoord[1]
        dy = nextcoord[0]-prevcoord[0]
        v = np.array([dx,dy])
        # Get perpendicular vector
        dp = np.empty_like(v)
        dp[0] = -v[1]
        dp[1] = v[0]
        # Convert to unit vector
        mag = np.sqrt(dp[0]**2+dp[1]**2)
        dp[0] = dp[0]/mag
        dp[1] = dp[1]/mag
        # Array indices must be integers, rounding
        dp[0] = round(dp[0])
        dp[1] = round(dp[1])
        # Variables to store x and y displacement vectors for width visualization
        xs = []
        ys = []
        # Move in positive dp until we hit a Canny-identified edge
        bp= 0
        coord_offset = np.array([round(coord[1]),round(coord[0])])
        while edges[coord_offset[0],coord_offset[1]] == 0:
            bp+=1
            xs.append(coord_offset[0])
            ys.append(coord_offset[1])
            coord_offset[0] = coord_offset[0]+dp[0]
            coord_offset[1] = coord_offset[1]+dp[1]
        # Move in negative dp until we hit a Canny-identified edge
        bn = 0
        coord_offset = np.array([round(coord[1]),round(coord[0])])
        while edges[coord_offset[0],coord_offset[1]] == 0:
            bn+=1
            xs.append(coord_offset[0])
            ys.append(coord_offset[1])
            coord_offset[0] = coord_offset[0]-dp[0]
            coord_offset[1] = coord_offset[1]-dp[1]
        if (wctr % 2) == 0 and show_width_calculations:
            plt.plot(ys,xs,markersize=1,linewidth=1, color='#a09516')
        # Add width to coord characteristics
        coord = np.append(coord,np.array([bp+bn]))
        coordinfo_new.append(coord)
        # TODO compare with previous coordinate width. If significantly larger, (i.e. 4 -> 12), set to previous
        # coordinate width. 
    coords[key] = coordinfo_new
if show_width_calculations:
    plt.show()

# Write to CSV
with open(args.output_file, "w", newline='') as outfile:
    writer = csv.writer(outfile)
    for key in coords.keys():
        for coord in coords[key]:
            writer.writerow([key,coord[0],coord[1],coord[2],coord[3],coord[4]])