import os

import pystops
import yaml


report_file = os.path.join('data', 'Results.prn')

for table in ['2.04', '9.01', '10.01', '93.01', '177.01', '261.01', '345.01', '350.01', '429.01', '513.01', '597.01', '681.01']:
    print('Parse Table: {}'.format(table))
    print(pystops.parse_table(report_file, table).head())
    print(pystops.parse_table(report_file, table).dtypes)

