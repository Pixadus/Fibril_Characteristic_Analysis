#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Mon 6.5.22
@title: Curve Tracing
@author: Parker Lamb
@description: Module which can be used to manually and automatically trace out curvilinear features.
@usage: todo
"""

import sunkit_image.trace
from astropy.io import fits

class AutoTracing:
    def __init__(self, image_path):
        """
        Autotracing class which acts as a wrapper for sunkit's OCCULT-2 implementation to 
        trace out curvilinear features on an image. 

        Each AutoTracing instance should act on a single image. 

        Parameters
        ----------
        image_path : str
            Path to the image containing features to trace. Image must be in .fits format.
        """

        # Test if file is a FITS file
        if ".fits" in image_path:
            f = fits.open(self.path, ignore_missing_end=True)
            self.img_data = f[0].data
        else:
            raise Exception("Did not detect .fits extension in image path.")

    
    def run(self, nsm1=4, rmin=45, lmin=35, nstruc=2000, ngap=1, qthresh1=0, qthresh2=3):
        """
        Run OCCULT-2 with given parameters. 

        Parameters
        ----------
        nsm1 : int (opt)
            Low pass (freq < cutoff freq) filter boxcar smoothing constant
        rmin : int (opt)
            Minimum feature radius of curvature, in pixels
        lmin : int (opt)
            Minimum feature length, in pixels
        nstruc : int (opt)
            Maximum number count of structures
        ngap : int (opt)
            Number of per-feature pixels below threshold
        qthresh1 : float (opt)
            Ratio of image base and median flux. All pixels below qthresh1 * median intensity = 0
        qthresh2 : float (opt)
            Factor which determines noise in image - intensities below qthresh2 * median are noise

        Returns
        -------
        list
            List of features, with a list of coordinates per feature
        """

        features = sunkit_image.trace.occult2(
            self.img_data, 
            nsm1, 
            rmin, 
            lmin, 
            nstruc, 
            ngap, 
            qthresh1, 
            qthresh2
            )
        
        return(features)
    
    def save(self, features, save_path):
        """
        Save features in a list to a .csv file.

        Parameters
        ----------
        features : list
            List of features and their coordinates returned by AutoTracing.run()
        save_path : str
            Path to save the .csv containing features to
        """