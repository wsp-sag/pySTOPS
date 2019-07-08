## pySTOPS
A simple utility for parsing and reading FTA STOPS outputs with python and Pandas. The tool currently supports parsing tables 2.04, 2.05, 2.07, 2.08, 3.01, 9.01, 10.01, and 350.01. More table parsers coming soon.

Happily accepting additions.

## Installation
The project relies on Python.

3. Create a pySTOPS-oriented virtual python environment. Recommend using a Anaconda Conda virtual env with the environment.yml included in this repository.
```
>>conda env create -f environment.yml
```
4. Switch the Virtual Env
```
conda activate pystops
```
5. Use the setup.py to install the package.
```
>>python setup.py install
```
6. Move to the test folder.
```
>>cd tests
```

7. Run example
```python
python example.py
```

## Usage
In a real world usage, reading in a STOPS Report table into a Pandas dataframe becomes trivial.

```python
import pystops

pystops.parse_table(report_file, '10.01')
```

For the data file in the example directory, this will return the following Pandas dataframe.

|route_id|route_name               |route_count|exist_walk|exist_knr|exist_pnr|exist_all|...|bld_all|
|--------|----------               |----------:|---------:|--------:|--------:|--------:|---|------:|
|1&C     |--1-Metric/South Congress| 6227      | 5394     | 242     |      117|  5754   |...|    117|
|...     |...                      | ...       |          |         |         |         |...|       |
|990&C   |--990-Manor/Elgin Express| 83        | 1        |     42  | 10      |  52     |...|     52|

## Additional Tables
The pySTOPS library searches the STOPS Results file for tags the start and end of each table, and the library
then processes these tags to create Pandas DataFrames. If you want to add support for an additional table, 
modify the _table_parameters dictionary in the reader.py Python file.

The table name (e.g., '2.04', '10.01') is the key for each dictionary entry, and it is the way that the library
finds the appropriate table. The rest of potential tags are below.

|Tag|Required|Description|
|:---|:---:|:---|
|df_drop_top_rows|| (Integer) Number of any extranenous top rows to discard|
|df_drop_tail_rows|| (Integer) Number of any extranenous bottom (tail) rows to discard|
|end_table_tag| X| (String) Identify the last row of the data table|
|int_columns| | (String Array) Force a retyping of columns to integers|
|index_col|| (String) Set the index of the DataFrame to a specific column|
|rename_columns|| (Dictionary) Column name mappings|
|reset_header| | (Boolean) Change the header names to column numbers|
|skip_rows| | (Integer) Number of lines to skip in the table header|
|widths||(Integer Array) Fixed width column lengths for the table|
