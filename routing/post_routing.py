import geopandas as gpd
import pandas as pd
import numpy as np


def merge_tsp_solution(dict_distance_matrix: dict, plan_output:str, crs: str) -> gpd.GeoDataFrame:
    """This function creates a GeoDataFrame containing the optimized route.

    Args:
        dict_distance_matrix (dict): The in tsp.py created dictionary for the matrices and properties of TSP
        plan_output (str): The in tsp.py created output plan containing the order of cities
        crs (str): The desired coordinate reference system of the output route GeoDataFrame

    Returns:
        gpd.GeoDataFrame:  Each row is one part of the route and a pair of cites (start and end)
    """
    plan_list = plan_output.split(' ')
    plan_list.remove('')

    # Create empty Dictionary for GeoDataFrame
    route_dict = {'start_city': [], 'end_city': [], 'geometry': [], 'distance': [], 'order': []}

    for i in range(len(plan_list)-1):
        start_city_index = int(plan_list[i])
        end_city_index = int(plan_list[i+1])
        route = dict_distance_matrix['path_matrix'][start_city_index][end_city_index]
        distance = dict_distance_matrix['distance_matrix'][start_city_index][end_city_index]
        route_dict['start_city'].append(dict_distance_matrix['stop'][start_city_index]) 
        route_dict['end_city'].append(dict_distance_matrix['stop'][end_city_index]) 
        route_dict['geometry'].append(route) 
        route_dict['distance'].append(distance) 
        route_dict['order'].append(i+1)

    route_df = pd.DataFrame (route_dict, columns = ['start_city','end_city', 'geometry', 'distance', 'order'])
    route_gdf = gpd.GeoDataFrame(route_df, crs=crs)

    return(route_gdf)

def features_on_way(feature_gdf: gpd.GeoDataFrame, line_gdf: gpd.GeoDataFrame, list_input_city: list, offset: int, crs: str) -> gpd.GeoDataFrame:
    """This function select features which intersect with the lines

    Args:
        feature_gdf (gpd.GeoDataFrame): geopandas GeoDataFrame with point geometry
        line_gdf (gpd.GeoDataFrame): geopandas GeoDataFrame with line geometry
        list_input_city (list[str]): list of destination cities
        offset (int): Tolerance for point to be snipped to line in crs metrics
        crs (str): Set output crs

    Returns:
        gpd.GeoDataFrame: Point GeoDataFrame with selection 
    """
    # Create bounding box for the points in offset distance in meters (that's the reason for the reprojection)
    feature_bbox = feature_gdf.bounds + [-offset, -offset, offset, offset]

    # Apply an operation to this feature_bbox to get a list of the lines that overlap
    hits = feature_bbox.apply(lambda row: list(line_gdf.sindex.intersection(row)), axis=1)

    # Create a better datastructure to relate the points to their lines in tolerance distance
    tmp = pd.DataFrame({
        "ft_idx": np.repeat(hits.index, hits.apply(len)),
        "line_i": np.concatenate(hits.values)
    })

    tmp["line_i"] = tmp["line_i"].astype(int)

    # Join back to the geometries
    tmp = tmp.join(feature_gdf.reset_index(drop=True), on="ft_idx") 
    tmp = tmp.join(line_gdf.geometry.rename("line"), on="line_i") 
    tmp = gpd.GeoDataFrame(tmp, geometry="geometry", crs=crs) 

    # Calculate the distance between each line and its associated point feature
    tmp["dist"] = tmp.geometry.distance(gpd.GeoSeries(tmp.line))

    # Discard points by distance to each rail
    tmp = tmp.loc[tmp.dist <= offset] # discard any features that are greater than tolerance from points
    # Sort out unimportant cities and duplicates if closest cities are looked for
    if "place" in tmp.columns:
        tmp = tmp[tmp["place"] == "city"]
        duplicates = tmp["name"].isin(list_input_city)
        newbies = [not b for b in duplicates]
        tmp = tmp[newbies]

    tmp = tmp.reset_index()
    tmp = tmp.drop(columns=["index", "ft_idx", "line", "dist"])
    tmp = gpd.GeoDataFrame(tmp, geometry="geometry", crs=crs)

    return tmp
