# Python Scripts for Studying and Characterizing Fibrils

These are some scripts I designed for characterizing chromospheric fibrils for the Boulder Solar Alliance 2021 program, working with Dr. Gianna Cauzzi and Dr. Kevin Reardon. 

Note, that these scripts generally work hand-in-hand with the OCCULT-2 loop recognition program, by Markus Aschwanden. You can find more information on this script, including downloading and installation, [from this blog post](https://blog.andromeda.is/posts/week-2-plotting-occult2/). 

## Workflow

1. Manually trace lines or loops in your image (see the Curve-Tracing/ folder)
2. Automatically trace lines or loops, using OCCULT-2 (see the blog post linked above)
3. Compare manual tracings with automatic tracings to optimize your OCCULT-2 parameters (see the Histogram/ folder)
4. Map the OCCULT-2 calculated values to the original image (see the Mapping/ folder)
5. Analyze the mapping results to find correlations (see the Analysis/ folder)