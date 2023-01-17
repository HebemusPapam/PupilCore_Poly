# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 12:39:29 2023

@author: marion
"""

import h5py
import pandas as pd

data_path = "C:/Users/marion/Documents/Gaze_recording/ExplorationImgCoder/data/"
file = "ExploIMG_PupilCore_m_001.hdf5"

filename = data_path + file

id = filename.split("/")[1].split("_")[0]
with h5py.File(filename, "r") as f:

    # get the list of eyetracker measures available in the hdf5
    eyetracker_measures = list(f['data_collection']['events']['eyetracker'])

    for measure in eyetracker_measures:
        print('Extracting events of type: ', measure)
        data_collection = list(f['data_collection']['events']['eyetracker'][measure])
        if len(data_collection)>0:
            column_headers = data_collection[0].dtype.descr
            cols = []
            data_dict = {}
            for ch in column_headers:
                cols.append(ch[0])
                data_dict[ch[0]] = []

            for row in data_collection:
                for i, col in enumerate(cols):
                    data_dict[col].append(row[i])
            pd_data = pd.DataFrame.from_dict(data_dict)
            pd_data.to_csv(id+'_'+measure+'.csv', index = False)
        else:
            print('No data for type', measure, ' moving on')
            
        # get the list of eyetracker measures available in the hdf5
        event_measures = list(f['data_collection']['events']['experiment'])

    for measure in event_measures:
        print('Extracting events of type: ', measure)
        data_collection = list(f['data_collection']['events']['experiment'][measure])
        if len(data_collection)>0:
            column_headers = data_collection[0].dtype.descr
            cols = []
            data_dict = {}
            for ch in column_headers:
                cols.append(ch[0])
                data_dict[ch[0]] = []

            for row in data_collection:
                for i, col in enumerate(cols):
                       data_dict[col].append(row[i])
            pd_data = pd.DataFrame.from_dict(data_dict)
            pd_data.to_csv(id+'_'+measure+'.csv', index = False)
        else:
            print('No data for type', measure, ' moving on')