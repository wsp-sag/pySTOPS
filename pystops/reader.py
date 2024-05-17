from io import StringIO

import numpy as np
import pandas as pd
import os

class TableDef:

    def __init__(self, table_id, end_table_tag, skip_rows=0, skip_column=0, widths=None,
                 df_drop_top_rows=None, df_drop_tail_rows=None, reset_header=False, drop_row=None, read_row=None, drop_column = None,
                 rename_columns=None, add_columns=None, add_columns_vals=None, remove_char_column=None, remove_char_column_str = None, convert_numerics=False, int_columns=None, remove_str=None,
                 index_col=None, melt_id_var=None, melt_value_var=None, melt_var_name=None, melt_value_name=None
                 ):
        self.table_id = table_id
        self.end_table_tag = end_table_tag
        self.skip_rows = skip_rows
        self.widths = widths
        self.df_drop_top_rows = df_drop_top_rows
        self.df_drop_tail_rows = df_drop_tail_rows
        self.drop_row = drop_row
        self.read_row = read_row
        self.drop_column = drop_column
        self.reset_header = reset_header
        self.rename_columns = rename_columns
        self.add_columns = add_columns
        self.add_columns_vals = add_columns_vals
        self.remove_char_column =  remove_char_column
        self.remove_char_column_str = remove_char_column_str
        self.convert_numerics = convert_numerics
        self.int_columns = int_columns
        self.index_col = index_col
        self.remove_str = remove_str
        self.melt_id_var = melt_id_var
        self.melt_value_var = melt_value_var
        self.melt_var_name = melt_var_name
        self.melt_value_name = melt_value_name


