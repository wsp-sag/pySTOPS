import os
import pandas as pd
from shapely.geometry import LineString
import geopandas as gpd
from pathlib import Path 
def combine_gtfs_data(GTFS_PATH, OUTPUT_DIR):
    """
    Combines GTFS Data in specific folders
    """
    files_to_be_joined = {
        "agency": [],
        "calendar": [],
        "routes": [],
        "stop_times": [],
        "stops": [],
        "trips": [],
    }
    for dir in GTFS_PATH.iterdir():
        scen_folder = dir.stem
        pk_or_op = scen_folder.split("_")[0]
        pk_or_op = pk_or_op.replace("OP", "non_peak").replace("PK", "peak")

        scen_name = scen_folder.split("_")[-1]
        scen_name = (
            scen_name.replace("BLD-", "Build")
            .replace("EXST", "Existing")
            .replace("NOBL", "No-Build")
        )
        print(scen_name)

        for key in files_to_be_joined:
            read_path = (dir / key).with_suffix(".txt")
            df = pd.read_csv(read_path)
            df["scen_folder"] = scen_folder
            df["period"] = pk_or_op
            df["option_name"] = scen_name

            files_to_be_joined[key].append(df)

    gtfs_folder = OUTPUT_DIR / "GTFS"
    if not gtfs_folder.exists():
        os.makedirs(gtfs_folder)

    for key, dfs_to_concat in files_to_be_joined.items():
        out_file = (gtfs_folder / key).with_suffix(".csv")
        df = pd.concat(dfs_to_concat)

        df.to_csv(out_file)
        if key=="routes":
            unique_rail_lines = df.loc[df['route_type'].isin([0,1,2]), "route_id"].unique()
            pd.DataFrame(unique_rail_lines).to_csv(gtfs_folder / "rail_routes.csv")
    
    return unique_rail_lines

def create_shapefiles_from_gtfs_data(GTFS_DIRECTORY: Path, OUTPUT_DIR: Path):
    """
    finds all gtfs files (shapes.txt, routes.txt and trips.txt)
    and combines them all into a single shapefile for viewing
    (note only unique shape ids and trip types are returned)
    """
    gtfs_data = {}

    for shapes_path in GTFS_DIRECTORY.rglob("shapes.txt"):
        route_path = shapes_path.with_name("routes.txt")
        trips_path = shapes_path.with_name("trips.txt")
        folder_name = shapes_path.parent.name
        
        gtfs_data[folder_name] = (
            pd.read_csv(shapes_path),
            pd.read_csv(trips_path),
            pd.read_csv(route_path),
        )

    all_dataframes = []
    for folder_name, (shapes_df, trips_df, route_df) in gtfs_data.items():
        
        # Get shapefile
        to_be_shape_df = []
        for shape_id, sub_df in shapes_df.groupby("shape_id"):
            sub_df = sub_df.sort_values(by="shape_pt_sequence")
            linestring = LineString(sub_df[[ "shape_pt_lon", "shape_pt_lat"]].to_numpy())
            to_be_shape_df.append((shape_id, linestring))
        
        shapes_processed_gdf = pd.DataFrame(to_be_shape_df, columns=("shape_id", "geometry"))
        
        try:
            final_frame = shapes_processed_gdf.merge(
                trips_df, how="left", on="shape_id"
            ).merge(
                route_df, how="left", on="route_id"
            )
            final_frame["folder_name"] = folder_name
            all_dataframes.append(final_frame)
        except KeyError as key:
            print("WARN:", folder_name, "is missing column header", key, "and does not follow gtfs format, it will be skipped")

    one_gdf = pd.concat(all_dataframes)
    one_gdf = one_gdf.drop_duplicates(subset=["shape_id", "route_type"])
    one_gdf = gpd.GeoDataFrame(one_gdf, geometry="geometry")

    route_type_labels = {
        0: "Rail",
        1: "Rail",
        2: "Rail: Long Distance",
        3: "Bus"
    }
    one_gdf["route_mode"] = one_gdf["route_type"].map(route_type_labels)

    one_gdf.to_file(OUTPUT_DIR)