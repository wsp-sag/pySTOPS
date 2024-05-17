# %%
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Callable

# %%
def find_line(line_iterator: iter, condition_met: Callable):
    """finds line where current line meats condition"""
    while True:
        current_line = next(line_iterator)
        if condition_met(current_line):
            return current_line


# TODO might replace with pandas methods read_fwt
def read_table(line_iterator: iter) -> dict:
    """
    given iterator at current line of a file, will read the next table and return it as a 
    dictionary.
    """
    def parse_line(line, column_break_loc):
        # +1 because we want to avoid the space between columns
        # print(column_break_loc)
        starts = [0] + list(column_break_loc)
        ends = list(column_break_loc) + [len(line) + 99999]
        return [line[start:end].strip() for start, end in zip(starts, ends)]

    return_dict = dict()
    column_names: list[str] = None
    column_break_locations: list[str] = None
    rows = []

    current_line = next(line_iterator).strip()
    while True:
        prev_line = current_line  # used for finding the header
        current_line = next(line_iterator).strip()
        # if column names is not none we have found table and are reading
        # Else, find a table
        if column_names is not None:
            if current_line == "":
                return rows, column_names
            rows.append(parse_line(current_line, column_break_locations))

        elif set(current_line) == {"-", " "} or set(current_line) == {"=", " "}:
            # May need to change .replace("  ", " ") in future
            column_break_locations = np.where(
                np.array(list(current_line.replace("  ", " "))) == " "
            )[0]
            # get column names
            column_names = parse_line(prev_line, column_break_locations)

def read_table_2(line_iterator: iter) -> dict:
    """
    A slight modificiation to the read table function as
    some tables are a bit trickey to read
    """

    def parse_line(line, column_break_loc):
        # +1 because we want to avoid the space between columns
        # print(column_break_loc)
        starts = [0] + list(column_break_loc + 1)
        ends = list(column_break_loc + 1) + [len(line) + 99999]
        return [line[start:end].strip() for start, end in zip(starts, ends)]

    return_dict = dict()
    column_names: list[str] = None
    column_break_locations: list[str] = None
    rows = []

    current_line = next(line_iterator)[:-1]
    while True:
        prev_line = current_line  # used for finding the header
        current_line = next(line_iterator)#.strip()
        # if column names is not none we have found table and are reading
        # Else, find a table
        current_line = current_line[:-1]

        if column_names is not None:
            if current_line == "":
                return rows, column_names
            rows.append(parse_line(current_line, column_break_locations))

        elif set(current_line) == {"-", " "} or set(current_line) == {"=", " "}:
            # May need to change .replace("  ", " ") in future
            list_of_col_width_strings = current_line.replace("=", "-").split(" -")
            # we want to recreate the original string before the split so add " -"
            # we subtract 1 because we want the location beween " " and "-
            column_break_locations = np.cumsum([len(val + " -") for val in list_of_col_width_strings[:-1]]) - 2
            
            column_names = parse_line(prev_line, column_break_locations)


def _to_pandas(data: list[list], col_names:list[str]):
    data = np.array(data)
    return pd.DataFrame(data, columns=col_names)


def read_table_16(path):
    def find_section_16_heading(line: str) -> bool:
        temp_list = line.split()
        if len(temp_list) <= 1:
            return False

        return temp_list[0] == "SECTION" and temp_list[1] == "16:"
    
    def find_table(line:str, num: str):
        temp_list = line.split()
        if len(temp_list) <= 1:
            return False
        return temp_list[0] == "Table" and temp_list[1] == num
    
    # list of tables that point to sub tables
    has_sub_tables = {
        "1023.01", 
        "1024.01", 
        "1025.01", 
        "1026.01", 
        "1027.01", 
        "1028.01"
    } 

    section_16_table_names = None
    with open(path, "r", errors="ignore") as report:
        # we are going to have a fairly complex state so we are
        # going to handle to report in as an iterator, and pass it into a function to handle
        # note this can only work down the report
        line_iterator = iter(report)
        output_str = find_line(line_iterator, find_section_16_heading)
        table_names_df = _to_pandas(*read_table(line_iterator))

        all_tables = {}
        for _, table_att in table_names_df.iterrows():
            table_name = table_att.iloc[-1]
            print(table_name)
            output_str = find_line(line_iterator, lambda x: find_table(x, table_name))
            if table_name != "1030.01":
                main_table = _to_pandas(*read_table_2(line_iterator))
            else:
                main_table = _to_pandas(*read_table(line_iterator))
            # if there are no sub tables this will be taken as the final table
            final_table = main_table.copy()


            if table_name in has_sub_tables:
                sub_tables_to_concat = []
                for _, sub_table_att in main_table.iterrows():
                    sub_table_name = sub_table_att.iloc[-1]
                    # print(sub_table_name)
                    if sub_table_name != "":
                        output_str = find_line(line_iterator, lambda x: find_table(x, sub_table_name))
                        sub_table = _to_pandas(*read_table_2(line_iterator))
                        sub_table = sub_table[sub_table.iloc[:, -1] != ""]
                        sub_tables_to_concat.append(sub_table)
                        for att_name, att_val in sub_table_att.items():
                            sub_table[att_name] = att_val
                    
                # if there are sub tables this will be taken as the final table
                final_table = pd.concat(sub_tables_to_concat)

            # tag all the tables we just read with the relevant data
            for table_att_name, table_att_val in table_att.items():
                final_table[table_att_name] = table_att_val
            all_tables[table_name] = final_table

    return all_tables
                