_table_parameters = {
    '1.01': TableDef('1.01', end_table_tag = 'Control Filename', skip_rows=2, df_drop_top_rows=1,
                     reset_header=False,
                     rename_columns={'Run Parameters': 'Scenario', 'Unnamed: 1': 'temp1', 'Unnamed: 2': 'temp2', 'Unnamed: 3': 'Year'}, 
                     int_columns=['Year'],
                     drop_column = ['temp1', 'temp2'],
                     remove_char_column = 'Scenario',
                     remove_char_column_str = 'Year:',
                     convert_numerics=False),

    #Station Listing
    '1.02': TableDef('1.02', end_table_tag = ' Adjustment of', skip_rows=3, df_drop_top_rows=1,
                     df_drop_tail_rows=4, reset_header=False,
                     rename_columns=None, convert_numerics=False, 
                     int_columns=['BoardCount'],
                     index_col=None),
                     
    #Station Group Boardings Prior to Adjustment
    '2.04': TableDef('2.04', end_table_tag = 'COUNT', skip_rows=10, df_drop_top_rows=1,
                     df_drop_tail_rows=2, rename_columns={'Unnamed: 0': 'origin'},
                     index_col = 'origin', convert_numerics=True,
                     ),

    #Station Group Boarding Factor for Application to Later Iterations
    '2.05': TableDef('2.05',end_table_tag='-----------', skip_rows=5,
                     df_drop_top_rows=1,df_drop_tail_rows=1,
                     rename_columns={'Unnamed: 0': 'origin'}, index_col='origin',
                     convert_numerics=True),
    
    #Type 10/12 Group-Level Calibration Summary-Stations/Stops
    '2.07': TableDef('2.07', end_table_tag='-----------', skip_rows=8, # 'df_drop_top_rows': 1,
                     df_drop_tail_rows=1, reset_header=True, widths=[7, 11, 11, 11, 11],
                     rename_columns={0: 'station_group',
                                     1: 'pre_calib_board',
                                     2: 'station_count',
                                     3: 'station_target',
                                     4: 'post_calib_board'},
                    convert_numerics=True,int_columns='station_group', index_col='station_group'),

    #Type 11/12 Group-Level Calibration Summary-Station/Route Summary
    '2.08': TableDef('2.08', end_table_tag='Number of unique', skip_rows=8, # 'df_drop_top_rows': 1,
                     df_drop_tail_rows=1, reset_header=True, widths=[6, 22, 11, 11, 11, 10],
                     rename_columns={
                        0: 'route_group_num',
                        1: 'route_group',
                        2: 'pre_calib_board',
                        3: 'route_count',
                        4: 'route_target',
                        5: 'post_calib_board'
                    }, convert_numerics=True, #'int_columns': 'station_group',
                    index_col='route_group_num'),
                    
    #Station Group to Station Group Ridership-Existing
    '3.01': TableDef('3.01', end_table_tag='TOTAL', skip_rows=8,
                     df_drop_top_rows=1, index_col='origin',
                     rename_columns={'Unnamed: 0': 'origin'}),
                     
    #Station Group to Station Group Ridership-No-Build
    '3.02': TableDef('3.02', end_table_tag='TOTAL', skip_rows=8,
                     df_drop_top_rows=1, index_col='origin',
                     rename_columns={'Unnamed: 0': 'origin'}),
                     
    #Station Group to Station Group Ridership-Build
    '3.03': TableDef('3.03', end_table_tag='TOTAL', skip_rows=8,
                     df_drop_top_rows=1, index_col='origin',
                     rename_columns={'Unnamed: 0': 'origin'}),
                     
    # Weekday Linked District-to-District Transit Trips
    '4.01': TableDef('4.01', end_table_tag='Total', skip_rows=5,
                    df_drop_top_rows=1,
                    rename_columns={'Idist': 'origin'},
                    melt_id_var = ['origin'],
                    melt_var_name = 'destination',
                    melt_value_name = 'Transit Trip'),
                    
    # Weekday Incremental Linked Dist-to-Dist Transit Trips               
    '4.02': TableDef('4.02', end_table_tag='Total', skip_rows=5,
                    df_drop_top_rows=1,
                    rename_columns={'Idist': 'origin'},
                    melt_id_var = ['origin'],
                    melt_var_name = 'destination',
                    melt_value_name = 'Transit Trip'),
                    
    # Weekday Linked District-to-District Project Trips            
    '4.03': TableDef('4.03', end_table_tag='Total', skip_rows=5,
                    df_drop_top_rows=1,
                    rename_columns={'Idist': 'origin'},
                    melt_id_var = ['origin'],
                    melt_var_name = 'destination',
                    melt_value_name = 'Transit Trip'),
                    
    # Weekday Unlinked Station-to-Station Project Trips              
    '4.04': TableDef('4.04', end_table_tag='Total', skip_rows=5,
                    df_drop_top_rows=1,
                    rename_columns={'Unnamed: 0': 'origin'},
                    melt_id_var = ['origin'],
                    melt_var_name = 'destination',
                    melt_value_name = 'Transit Trip'),
                    
    #Incremental District-to-District Vehicle PMT
    '8.01': TableDef('8.01', end_table_tag='Total', skip_rows=5,
                     df_drop_top_rows=1, 
                     rename_columns={'Idist': 'origin'},
                     melt_id_var = ['origin'],
                     melt_var_name = 'destination',
                     melt_value_name = 'Incremental PMT'),

    # Average Weekday Station Boardings by Mode of Access
    '9.01': TableDef('9.01', end_table_tag='\x00', skip_rows=8,
                     reset_header=True,
                     rename_columns={0: 'stop_id', 1: 'station_name',
                                     2: 'EXST_wlk', 3: 'EXST_knr', 4: 'EXST_pnr', 5: 'EXST_xfr', 6: 'EXST_all',
                                     7: 'NOBL_wlk', 8: 'NOBL_knr', 9: 'NOBL_pnr', 10: 'NOBL_xfr', 11: 'NOBL_all',
                                    12: 'BLD_wlk', 13: 'BLD_knr', 14: 'BLD_pnr', 15: 'BLD_xfr', 16: 'BLD_all',},
                     int_columns=['EXST_wlk','EXST_knr', 'EXST_pnr', 'EXST_xfr', 'EXST_all',
                                  'NOBL_wlk', 'NOBL_knr', 'NOBL_pnr', 'NOBL_xfr', 'NOBL_all',
                                  'BLD_wlk', 'BLD_knr', 'BLD_pnr', 'BLD_xfr', 'BLD_all'],
                     melt_id_var = ['stop_id','station_name'],
                     melt_value_var = ['EXST_wlk','EXST_knr', 'EXST_pnr', 'EXST_xfr', 'EXST_all',
                                       'NOBL_wlk', 'NOBL_knr', 'NOBL_pnr', 'NOBL_xfr', 'NOBL_all',
                                       'BLD_wlk', 'BLD_knr', 'BLD_pnr', 'BLD_xfr', 'BLD_all'],
                     melt_var_name = 'Type',
                     melt_value_name = 'Transit Trip'),

    # Average Weekday Route Boardings by Zone (Production-End) Access Type
    '10.01': TableDef('10.01', end_table_tag='               Total', skip_rows=7,
                      reset_header=True, widths=[25, 30] + [10] * 13, df_drop_top_rows=1,
                      rename_columns={0: 'route_id', 1: 'route_name', 2: 'route_count',
                                      3: 'EXST_wlk', 4: 'EXST_knr', 5: 'EXST_pnr', 6: 'EXST_all',
                                      7: 'NOBL_wlk', 8: 'NOBL_knr', 9: 'NOBL_pnr', 10: 'NOBL_all',
                                      11: 'BLD_wlk', 12: 'BLD_knr', 13: 'BLD_pnr', 14: 'BLD_all',},
                      int_columns=['route_count',
                                   'EXST_wlk', 'EXST_knr', 'EXST_pnr', 'EXST_all',
                                   'NOBL_wlk', 'NOBL_knr', 'NOBL_pnr', 'NOBL_all',
                                   'BLD_wlk', 'BLD_knr', 'BLD_pnr', 'BLD_all',],
                      melt_id_var = ['route_id','route_name','route_count'],
                      melt_value_var = ['EXST_wlk', 'EXST_knr', 'EXST_pnr', 'EXST_all',
                                        'NOBL_wlk', 'NOBL_knr', 'NOBL_pnr', 'NOBL_all',
                                        'BLD_wlk', 'BLD_knr', 'BLD_pnr', 'BLD_all'],
                      melt_var_name = 'Type',
                      melt_value_name = 'Transit Trip'),
                     
    #PEAK TRIPS, MILES AND HOURS BY ROUTE                 
    '10.03': TableDef('10.03', end_table_tag='                                                  Total', skip_rows=8, remove_str="--",
                      reset_header=True, widths=[25,30,7,13,13,7,13,13,7,13,13], df_drop_top_rows=1,
                      rename_columns={0: 'route_id', 1: 'route_name',
                                      2: 'EXST_trips', 3: 'EXST_miles', 4: 'EXST_hours',
                                      5: 'NOBL_trips', 6: 'NOBL_miles', 7: 'NOBL_hours',
                                      8: 'BLD_trips', 9: 'BLD_miles', 10: 'BLD_hours',},
                      melt_id_var = ['route_id','route_name'],
                      melt_var_name = 'Service',
                      melt_value_name = 'Measurements'),        

    #OFFPEAK TRIPS, MILES AND HOURS BY ROUTE                 
    '10.04': TableDef('10.04', end_table_tag='                                                  Total', skip_rows=8, remove_str="--",
                      reset_header=True, widths=[25,30,7,13,13,7,13,13,7,13,13], df_drop_top_rows=1,
                      rename_columns={0: 'route_id', 1: 'route_name',
                                      2: 'EXST_trips', 3: 'EXST_miles', 4: 'EXST_hours',
                                      5: 'NOBL_trips', 6: 'NOBL_miles', 7: 'NOBL_hours',
                                      8: 'BLD_trips', 9: 'BLD_miles', 10: 'BLD_hours',},
                      melt_id_var = ['route_id','route_name'],
                      melt_var_name = 'Service',
                      melt_value_name = 'Measurements'),
    
    #Avgerage Weekday Route Boardings by Route Access Type
    '10.05': TableDef('10.05', end_table_tag='               Total', skip_rows=7, remove_str="--",
                      reset_header=True, widths=[25,30,9,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10], df_drop_top_rows=1,
                      rename_columns={0: 'route_id', 1: 'route_name',
                                      2: 'counts',
                                      3: 'EXST_WLK', 4: 'EXST_KNR', 5: 'EXST_PNR', 6: 'EXST_XFR', 7: 'EXST_ALL',
                                      8: 'NOBL_WLK', 9: 'NOBL_KNR', 10: 'NOBL_PNR', 11: 'NOBL_XFR', 12: 'NOBL_ALL',
                                      13: 'BLD_WLK', 14: 'BLD_KNR', 15: 'BLD_PNR', 16: 'BLD_XFR', 17: 'BLD_ALL',},                                      
                      melt_id_var = ['route_id', 'route_name', 'counts'],
                      melt_value_var = ['EXST_WLK', 'EXST_KNR', 'EXST_PNR', 'EXST_XFR', 
                                        'NOBL_WLK', 'NOBL_KNR', 'NOBL_PNR', 'NOBL_XFR',
                                        'BLD_WLK', 'BLD_KNR', 'BLD_PNR', 'BLD_XFR'],
                      melt_var_name = 'Scenario_MOA',
                      melt_value_name = 'Transit Trip'),
                               
    #Home-Based Work                 
    '11.01': TableDef('11.01', end_table_tag='. . . . . . .', skip_rows=6, 
                      reset_header=True, widths=[9,20,12,1,8,8,1,8,8,1,8,8,1,8,8,1], 
                      df_drop_top_rows=1, df_drop_tail_rows=1, drop_row=["-|All"],
                      rename_columns={0: 'hh_car', 1: 'sub_mode', 2: 'access_mode',
                                      3:'dh1', 4: 'EXST_model', 5: 'EXST_survey',
                                      6:'dh2', 7: 'NOBL_model', 8: 'NOBL_survey',
                                      9:'dh3', 10: 'BLD_model', 11: 'BLD_survey', 
                                      12:'dh4',13: 'BLD_pj_model', 14: 'BLD_pj_survey',},
                      add_columns = "Purpose",
                      add_columns_vals = "HBW",
                      melt_id_var = ['hh_car', 'sub_mode', 'access_mode', 'Purpose'],
                      melt_value_var = ['EXST_model', 'EXST_survey', 
                                        'NOBL_model', 'NOBL_survey',
                                        'BLD_model', 'BLD_survey', 
                                        'BLD_pj_model', 'BLD_pj_survey'],
                      melt_var_name = 'Scenario',
                      melt_value_name = 'Transit Trip'),
                     
    #Home-Based Other
    '11.02': TableDef('11.02', end_table_tag='. . . . . . .', skip_rows=6, 
                      reset_header=True, widths=[9,20,12,1,8,8,1,8,8,1,8,8,1,8,8,1], 
                      df_drop_top_rows=1, df_drop_tail_rows=1, drop_row=["-|All"],
                      rename_columns={0: 'hh_car', 1: 'sub_mode', 2: 'access_mode',
                                      3:'dh1', 4: 'EXST_model', 5: 'EXST_survey',
                                      6:'dh2', 7: 'NOBL_model', 8: 'NOBL_survey',
                                      9:'dh3', 10: 'BLD_model', 11: 'BLD_survey', 
                                      12:'dh4',13: 'BLD_pj_model', 14: 'BLD_pj_survey',},
                      add_columns = "Purpose",
                      add_columns_vals = "HBO",
                      melt_id_var = ['hh_car','sub_mode', 'access_mode', 'Purpose'],
                      melt_value_var = ['EXST_model', 'EXST_survey', 
                                        'NOBL_model', 'NOBL_survey',
                                        'BLD_model', 'BLD_survey', 
                                        'BLD_pj_model', 'BLD_pj_survey',],
                      melt_var_name = 'Scenario',
                      melt_value_name = 'Transit Trip'),

    #Non-Home Based
    '11.03': TableDef('11.03', end_table_tag='. . . . . . .', skip_rows=6, remove_str=['-','\|'], drop_row=["-|All"],
                      reset_header=True, widths=[9,20,12,1,8,8,1,8,8,1,8,8,1,8,8,1], df_drop_top_rows=1, df_drop_tail_rows=1,
                      rename_columns={0: 'hh_car', 1: 'sub_mode', 2: 'access_mode',
                                      3:'dh1', 4: 'EXST_model', 5: 'EXST_survey',
                                      6:'dh2', 7: 'NOBL_model', 8: 'NOBL_survey',
                                      9:'dh3', 10: 'BLD_model', 11: 'BLD_survey', 
                                      12:'dh4',13: 'BLD_pj_model', 14: 'BLD_pj_survey',
                                      15:'dh5',},
                      add_columns = "Purpose",
                      add_columns_vals = "NHB",
                      melt_id_var = ['hh_car','sub_mode', 'access_mode', 'Purpose'],
                      melt_value_var = ['EXST_model', 'EXST_survey', 
                                        'NOBL_model', 'NOBL_survey',
                                        'BLD_model', 'BLD_survey', 
                                        'BLD_pj_model', 'BLD_pj_survey'],
                      melt_var_name = 'Scenario',
                      melt_value_name = 'Transit Trip'),

    # Section 16
#    'SECTION 16': TableDef('SECTION 16', end_table_tag='',
#                            df_drop_tail_rows=2, skip_rows=1, read_row=11, df_drop_top_rows=1),   
    'SECTION 16': TableDef('SECTION 16', end_table_tag='------------------------------------------------------------------------------------------------',
                            df_drop_tail_rows=1, skip_rows=1, df_drop_top_rows=1),   
                            
    # Section 15
    'SECTION 15': TableDef('SECTION 15', end_table_tag='SECTION 16', index_col='CARS',
                            df_drop_tail_rows=2, skip_rows=2, df_drop_top_rows=1)                              
}
import pandas as pd

