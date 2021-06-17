#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Wed 5.6.21
@title: Curve Tracing
@author: Parker Lamb
@description: Script used to manually trace out curvilinear features. Data is saved to coordinates.csv,
containing coordinate information for individual points, and characteristics.csv, containing info
(number and length) on each traced feature. 
@usage: To trace a curve, hold shift and click to add points. Release and press shift again to trace
another curve. Hit the enter key to save your data to the files indicated above. 
"""
# Reference: https://learn.astropy.org/FITS-images.html
import matplotlib.pyplot as plt
import numpy as np
import csv
from astropy.io import fits
from collections import OrderedDict

class Coordinates:
    ## Setup
    def __init__(self,path,datafile=None):
        self.path = path              # Image path
        self.datafile = datafile          # Already-existing data to use. Optional.
        self.num = 0                  # nth curve. Incremements whenever shift is released
        self.coords=  OrderedDict()   # We're storing our coordinates as {num: np.array([x1,y1],[x2,y2])}
        self.coords[0] = np.array([]) # Initialize the 0th curve array
        self.shift = False          # Is the shift key currently pressed?
        self.fig, self.ax = plt.subplots(figsize=(15,15)) # 15 inch by 15 inches
        # Four parameters: number, x coordinate, y coordinate, is shift pressed
        f = fits.open(self.path)
        # Color maps available at https://matplotlib.org/stable/tutorials/colors/colormaps.html
        im = self.ax.imshow(f[0].data, cmap="afmhot", origin="lower", vmin="0", vmax="700")
        # Events, such as mouse click, and button press/release.
        self.cidclick = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.cidpress = self.fig.canvas.mpl_connect('key_press_event', self.key_press)
        self.cidrelease = self.fig.canvas.mpl_connect('key_release_event', self.key_release)
        if self.datafile:
            self.plot_data()
        plt.show()

    ## Operation: whenever shift is held (either), and a click is detected, a point
    ## will be plotted. After shift key is released, the curve trace is complete, and 
    ## you can continue on to another curve. 
    def onclick(self, event):
        # Function will process all clicks on the figure canvas
        self.ix, self.iy = event.xdata, event.ydata
        if self.shift:
            # If the size of the array is zero, initialize it. Otherwise, just append to it.
            if np.size(self.coords[self.num]) == 0:
                self.coords[self.num] = np.array([[self.ix,self.iy]])
            else:
                self.coords[self.num] = np.append(self.coords[self.num], [np.array([self.ix,self.iy])], axis=0)
            # We store coordinates in a numpy array. 
            x = self.coords[self.num][:,0]
            y = self.coords[self.num][:,1]
            self.ax.scatter(x,y)
            self.ax.plot(x,y)
            self.fig.canvas.draw()

    # Note: keys must be pressed one at a time. 
    def key_press(self,event):
        if event.key == "shift":
            self.shift = True
        if event.key == "enter":
            self.save_to_files()
    def key_release(self,event):
        if event.key == "shift":
            self.num+=1
            self.shift = False
            self.coords[self.num] = np.array([])

    def save_to_files(self):
        self.coords.pop(self.num) # Last number will always have 0 entries
        # Save data to coordinates.csv and characteristics.csv in the local directory.
        try: 
            with open('coordinates.csv', 'w', newline='') as coordfile:
                coordwriter = csv.writer(coordfile)
                for key in self.coords.keys():
                    for coord in self.coords[key]:
                        coordwriter.writerow([key, coord[0], coord[1]])
            print("Coordinates saved to coordinates.csv")
        except Exception as e:
            print("Error writing to coordinates.csv: {}".format(e))

        try:
            with open('characteristics.csv', 'w', newline='') as charfile:
                charwriter = csv.writer(charfile)
                charwriter.writerow(["Loop Number", "Length (px)"])
                for key in self.coords.keys():
                    length = 0
                    self.prevcoord=np.array([])
                    for coord in self.coords[key]:
                        if self.prevcoord.size == 0:
                            self.prevcoord = coord
                        else:
                            length+=np.abs(np.linalg.norm(coord-self.prevcoord))
                            self.prevcoord = coord
                    print(key, length)
                    charwriter.writerow([key,length])
            print("Characteristics saved to characteristics.csv")
        except Exception as e:
            print("Error writing to characteristics.csv: {}".format(e))
        self.coords[self.num] = np.array([])
    
    def plot_data(self):
        # If we already have data stored in a CSV, we can supply it as an optional argument to be plotted.
        with open(self.datafile, newline='') as datafile:
            datareader = csv.reader(datafile, delimiter=',')
            for row in datareader:
                try:
                    self.coords[int(row[0])]
                except KeyError:
                    self.coords[int(row[0])] = np.array([])
                if np.size(self.coords[int(row[0])]) == 0:
                    self.coords[int(row[0])] = np.array([[float(row[1]),float(row[2])]])
                else:
                    self.coords[int(row[0])] = np.append(self.coords[int(row[0])], [np.array([float(row[1]),float(row[2])])], axis=0)
                self.num = int(row[0])
                x = self.coords[self.num][:,0]
                y = self.coords[self.num][:,1]
                self.ax.scatter(x,y)
                self.ax.plot(x,y)
            self.fig.canvas.draw()
            print(self.num)
            self.num+=1
            self.coords[self.num] = np.array([])


if __name__ == "__main__":
    # If we're running this program directly from the command line
    fits_file = "TRACE_19980519.fits"
    datafile = "coordinates.csv"
    Coordinates(fits_file, datafile)