import shapely.geometry as sg
from shapely.ops import split
from shapely.geometry import Point, MultiPoint, MultiLineString
import pprint as pp
import geopandas as gpd
import pandas as pd
import numpy as np


def snap_with_spatial_index(point_gdf: gpd.GeoDataFrame, line_gdf: gpd.GeoDataFrame, offset: int) -> gpd.GeoDataFrame:
    """This function snaps points to the closest point of a line based on spatial indexing

    Args:
        point_gdf (gpd.GeoDataFrame)
        line_gdf (gpd.GeoDataFrame)
        offset (int): Tolerance for point to be snipped to line in crs metrics

    Returns:
        gpd.GeoDataFrame: Point GeoDataFrame with updated locations snapped to lines, point outside the tolerance are deleted 
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

    # Join back to the lines on line_i 
    tmp = tmp.join(line_gdf.reset_index(drop=True), on="line_i") # reset_index() to give us the ordinal position of each line
    tmp = tmp.join(point_gdf.geometry.rename("point"), on="pt_idx") # join back to the original points to get their geometry and rename the point geometry as "point"   
    tmp = gpd.GeoDataFrame(tmp, geometry="geometry", crs=point_gdf.crs) # convert back to a GeoDataFrame, so we can do spatial ops

    # Calculate the distance between each line and its associated point feature
    tmp["snap_dist"] = tmp.geometry.distance(gpd.GeoSeries(tmp.point))

    # Discard and sort lines by distance to each point
    tmp = tmp.loc[tmp.snap_dist <= offset] # discard any lines that are greater than tolerance from points
    tmp = tmp.sort_values(by=["snap_dist"]) # sort on ascending snap distance, so that closest goes to top

    # Find closest line to a point
    closest = tmp.groupby("pt_idx").first() # group by the index of the points and take the first, which is the closest line 
    closest = gpd.GeoDataFrame(closest, geometry="geometry") # construct a GeoDataFrame of the closest lines

    # Real Snapping: 
    pos = closest.geometry.project(gpd.GeoSeries(closest.point)) # position of nearest point from start of the line
    new_pts = closest.geometry.interpolate(pos) # get new point location geometry

    # Join back the new geometry to our original station  
    line_columns = [] # identify the columns we want to copy from the closest line to the point, such as a line ID.   
    snapped = gpd.GeoDataFrame(closest[line_columns],geometry=new_pts) # create a new GeoDataFrame from the columns from the closest line and new point geometries (which will be called "geometries")
    updated_points = point_gdf.drop(columns=["geometry"]).join(snapped) # join back to the original points:
    updated_points = updated_points.dropna(subset=["geometry"]) # drop any that didn't snap

    return updated_points 
    

def connect_stations(stations: gpd.GeoDataFrame,groupby_var: str,rails: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    This function to conenct the stations points with the same name together in Linestring
    
    Args:
        stations: Geo-DataFrame  = The Stations Geo-DataFrame
        Groupby_var: str = The name of the station's name column inside the Stations Geo-DataFrame
        rails: Geo-DataFrame = The rails Geo-DataFrame
    Returns:
        Update the Geo-DataFrame of the rails with adding the Linstring created
    """
    new_stations = stations[[groupby_var,'geometry']].groupby('name').count()
    new_stations.columns = ["count"]
    new_stations = new_stations[new_stations["count"] > 1]
    stations_list = list(new_stations.index)
    stations_list.remove("nan")

    for n in stations_list:
        line_string = sg.LineString(list(stations[stations[groupby_var] == n]["geometry"]))
        x = dict(name = f"{n}_change", geometry = line_string)
        rails = rails.append(x, ignore_index=True)
    return(rails)


def split_line_by_nearest_points(gdf_line: gpd.GeoDataFrame, gdf_points: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Split the union of lines with the union of points resulting 
    Parameters
    ----------
    gdf_line : geoDataFrame
        geodataframe with multiple rows of connecting line segments
    gdf_points : geoDataFrame
        geodataframe with multiple rows of single points

    Returns
    -------
    gdf_segments : geoDataFrame
        geodataframe of segments
    """

    # union all geometries
    line = gdf_line.geometry.unary_union
    coords = gdf_points.geometry.unary_union

    # split coords on line
    # returns GeometryCollection
    split_line = split(line, coords)

    # transform Geometry Collection to GeoDataFrame
    segments = [feature for feature in split_line]

    gdf_segments = gpd.GeoDataFrame(
        list(range(len(segments))), geometry=segments, crs=gdf_points.crs)
    gdf_segments.columns = ['index', 'geometry']

    return gdf_segments