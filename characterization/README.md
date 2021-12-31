# Characterization

For all OCCULT-2 fibril coordinates, this script will identify corresponding:

1. Intensity values from coreint map
2. Breadth values (how wide the fibril is)
3. Doppler velocity values (from velocity map)

A new dataset with corresponding values will be generated in data/occult_results, of the format "file-name-characteristics.csv". 

## TODO

- [ ] Get intensity values from coreint map. Verify [250, 250] and [450, 250] values are the same in both IDL and Python, make necessary array
transformations if not. 
- [ ] Get velocity values from the velocity map. 
- [ ] Try to use Canny edge detection from OpenCV to detect edges, and hence find width. 