def get_table_15_lookups(table_15_path = 'table_15_types.csv', starting_col=3):
    
    table_15_lookups = pd.read_csv(table_15_path)
    table_15_lookups = table_15_lookups.fillna(method="ffill")

    columns = table_15_lookups.columns

    table_lookup_dicts = {}
    for index, row in table_15_lookups.iterrows():
        for table_num, mode in zip(row.iloc[starting_col:], columns[starting_col:]):
            table_lookup_dicts[str(table_num)] = list(row[:starting_col])
            # print(row.iloc[:starting_col])
            # table_15_lookups[table_num] = list()

    return table_lookup_dicts, table_15_lookups.columns[:starting_col]

def parse_table(result_file_path, table_label, path):
    def replace_dash(x):
        return 0 if x == '-' else x
    if table_label == "SECTION 16":
        raise NotImplementedError(
            "this has been depricated, refer to the read_16.py for updated logic")
        table_def = _table_parameters[table_label]
        start_table_tag_1 = table_label
        end_table_tag_1 = table_def.end_table_tag
        skip_rows_1 = table_def.skip_rows

        
        found_table_1 = False
        table_1 = StringIO('')
        
        with open(result_file_path, 'r', errors="replace") as result_file:
            for line_1 in result_file:
                if line_1.startswith(start_table_tag_1):
                    found_table_1 = True

                if found_table_1:
                    if line_1.startswith(end_table_tag_1):
                        found_table_1 = False
                    else:
                        table_1.write(line_1)
        table_1.seek(0)
        df_1 = pd.read_fwf(table_1, widths=None, skiprows=skip_rows_1, skip_blank_lines=True)
        
        # print(df_1)
