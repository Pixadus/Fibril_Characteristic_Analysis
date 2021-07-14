# -*- coding: utf-8 -*-
"""
Created on Wed July 07 2021

@author: Parker Lamb
@description: generates a histogram of manual measurements.
"""
import matplotlib.pyplot as plt
from os import listdir
import csv
import re
import numpy as np

def Histogram():
    """
    Opens a coordinates.csv file in data/, reads it's x and y coordinates, computes lengths, and generates a histogram. 

    Inputs
    ---
    - Manually generated coordinates.csv file in data/ 

    Outputs:
    ---
    - histogram opened in matplotlib window
    """
    files = listdir("data/")

    # Get the name of the coordinates file
    fn = []
    for filename in files:
        if "coordinate" in filename:
            fn.append(filename)

    # Create matplotlib subplot
    fig, axes = plt.subplots()

    # Generate histograms
    for filename in fn:
        lengths = ReadDat(filename)
        axes.hist(lengths, bins=53)
        axes.set_xlabel("Length")
        axes.set_xlabel("Number")
        axes.set_title("Manual Tracing Histogram of Lengths, A%.2f, Z%d" % (np.average(lengths), lengths.size))
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
    with open("data/"+file, newline='') as datafile:

        # Coordinates are stored in a numpy arrray
        coords = {0: np.array([])}

        # The CSV reader allows us to reuse code from image-tracing.py
        for row in datafile:
            # Remove extra whitespace, and replace with commas. 
            row = row.split(",")
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