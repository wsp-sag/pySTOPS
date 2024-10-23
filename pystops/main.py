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


import GTFS_processing
from helper_functions import table_out_file
from legacy_read_table import legacy_read_table
import post_process_functions
import read_table.read_table as read_tale

import warnings

# TODO once legacy code has been superseded, we should be able to turn this off in
# production version
warnings.filterwarnings("ignore")

# %%

os.chdir(r"C:\Users\USLP095001\code\pytstops\client_package_deploy")
CUR_DIR = Path(os.getcwd())
print("------------------- executing analysis in directory --------------------")
print(CUR_DIR, end="\n\n")

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
    "test": (STOP_RUNS_PATH / "Reports", "EXST"),
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
## %% ---------------------------------------------------------------------------------------

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

# create output files
output16_path = OUTPUT_DIR / "SECTION 16"
output15_path = OUTPUT_DIR / "SECTION 15"

for i in range(1, 17):
    out_subfolder = OUTPUT_DIR / ("SECTION " + str(i))
    if not os.path.exists(out_subfolder):
        os.makedirs(out_subfolder)


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

        try:
            text_table, df, table_name = read_tale.get_table(
                report_file,
                table,
                error_on_bad=True,  # we have legacy mode as backup we will give up if we are not sure we will error
            )
            df.to_csv(write_path_for_table)
            combined_table = df.copy()

        except Exception:
            print(
                "\033[91mError with new File Read System\033[0m, reverting to legacy...",
                end="\n\n",
            )
            combined_table = legacy_read_table(
                scen_run,
                output15_path,
                rail_routes,
                table,
                report_file,
                write_path_for_table,
            )

        combined_table["run_name"] = scen_name
        combined.append(combined_table)

    one_table = pd.concat(combined)
    one_table.to_csv(output_path)
# %%

input_files = [
    key for key, (path, year, run_type) in input_files.items() if run_type == "BLD-"
]

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
