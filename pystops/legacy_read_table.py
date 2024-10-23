from helper_functions import table_out_file, stack_columns, tag_rail_routes
import reader as pystops
import pandas as pd
import read_16
from pathlib import Path
import glob
import os


def legacy_read_table(
    scen_run, output15_path, rail_routes, table, report_file, write_path_for_table
):
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

        combined_csv["is_rail"] = tag_rail_routes(combined_csv["ROUTE"], rail_routes)

        combined_csv = stack_columns(combined_csv, ["Boards", "Alights", "Leave-Load"])

        combined_csv.to_csv(
            write_path_for_table,
            index=False,
            encoding="utf-8-sig",
        )
        all_csvs["1029.01"].to_csv(
            write_path_for_table.with_stem(write_path_for_table.stem + "_route_summary")
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
            os.path.join("..", "tests", "SECTION " + table_no[: len(table_no) - 3], ""),
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
    return combined_table
