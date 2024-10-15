# %%
import sys
import os
import glob
import pandas as pd
import geopandas as gpd
from pathlib import Path
from itertools import product
from shapely.geometry import LineString
import pprint


import read_16
import post_process_functions
import GTFS_processing
from helper_functions import table_out_file, stack_columns, tag_rail_routes
import reader as pystops

os.chdir(r"C:\Users\USLP095001\code\pytstops\client_package_deploy")
CUR_DIR = Path(os.getcwd())
print("------------------- executing analysis in directory --------------------")
print(CUR_DIR)
print()
OUTPUT_DIR = CUR_DIR / "visualizations" / "db01" / "data"
GTFS_PATH = CUR_DIR / "gtfs_data" / "GTFOutput"

ALL_GTFS_FOR_SHAPE = CUR_DIR / "gtfs_data" / "Inputs"
GTFS_GEOJSON_OUTPUT_DIR = (
    CUR_DIR / "visualizations" / "db01" / "data" / "GTFS" / "gtfs_shapes.geojson"
)
# ================== README =====================
# this section of populates input_files variables
# if you know what you are doing feel free to populate the input_files manually
# yourself, otherwise just change the input_folders and scenarios path
# variable
# =================================================

STOP_RUNS_PATH = CUR_DIR / "STOPS_runs"
input_folders = {
    "test": (STOP_RUNS_PATH / "Reports", "BLD-"),
    "test2": (STOP_RUNS_PATH / "Reports", "BLD-"),
    # "Existing": (STOP_RUNS_PATH / "A", "EXST"),
    # # "No Build": (STOP_RUNS_PATH / "A", "NOBL"),# this was requested to be removed, uncomment to re-add no build scenario
    # "Scenario A": (STOP_RUNS_PATH / "A", "BLD-"),
    # "Scenario B": (STOP_RUNS_PATH / "B", "BLD-"),
    # "Scenario C": (STOP_RUNS_PATH / "C", "BLD-"),
    # "Scenario D": (STOP_RUNS_PATH / "D", "BLD-"),
    # "Scenario E": (STOP_RUNS_PATH / "E", "BLD-"),
}
# This will crawl the given folders and look for valid prn files to load in
# input files is the important
input_files: dict[tuple[Path, int, str]] = dict()
for input_names, (file_dir, scen_run) in input_folders.items():
    for scenario_path in (file_dir).glob("*Results.prn"):
        year = scenario_path.stem[
            -11:-7
        ]  # define year as last 4 characters before result
        input_files[f"{input_names}"] = (scenario_path, year, scen_run)
        # if you would like to have multiple results.prn per folder
        # and you would like the year use the below line instead
        # input_files[f"{input_names}_{year}"] = (scenario_path, year, scen_run)
print("--------------- found the following files to be analyzed ---------------")
pprint.pprint(input_files)
print()
# %% ---------------------------------------------------------------------------------------

tables = [
    "1.01",
    "1.02",
    "2.04",
    "2.05",
    "2.07",
    "3.01",
    "3.02",
    "3.03",
    "4.01",
    "4.02",
    "4.03",
    "4.04",
    "8.01",
    "9.01",
    "10.01",
    "10.03",
    "10.04",  # "10.05" is not in current model runs
    "11.01",
    "11.02",
    "11.03",
    "SECTION 16",
    "SECTION 15",
]
# match table name with a filepath
tables_and_outputs = [(table, table_out_file(table, OUTPUT_DIR)) for table in tables]

# %%
# create output files
output16_path = OUTPUT_DIR / "SECTION 16"
output15_path = OUTPUT_DIR / "SECTION 15"

for i in range(1, 17):
    out_subfolder = OUTPUT_DIR / ("SECTION " + str(i))
    if not os.path.exists(out_subfolder):
        os.makedirs(out_subfolder)

# %%
print("Processing GTFS...")

rail_routes = GTFS_processing.combine_gtfs_data(GTFS_PATH, OUTPUT_DIR)
# rail routes are saved for later when we are processing table 16
# not important right now
rail_routes = pd.Series(rail_routes)
print("done\n")

print("Combining GTFS, to create shapefiles...")
GTFS_processing.create_shapefiles_from_gtfs_data(
    ALL_GTFS_FOR_SHAPE, GTFS_GEOJSON_OUTPUT_DIR
)
print("done\n")

# %%

