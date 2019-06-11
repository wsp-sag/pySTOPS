import os

import pystops

report_file = os.path.join('data', 'Results.prn')

for table in ['2.04', '9.01', '10.01']:
    print('Parse Table: {}'.format(table))
    print(pystops.parse_table(report_file, table).head())
