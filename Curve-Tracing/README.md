# Curve Tracing

This script is designed to manually trace features in solar images, in .fits format. Note that purpose is an arbitrary idea - the program is designed to trace lines, so you can really use it for anything. 

## Usage

You must use a .fits image file for now. Within the `__main__` section of the program, there is a string called `fits_file`. Indicate the path to your fits file - you can use either a relative (i.e. `../file.fits`) path or an absolute (i.e. `/home/user/file.fits`) path. 

After running the program and opening the image, your workflow will generally look like:
1. Hold shift and click to plot points on a curve.
2. Release shift once you are finished plotting your curve.
3. Repeat steps 1 and 2 for all curves. 
4. Once finished, hit the *Enter* key to save the coordinates of each point, and length of each curve, to two files: **coordinates.csv** and **characteristics.csv**. 

The structure of **coordinates.csv** is described below:
| Curve number | X Point Coordinate (pixels) | Y Point Coordinate (pixels) |
| ------------ | --------------------------- | ---------------------------- |
| 0 | 341.21 | 551.23 |
| 0 | 321.51 | 451.23 |
| 1 | ... | ... |

And so on. **characteristics.csv** has a header which describes it's internal content. 