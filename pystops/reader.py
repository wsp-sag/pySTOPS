from io import StringIO

import numpy as np
import pandas as pd


_table_parameters = {
    '2.04': {
        'end_table_tag': 'COUNT',
        'skip_rows': 10,
        'df_drop_top_rows': 1,
        'df_drop_tail_rows': 2,
        # 'convert_numerics': True,
        'rename_columns': {
        'Unnamed: 0': 'origin'
        },
        'index_col': 'origin',
    },
    '2.05': {
        'end_table_tag': '-----------',
        'skip_rows': 5,
        'df_drop_top_rows': 1,
        'df_drop_tail_rows': 1,
        # 'convert_numerics': True,
        'rename_columns': {
            'Unnamed: 0': 'origin'
        },
        'index_col': 'origin',
    },
    '2.07': {
        'end_table_tag': '-----------',
        'skip_rows': 8,
        # 'df_drop_top_rows': 1,
        'df_drop_tail_rows': 1,
        'reset_header': True,
        'widths': [7, 11, 11, 11, 11],
        'rename_columns': {
            0: 'station_group',
            1: 'pre_calib_board',
            2: 'station_count',
            3: 'station_target',
            4: 'post_calib_board'
        },
        'convert_numerics': True,
        'int_columns': 'station_group',
        'index_col': 'station_group',
    },
    '2.08': {
        'end_table_tag': 'Number of unique',
        'skip_rows': 8,
        # 'df_drop_top_rows': 1,
        'df_drop_tail_rows': 1,
        'reset_header': True,
        'widths': [6, 22, 11, 11, 11, 10],
        'rename_columns': {
            0: 'route_group_num',
            1: 'route_group',
            2: 'pre_calib_board',
            3: 'route_count',
            4: 'route_target',
            5: 'post_calib_board'
        },
        #'convert_numerics': True,
        #'int_columns': 'station_group',
        'index_col': 'route_group_num',
    },
    '3.01': {
        'end_table_tag': 'TOTAL',
        'skip_rows': 8,
        'df_drop_top_rows': 1,
        'rename_columns': {
            'Unnamed: 0': 'origin'
        },
        'index_col': 'origin',
    },
    '3.02': {
        'end_table_tag': 'TOTAL',
        'skip_rows': 8,
        'df_drop_top_rows': 1,
        'rename_columns': {
            'Unnamed: 0': 'origin'
        },
        'index_col': 'origin',
    },
    '3.03': {
        'end_table_tag': 'TOTAL',
        'skip_rows': 8,
        'df_drop_top_rows': 1,
        'rename_columns': {
            'Unnamed: 0': 'origin'
        },
        'index_col': 'origin',
    },
    '4.01': {
        'end_table_tag': 'Total',
        'skip_rows': 5,
        'df_drop_top_rows': 1,
        'rename_columns': {
            'Idist': 'origin'
        },
        'index_col': 'origin',
    },
    '9.01': {
        'end_table_tag': '\x00',
        'skip_rows': 8,
        'reset_header': True,
        'rename_columns': {
            0: 'stop_id',
            1: 'station_name',
            2: 'exist_wlk',
            3: 'exist_knr',
            4: 'exist_pnr',
            5: 'exist_xfr',
            6: 'exist_all',
            7: 'nb_wlk',
            8: 'nb_knr',
            9: 'nb_pnr',
            10: 'nb_xfr',
            11: 'nb_all',
            12: 'bld_wlk',
            13: 'bld_knr',
            14: 'bld_pnr',
            15: 'bld_xfr',
            16: 'bld_all',
        }
    },
    '10.01': {
        'end_table_tag': '               Total',
        'skip_rows': 7,
        'reset_header': True,
        'widths': [25, 30] + [10] * 13,
        'df_drop_top_rows': 1,
        'rename_columns': {
            0: 'route_id',
            1: 'route_name',
            2: 'route_count',
            3: 'exist_wlk',
            4: 'exist_knr',
            5: 'exist_pnr',
            6: 'exist_all',
            7: 'nb_wlk',
            8: 'nb_knr',
            9: 'nb_pnr',
            10: 'nb_all',
            11: 'bld_wlk',
            12: 'bld_knr',
            13: 'bld_pnr',
            14: 'bld_all',
        },
        'int_columns': ['route_count',
            'exist_wlk', 'exist_knr', 'exist_pnr', 'exist_all',
            'nb_wlk', 'nb_knr', 'nb_pnr', 'nb_all',
            'bld_wlk', 'bld_knr', 'bld_pnr', 'bld_all',
        ]
    },
    '350.01': {
        'end_table_tag': 'Total',
        'skip_rows': 5,
        'df_drop_top_rows': 1,
        'rename_columns': {
            'Idist': 'origin'
        },
        'index_col': 'origin',
        #'convert_numerics': True,
    }
}


def parse_table(result_file_path, table_label):
    parse_parameters = _table_parameters[table_label]
    start_table_tag = 'Table{:>9s}\n'.format(table_label)

    end_table_tag = parse_parameters['end_table_tag']
    skip_rows = parse_parameters['skip_rows']

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

    widths = parse_parameters['widths'] if ('widths' in parse_parameters) else None

    df = pd.read_fwf(table, widths=widths, skiprows=skip_rows)

    if 'df_drop_top_rows' in parse_parameters:
        df = df[parse_parameters['df_drop_top_rows']:]

    if 'df_drop_tail_rows' in parse_parameters:
        df = df[:-parse_parameters['df_drop_tail_rows']]

    if 'reset_header' in parse_parameters and parse_parameters['reset_header']:
        columns = df.columns
        df.columns = np.arange(len(columns))

    if 'rename_columns' in parse_parameters:
        df = df.rename(columns=parse_parameters['rename_columns'])

    if 'convert_numerics' in parse_parameters and parse_parameters['convert_numerics']:
        df = df.apply(pd.to_numeric)

    if 'int_columns' in parse_parameters:
        df[parse_parameters['int_columns']] = df[parse_parameters['int_columns']].astype(np.int64)

    if 'index_col' in parse_parameters:
        df = df.set_index(parse_parameters['index_col'])

    return df.copy()
