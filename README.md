# Python Scripts for Studying and Characterizing Fibrils

These are some scripts I designed for characterizing chromospheric fibrils for the Boulder Solar Alliance 2021 program, working with Dr. Gianna Cauzzi and Dr. Kevin Reardon. 

Note, that these scripts generally work hand-in-hand with the OCCULT-2 loop recognition program, by Markus Aschwanden. You can find more information on this script, including downloading and installation, [from this blog post](https://blog.andromeda.is/posts/week-2-plotting-occult2/). 

## Workflow

1. Manually trace lines or loops in your image (see the curve-tracing/ folder)
2. Use the Optimization/ folder to generate an optimized parameter set for OCCULT-2 (see optimization/ folder)
3. Determine breath and intensity for each pixel coordinate (see characterization/ folder)
4. Analyze the mapping results to find correlations (see the analysis/ folder)

Data, images and results are available in the data/ folder. 