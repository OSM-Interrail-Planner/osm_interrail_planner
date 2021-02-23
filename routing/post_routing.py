import geopandas as gpd
import pandas as pd
import numpy as np
import pprint as pp


def merge_tsp_solution(dict_distance_matrix: dict, plan_output:str, crs: str) -> gpd.GeoDataFrame:

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
    pp.pprint(route_dict)

    route_df = pd.DataFrame (route_dict, columns = ['start_city','end_city', 'geometry', 'distance', 'order'])
    print(route_df)
    route_gdf = gpd.GeoDataFrame(route_df, crs=crs)
    print(route_gdf)

    return(route_gdf)

def cities_on_way(point_gdf: gpd.GeoDataFrame, line_gdf: gpd.GeoDataFrame, list_input_point: list, offset: int, crs: str) -> gpd.GeoDataFrame:
    """This function selects points which intersect with the lines

    Args:
        point_gdf (gpd.GeoDataFrame): geopandas GeoDataFrame with point geometry
        line_gdf (gpd.GeoDataFrame): geopandas GeoDataFrame with line geometry
        list_input_city (list[str]): list of destination cities
        offset (int): Tolerance for point to be snipped to line in crs metrics
        crs (str): Set output crs

    Returns:
        gpd.GeoDataFrame: Point GeoDataFrame with selection 
    """
    # Create bounding box for the points in offset distance in meters (that's the reason for the reprojection)
    station_bbox = point_gdf.bounds + [-offset, -offset, offset, offset]

    # Apply an operation to this station_bbox to get a list of the lines that overlap
    hits = station_bbox.apply(lambda row: list(line_gdf.sindex.intersection(row)), axis=1)

    # Create a better datastructure to relate the points to their lines in tolerance distance
    tmp = pd.DataFrame({
        # index of points table
        "pt_idx": np.repeat(hits.index, hits.apply(len)),
        # ordinal position of line - access via iloc later
        "line_i": np.concatenate(hits.values)
    })

    tmp["line_i"] = tmp["line_i"].astype(int)

    # Join back to the lines on line_i 
    tmp = tmp.join(point_gdf.reset_index(drop=True), on="pt_idx") # reset_index() to give us the ordinal position of each line
    tmp = tmp.join(line_gdf.geometry.rename("line"), on="line_i") # join back to the original points to get their geometry and rename the point geometry as "point"   
    tmp = gpd.GeoDataFrame(tmp, geometry="geometry", crs=crs) # convert back to a GeoDataFrame, so we can do spatial ops

    # Calculate the distance between each line and its associated point feature
    tmp["dist"] = tmp.geometry.distance(gpd.GeoSeries(tmp.line))

    # Discard points by distance to each rail
    tmp = tmp.loc[tmp.dist <= offset] # discard any points that are greater than tolerance from points
    # Sort out unimportant cities and duplicates
    tmp = tmp[tmp["place"] == "city"]
    duplicates = tmp["name"].isin(list_input_point)
    newbies = [not b for b in duplicates]
    tmp = tmp[newbies]

    tmp = tmp.reset_index()
    tmp = tmp.drop(columns=["index", "pt_idx", "line", "dist"])
    tmp = gpd.GeoDataFrame(tmp, geometry="geometry", crs=crs)

    # Sort out unimportant cities
    tmp = tmp[tmp["place"] == "city"]

    print(tmp)

    return tmp
