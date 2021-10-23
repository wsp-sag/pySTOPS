import os

import pystops

report_file = os.path.join('..', 'data', 'STOPS', 'Reports', 'AC_m19-s19-d19#m19-s19-d19#m20-s19-d19-alt2_20_STOPSY2019Results.prn')

for table in ['1.02','2.04', '4.04', '9.01', '10.01', '345.01']:
    print('Parse Table: {}'.format(table))
    table = pystops.parse_table(report_file, table)
    print(table.head())
    
skim = pystops.read_skim(report_file, scenario='nobuild', mode='fg', access='pnr', period='pk')
print(skim)
