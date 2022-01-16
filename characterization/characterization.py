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
import sys
import numpy as np
import cv2
from scipy.io import readsav
from matplotlib import pyplot as plt
from collections import OrderedDict
from os.path import exists

# Parse command line arguments
parser = argparse.ArgumentParser(description="Characterize fibrils on a coordinate-by-coordinate basis. ")
parser.add_argument('coordinate_file', help='OCCULT-2 coordinates file')
parser.add_argument('sav_file', help='ha sav file')
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
# for key in coords.keys():
#     coord_info = []
#     for coordpair in coords[key]:
#         x = int(coordpair[0])
#         y = int(coordpair[1])
#         intensity = core_map[y,x]
#         velocity = vel_map[y,x]
#         coord_info.append([coordpair[0],coordpair[1],intensity,velocity])
#     coords[key] = coord_info

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

# Create a much sharpened image, then blur it a bit to get rid of noise
wm_sharp = unsharp_mask(width_map_cv2, amount=10.0)
wm_sharp_gauss = cv2.GaussianBlur(wm_sharp, (5,5), 8.0)

edges = cv2.Canny(wm_sharp_gauss, threshold1=260, threshold2=280, apertureSize=7)
overlay = cv2.addWeighted(width_map_cv2, 0.7, edges, 0.4,0)

# Test if Canny boundaries match OCCULT-identified fibrils
fig, ax = plt.subplots()
plt.imshow(overlay, origin='lower')
for key in coords.keys():
     x = coords[key][:,0]
     y = coords[key][:,1]
     plt.scatter(x,y, 1.0, '#ff0000')
plt.show()

# This works really well. More noise than others, but edges clearly defined. 

# LSD test - this works really well, alternative to OCCULT-2
#lsd = cv2.createLineSegmentDetector(0)
#lines = lsd.detect(width_map_cv2_blur)[0] #Position 0 of the returned tuple are the detected lines
#drawn_img = lsd.drawSegments(width_map_cv2,lines)
#plt.imshow(drawn_img, origin="lower")
#plt.show()
#cv2.waitKey(0)

# # Test coordinate alignment
# fig, ax = plt.subplots(figsize=(15,15)) # 15 inch by 15 inches
# plt.imshow(core_map, origin="lower")
# for key in coords.keys():
#     x = coords[key][:,0]
#     y = coords[key][:,1]
#     plt.scatter(x,y)
#     plt.plot(x,y)
#     fig.canvas.draw()
# plt.show()