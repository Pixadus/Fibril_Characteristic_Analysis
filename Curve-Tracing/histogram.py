#!/usr/bin/python3
import matplotlib.pyplot as plt
import csv
import numpy as np
from scipy import stats

"""
Opens characteristics.csv, reads the lengths and then generates a histogram of them. 
"""

charfile = "characteristics-parker-2021-06-25-11.csv"
lengths = np.array([0])

with open("data/"+charfile, newline='') as datafile:
    datareader = csv.reader(datafile, delimiter=',')
    for row in datareader:
        if row[1] == '':
            continue
        if 'Loop' in row[0]:
            continue
        lengths = np.append(lengths,np.array([float(row[1])]))

plt.hist(lengths, bins=53)
plt.xlabel("Length")
plt.ylabel("Number")
plt.title("Histogram of Loop Lengths")
plt.grid(True)
plt.show()