import os

import pystops

report_file = os.path.join('data', 'Results.prn')

for table in ['2.04', '9.01', '10.01', '345.01']:
    print('Parse Table: {}'.format(table))
    table = pystops.parse_table(report_file, table)
    print(table.head())
    print(table.dtypes)
