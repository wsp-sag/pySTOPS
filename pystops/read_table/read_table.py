# %%
import pandas as pd
import numpy as np
import os

from itertools import tee
from collections.abc import Iterator
from typing import Callable, Union, Literal
from pathlib import Path
import yaml

LineIterator = Iterator[tuple[int, str]]


# %%
def find_table_line(line_iterator: LineIterator, table_number: str) -> tuple[int, str]:
    """finds line where table number is in"""
    while True:
        line_number, current_line = next(line_iterator)
        if "table" in current_line.lower():
            split_line = current_line.lower()
            split_line = split_line.split("table")
            assert len(split_line) == 2

            if table_number in split_line[-1]:
                return line_number, current_line


def _parse_line(line, column_break_loc):
    # +1 because we want to avoid the space between columns
    # print(column_break_loc)
    starts = [0] + list(column_break_loc)
    ends = list(column_break_loc) + [len(line) + 99999]
    return [line[start:end].strip() for start, end in zip(starts, ends)]


def _stop_reading_table(line):
    return line == ""


def _slice_string_with_bool_arr(string, bool_array):
    """
    slices string with list/numpy array of boolean (works same as pandas slicing)
    """
    assert len(string) == len(bool_array)
    return "".join([char for char, keep_char in zip(string, bool_array) if keep_char])


def _breakup_according_to_column_breakup_array(
    line: str, column_breakup_array: np.ndarray
):
    # shouldnt need this line, but it is in for safety
    line = line.replace("\n", "")

    # copy because we need buffer breakup requires duplication
    buffered_breakup_array = column_breakup_array.copy()
    buffered_line = line

    # make sure column_breakup_array and line are the same length
    if len(line) > len(column_breakup_array):
        buffered_breakup_array = np.full(len(line), column_breakup_array[-1])
        buffered_breakup_array[: len(column_breakup_array)] = column_breakup_array

    elif len(column_breakup_array) > len(line):
        buffered_line = line.ljust(len(column_breakup_array))

    assert len(buffered_line) == len(buffered_breakup_array)

    return [
        _slice_string_with_bool_arr(buffered_line, buffered_breakup_array == col_index)
        for col_index in range(max(column_breakup_array) + 1)
    ]


def _tuple_lists_to_header(index_set: tuple[int], headers: list[list[str]]):
    strings_to_join = []
    for index, header_at_level in zip(index_set, headers):
        strings_to_join.append(header_at_level[index].strip())
    return tuple(strings_to_join)


def _read_table_header(
    line_iterator: LineIterator,
    heading_character: Literal["=", "-"] = "=",  # is usually -
    max_number_of_heading_lines: int = 10,
) -> tuple[list[tuple[str, str]], np.ndarray, LineIterator]:
    """
    there are a couple cases this function needs to handle

    CASE 1 we have 2 rows which look (something) like this:

        #Trips     Miles        Hours    #Trips     Miles        Hours    #Trips     Miles        Hours
        ====== ============ ============ ====== ============ ============ ====== ============ ============

        should return:
        [#Trips, Miles, Hours, #Trips, Miles, Hours, #Trips, Miles, Hours]

    CASE 2 we have 4 rows of text that look (something) like this:
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

    we will also return a 'column_breakup_array' in terms of the final heading that looks like:
        [0,0,0,0,0,0,0,0,1,1,1,1,1,1 ...]
        that increases every time it finds the ' =' character of the bottom most header string

    it will also return the line iterator starting where the next iteration will be on
    the first row of the table values
    """

    column_breakup_array: np.ndarray
    iterator_where_next_line_is_table, line_iterator = tee(line_iterator, 2)
    previous_string: str
    headers_and_arrays: tuple[str, np.ndarray] = []

    for number_of_lines_looked_at in range(max_number_of_heading_lines):
        line_number, line_string = next(line_iterator)

        # ignore new line character
        line_string = line_string.replace("\n", "")

        if set(line_string) == {heading_character, " "}:
            print(f"        Found Table Heading {line_number}")
            column_breakup_array = np.cumsum(
                [
                    (current_char == " ") and (next_char == "=")
                    for current_char, next_char in zip(
                        line_string[0:-1], line_string[1:]
                    )
                ]
            )
            headers_and_arrays.append(
                (
                    _breakup_according_to_column_breakup_array(
                        previous_string, column_breakup_array
                    ),
                    column_breakup_array,
                )
            )
            num_to_iterate_return_iterator = number_of_lines_looked_at

        previous_string = line_string

    if len(headers_and_arrays) == 0:
        raise ValueError(f"Table Heading not found on around {line_number}")

    # we want to return an iterator at the correct location
    for _ in range(num_to_iterate_return_iterator):
        next(iterator_where_next_line_is_table)

    # we have extracted data sets now we just need to map some things together
    max_breakup_array_len = max(
        len(breakup_array) for _, breakup_array in headers_and_arrays
    )
    table_index_join_table = []
    for str_col in range(max_breakup_array_len):
        table_index_join_table.append(
            tuple([char_array[str_col] for _, char_array in headers_and_arrays])
        )
    # we want unique column combinations
    table_index_sets = set(table_index_join_table)
    table_index_sets = sorted(table_index_sets)

    # sort indexes by first index, then second, then third ect
    headers = [header for header, _ in headers_and_arrays]

    table_header = [
        _tuple_lists_to_header(index_set, headers) for index_set in table_index_sets
    ]
    # iterate this to the table
    return table_header, column_breakup_array, iterator_where_next_line_is_table


