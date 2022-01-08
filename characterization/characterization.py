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
for key in coords.keys():
    for coordpair in coords[key]:
        x = int(coordpair[0])
        y = int(coordpair[1])
        intensity = core_map[y,x]
        velocity = vel_map[y,x]
        coords[key] = np.array([coordpair[0],coordpair[1],intensity,velocity])
        #np.append(coords[key],np.array([intensity,velocity]))
print(coords)

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