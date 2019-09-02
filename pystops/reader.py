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

    '9.01': TableDef('9.01', end_table_tag='\x00', skip_rows=8,
                     reset_header=True,
                     rename_columns={
                         0: 'stop_id', 1: 'station_name',
                         2: 'exist_wlk', 3: 'exist_knr', 4: 'exist_pnr', 5: 'exist_xfr', 6: 'exist_all',
                         7: 'nb_wlk', 8: 'nb_knr', 9: 'nb_pnr', 10: 'nb_xfr', 11: 'nb_all',
                         12: 'bld_wlk', 13: 'bld_knr', 14: 'bld_pnr', 15: 'bld_xfr', 16: 'bld_all',
                     }),

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

    #Existing - HBW - TRN - ALL
    '93.01': TableDef('93.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    #Existing - HBO - TRN - ALL
    '177.01': TableDef('177.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    #Existing - NHB - TRN - ALL
    '261.01': TableDef('261.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    #Existing - All Trips - TRN - ALL
    '345.01': TableDef('345.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # No Build - HBW - TRN - ALL
    '429.01': TableDef('429.01', end_table_tag='Total', skip_rows=5,
                      df_drop_top_rows=1, index_col='origin',
                      rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # No Build - HBO - TRN - ALL
    '513.01': TableDef('513.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # No Build - NHB - TRN - ALL
    '597.01': TableDef('597.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # No Build - All Trips - TRN - ALL
    '681.01': TableDef('681.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # Build - HBW - TRN - ALL
    '765.01': TableDef('765.01', end_table_tag='Total', skip_rows=5,
                      df_drop_top_rows=1, index_col='origin',
                      rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # Build - HBO - TRN - ALL
    '849.01': TableDef('849.01', end_table_tag='Total', skip_rows=5,
                       df_drop_top_rows=1, index_col='origin',
                       rename_columns={'Idist': 'origin'}, convert_numerics=True),

    # Build - NHB - TRN - ALL
    '933.01': TableDef('933.01', end_table_tag='Total', skip_rows=5,
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

    if table_def.int_columns is not None:
        df[table_def.int_columns] = df[table_def.int_columns].astype(np.int64)

    if table_def.index_col is not None:
        df = df.set_index(table_def.index_col)

    if table_def.convert_numerics:
        df = df.applymap(np.vectorize(replace_dash))
        df = df.apply(pd.to_numeric)

    return df.copy()
