# -*- coding: utf-8 -*-
"""
Created on Wed July 07 2021

@author: Parker Lamb
@description: generates a histogram of OCCULT-2 lengths for different parameters.
"""
import matplotlib.pyplot as plt
from os import listdir
import csv
import re
import numpy as np

def Histogram():
    """
    Opens files in the data/IDL/ directory, reads their lengths, and creates histograms out of them. We'll have one histogram per file, so the number of subplots is the number of files in data/IDL/. Note, the contents of data/IDL/ must ONLY contain usable data files. 

    Inputs
    ---
    - Files in data/IDL/ directory, with name structure 'Halpha-NxRyLzGk.dat', such as 'Halpha-N5R30L25G3.dat'.

    Outputs:
    ---
    - n x m image of histograms in a matplotlib window, with n being the span of NSM1 values, and m the span of NGAP values
    """
    files = listdir("data/IDL/")

    # Get the number of columns - i.e. the range of used NSM1 values
    nsm1 = []
    for filename in files:
        slice = filename[8:9]
        nsm1.append(int(slice))
    columns = max(nsm1)-min(nsm1)+1

    # Get the number of columns - i.e. the range of used NGAP values
    ngap = []
    for filename in files:
        slice = filename[16:17]
        ngap.append(int(slice))
    rows = max(ngap)-min(ngap)+1

    # Create matplotlib subplots
    fig, axes = plt.subplots(nrows=rows,ncols=columns)


    # Generate histograms
    for filename in files:
        row = int(filename[16:17])-1
        col = int(filename[8:9])-3
        t1 = float(filename[19:23])
        t2 = int(filename[22:23])
        print(filename, col, row)
        lengths = ReadDat(filename)
        axes[row][col].hist(lengths, bins=53)
        axes[row][col].set_xlim(left=0,right=220)
        axes[row][col].set_xlabel("Length")
        axes[row][col].set_xlabel("Number")
        axes[row][col].set_title("Histogram of Lengths, N%d, G%d, T1%.2f, T2%s, A%.2f, Z%d" % (col+3, row+1, t1, t2, np.average(lengths), lengths.size))
    fig.tight_layout()
    plt.show()

def ReadDat(file):
    """
    Opens the OCCULT-2 data file, then reads in x and y values. Calculates lengths for each traced loop. 

    Inputs
    ---
    file : string
        Name of file to read from data/IDL/ directory. 

    Outputs
    ---
    lengths : float
        Length of the fibril in pixels
    """
    # Open the file
    with open("data/IDL/"+file, newline='') as datafile:

        # Coordinates are stored in a numpy arrray
        coords = {0: np.array([])}

        # The CSV reader allows us to reuse code from image-tracing.py
        for row in datafile:
            # Remove extra whitespace, and replace with commas. 
            row = re.sub('\s+',',',row)
            row = row.split(",")
            row.pop(0)
            if row[1] == '' or row[2] == '':
                continue
            try:
                coords[int(round(float(row[0])))]
            except KeyError:
                coords[int(round(float(row[0])))] = np.array([])
            if np.size(coords[int(round(float(row[0])))]) == 0:
                coords[int(round(float(row[0])))] = np.array([[float(row[1]),float(row[2])]])
            else:
                coords[int(round(float(row[0])))] = np.append(coords[int(round(float(row[0])))], [np.array([float(row[1]),float(row[2])])], axis=0)

        # Calculate the lengths of each curve
        lengths = np.array([])
        for key in coords.keys():
            length = 0
            prevcoord=np.array([])
            for coord in coords[key]:
                if coord.any() == False:
                    pass
                if prevcoord.size == 0:
                    prevcoord = coord
                else:
                    length+=np.abs(np.linalg.norm(coord-prevcoord))
                    prevcoord = coord
            if lengths.size == 0:
                lengths = np.array([length])
            else:
                lengths = np.append(lengths, length)
        return(lengths)
if __name__ == "__main__":
    Histogram()