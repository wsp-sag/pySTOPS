# %%
import pandas as pd
import numpy as np
import os

from itertools import tee
from typing import Callable, Union
from pathlib import Path
import yaml


# %%
def find_table_line(line_iterator: iter, table_number: str) -> str:
    """finds line where table number is in"""
    while True:
        row, current_line = next(line_iterator)
        if "table" in current_line.lower():
            split_line = current_line.lower()
            split_line = split_line.split("table")
            assert len(split_line) == 2

            if table_number in split_line[-1]:
                return current_line


def _parse_line(line, column_break_loc):
    # +1 because we want to avoid the space between columns
    # print(column_break_loc)
    starts = [0] + list(column_break_loc)
    ends = list(column_break_loc) + [len(line) + 99999]
    return [line[start:end].strip() for start, end in zip(starts, ends)]


def _stop_reading_table(line):
    return line == ""


def _read_table_header(
    line_iterator: iter, heading_limit: int = 10
) -> tuple[iter, list[str] | list[tuple[str, str]]]:
    """
    we have 4 rows of text that look like this:
    Y2023 EXISTING                   Y2023 NO-BUILD                   Y2023 BUILD
    ================================ ================================ ================================
    #Trips     Miles        Hours    #Trips     Miles        Hours    #Trips     Miles        Hours
    ====== ============ ============ ====== ============ ============ ====== ============ ============

    we will return something like this:
    [
        (Y2023 EXISTING, #Trips),
        (Y2023 EXISTING, Miles),
        (Y2023 EXISTING, Hours),
        (Y2023 NO-BUILD, #Trips),
        (Y2023 NO-BUILD, Miles),
        (Y2023 NO-BUILD, Hours),
        (Y2023 BUILD, #Trips),
        (Y2023 BUILD, Miles),
        (Y2023 BUILD, Hours),
    ]
    thinking: when we are reading column sub heading names
    """
    current_iterator, copied_iterator = tee(line_iterator)

    start = 0
    for index, string in copied_iterator:
        start += 1
        if start >= heading_limit:
            raise ValueError("Table Not Found")
        print(repr(string[:-1]))

    table_header = 10
    return current_iterator, table_header


def read_table(line_iterator: iter) -> dict:
    """
    given iterator at current line of a file, will read the next table and return it as a
    dictionary.
    """

    return_dict = dict()
    column_names: list[str] = None
    column_break_locations: list[str] = None
    rows = []
    line_iterator, table_header = _read_table_header(line_iterator)
    index, unstriped_current_line = next(line_iterator)
    current_line = unstriped_current_line.strip()
    while True:
        prev_line = current_line  # used for finding the header
        prev_unstriped_line = unstriped_current_line
        index, unstriped_current_line = next(line_iterator)
        current_line = unstriped_current_line.strip()
        # if column names is not none we have found table and are reading
        # Else, find a table
        if column_names is not None:
            if _stop_reading_table(current_line):
                return rows, column_names
            rows.append(_parse_line(current_line, column_break_locations))

        elif set(current_line) == {"-", " "} or set(current_line) == {"=", " "}:
            # May need to change .replace("  ", " ") in future
            column_break_locations = np.where(
                np.array(list(current_line.replace("  ", " "))) == " "
            )[0]
            # get column names
            column_names = _parse_line(prev_line, column_break_locations)


# # # TODO might replace with pandas methods read_fwt
# def read_table(line_iterator: iter) -> dict:
#     """
#     given iterator at current line of a file, will read the next table and return it as a
#     dictionary.
#     """
#     return_dict = dict()
#     column_names: list[str] = None
#     column_break_locations: list[str] = None
#     rows = []

#     index, unstriped_current_line = next(line_iterator)
#     current_line = unstriped_current_line.strip()
#     while True:
#         prev_line = current_line  # used for finding the header
#         prev_unstriped_line = unstriped_current_line
#         index, unstriped_current_line = next(line_iterator)
#         current_line = unstriped_current_line.strip()
#         # if column names is not none we have found table and are reading
#         # Else, find a table
#         if column_names is not None:
#             if _stop_reading_table(current_line):
#                 return rows, column_names
#             rows.append(_parse_line(current_line, column_break_locations))

#         if set(current_line) == {"-", " "} or set(current_line) == {"=", " "}:
#             # May need to change .replace("  ", " ") in future
#             prev_column_break_locations = column_break_locations
#             column_break_locations = np.where(
#                 np.array(list(current_line.replace("  ", " "))) == " "
#             )[0]

#             # get column names
#             # this code only works on 2 levels
#             if column_names is None:
#                 column_names = _parse_line(prev_line, column_break_locations)
#                 previous_column_names = prev_unstriped_line
#                 previous_column_break_footer = unstriped_current_line