#        df_1.to_csv('c:\df_1_old_1.csv')
        if table_def.df_drop_top_rows is not None:
            df_1 = df_1[table_def.df_drop_top_rows:]
#        df_1.to_csv('c:\df_1_old_2.csv')
        if table_def.df_drop_tail_rows is not None:
            df_1 = df_1[:-table_def.df_drop_tail_rows]
 #       df_1.to_csv('c:\df_1_old_3.csv')
        # print(df_1.columns.tolist())         
        # print(df_1.head())
 #       print(df_1["Table No."].tolist())

        i = 1 
        # print(df_1.columns)
        # print("Table No." in df_1.columns)
        # print(df_1.shape)
        # print(df_1)
        # print("--")
        # print(f'|{df_1["SCENARIO  Period"].iloc[0]}|')
        # print(df_1["SCENARIO  Period"].str.len())
        # absolute hack, sometimes the table is parsed incorrectly, we will fix it here
        # should probably consider giving this script a re-write
        if df_1.shape[1] == 1:
            delimiter_index = df_1[df_1['SCENARIO  Period  Table No.'].str.contains('==')].index[0]
            # Filter out rows after the delimiter
            df_1 = df_1.loc[:delimiter_index - 1]
            df_1["Table No."] = df_1.iloc[:, 0].str.split().str[-1]
            df_1["SCENARIO  Period"] = df_1['SCENARIO  Period  Table No.'].str.split("   1").str[0]
            # df_1["TA"]

        for index_table_2 in df_1["Table No."][:6]:
            start_table_tag_2 = 'Table{:>9s}\n'.format(index_table_2) 
            # print(start_table_tag_2)
            end_table_tag_2 = "number of tripgroupstops"
            skip_rows_2 = 3
            
            found_table_2 = False
            table_2 = StringIO('')   
            with open(result_file_path, 'r', errors="replace") as result_file:
                for line_2 in result_file:
                    if line_2.startswith(start_table_tag_2):
                        found_table_2 = True
                    if found_table_2:
                        if line_2.startswith(end_table_tag_2):
                            found_table_2 = False
                        else:
                            table_2.write(line_2)
            table_2.seek(0)

            df_2 = pd.read_fwf(table_2,skiprows=skip_rows_2, skip_blank_lines=True)
            df_2 = df_2[1:]
            df_2 = df_2.assign(SCENARIO_Period=df_1["SCENARIO  Period"][i])
