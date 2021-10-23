import os

import numpy as np
import pandas as pd


def read_skim(result_file, scenario='build', mode='fg', access='walk', period='pk'):
    assert scenario in ('exist', 'nobuild', 'build')
    assert mode in ('bs', 'fg', 'tr')
    assert access in ('walk', 'pnr', 'knr')
    assert period in ('op', 'pk')
    
    scenario_aliases = {
        'exist': 'EXST',
        'nobuild': 'NOBL',
        'build': 'BLD-'
    }
    
    access_aliases = {
        'walk': 'WLK',
        'knr': 'KNR',
        'pnr': 'PNR',
    }
    
    # Build out the skim path
    path, file_name = os.path.split(result_file)
    skim_path = os.path.join(os.path.split(path)[0], 'Skims')
    
    # Break up the filename to get the respective scenario names
    exst, nobld, bld = file_name[3:file_name.find('STOPSY')-1].split('#')
    core_name = exst

    if scenario == 'build':
        core_name = bld

    if scenario == 'nobuild':
        core_name = nobld
    
    skim_path = os.path.join(skim_path, f'AC_{core_name}_STOPS_Path_{period.upper()}_{mode.upper()}_{scenario_aliases[scenario]}{access_aliases[access]}skim.bin')
    return binary_as_pandas(skim_path)


def retrieve_binary_structure(bin_file_path):
    col_names = []
    str_cols = []
    pfmt = []
    dcb_path = f'{bin_file_path[:-4]}.dcb'
    
    with open(dcb_path, 'r') as f:
        line_number = 0
        for line in f:
            line_number = line_number + 1
            if line_number < 3:
                continue
            values = line.split(',')
            col_names.append(values[0][1:-1])
            dtype = values[1]
            dsize = values[3]
            if dtype == 'I':
                ptype = f'i{dsize}'
            if dtype == 'F':
                ptype = f'f{dsize}'
            if dtype == 'C':
                ptype = f'a{dsize}'
                str_cols.append(values[0][1:-1])
            pfmt.append(ptype)

    return np.dtype(list(zip(col_names, pfmt))), str_cols


def binary_as_pandas(bin_file_path):
    file_struct, str_cols = retrieve_binary_structure(bin_file_path)
    arr = np.fromfile(bin_file_path, file_struct)
    
    df = pd.DataFrame(arr)
    df[str_cols] = df[str_cols].applymap(lambda x: x.decode('UTF-8').strip()) 
    
    return df