def read_table(line_iterator: LineIterator) -> dict:
    """
    given iterator at current line of a file, will read the next table and return it as a
    dictionary.
    """

    # column_names: list[str] = None
    # column_break_locations: list[str] = None
    # rows = []
    # line_number, table_header = _read_table_header(line_iterator)
    # index, unstriped_current_line = next(line_iterator)
    # current_line = unstriped_current_line.strip()
    # while True:
    #     prev_line = current_line  # used for finding the header
    #     prev_unstriped_line = unstriped_current_line
    #     index, unstriped_current_line = next(line_iterator)
    #     current_line = unstriped_current_line.strip()
    #     # if column names is not none we have found table and are reading
    #     # Else, find a table
    #     if column_names is not None:
    #         if _stop_reading_table(current_line):
    #             return rows, column_names
    #         rows.append(_parse_line(current_line, column_break_locations))

    #     elif set(current_line) == {"-", " "} or set(current_line) == {"=", " "}:
    #         # May need to change .replace("  ", " ") in future
    #         column_break_locations = np.where(
    #             np.array(list(current_line.replace("  ", " "))) == " "
    #         )[0]
    #         # get column names
    #         column_names = _parse_line(prev_line, column_break_locations)
    table_header, breakup_array, line_iterator = _read_table_header(line_iterator)
    print(table_header)
    return None, None


def _find_indexes_col_name(
    input_string: str,
    location: int,
    character: str = "=",
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
    return return_list


def _to_pandas(data: list[list], col_names: list[str]):
    data = np.array(data)
    return pd.DataFrame(data, columns=col_names)


def _get_text_table(line_iterator: Iterator[int, str], current_line_string):
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

        line_number, current_line = find_table_line(line_iterator, table_number)
        print(f"    Found: {current_line.strip()}    on line: {line_number}")

        for_getting_csv, for_raw_text = tee(line_iterator)  # <- duplicates iterator
        text_table = _get_text_table(for_raw_text, current_line)
        assert False, (
            "We should verify the integrity of the text table.\n"
            "If it is bad revert to legacy mode and/or fix table before pandas"
        )
        # TODO Ideally re read in the text table we just made and make a new iterator

        data, column_names = read_table(for_getting_csv)
        # data = [sub_row for sub_row in data if len(sub_row) == len(column_names)]
        # df = _to_pandas(data, column_names)

    # return text_table, df, current_line.strip()


# input_path = Path(r"C:/Users/USLP095001/code/pytstops/pySTOPS/r_scripts/example_input")
# get_table(input_path / "CUR.prn", "4.02")
def main(input_dir: str, output_dir: str, tables_to_output: str):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    ret_dfs = []

    for prn_file_path in input_dir.glob("*.prn"):
        name = prn_file_path.stem
        print(f"Reading {name}.prn")
        os.makedirs(output_dir / name, exist_ok=True)

        for table_number in tables_to_output:
            get_table(prn_file_path, table_number)
    #         text_table, df, table_name = get_table(prn_file_path, table_number)
    #         with open(output_dir / name / f"{table_name}.txt", "w") as f:
    #             f.write(text_table)

    #         # replace tab with a space for bacwards compatibility
    #         split_table = table_name.split(" ")

    #         formatted_name = f"{split_table[0]} {split_table[-1]}"
    #         df.to_csv(output_dir / name / f"{formatted_name}.csv")
    #         ret_dfs.append(df)

    # return ret_dfs


if __name__ == "__main__":
    cwd = Path(os.getcwd())
    with open(cwd / "config.yml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    dfs = main(**config)
# dfs[0]