#            print(type(df_2))
            # print(df_2.head(6))
            i = i + 1
            j = 1          
            for index_table_3 in df_2["Table No."]:
                start_table_tag_3 = 'Table{:>12s}\n'.format(index_table_3) 
#                print(start_table_tag_3)
                end_table_tag_3 = " *** Thru trips to next trip, this block"
                skip_rows_3 = 6
                widths_3=[10, 8, 26, 41, 10, 11, 12, 10]
                index_col_3 = ['Stop_seq', 'Stop_No', 'Stop_ID', 'Stop_Name', 'ROUTE', 'TRIP_ID', 'SCENARIO_Period']
                rename_columns_3={0: 'Stop_seq',
                                  1: 'Stop_No',
                                  2: 'Stop_ID',
                                  3: 'Stop_Name',
                                  4: 'Boards',
                                  5: 'Alights',
                                  6: 'Leave-Load',
                                  7: 'Cumulative'}
                df_drop_top_rows_3 = 2
               
                melt_id_var_3 = ['Stop_seq', 'Stop_No', 'Stop_ID', 'Stop_Name', 'ROUTE', 'TRIP_ID', 'SCENARIO_Period']
                melt_value_var_3 = ['Boards', 'Alights', 'Leave-Load']
                melt_var_name_3 = 'Activity'
                melt_value_name_3 = 'Number'
                
                found_table_3 = False
                table_3 = StringIO('')
                with open(result_file_path, 'r', errors="replace") as result_file:
                    for line_3 in result_file:
                        if line_3.startswith(start_table_tag_3):
                            found_table_3 = True

                        if found_table_3:
                            if line_3.startswith(end_table_tag_3):
                                found_table_3 = False
                            else:
                                table_3.write(line_3)
                table_3.seek(0) 
         
                df_3 = pd.read_fwf(table_3, widths=widths_3, skiprows=skip_rows_3, skip_blank_lines=True)
                df_3 = df_3[df_drop_top_rows_3:]
                df_3 = df_3.rename(columns=rename_columns_3)
                df_3 = df_3.assign(ROUTE = df_2["ROUTE"][j], TRIP_ID = df_2["TRIP_ID"][j], SCENARIO_Period = df_2["SCENARIO_Period"][j])
                # print(df_3.head(3))
                df_3 = df_3.melt(melt_id_var_3, melt_value_var_3, melt_var_name_3, melt_value_name_3)
                
                j = j + 1
                df_3.to_csv(os.path.join(path, r'Table_{}.csv'.format(index_table_3)),index=False)


    elif table_label == "SECTION 15":
        table_def = _table_parameters[table_label]
        start_table_tag_1 = table_label
        end_table_tag_1 = table_def.end_table_tag
        skip_rows_1 = table_def.skip_rows
        melt_id_var_1 = ['SCENARIO', 'PURPOSE', 'CARS']
        melt_value_var_1 = ['FGO-WLK', 'FGO-KNR', 'FGO-PNR', 
                            'FGB-WLK', 'FGB-KNR', 'FGB-PNR', 
                            'BUS-WLK', 'BUS-KNR', 'BUS-PNR']
        melt_var_name_1 = "Mode"
        melt_value_name_1 = "Table No."

        found_table_1 = False
        table_1 = StringIO('')
        with open(result_file_path, 'r', encoding='utf-8', errors='ignore') as result_file:
            for line_1 in result_file:
                if line_1.startswith(start_table_tag_1):
                    found_table_1 = True
                if found_table_1:
                    if line_1.startswith(end_table_tag_1):
                        found_table_1 = False
                    else:
                        table_1.write(line_1)
                        
        table_1.seek(0)
        df_1 = pd.read_fwf(table_1, widths=None, skiprows=skip_rows_1, skip_blank_lines=True)

        if table_def.df_drop_top_rows is not None:
            df_1 = df_1[table_def.df_drop_top_rows:]
        if table_def.df_drop_tail_rows is not None:
            df_1 = df_1[:-table_def.df_drop_tail_rows]   
            


        column_SCENARIO = ['EXST D2D Linked Trip', 'EXST S2S Total Flow', 
                       'NOBL D2D Linked Trip', 'NOBL S2S Total Flow', 
                       'BLD D2D Linked Trip', 'BLD Incremental Linked Trip', 'BLD Linked Trip on Project', 'BLD S2S Total Flow', 'BLD S2S Project Flow']
        column_PURPOSE = ['HBW', 'HNW', 'NHB', 'All']
        
        # print(df_1)
