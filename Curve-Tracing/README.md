# Curve Tracing

This script is designed to manually trace features in solar images. Note that purpose is an arbitrary idea - the program is designed to trace lines, so you can really use it for anything. 

## Prerequisites

You need a few packages to get started. Install them with
```
python -m pip install numpy scipy astropy matplotlib
```
> **Note**: your Python version *must* be 3.5<. You can find this out with the console command `python --version`.  

For Mac users, run the command `brew install python-tk` to install Python with tkinter support. 

## Running

You may use either an IDL .sav file, or a .fits file for this script. The program is run with the following arguments:

```
python image-tracing.py <image-path> [x-offset] [y-offset] [coordinates-file]
```
* The image path is the absolute or relative path to your .fits or .sav file
* If the image is a slice of another image, the x-offset can be indicated to the x-offset of the origin as compared to the original image. (*optional*)
* The y-offset is the offset of the origin relative to an original image. (*optional*)
* The coordinates file can be used to load saved data. Supply as an absolute or relative path. 

A typical example, loading data from a saved coordinate grid and a given image with zero offset,

```
python image-tracing.py TRACE_19980519.fits 0 0 coordinates-2021-06-24-11:06:25.csv
```
or, with just the image, no offset:
```
python image-tracing.py TRACE_19980519.fits
```

## Usage

After running the program and opening the image, your workflow will generally look like:
1. Hold shift and click to plot points on a curve.
2. Release shift once you are finished plotting your curve.
3. Repeat steps 1 and 2 for all curves. 
4. Once finished, hit the *Enter* key to save the coordinates of each point, and length of each curve, to two files within the `data` directory: **coordinates.csv** and **characteristics.csv**. 

The structure of **coordinates.csv** is described below:
| Curve number | X Point Coordinate (pixels) | Y Point Coordinate (pixels) |
| ------------ | --------------------------- | ---------------------------- |
| 0 | 341.21 | 551.23 |
| 0 | 321.51 | 451.23 |
| 1 | ... | ... |

And so on. **characteristics.csv** has a header which describes it's internal content. 

## Mac Steps
The `matplotlib` library is currently a little bugged on MacOSX Big Sur, so we have an additional file for it. Use `image-tracing-mac` if you're on OSX. 

See [Issue #20486](https://github.com/matplotlib/matplotlib/issues/20486) for more details.
