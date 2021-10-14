from io import StringIO

import numpy as np
import pandas as pd


class TableDef:

    def __init__(self, table_id, end_table_tag, skip_rows=0, widths=None,
                 df_drop_top_rows=None, df_drop_tail_rows=None, reset_header=False,
                 rename_columns=None, convert_numerics=False, int_columns=None,
                 index_col=None
                 ):
        self.table_id = table_id
        self.end_table_tag = end_table_tag
        self.skip_rows = skip_rows
        self.widths = widths
        self.df_drop_top_rows = df_drop_top_rows
        self.df_drop_tail_rows = df_drop_tail_rows
        self.reset_header = reset_header
        self.rename_columns = rename_columns
        self.convert_numerics = convert_numerics
        self.int_columns = int_columns
        self.index_col = index_col


_table_parameters = {
    '1.02': TableDef('1.02', ' Adjustment of', skip_rows=3, df_drop_top_rows=1,
                     df_drop_tail_rows=4, reset_header=False,
                     rename_columns=None, convert_numerics=False, 
                     int_columns=['BoardCount'],
                     index_col=None),
    '2.04': TableDef('2.04', 'COUNT', skip_rows=10, df_drop_top_rows=1,
                     df_drop_tail_rows=2, rename_columns={'Unnamed: 0': 'origin'},
                     index_col = 'origin', convert_numerics=True,
                     ),

    '2.05': TableDef('2.05',end_table_tag='-----------', skip_rows=5,
                     df_drop_top_rows=1,df_drop_tail_rows=1,
                     rename_columns={'Unnamed: 0': 'origin'}, index_col='origin',
                     convert_numerics=True),

    '2.07': TableDef('2.07', end_table_tag='-----------', skip_rows=8, # 'df_drop_top_rows': 1,
                     df_drop_tail_rows=1, reset_header=True, widths=[7, 11, 11, 11, 11],
                     rename_columns={
                        0: 'station_group',
                        1: 'pre_calib_board',
                        2: 'station_count',
                        3: 'station_target',
                        4: 'post_calib_board'
                    },
                    convert_numerics=True,int_columns='station_group', index_col='station_group'),

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

    '3.01': TableDef('3.01', end_table_tag='TOTAL', skip_rows=8,
                     df_drop_top_rows=1, index_col='origin',
                     rename_columns={'Unnamed: 0': 'origin'}),

    '3.02': TableDef('3.02', end_table_tag='TOTAL', skip_rows=8,
                     df_drop_top_rows=1, index_col='origin',
                     rename_columns={'Unnamed: 0': 'origin'}),

    '3.03': TableDef('3.03', end_table_tag='TOTAL', skip_rows=8,
                     df_drop_top_rows=1, index_col='origin',
                     rename_columns={'Unnamed: 0': 'origin'}),

    '4.01': TableDef('4.01', end_table_tag='Total', skip_rows=5,
                    df_drop_top_rows=1,index_col='origin',
                    rename_columns={'Idist': 'origin'}),
    
    '4.04': TableDef('4.04', end_table_tag='Total', skip_rows=5,
                    df_drop_top_rows=1,
                    rename_columns={'Unnamed: 0': 'origin'}),

    '8.01': TableDef('8.01', end_table_tag='Total', skip_rows=5,
                     df_drop_top_rows=1, index_col='origin',
                     rename_columns={'Idist': 'origin'},
                     convert_numerics=True
                     ),

    # Stop Level Boardings
    '9.01': TableDef('9.01', end_table_tag='\x00', skip_rows=8,
                     reset_header=True,
                     rename_columns={
                         0: 'stop_id', 1: 'station_name',
                         2: 'exist_wlk', 3: 'exist_knr', 4: 'exist_pnr', 5: 'exist_xfr', 6: 'exist_all',
                         7: 'nb_wlk', 8: 'nb_knr', 9: 'nb_pnr', 10: 'nb_xfr', 11: 'nb_all',
                         12: 'bld_wlk', 13: 'bld_knr', 14: 'bld_pnr', 15: 'bld_xfr', 16: 'bld_all',
                     },
                     int_columns=['exist_wlk','exist_knr', 'exist_pnr', 'exist_xfr', 'exist_all',
                                  'nb_wlk', 'nb_knr', 'nb_pnr', 'nb_xfr', 'nb_all',
                                  'bld_wlk', 'bld_knr', 'bld_pnr', 'bld_xfr', 'bld_all']
                     ),

    # Route Ridership
    '10.01': TableDef('10.01', end_table_tag='               Total', skip_rows=7,
                      reset_header=True, widths=[25, 30] + [10] * 13, df_drop_top_rows=1,
                      rename_columns={
                          0: 'route_id', 1: 'route_name', 2: 'route_count',
                          3: 'exist_wlk', 4: 'exist_knr', 5: 'exist_pnr', 6: 'exist_all',
                          7: 'nb_wlk', 8: 'nb_knr', 9: 'nb_pnr', 10: 'nb_all',
                          11: 'bld_wlk', 12: 'bld_knr', 13: 'bld_pnr', 14: 'bld_all',
                      },
                      int_columns=[
                          'route_count',
                          'exist_wlk', 'exist_knr', 'exist_pnr', 'exist_all',
                          'nb_wlk', 'nb_knr', 'nb_pnr', 'nb_all',
                          'bld_wlk', 'bld_knr', 'bld_pnr', 'bld_all',
                      ]),

    #Existing - HBW - TRN - 0 Car
    '30.01': TableDef('30.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
    
    #Existing - HBW - TRN - 1 Car
    '51.01': TableDef('51.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
    
    #Existing - HBW - TRN - 2 Car
    '72.01': TableDef('72.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
                       
    #Existing - HBW - TRN - ALL
    '93.01': TableDef('93.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    #Existing - HBO - TRN - 0 Car
    '114.01': TableDef('114.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
    #Existing - HBO - TRN - 1 Car
    '135.01': TableDef('135.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
    
    #Existing - HBO - TRN - 2 Car
    '156.01': TableDef('156.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    #Existing - HBO - TRN - ALL
    '177.01': TableDef('177.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    #Existing - NHB - TRN - 0 Car
    '198.01': TableDef('198.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
    
    #Existing - NHB - TRN - 1 Car
    '219.01': TableDef('219.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
    
    #Existing - NHB - TRN - 2 Car
    '240.01': TableDef('240.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
                       
    #Existing - NHB - TRN - ALL
    '261.01': TableDef('261.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    #Existing - All Trips - TRN - 0 Car
    '282.01': TableDef('282.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
                       
    #Existing - All Trips - TRN - 1 Car
    '303.01': TableDef('303.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
                       
    #Existing - All Trips - TRN - 2 Car
    '324.01': TableDef('324.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
                
    #Existing - All Trips - TRN - ALL
    '345.01': TableDef('345.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # No Build - HBW - TRN - 0 Car
    '366.01': TableDef('366.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
    
    # No Build - HBW - TRN - 1 Car
    '387.01': TableDef('387.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
    
    # No Build - HBW - TRN - 2 Car
    '408.01': TableDef('408.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # No Build - HBW - TRN - ALL
    '429.01': TableDef('429.01', end_table_tag='Total', skip_rows=5,
                      df_drop_top_rows=1, index_col='origin',
                      rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # No Build - HBO - TRN - O Car
    '450.01': TableDef('450.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
    
    # No Build - HBO - TRN - 1 Car
    '471.01': TableDef('471.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
    
    # No Build - HBO - TRN - 2 Car
    '492.01': TableDef('492.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
    
    # No Build - HBO - TRN - ALL
    '513.01': TableDef('513.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # No Build - NHB - TRN - 0 Car
    '534.01': TableDef('534.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # No Build - NHB - TRN - 1 Car
    '555.01': TableDef('555.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # No Build - NHB - TRN - 2 Car
    '576.01': TableDef('576.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
    
    # No Build - NHB - TRN - ALL
    '597.01': TableDef('597.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # No Build - All Trips - TRN - 0 Car
    '618.01': TableDef('618.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
    # No Build - All Trips - TRN - 1 Car
    '639.01': TableDef('639.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
    # No Build - All Trips - TRN - 2 Car
    '660.01': TableDef('660.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
    # No Build - All Trips - TRN - ALL
    '681.01': TableDef('681.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # Build - HBW - TRN - 0 Car
    '702.01': TableDef('702.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # Build - HBW - TRN - 1 Car
    '723.01': TableDef('723.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # Build - HBW - TRN - 2 Car
    '744.01': TableDef('744.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
    
    # Build - HBW - TRN - ALL
    '765.01': TableDef('765.01', end_table_tag='Total', skip_rows=5,
                      df_drop_top_rows=1, index_col='origin',
                      rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # Build - HBO - TRN - 0 Car
    '786.01': TableDef('786.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # Build - HBO - TRN - 1 Car
    '807.01': TableDef('807.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # Build - HBO - TRN - 2 Car
    '828.01': TableDef('828.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # Build - HBO - TRN - ALL
    '849.01': TableDef('849.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # Build - NHB - TRN - 0 Car
    '870.01': TableDef('870.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # Build - NHB - TRN - 1 Car
    '891.01': TableDef('891.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # Build - NHB - TRN - 2 Car
    '912.01': TableDef('912.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # Build - NHB - TRN - ALL
    '933.01': TableDef('933.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # Build - All Trips - TRN - ALL
    '954.01': TableDef('954.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # Build - All Trips - TRN - ALL
    '975.01': TableDef('975.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # Build - All Trips - TRN - ALL
    '996.01': TableDef('996.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # Build - All Trips - TRN - ALL
    '1017.01': TableDef('1017.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),
}


def parse_table(result_file_path, table_label):
    def replace_dash(x):
        return 0 if x == '-' else x

    table_def = _table_parameters[table_label]
    start_table_tag = 'Table{:>9s}\n'.format(table_def.table_id)

    end_table_tag = table_def.end_table_tag
    skip_rows = table_def.skip_rows

    found_table = False
    table = StringIO('')

    with open(result_file_path, 'r') as result_file:
        for line in result_file:
            if line.startswith(start_table_tag):
                found_table = True

            if found_table:
                if line.startswith(end_table_tag):
                    found_table = False
                else:
                    table.write(line)

    table.seek(0)

    df = pd.read_fwf(table, widths=table_def.widths, skiprows=skip_rows)

    if table_def.df_drop_top_rows is not None:
        df = df[table_def.df_drop_top_rows:]

    if table_def.df_drop_tail_rows is not None:
        df = df[:-table_def.df_drop_tail_rows]

    if table_def.reset_header:
        columns = df.columns
        df.columns = np.arange(len(columns))

    if table_def.rename_columns is not None:
        df = df.rename(columns=table_def.rename_columns)

    if table_def.int_columns is not None or table_def.convert_numerics:
        df = df.applymap(np.vectorize(replace_dash))

    if table_def.int_columns is not None:
        df[table_def.int_columns] = df[table_def.int_columns].astype(np.int64)

    if table_def.index_col is not None:
        df = df.set_index(table_def.index_col)

    if table_def.convert_numerics:
        df = df.apply(pd.to_numeric)

    return df.copy()


def summarize_access_modes(result_file_path, percentage=False):
    table_label = '9.01'
    tbl = parse_table(result_file_path, table_label)
    table_def = _table_parameters[table_label]
    
    if not percentage:
        return tbl[table_def.int_columns].sum()
    
    exist = tbl[['exist_wlk','exist_knr', 'exist_pnr', 'exist_xfr']].sum() / tbl[['exist_wlk','exist_knr', 'exist_pnr', 'exist_xfr']].sum().sum()
    nb = tbl[['nb_wlk', 'nb_knr', 'nb_pnr', 'nb_xfr']].sum() / tbl[['nb_wlk', 'nb_knr', 'nb_pnr', 'nb_xfr']].sum().sum()
    bld = tbl[['bld_wlk', 'bld_knr', 'bld_pnr', 'bld_xfr']].sum() / tbl[['bld_wlk', 'bld_knr', 'bld_pnr', 'bld_xfr']].sum().sum()
    
    exist.index = exist.index.str[-3:]
    nb.index = nb.index.str[-3:]
    bld.index = bld.index.str[-3:]
    
    return pd.concat([exist, nb, bld], axis=1, keys=['existing', 'nb', 'bld']).transpose()
    