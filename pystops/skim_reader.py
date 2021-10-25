import os

import numpy as np
import pandas as pd


def _apply_stop_names(skim, result_file, scenario='build', mode='fg', period='pk'):
    root_skim_path = _root_skim_path(result_file, scenario, mode, '', period)
    dtypes = {
        'stop_no': np.int16,
        'orig_stop_id': str,
        'stop_name': str
    }

    stops = pd.read_csv(f'{root_skim_path}stops.txt',
                        usecols=dtypes.keys(), dtype=dtypes
                        )

    for col in ['ISTOP_NO-01', 'JSTOP_NO-01','ISTOP_NO-02','JSTOP_NO-02','ISTOP_NO-03','JSTOP_NO-03','ISTOP_NO-04','JSTOP_NO-04']:
        skim = pd.merge(skim, stops, left_on=col, right_on='stop_no', how='left')
        skim = skim.drop(columns=['stop_no', col])
        skim = skim.rename(columns={'orig_stop_id': col, 'stop_name': f'{col}_name'})
    
    return skim


def _apply_trip_names(skim, result_file, scenario='build', mode='fg', period='pk'):
    root_skim_path = _root_skim_path(result_file, scenario, mode, '', period)
    

    cols = ['trip_no','comma','trip_id','comma','orig_trip_id', 'route_no', 'comma',
            'route_id','comma','orig_route_id','comma',
            'route_short_name','comma','route_long_name','comma','route_desc','comma',
            'route_type','comma','route_used','comma','begin_time','comma','end_time','comma',
            'mileage']

    widths = [10,1,10,1,25,10,1,
              10,1,25,1,40,1,
              40,1,40,1,2,1,
              2,1,10,1,10,1,10]

    trips = pd.read_fwf(f'{root_skim_path}trips.txt', widths=widths)
    trips.columns = cols
    trips = trips[['trip_no', 'orig_trip_id', 'orig_route_id', 'route_short_name']].copy()
    trips[['orig_trip_id', 'orig_route_id', 'route_short_name']] = trips[['orig_trip_id', 'orig_route_id', 'route_short_name']].applymap(lambda x: x.strip())
    trips.columns = ['trip_no', 'trip_id', 'route_id', 'route_short_name']
    
    for col in ['TRIP_NO-01', 'TRIP_NO-02', 'TRIP_NO-03', 'TRIP_NO-04']:
        skim = pd.merge(skim, trips, left_on=col, right_on='trip_no', how='left')
        skim = skim.drop(columns=['trip_no', col])
        skim = skim.rename(columns={'trip_id': col, 'route_id': f'{col}_route_id', 'route_short_name': f'{col}_route_name'})
    
    return skim


def _root_skim_path(result_file, scenario='build', mode='fg', access='walk', period='pk'):
    assert scenario in ('exist', 'nobuild', 'build', '')
    assert mode in ('bs', 'fg', 'tr', '')
    assert access in ('walk', 'pnr', 'knr', '')
    assert period in ('op', 'pk', '')
    
    scenario_aliases = {
        'exist': 'EXST',
        'nobuild': 'NOBL',
        'build': 'BLD-'
    }
    
    access_aliases = {
        'walk': 'WLK',
        'knr': 'KNR',
        'pnr': 'PNR',
        '': ''
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
    
    return os.path.join(skim_path, f'AC_{core_name}_STOPS_Path_{period.upper()}_{mode.upper()}_{scenario_aliases[scenario]}{access_aliases[access]}skim')


def read_skim(result_file, scenario='build', mode='fg', access='walk', period='pk', apply_stop_name=False):
    root_skim_path = _root_skim_path(result_file, scenario, mode, access, period)
    
    skim_path = f'{root_skim_path}.bin'
    skim = binary_as_pandas(skim_path)
    if apply_stop_name:
        skim = _apply_stop_names(skim, result_file, scenario, mode, period)
        skim = _apply_trip_names(skim, result_file, scenario, mode, period)
    return skim


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
