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
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import csv
import sys
import scipy.io as sio
from datetime import datetime
from astropy.io import fits
from collections import OrderedDict

matplotlib.use("TkAgg")

class Coordinates:
    ## Setup
    def __init__(self,path, x_off=0, y_off=0, datafile=None, ):
        self.path = path              # Image path
        self.datafile = datafile
        self.x_off = x_off
        self.y_off = y_off
        self.num = 0                  # nth curve. Incremements whenever shift is released
        self.coords =  OrderedDict()   # We're storing our coordinates as {num: np.array([x1,y1],[x2,y2])}
        self.coords[0] = np.array([]) # Initialize the 0th curve array
        self.shift = False          # Is the shift key currently pressed?
        self.fig, self.ax = plt.subplots(figsize=(15,15)) # 15 inch by 15 inches
        # Four parameters: number, x coordinate, y coordinate, is shift pressed
        if ".fits" in path:
            f = fits.open(self.path, ignore_missing_end=True)
            ext = [x_off, f[0].data.shape[0]+x_off, y_off, f[0].data.shape[1]+y_off]
            f = np.flipud(f) # IDL arrays appear vertically "flipped" to Python. We reset it here. 
            self.ax.imshow(f[0].data, cmap="ocean", vmin="0", vmax="700", extent=ext)
        elif ".sav" in path:
            f = sio.readsav(self.path)
            if len(f) > 1:
                n = 0
                print("Multiple images available in save. Choose the number that corresponds with the image you want.")
                for im_name in f.keys():
                    print("{}: {}".format(n,im_name))
                    n+=1
                opt = input("> ")
                f = f[list(f.keys())[int(opt)]]
                f = np.flipud(f) # IDL arrays appear vertically "flipped" to Python. We reset it here. 
                ext = [x_off, f.shape[0]+x_off, y_off, f.shape[1]+y_off]
                self.ax.imshow(f, cmap="ocean", vmin="0.99", vmax="1.25", extent=ext)
            else:
                f = f[list(f.keys())[0]]
                f = np.flipud(f) # IDL arrays appear vertically "flipped" to Python. We reset it here. 
                ext = [x_off, f.shape[0]+x_off, y_off, f.shape[1]+y_off]
                self.ax.imshow(f, extent=ext)
                # NOTE: the vmin and vmax values above should be modified to provide max contrast to image. Open plot options in image to find this. 
        # Color maps available at https://matplotlib.org/stable/tutorials/colors/colormaps.html
        # Events, such as mouse click, and button press/release.
        self.cidclick = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.cidpress = self.fig.canvas.mpl_connect('key_press_event', self.key_press)
        self.cidrelease = self.fig.canvas.mpl_connect('key_release_event', self.key_release)
        if self.datafile:
            self.plot_data()
        else:
            self.datafile = "coordinates-{}.csv".format(datetime.now().strftime("%Y-%m-%d-%H:%m:%S"))
        # Our characterfile will just be dependent on the naming of our coordfile, so we don't have to repeat logic. 
        self.characterfile="characteristics-{}.csv".format(self.datafile[self.datafile.find('-')+1:self.datafile.find('.')])
        print(self.characterfile)
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
        # Note: this does NOT work on MacOS. See: https://github.com/matplotlib/matplotlib/issues/20486
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
            with open("data/"+self.datafile, 'w', newline='') as coordfile:
                coordwriter = csv.writer(coordfile)
                for key in self.coords.keys():
                    for coord in self.coords[key]:
                        coordwriter.writerow([key, coord[0], coord[1]])
            print("Coordinates saved to {}".format("data/"+self.datafile))
        except Exception as e:
            print("Error writing to {}: {}".format("data/"+self.datafile, e))

        try:
            with open('data/'+self.characterfile, 'w', newline='') as charfile:
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
            print("Characteristics saved to data/"+self.characterfile)
        except Exception as e:
            print("Error writing to {}: {}".format(self.characterfile, e))
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

    if len(sys.argv) == 2:
        if sys.argv[1] == "--help":
            print("Usage: python image-tracing.py <image_name> [image offset x] [image offset y] [savefile_name]")
            sys.exit(0)
        Coordinates(sys.argv[1])
    elif len(sys.argv) == 4:
        Coordinates(sys.argv[1], x_off=int(sys.argv[2]), y_off=int(sys.argv[3]))
    elif len(sys.argv) == 5:
        Coordinates(sys.argv[1], x_off=int(sys.argv[2]), y_off=int(sys.argv[3]), datafile=sys.argv[4])
    elif len(sys.argv) == 6:
        Coordinates(sys.argv[1], x_off=int(sys.argv[2]), y_off=int(sys.argv[3]), datafile=sys.argv[4])
    else:
        print("Usage: python image-tracing.py <image_name> [image offset x] [image offset y] [savefile_name]")
        sys.exit(0)
