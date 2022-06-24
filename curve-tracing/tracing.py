#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Mon 6.5.22
@title: Curve Tracing
@author: Parker Lamb
@description: Module which can be used to manually and automatically trace out curvilinear features.
@usage: todo
"""

import csv
from json import tool
import sys
import sunkit_image.trace
from astropy.io import fits
from PySide6.QtGui import (QAction, QIcon)
from PySide6.QtWidgets import (QApplication, QFileDialog, QMainWindow, QToolBar)


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
        
        self.path = image_path

        # Test if file is a FITS file
        if ".fits" in self.path:
            f = fits.open(self.path, ignore_missing_end=True)
            self.img_data = f[0].data
        else:
            raise Exception("Did not detect .fits extension in image path.")

    
    def run(self, nsm1=4, rmin=45, lmin=35, nstruc=2000, ngap=1, qthresh1=0, qthresh2=3):
        """
        Run OCCULT-2 with given parameters. 

        Parameters
        ----------
        nsm1 : int
            Low pass (freq < cutoff freq) filter boxcar smoothing constant
        rmin : int
            Minimum feature radius of curvature, in pixels
        lmin : int
            Minimum feature length, in pixels
        nstruc : int
            Maximum number count of structures
        ngap : int
            Number of per-feature pixels below threshold
        qthresh1 : float
            Ratio of image base and median flux. All pixels below qthresh1 * median intensity = 0
        qthresh2 : float
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

        with open(save_path, 'w', encoding='utf8') as savefile:
            savewriter = csv.writer(savefile)
            fibril_num = 1
            for fibril in features:
                fibril_num += 1
                for coord in fibril:
                    savewriter.writerow([fibril_num, coord[0], coord[1]])
    
class ManualTrace:
    def __init__(self, image_path=""):
        """
        Manual tracing class. 

        Parameters
        ----------
        image_path : str
            Path to the .fits file you want to manually trace.
        """
        
        # By default, no image is supplied.
        self.img_data = False

        # Test if file is a FITS file
        if ".fits" in image_path:
            f = fits.open(image_path, ignore_missing_end=True)
            self.img_data = f[0].data
    
    class Window(QMainWindow):
        def __init__(self):
            """
            Window widget, where we set up the application
            """
            super().__init__()

            self.setWindowTitle("Manual Feature Tracing")

            toolbar = QToolBar()
            self.addToolBar(toolbar)
            
            openAction = QAction(text="Open image", parent=self, triggered=self.open)
            toolbar.addAction(openAction)

            loadAction = QAction(text="Load data", parent=self, triggered=self.load)
            toolbar.addAction(loadAction)


        def open(self):
            """
            Open a file browser and select an image.
            """
            dialog = QFileDialog()
            # Only allow single, existing files
            dialog.setFileMode(QFileDialog.ExistingFile)
            # Image is a tuple of (path, file_type)
            image = dialog.getOpenFileName(self, "Open image", filter="FITS file (*.fits)")
        
        def load(self):
            """
            Open a .csv file containing previous data.
            """
            dialog = QFileDialog()
            # Only allow single, existing files
            dialog.setFileMode(QFileDialog.ExistingFile)
            # Image is a tuple of (path, file_type)
            data = dialog.getOpenFileName(self, "Open data", filter="CSV file (*.csv)")

    def run(self):
        """
        Run the manual tracing application.
        """
        app = QApplication([])
        window = self.Window()
        window.resize(800,600)
        window.show()

        sys.exit(app.exec())