#        df_1.to_csv(os.path.join(path, r'Table_temp.csv'),index=False)  
           
        k = 0
        n = 16
        m = 4
        for k in range(0, len(df_1)):
            df_1["PURPOSE"][k+1] = column_PURPOSE[(int(k/m)-int(k/n)*m)]
            df_1["SCENARIO"][k+1] = column_SCENARIO[int(k/n)]
            k = k + 1       
            
        df_1 = df_1[df_1.CARS != 'All']
        df_1 = df_1[df_1.PURPOSE != 'All']
        df_1 = df_1[~df_1["SCENARIO"].str.contains('Flow')]
        df_1 = df_1.melt(melt_id_var_1, melt_value_var_1, melt_var_name_1, melt_value_name_1)   

        # print(df_1)
#        df_1.to_csv(os.path.join(path, r'Table_temp1.csv'),index=False)    
             
        i = 0     
        for index_table_2 in df_1["Table No."]:
            start_table_tag_2 = 'Table{:>9s}\n'.format(index_table_2) 
            end_table_tag_2 = "Total"
            skip_rows_2 = 5
            df_drop_top_rows_2 = 1
            rename_columns_2a = {'Idist': 'origin'}
            rename_columns_2b = {'Unnamed: 0': 'origin'}
            melt_id_var_2 = ['origin']
            melt_var_name_2 = 'destination'
            melt_value_name_2 = 'Transit Trip'
            
            found_table_2 = False    
            table_2 = StringIO('')            
            with open(result_file_path, 'r', errors="replace") as result_file:
                for line_2 in result_file:
                    if line_2.startswith(start_table_tag_2):
                        found_table_2 = True
                    if found_table_2:
                        if line_2.startswith(end_table_tag_2):
                            found_table_2 = False
                        else:
                            table_2.write(line_2)
            table_2.seek(0)
            
            df_2 = pd.read_fwf(table_2, widths=None, skiprows=skip_rows_2, skip_blank_lines = True)
            df_2 = df_2[df_drop_top_rows_2:]
            if df_2.columns[0] == "Idist":
                df_2 = df_2.rename(columns = rename_columns_2a)
            else:
                df_2 = df_2.rename(columns = rename_columns_2b)                
            df_2 = df_2.melt(melt_id_var_2,df_2.columns[len(melt_id_var_2):-1], melt_var_name_2, melt_value_name_2)           
            df_2 = df_2.assign(SCENARIO=df_1["SCENARIO"][i], PURPOSE=df_1["PURPOSE"][i], CARS=df_1["CARS"][i], Mode=df_1["Mode"][i])

            i = i + 1       
            df_2.to_csv(os.path.join(path, r'Table_{}.csv'.format(index_table_2)),index=False)    
            # print(start_table_tag_2)
            # print("Outputed")  
       
    else:
        table_def = _table_parameters[table_label]     
        start_table_tag = 'Table{:>9s}\n'.format(table_def.table_id)
        # print(start_table_tag)
        
        end_table_tag = table_def.end_table_tag
        skip_rows = table_def.skip_rows

        found_table = False
        table = StringIO('')

        with open(result_file_path, 'r', errors="replace") as result_file:
            for line in result_file:
                if line.startswith(start_table_tag):
                    found_table = True
                if found_table:
                    if line.startswith(end_table_tag):
                        found_table = False
                    else:
                        table.write(line)
        
        table.seek(0)
        df = pd.read_fwf(table, widths=table_def.widths, skiprows=skip_rows, skip_blank_lines=True)
        
        if table_def.df_drop_top_rows is not None:
            df = df[table_def.df_drop_top_rows:]
        if table_def.df_drop_tail_rows is not None:
            df = df[:-table_def.df_drop_tail_rows]
        if table_def.reset_header:
            columns = df.columns
            df.columns = np.arange(len(columns))
        if table_def.rename_columns is not None:
            df = df.rename(columns=table_def.rename_columns)
        if table_def.add_columns is not None:
            df = df.assign(new_column = table_def.add_columns_vals)
            df = df.rename(columns={"new_column": table_def.add_columns})
        if table_def.int_columns is not None or table_def.convert_numerics:
            df = df.applymap(np.vectorize(replace_dash))
        if table_def.int_columns is not None:
            df[table_def.int_columns] = df[table_def.int_columns].astype(np.int64)
        if table_def.index_col is not None:
            df = df.set_index(table_def.index_col)
        if table_def.convert_numerics:
            df = df.apply(pd.to_numeric)
        if table_def.drop_row is not None:
            for temp in table_def.melt_id_var:
                for words in table_def.drop_row: 
                    df = df[df[temp].str.contains(words)==False]
        if table_def.drop_column is not None:
            df = df.drop(table_def.drop_column,axis=1)
        if table_def.remove_char_column is not None:
            df[table_def.remove_char_column] = df[table_def.remove_char_column].str.strip(table_def.remove_char_column_str)
            
        # print(df.head(5))
        
        if table_def.melt_id_var is not None:
            if table_def.melt_value_var is None:
                df = df.melt(table_def.melt_id_var,df.columns[len(table_def.melt_id_var):], table_def.melt_var_name, table_def.melt_value_name)
            else:
                df = df.melt(table_def.melt_id_var, table_def.melt_value_var, table_def.melt_var_name, table_def.melt_value_name)
            

    #    result_file.close()
    #   print(result_file.closed)
        return df.copy()


    