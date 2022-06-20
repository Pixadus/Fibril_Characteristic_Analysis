# Characterization

For all OCCULT-2 fibril coordinates, this script will identify corresponding:

1. Intensity values from coreint map
2. Breadth values (how wide the fibril is)
3. Doppler velocity values (from velocity map)

A new dataset with corresponding values will be generated in data/occult_results, of the format "file-name-characteristics.csv". 

## Usage

`characterization.py coordinate_file sav_file output_file`, where:

* The `coordinate_file` is the list of fibrils and their coordinates returned by OCCULT-2 
* The `sav_file` is the IDL .sav file containing the Halpha width, velocity and core intensity maps
* The `output_file` is a .csv file where we return our data

```python3 characterization.py data/occult_results/occult_output.dat data/images/sav/Halpha_cropped.sav data/characteristics/characteristics.csv```

## Output

`characteristics.csv` will contain, on a per-coordinate basis, data about:

* fibril_id, x, y, intensity, velocity, width (from width_map), calculated breadth

The script will also return plaintext data about the fibril count and averages for each above qualitative value. 