#             else:
#                 raise Exception("Table has double Index")
#                 # column_names = _parse_second_row(
#                 #     prev_line,
#                 #     column_break_locations,
#                 #     previous_column_names,
#                 #     previous_column_break_footer,
#                 # )


def _find_indexes_col_name(
    input_string,
    location,
    character="=",
) -> tuple[int, int]:
    """
    input string: "    ===   == ======="
    start index: 6      ^ this character in the string
    returns: (4, 8)   ^   ^ those locations
    """
    mask = [char == character for char in input_string] + [False]
    end_index = location
    start_index = location
    while mask[end_index]:
        end_index += 1

    while mask[end_index]:
        start_index -= 1

    return start_index, end_index


def _parse_second_row(
    line,
    column_break_loc,
    previous_column_names,
    previous_column_break_footer,
):
    """
    we have 4 rows of text that look like this:
    Y2023 EXISTING                   Y2023 NO-BUILD                   Y2023 BUILD
    ================================ ================================ ================================
    #Trips     Miles        Hours    #Trips     Miles        Hours    #Trips     Miles        Hours
    ====== ============ ============ ====== ============ ============ ====== ============ ============

    we will return something like this:
    [
        (Y2023 EXISTING, #Trips),
        (Y2023 EXISTING, Miles),
        (Y2023 EXISTING, Hours),
        (Y2023 NO-BUILD, #Trips),
        (Y2023 NO-BUILD, Miles),
        (Y2023 NO-BUILD, Hours),
        (Y2023 BUILD, #Trips),
        (Y2023 BUILD, Miles),
        (Y2023 BUILD, Hours),
    ]
    thinking: when we are reading column sub heading names
    we go up 1 level
    we go left until we see a space
    we go right until we see space
    then read these indexes from those indexes
    strip it
    that is the super column name
    """

    starts = [0] + list(column_break_loc)
    ends = list(column_break_loc) + [len(line) + 99999]

    return_list = []
    for sub_col_start, sub_col_end in zip(starts, ends):
        sub_col_name = line[sub_col_start:sub_col_end].strip()
        col_start, col_end = _find_indexes_col_name(
            previous_column_break_footer, sub_col_start
        )
        col_name = previous_column_names[col_start:col_end].strip()

        return_list.append(col_name + "_" + sub_col_name)

    # [line[start:end].strip() for start, end in zip(starts, ends)]
    print(return_list)
    return return_list


def _to_pandas(data: list[list], col_names: list[str]):
    data = np.array(data)
    return pd.DataFrame(data, columns=col_names)


def _get_text_table(line_iterator, current_line_string):
    text = current_line_string

    # first line will be blank we want to skip it
    index, line = next(line_iterator)
    text = text + line
    # iterate until blank line
    while True:
        index, line = next(line_iterator)
        text = text + line

        if _stop_reading_table(line.strip()):
            return text


def get_table(path: Union[str, Path], table_number: str):

    with open(path, "r", errors="ignore") as report:
        # we are going to have a fairly complex state so we are
        # going to handle to report in as an iterator, and pass it into a function to handle
        # note this can only work down the report
        line_iterator = enumerate(iter(report))

        current_line: str = find_table_line(line_iterator, table_number)
        print(f"   found: {current_line.strip()}")
        for_getting_csv, for_raw_text = tee(line_iterator)  # <- duplicates iterator
        text_table = _get_text_table(for_raw_text, current_line)
        data, column_names = read_table(for_getting_csv)
        data = [sub_row for sub_row in data if len(sub_row) == len(column_names)]
        df = _to_pandas(data, column_names)
        # *read_table(for_getting_csv)

    return text_table, df, current_line.strip()


# input_path = Path(r"C:/Users/USLP095001/code/pytstops/pySTOPS/r_scripts/example_input")
# get_table(input_path / "CUR.prn", "4.02")
def main(input_dir: str, output_dir: str, tables_to_output: str):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    ret_dfs = []

    for prn_file_path in input_dir.glob("*.prn"):
        name = prn_file_path.stem
        print(name)
        os.makedirs(output_dir / name, exist_ok=True)

        for table_number in tables_to_output:
            text_table, df, table_name = get_table(prn_file_path, table_number)
            with open(output_dir / name / f"{table_name}.txt", "w") as f:
                f.write(text_table)

            # replace tab with a space for bacwards compatibility
            split_table = table_name.split(" ")

            formatted_name = f"{split_table[0]} {split_table[-1]}"
            df.to_csv(output_dir / name / f"{formatted_name}.csv")
            ret_dfs.append(df)

    return ret_dfs


if __name__ == "__main__":
    cwd = Path(os.getcwd())
    with open(cwd / "config.yml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    dfs = main(**config)
# dfs[0]

# %%
"sadfaf\n"[:-1]
