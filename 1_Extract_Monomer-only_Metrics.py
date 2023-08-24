#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Purpose: C
"""


# USER INPUTS ####################

# Provide file path to analysed data:
path = r'/Volumes/chem-mh-store.chem.ed.ac.uk-1/Horrocks/Outputs/Papers/STAPull paper/RelevantData/aSyn_Data/20230726_JL_STAPull_rebutal1_analysis/Analysis/'


# MAIN CODE ######################

# Import required libraries
import csv
import pandas as pd
import os


# Initialise empty dataframes to contain compiled data
dataSummary = pd.DataFrame()
descriptorAnalysis = pd.DataFrame()

# Iterate over folders and files
for folder in os.listdir(path):

    if not folder == '.DS_Store':
        for file in os.listdir(path + folder):

            # Identify data associated with a single FOV
            if file.endswith('Test-Results.csv') and not file.startswith('._'):
                print(folder + file)

                # Initialise CSV readers to read the CSV files
                with open(path + folder + '/' + file) as f:
                    freader = csv.reader(f)
                    with open(path + folder + '/' + file[0 : file.index("Test-Results.csv")] + "Transform-Results.csv") as ft:
                        ft_reader = csv.reader(ft)

                        # Check the number of rows in each CSV
                        f_row_count = sum(1 for row in freader)
                        ft_row_count = sum(1 for row in ft_reader)
                        
                        # Reset the CSV readers to read the first row after the column headers
                        f.seek(0)
                        ft.seek(0)
                        next(freader)
                        next(ft_reader)

                        # Skip the FOV if the CSV row count does not equal 2 in each case (indicates erroneous data)
                        if (f_row_count == 2) & (ft_row_count == 2):
                            for row in freader:
                                
                                # Check if the FOV produced no detections (5 column data) or at least one detection (7 column data)
                                if len(row) == 7 or len(row) == 5:
                                    
                                    # Read in the CSV file and rename the columns
                                    if len(row) == 7:
                                        appendRow = pd.DataFrame(row).transpose()
                                        appendRow.columns=['Slice', 'Frame', 'AF647_detections', 'AF488_detections', 'Coincident_detections', 'Percent_AF647_coincident', 'Percent_AF488_coincident']

                                   # In cases where no detections were found in either channel, CSV will have reduced columns. Populate such rows with zero. 
                                    elif len(row) == 5:
                                        appendRow = pd.DataFrame(columns = ['Slice', 'Frame', 'AF647_detections', 'AF488_detections', 'Coincident_detections', 'Percent_AF647_coincident', 'Percent_AF488_coincident'])
                                        appendRow.loc[0] = [1, 1, 0, 0, 0, "NaN", "NaN"]
                                        
                                    # Add and populate file/folder name columns
                                    appendRow.insert(0, 'File', [file])
                                    appendRow.insert(0, 'Folder', [folder])
    
                                    # Repeat for tranformed data
                                    for row in ft_reader:
                                        
                                       
                                        if len(row) == 7:
                                            controlRow = pd.DataFrame(row).transpose()                                                                             
                                            
                                            # Remove unnecessary columns and combine test and transform data into a single row
                                            controlRow = controlRow.drop(controlRow.columns[[0, 1, 2, 3]], axis=1)
                                            controlRow.columns = ['Chance_Coincident_detections', 'Percent_AF647_chance-coincident', 'Percent_AF488_chance-coincident'] 

                                        # If data had no detections (5 columns), set coincidence columns to 0
                                        elif len(row) == 5:
                                            controlRow = pd.DataFrame(columns = ['Chance_Coincident_detections', 'Percent_AF647_chance-coincident', 'Percent_AF488_chance-coincident'])
                                            controlRow.loc[0] = [0,0,0]
                                        appendRow = pd.concat([appendRow, controlRow], axis=1)

                                    
                                    # Add the row on to the bottom of the summary data table
                                    dataSummary = pd.concat((dataSummary, appendRow), axis = 0)
                               
    
                                else:
                                    print("ERROR - Incorrect table size, data excluded.")
                                    

                    # Import all descriptor data for the current FOV into a dataframe, use existing column names
                    try:
                        col_names = pd.read_csv(path + folder + '/' + file[0 : file.index("Test-Results.csv")] + "descriptors.csv", nrows=0).columns.tolist()
                        events = pd.read_table(path + folder + '/' + file[0 : file.index("Test-Results.csv")] + "descriptors.csv", sep=",", header=None, skiprows=[0])
                        events.columns = col_names
                    
                        # Filter for coincident events only
                        appendRows = events.loc[(events['ColocCh1'] == 0) | (events['ColocCh2'] == 0)] # For non-coincident events
                        
                        
                        # Remove unnecessary data columns
                        appendRows = appendRows.drop(appendRows.columns[[0, 1, 4, 5, 6, 14, 15, 16, 17, 18]], axis=1) # For coincident filtering
                        #appendRows = appendRows.drop(appendRows.columns[[0, 1, 4, 5, 6, 16, 17, 18]], axis=1) # For non-coincident filtering
                        
                        # Insert columns with relevant file/folder names
                        appendRows.insert(0, 'File', [file] * appendRows.shape[0])
                        appendRows.insert(0, 'Folder', [folder] * appendRows.shape[0])
                        
                        # Append new rows to the descriptor dataframe
                        descriptorAnalysis = pd.concat((descriptorAnalysis, appendRows), axis=0) 
                    except:
                        print("No detections to report from file")


# Rename column headers in data summary
dataSummary.columns=['Folder', 'File', 'Slice', 'Frame', 'AF647_detections', 'AF488_detections', 'Coincident_detections', 'Percent_AF647_coincident', 'Percent_AF488_coincident', 'Chance_Coincident_detections', 'Percent_AF647_chance-coincident', 'Percent_AF488_chance-coincident']

# Convert datatype of numberic columns to float
dataSummary[['AF647_detections', 'AF488_detections', 'Coincident_detections', 'Percent_AF647_coincident', 'Percent_AF488_coincident', 'Chance_Coincident_detections', 'Percent_AF647_chance-coincident', 'Percent_AF488_chance-coincident']] = dataSummary[['AF647_detections', 'AF488_detections', 'Coincident_detections', 'Percent_AF647_coincident', 'Percent_AF488_coincident', 'Chance_Coincident_detections', 'Percent_AF647_chance-coincident', 'Percent_AF488_chance-coincident']].apply(pd.to_numeric, errors='coerce')

# Compute and add columns containing values less the threshold (i.e. chance values)
dataSummary['thresholded_coincident_detections'] = dataSummary['Coincident_detections'] - dataSummary['Chance_Coincident_detections']
dataSummary['thresholded_percent_AF647_coincident'] = dataSummary['Percent_AF647_coincident'] - dataSummary['Percent_AF647_chance-coincident']
dataSummary['thresholded_percent_AF488_coincident'] = dataSummary['Percent_AF488_coincident'] - dataSummary['Percent_AF488_chance-coincident']

# Save dataframes as CSVs
descriptorAnalysis.to_csv(path + 'furtherdescriptors.csv', index=False)