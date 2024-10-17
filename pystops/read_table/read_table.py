# %%
import pandas as pd
import numpy as np
import os

from itertools import tee
from collections.abc import Iterator
from typing import Callable, Union, Literal, NamedTuple
from dataclasses import dataclass
from pathlib import Path
import yaml

LineIterator = Iterator[tuple[int, str]]
IsLastLineFunc = Callable[[str], bool]


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
    for _ in range(num_to_iterate_return_iterator + 1):
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


def _general_stop_reading_table(
    line,
    distance_from_table_name: int | None = None,
    min_table_length_from_table_name: int = 10,
):
    """check if line is the end of a table"""
    if distance_from_table_name is not None:
        if distance_from_table_name <= min_table_length_from_table_name:
            return False

    return line == ""


def _get_dataframe(
    line_iterator: LineIterator, text_ends_table: IsLastLineFunc
) -> dict:
    """
    given iterator at current line of a file, will read the next table and return it as a
    dictionary.
    """

    table_header, breakup_array, line_iterator = _read_table_header(line_iterator)

    rows = []
    for line_number, line_text in line_iterator:
        line_text = line_text.replace("\n", "")
        if text_ends_table(line_text):
            break
        rows.append(
            _breakup_according_to_column_breakup_array(line_text, breakup_array)
        )

    return pd.DataFrame(np.array(rows), columns=table_header)


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


def _get_text_table(line_iterator: Iterator[int, str], current_line_string):
    text = current_line_string

    # first line will be blank we want to skip it
    index, line = next(line_iterator)
    text = text + line
    # iterate until blank line
    distance_from_table_name = 0
    while True:
        index, line = next(line_iterator)
        text = text + line
        distance_from_table_name = distance_from_table_name + 1
        if _general_stop_reading_table(
            line.strip(), distance_from_table_name=distance_from_table_name
        ):
            return text


def txt_block_to_array(text_block: str) -> np.ndarray:
    lines = text_block.split("\n")
    max_len = max(len(line) for line in lines)
    padded_lines = [list(line.ljust(max_len)) for line in lines]
    return np.array(padded_lines)


def fill_start_of_line_with_string_if_header(
    text_block: str, heading_char: str = "="
) -> str:
    """
    just takes a block of text like this:

                                                            Y2023 EXISTING                   Y2023 NO-BUILD                   Y2023 BUILD
                                                            ================================ ================================ ================================
    Route_ID                 --Route Name                   #Trips     Miles        Hours    #Trips     Miles        Hours    #Trips     Miles        Hours
    ======================================================= ====== ============ ============ ====== ============ ============ ====== ============ ============
    1&T                      --1-Dixie Hwy/Florence             22       329.57        25.30     22       329.57        25.30     22       329.57        25.30
    1-348&L                  --1-Mt. Adams - Eden Park           9        30.01         2.62      0         0.00         0.00      0         0.00         0.00

    and turns it into this:


                                                            Y2023 EXISTING                   Y2023 NO-BUILD                   Y2023 BUILD
    ======================================================================================== ================================ ================================
    Route_ID                 --Route Name                   #Trips     Miles        Hours    #Trips     Miles        Hours    #Trips     Miles        Hours
    ======================================================= ====== ============ ============ ====== ============ ============ ====== ============ ============
    1&T                      --1-Dixie Hwy/Florence             22       329.57        25.30     22       329.57        25.30     22       329.57        25.30
    1-348&L                  --1-Mt. Adams - Eden Park           9        30.01         2.62      0         0.00         0.00      0         0.00         0.00
    """
    fixed_string_rows = []
    for line in text_block.split("\n"):
        if set(line) == {heading_char, " "}:
            filled_start_line = False
            to_be_line = []
            for char in line:
                if not filled_start_line:
                    to_be_line.append(heading_char)
                else:
                    to_be_line.append(char)
            line = "".join(to_be_line)

        fixed_string_rows.append(line)
    return "\n".join(fixed_string_rows)


def verify_table(text_block: str, *, align_radius: int = 3) -> tuple[bool, str | None]:
    """
    given a text_block, verify that the table is correct, if it is correct
    it should be able to turn into a csv, otherwise we will suggest a fix and return that
    table.

    returns:
        arg 1: bool: weather the table
        arg 2: str | None: if arg 1 is True, will return a fixed string
    This function verifies the following defects:

    DEFECT 1: Columns dont align:
        sometimes, tables will have headers that slightly miss-align with the columns
        EG:
            txt1    txt2      tx3
            ------ ---------- -----
               27.2         16   foo
               28.3         01   bar

        DETECTION CRITERIA: " " in heading footer should be blank in all lines below header

        FIX:
            POTENTIAL!!!!! Not Implemented Yet
            Move header / table left/right until realigned

    DEFECT 2:
        ...
    """
    for_text_array = fill_start_of_line_with_string_if_header(text_block)
    text_array = txt_block_to_array(for_text_array)

    # Initialise as array of false
    where_heading_has_empty_string: np.ndarray = 1 == np.zeros_like(text_array[0])
    for row_index, row in enumerate(text_array):
        if set(row) == {" ", "="}:
            where_heading_has_empty_string = row == " "
        elif set(row) == {" ", "-"}:
            where_heading_has_empty_string = row == " "
        elif set(row[where_heading_has_empty_string]) == set():
            ...  # flow control, make sure it doesnt go to next line
        elif set(row[where_heading_has_empty_string]) != {" "}:
            return False, None

    return True, None


def get_table(path: Union[str, Path], table_number: str):

    with open(path, "r", errors="ignore") as report:
        # we are going to have a fairly complex state so we are
        # going to handle to report in as an iterator, and pass it into a function to handle
        # note this can only work down the report
        line_iterator = enumerate(iter(report))

        line_number, current_line = find_table_line(line_iterator, table_number)
        table_name = current_line.strip()
        print(f"    Found: {table_name}    on line: {line_number}")

        for_getting_csv, for_raw_text = tee(line_iterator)  # <- duplicates iterator
        text_table = _get_text_table(for_raw_text, current_line)

        table_is_verified, fixed_table = verify_table(text_table)
        if not table_is_verified:
            raise NotImplementedError("Need to implement Manual Fixes")

        df = _get_dataframe(for_getting_csv, _general_stop_reading_table)
        df.to_clipboard()

    return text_table, df, table_name


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
            text_table, df, table_name = get_table(prn_file_path, table_number)
            with open(output_dir / name / f"{table_name}.txt", "w") as f:
                f.write(text_table)

            # replace tab with a space for bacwards compatibility
            split_table = table_name.split(" ")

            formatted_name = f"{split_table[0]} {split_table[-1]}"
            df.to_csv(output_dir / name / f"{formatted_name}.csv")
            ret_dfs.append(df)

    # return ret_dfs


if __name__ == "__main__":
    cwd = Path(os.getcwd())
    with open(cwd / "config.yml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    dfs = main(**config)
# dfs[0]
