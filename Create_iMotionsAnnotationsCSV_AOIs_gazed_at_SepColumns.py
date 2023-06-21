import os
import pandas as pd
import numpy as np

# SCRIPT FUNCTION: 
# Creates iMotions Annotations CSV file based on iMotions Raw Sensor Data CSV file 
# Sensor data export must be MERGED with "Show separate AOI columns per Stimulus" checked 
# This script iterates through each Respondent in the merged data, 
# then iterates through each Stimulus in the respondent's data
# and each AOI ("AOI NAME gaze at on STIMULUS NAME" data columns) 
#
# iMotions Annotations CSV headers/columns/format: 
# 1. Respondent Name
# 2. Stimulus Name
# 3. Marker Type
# 4. Marker Name
# 5. Start Time (ms)
# 6. End Time (ms)
# 7. Comment
# 8. Color

# REQUIRED INPUT FILE:
# "merged_datafile" - Merged raw sensor data CSV file exported from iMotions
merged_datafile = 'ExportMerge_CEZ_sepearatecolumns.csv'

# REQUIRED INPUT PARAMTERS:
CSV_fileout_Annotations = 'iMotionsAnnotations_CEZ.csv'
Marker_Type = 'Respondent Annotation'
Comment = ''
Color = '#FF0000'
AOI_NotGazedFlag = 'None'

# Initialize components lists for Annotations
Annotations = list()

# Automatically count the number of header rows in sensor data export
# (number of header rows depends on the number of respondents)
df_temp = pd.read_csv(merged_datafile)
header_rows = df_temp[df_temp[df_temp.columns[0]]=='Row'].index[0]

df_rawdata = pd.read_csv(merged_datafile, skiprows=header_rows)

respondent_array = df_rawdata.Respondent.unique()

for respondent in respondent_array:    
    print('STARTING ANNOTATIONS FOR ' + respondent)
    # Get respondent data from merged sensor data
    df_respdata = df_rawdata[df_rawdata.Respondent==respondent]    
    # Remove slide event rows
    df_respdata = df_respdata[pd.isnull(df_respdata['EventSource'])]
    
    # Get list of unique stimuli (to iterate through)
    resp_stimulus_array = df_respdata.SourceStimuliName.unique()     
    
    for stim in resp_stimulus_array:
        # Get data for this stimulus from respondent data 
        df_respstimdata = df_respdata[df_respdata.SourceStimuliName==stim]
        
        
        # Get 'AOI gazed at' data for this stimulus/respondent
        df_aoi_gazed_at_on_stim = df_respstimdata[df_respstimdata.columns[df_respstimdata.columns.str.contains(' gazed at on '+stim)]]
        
        # Replace NaNs with 'None' to facilitate analysis
        df_aoi_gazed_at_on_stim = df_aoi_gazed_at_on_stim.replace(np.nan, AOI_NotGazedFlag, regex=True)
        #aoi_names = df_aoi_gazed_at_on_stim.columns.str.replace(' gazed at on '+stim, '')
        
        # Iterate through stimulus AOIs (i.e. "aoi gazed at" columns)
        for column in df_aoi_gazed_at_on_stim.columns:
            aoi_gazed_at = df_aoi_gazed_at_on_stim[column]
            aoi_gazed_at_changes = aoi_gazed_at.ne(aoi_gazed_at.shift().bfill()).astype(int)
            aoi_gazed_at_changes_indices = aoi_gazed_at_changes[aoi_gazed_at_changes==1].index
            #print('OK')
            
            I = range(len(aoi_gazed_at_changes_indices))
            for i in I:
                temp_respondent = respondent
                temp_stimname = stim
                temp_markertype = Marker_Type
                temp_markername = column #stim #+ ' gazed at' #df_respstimdata['AOIs gazed at'][respstim_AOIchanges_indices[i]]
                temp_starttime = df_respstimdata['Timestamp'][aoi_gazed_at_changes_indices[i]]

                temp_comment = Comment
                temp_color = Color
                
                # Accomodate final change
                if i==I[-1]: #len(respstim_AOIchanges_indices):                
                    # Accomodate last change (What is the EndTime for the final Annotation?)
                    temp_endtime = df_respstimdata['Timestamp'][df_respstimdata.index[-1]]
                else:
                    temp_endtime = df_respstimdata['Timestamp'][aoi_gazed_at_changes_indices[i+1]]
                
                # Ignore annotations with the same start and end time (e.g. a single, final sample on an AOI)
                if temp_starttime != temp_endtime:
                    temp_annotation = [temp_respondent, temp_stimname, temp_markertype, temp_markername, temp_starttime, temp_endtime, temp_comment, temp_color]            
                    Annotations.extend([temp_annotation])
                    
            print('Done with ' + column)
        print('Done with ' + stim)
    print ('Done with ' + respondent)

####################################################  
### AFTER ITERATING THROUGH MERGED SENSOR DATA EXPORT:
# FORMAT FOR IMOTIONS ANNOTATIONS AND PRINT TO CSV
dfa = pd.DataFrame(Annotations, columns = ['Respondent Name', 'Stimulus Name', 'Marker Type', 'Marker Name', 'Start Time (ms)', 'End Time (ms)', 'Comment', 'Color'])
dfa.to_csv(CSV_fileout_Annotations, index=False)    
    
print('DONE')