for table, output_path in tables_and_outputs:

    print()
    print(f"------------------------ Extracting Table {table} ------------------------")

    combined = []
    for scen_name, (report_file, year, scen_run) in input_files.items():

        write_path_for_table = output_path.with_name(
            output_path.stem + "_" + scen_name + ".csv"
        )

        print(scen_name, ">> writing to >> ", write_path_for_table)

        if table == "SECTION 16":
            print("Parse Table Series in : {}".format(table))

            all_csvs = read_16.read_table_16(report_file)

            # Clean up tables
            for table_name, df in all_csvs.items():
                # TODO fix reader so this doesn't happen
                df.rename(
                    columns={"Perio": "Period", "d  Table No.": "Table No."},
                    inplace=True,
                )
                # print(df["Period"].unique())
                df["Period"] = df["Period"].map({"Peak": "peak", "Off-Pe": "non_peak"})

            # we will only concat the tables that are not already an aggregation
            concat_tables = [
                "1023.01",
                "1024.01",
                "1025.01",
                "1026.01",
                "1027.01",
                "1028.01",
            ]

            combined_csv = pd.concat(
                [df for key, df in all_csvs.items() if key in concat_tables]
            )
            # TODO fix this
            combined_csv.drop(columns="", inplace=True)
            combined_csv["Stop_ID"] = combined_csv["Stop_ID"].str.split().str[0]

            replace_dict = {"EXST": "Existing", "NOBL": "No-Build", "BLD-": "Build"}
            slicer = combined_csv["SCENARIO"] == replace_dict[scen_run]
            assert slicer.sum() > 0
            combined_csv = combined_csv[slicer]

            combined_csv["is_rail"] = tag_rail_routes(
                combined_csv["ROUTE"], rail_routes
            )

            combined_csv = stack_columns(
                combined_csv, ["Boards", "Alights", "Leave-Load"]
            )

            combined_csv.to_csv(
                write_path_for_table,
                index=False,
                encoding="utf-8-sig",
            )
            all_csvs["1029.01"].to_csv(
                write_path_for_table.with_stem(
                    write_path_for_table.stem + "_route_summary"
                )
            )
            all_csvs["1030.01"].to_csv(
                write_path_for_table.with_stem(
                    write_path_for_table.stem + "_station_summary"
                )
            )

            combined_table = combined_csv.copy()

        elif table == "SECTION 15":

            # print("Parse Table Series in : {}".format(table))
            table_no = table
            _ = pystops.parse_table(report_file, table, output15_path)

            os.chdir(output15_path)
            extension = "csv"
            all_filenames = None

            all_filenames = [Path(i) for i in glob.glob("Table*.{}".format(extension))]

            all_dfs = [pd.read_csv(f) for f in all_filenames]
            for temp_df, filename in zip(all_dfs, all_filenames):
                lookup_name = filename.stem.split("_")[-1]
                temp_df["sub_table_name"] = lookup_name

            combined_csv = pd.concat(all_dfs)
            slicer = combined_csv["SCENARIO"].str.split(" ").str[0] == scen_run.replace(
                "-", ""
            )
            assert slicer.sum() > 0
            combined_csv = combined_csv[slicer]
            combined_csv["transit_trip_percentage"] = (
                100 * combined_csv["Transit Trip"] / combined_csv["Transit Trip"].sum()
            )
            combined_csv.to_csv(
                write_path_for_table,
                index=False,
                encoding="utf-8-sig",
            )
            combined_table = combined_csv.copy()

        else:
            # print("Parse Table: {}".format(table))
            table_no = table
            table_df = pystops.parse_table(
                report_file,
                table,
                os.path.join(
                    "..", "tests", "SECTION " + table_no[: len(table_no) - 3], ""
                ),
            )

            # table 8 only makes sense in a bld scenario
            # for the inputs into the tableu we want to filter only to the scenario we care
            # about
            if (
                table.split(".")[0] == "8" and scen_run != "BLD-"
            ):  # only display table 9 if its a bild scenario
                table_df["Incremental PMT"] = 0

            if table.split(".")[0] == "10":  # table 10.*
                # print(table_df)
                temp_name = "Type" if "Type" in table_df.columns else "Service"
                slicer = table_df[temp_name].str.split("_").str[0] == scen_run.replace(
                    "-", ""
                )
                assert slicer.sum() > 0
                table_df = table_df[slicer]

            elif table.split(".")[0] == "11":  # table 11
                slicer = table_df["Scenario"].str.split("_").str[0] == scen_run.replace(
                    "-", ""
                )
                assert slicer.sum() > 0
                table_df = table_df[slicer]

            table_df.to_csv(
                write_path_for_table,
                index=False,
            )

            combined_table = table_df.copy()

        combined_table["run_name"] = scen_name
        combined.append(combined_table)

    one_table = pd.concat(combined)
    one_table.to_csv(output_path)
# %%

input_files = [
    key for key, (path, year, run_type) in input_files.items() if run_type == "BLD-"
]
# %%
# one_table = pd.concat(combined)
import pandas as pd

combined_df = pd.read_csv(OUTPUT_DIR / "SECTION 16" / "16_combined.csv")
pivoted = combined_df.pivot_table(
    index=["ROUTE", "is_rail", "Period", "trip_type"],
    columns="run_name",
    values="count",
    aggfunc="sum",
)
pivoted = pivoted[input_files]

metro_buildup = (
    combined_df[["ROUTE", "trip_type", "run_name", "count"]]
    .groupby(["ROUTE", "run_name", "trip_type"])
    .agg({"count": "sum"})
    .unstack("run_name")
)
metro_buildup.columns = [col[1] for col in metro_buildup.columns]
# %%
deltas = metro_buildup[input_files].copy()
for prev_col, current_col in zip(input_files[:-1], input_files[1:]):
    deltas[current_col] = metro_buildup[current_col] - metro_buildup[prev_col]


deltas.stack().to_frame().reset_index().rename(
    columns={0: "count", "level_2": "run_name"}
).to_csv(OUTPUT_DIR / "SECTION 16" / "16_incremental_buildup.csv")
# %%
# %%
print("Post Processing Section 16")
post_process_functions.post_process_section_16(OUTPUT_DIR / "SECTION 16", input_files)

# %%
# %%
print("Post Processing Section 4")
post_process_functions.post_process_section_4(OUTPUT_DIR / "SECTION 4")
# "
# %%
print("Post Processing Section 10")
post_process_functions.post_process_section_10(OUTPUT_DIR / "SECTION 10")
# %%
