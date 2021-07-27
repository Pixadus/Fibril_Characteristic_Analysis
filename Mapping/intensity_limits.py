# -*- coding: utf-8 -*-
"""
Created on Fri July 23 2021

@author: Parker Lamb
@description: Analyzes image intensities by creating x-and-y slices across the entire image,
              looking for maxima and minima. Returns a percentage, which is the average percentage
              minima are of maxima.
"""
import matplotlib.pyplot as plt
import sys
from astropy.io import fits
import scipy.io as sio
from scipy.signal import argrelextrema
import numpy as np
import matplotlib.pyplot as plt

def get_intensity_limit(picture_path):
    """
    Evaluates the average image-wide difference between all local maxima and minima of intensity,
    to put constraints on max widths. Measures vertical differences first, then horizontal. 
    Inputs
    ------
    picture_path : string
        Path to the picture in .sav or .fits file formats.
    Returns
    -------
    image_difference : float
        Average difference between maxima and minima image-wide.
    """
    # 1. Open picture file

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

    # 2. Takes a slice along each vertical line across the entire image, then each horizontal. 
    #    Get local maxima and minima across line

    image_differences = []
    for line in range(np.shape(f)[0]):
        slice = f[:,line]
        slice_maxima = argrelextrema(slice, np.greater)[0]
        slice_minima = argrelextrema(slice, np.less)[0]

        # 3. Calculate the average percent difference between the maxs and the mins on the horizontal
        # 
        # NOTE if calculated difference between max and min is 2% or less, we discard it. 
        # This is because OCCULT-2 will not detect such extremely dim fibrils, so is just noise to the width measurements.

        differences = []
        for max, min in zip(slice_maxima,slice_minima):
            difference = slice[min]/float(slice[max])
            if difference < 0.98 and not np.isnan(difference):
                differences.append(difference)
        if len(differences) != 0:
            image_differences.append(np.mean(differences))
    for line in range(np.shape(f)[1]):
        slice = f[line,:]
        slice_maxima = argrelextrema(slice, np.greater)[0]
        slice_minima = argrelextrema(slice, np.less)[0]

        # 3. Calculate the average percent difference between the maxs and the mins on the vertical
        # 
        # NOTE if calculated difference between max and min is 2% or less, we discard it. 
        # This is because OCCULT-2 will not detect such extremely dim fibrils, so is just noise to the width measurements.

        differences = []
        for max, min in zip(slice_maxima,slice_minima):
            difference = slice[min]/float(slice[max])
            if difference < 0.98 and not np.isnan(difference):
                differences.append(difference)
        if len(differences) != 0:
            image_differences.append(np.mean(differences))
    
    return(np.mean(image_differences))


if __name__ == "__main__":
    picture_path = sys.argv[1]
    print(get_intensity_limit(picture_path))