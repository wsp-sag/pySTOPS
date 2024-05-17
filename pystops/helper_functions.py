from pathlib import Path
import pandas as pd

def table_out_file(section_label: str, OUTPUT_DIR: Path):
    if section_label == "SECTION 16":
        return OUTPUT_DIR / "SECTION 16" / "16_combined.csv"
    elif section_label == "SECTION 15":
        return OUTPUT_DIR / "SECTION 15" / "15_combined.csv"
    else:
        folder_num = section_label.split(".")[0]
        return OUTPUT_DIR / f"SECTION {folder_num}" / f"{section_label}.csv"
    

def stack_columns(df, columns, col_name="count", col_category_name="trip_type"):
    sub_dfs = []
    for column in columns:
        sub_df = df.copy()
        sub_df[col_name] = sub_df[column]
        sub_df.drop(columns=columns, inplace=True)
        sub_df[col_category_name] = column
        sub_dfs.append(sub_df)

    return pd.concat(sub_dfs)



def tag_rail_routes(routes:pd.Series, rail_routes: pd.Series):
    """
    given route names from stops and route names from gtfs, we will combine them
    and make sure all the stops routes are labled as rail or not rail
    """
    # since we cant rely on the strings to be exactly the same, we will only look
    # at the first 6 characters this tends to be the same
    routes = routes.str.replace("&", "").str.replace(" ", "").str[0:6]
    rail_routes = rail_routes.str.replace(" ", "").str[0:6]
    
    initial_stops = list(routes[routes.isin(rail_routes)].unique())
    print(f"{len(initial_stops)} stops in scenario: ", initial_stops)

    return routes.isin(rail_routes)