from io import StringIO
import pkg_resources

import numpy as np
import pandas as pd
import yaml


def _get_table_structures():
    yaml_file = pkg_resources.resource_filename('pystops', 'pystops.yaml')
    with open(yaml_file, 'r') as stream:
        data_loaded = yaml.safe_load(stream)
    return data_loaded


def parse_table(result_file_path, table_label):
    parse_parameters = _get_table_structures()[table_label]
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

    widths = eval(parse_parameters['widths']) if ('widths' in parse_parameters) else None

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

    if 'int_columns' in parse_parameters:
        df[parse_parameters['int_columns']] = df[parse_parameters['int_columns']].astype(np.int64)

    if 'index_col' in parse_parameters:
        df = df.set_index(parse_parameters['index_col'])

    if 'convert_numerics' in parse_parameters and parse_parameters['convert_numerics']:
        df = df.apply(pd.to_numeric)

    return df.copy()
