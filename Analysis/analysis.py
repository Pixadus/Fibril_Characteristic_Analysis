# -*- coding: utf-8 -*-
"""
Created on Mon July 26 2021

@author: Parker Lamb
@description: Looks at results from ../Mapping/; generates comparison plots, to
              determine if correlation between values exists. 
"""
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict

# 1. Open results file (csv format), read in rows to a dict. 
file_path = sys.argv[1]

# Initialize value dictionary as
# {loop1: [{"x":x,"y":y,"length":length,"intensity": intensity, "width":width},{x,y,length,intensity,width}, ... ]}
data_dict = OrderedDict()

with open(file_path, newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        # Check if on the first row; skip it if so. 
        if 'Loop' in row[0]:
            continue
        loop = int(row[0])
        data = {"x": float(row[1]), "y": float(row[2]), "length": float(row[3]), "intensity": float(row[4]), "width": int(row[5])}
        # Check if the current loop exists in the data_dict, and insert data
        try:
            data_dict[int(row[0])]
            data_dict[loop].append(data)
        # If not, create it and insert data
        except KeyError:
            data_dict[loop] = [data]

# 2. Generate plots for averages
average_widths = []
average_lengths = []
average_intensities = []

for loop in data_dict.keys():
    total_length = 0
    avg_width = []
    avg_intensity = []
    for coord_set in data_dict[loop]:
        total_length = coord_set["length"] # Last coord_set in list contains the total length
        avg_width.append(coord_set["width"])
        avg_intensity.append(coord_set["intensity"])
    average_lengths.append(total_length)
    average_widths.append(np.mean(avg_width))
    average_intensities.append(np.mean(avg_intensity))

# Length vs width
plt.xlabel('Average widths')
plt.ylabel('Average lengths')
plt.scatter(average_widths, average_lengths)
plt.savefig('results/width-vs-length.png')
plt.clf()

# Length vs intensity
plt.xlabel('Average intensity')
plt.ylabel('Average lengths')
plt.scatter(average_intensities, average_lengths)
plt.savefig('results/intensity-vs-length.png')
plt.clf()

# Width vs intensity
plt.xlabel('Average widths')
plt.ylabel('Average intensities')
plt.scatter(average_widths, average_intensities)
plt.savefig('results/width-vs-intensity.png')
plt.clf()

# -- a. Avg length versus avg width
# -- b. Avg length versus avg intensity
# -- c. Avg width versus avg intensity
# 3. Individual fibril analysis