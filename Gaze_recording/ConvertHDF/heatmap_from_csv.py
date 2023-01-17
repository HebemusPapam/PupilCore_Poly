# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 12:54:26 2023

@author: marion
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

data_path = "C:/Users/marion/Documents/Gaze_recording/ConvertHDF/"
file      = "Users_BinocularEyeSampleEvent.csv"
filename  = data_path + file

# read as pandas dataframe
data = pd.read_csv(filename)

# convert pandas arrays to no arrays
x = data['left_gaze_x'].to_numpy()
y = data['left_gaze_y'].to_numpy()

# remove nan values
x = x[~np.isnan(x)]
y = y[~np.isnan(y)]

# plot x and y values as a heat map
heatmap, xedges, yedges = np.histogram2d(x, y, bins=50)
extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

# show the plot
plt.clf()
plt.imshow(heatmap.T, extent=extent, origin='lower')
plt.show()