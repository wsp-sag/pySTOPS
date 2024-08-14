
import pandas as pd

def post_process_section_16(section_16_folder, input_files):
    """
    code for aggregating and cleaning tables in section 16, 
    """
    input_files = [key for key, (path, year, run_type) in input_files.items() if run_type == "BLD-"]

    to_be_concat = []
    for file in (section_16_folder).glob("*Scenario *route_summary.csv"):
        to_be_concat.append(pd.read_csv(file, index_col=False))
        to_be_concat[-1]["run_name"] = file.stem[12:22]
    pd.concat(to_be_concat).to_csv(
        section_16_folder / "16_combined_route_summary.csv"
    )

    to_be_concat = []
    for file in (section_16_folder).glob("*Scenario *station_summary.csv"):
        to_be_concat.append(pd.read_csv(file, index_col=False))
        to_be_concat[-1]["run_name"] = file.stem[12:22]
        combined_df = pd.concat(to_be_concat)

        ons = combined_df.drop(columns=["Ons"]).rename(columns={"Offs": "num"})
        ons["action"] = "Boarding"
        offs = combined_df.drop(columns=["Offs"]).rename(columns={"Ons": "num"})
        offs["action"] = "Alighting"
        combined_df = pd.concat([ons, offs])

    combined_df.dropna().to_csv(
        section_16_folder / "16_combined_station_summary.csv"
    )

    # build deltas for incremental buildup
    combined_df = pd.read_csv(section_16_folder / "16_combined.csv")
    pivoted = combined_df.pivot_table(index="ROUTE", columns='run_name', values='count', aggfunc='sum')
    pivoted = pivoted[input_files]
    deltas = pivoted.copy()
    for prev_col, current_col in zip(input_files[:-1], input_files[1:]):
        deltas[current_col] = pivoted[current_col] - pivoted[prev_col]
    
    deltas.unstack().to_frame().reset_index().rename(columns={0: "count"}).to_csv(section_16_folder / "16_incremental_buildup.csv")


def post_process_section_4(section_4_folder):
    """
    Post processing of 
    """

    names = {"4.01.csv": "Weekday Linked District-to-District Transit Trips", 
            "4.02.csv": "Weekday Incremental Linked Dist-to-Dist Transit Trips", 
            "4.03.csv": "Weekday Linked District-to-District Project Trips", 
            "4.04.csv": "Weekday Unlinked Station-to-Station Project Trips"}
    dataframes = []
    for file_name, desciption in names.items():
        current_file = (section_4_folder / file_name)
        dataframes.append(pd.read_csv(current_file))

        dataframes[-1]["table_number"] = file_name[:-4]
        dataframes[-1]["table_4_name"] = desciption
        
    pd.concat(dataframes).to_csv(section_4_folder / '4_combined.csv')

    incremental = dataframes[1][dataframes[1]["destination"] != "Total"]
    incremental = incremental.groupby("run_name").agg({"Transit Trip": "sum"})

    # buildup = incremental["Transit Trip"][3:] - incremental["Transit Trip"][2:-1]
    incremental["buildup"] = incremental["Transit Trip"] - incremental["Transit Trip"].shift(1)
    incremental.loc['Scenario A', "buildup"] = incremental.loc['Scenario A', "Transit Trip"]
    incremental.iloc[1:].to_csv(section_4_folder / "incremental_buildup.csv")


def route_no_to_group(s: pd.Series) -> pd.Series:
    return_s = s.copy()
    return_s[:] = "Others"
    s_int = pd.to_numeric(s, errors="coerce")
    return_s[s_int < 100] = "Bus 1-100"
    return_s[s_int >= 100] = (
        ((s_int[s_int >= 100] // 100) * 100).astype(int).astype(str)
    )
    return_s[s_int >= 100] += " Series"

    # be a bit carefull of this order, if you reverse it you will get different
    # results
    return_s[s.str.contains("RAIL") | s.str.contains("SILVER")] = "Commuter Rail"
    return_s[s.str.contains("LIGHT RAIL")] = "Light Rail"
    return return_s

def post_process_section_10(section_10_folder):

    file_10_03 = pd.read_csv(section_10_folder / "10.03.csv")
    file_10_03["peak_non_peak"] = "peak"
    file_10_04 = pd.read_csv(section_10_folder / "10.04.csv")
    file_10_04["peak_non_peak"] = "non_peak"
    out_file = pd.concat([file_10_03, file_10_04])
    out_file["SCENARIO"] = (
        out_file["Service"]
        .str.split("_")
        .str[0]
        .replace({"EXST": "Existing", "NOBL": "No-Build", "BLD": "Build"})
    )
    out_file["unit"] = out_file["Service"].str.split("_").str[-1]
    out_file["Route No."] = (
        out_file["route_name"].str.replace("--", "").str.split("-").str[0].str.strip()
    )
    out_file["route_group"] = route_no_to_group(out_file["Route No."])
    out_file.to_csv(section_10_folder / "10_03_and_10_04_combined.csv")
