import shapely.geometry as sg
from shapely.ops import split
from shapely.geometry import Point, MultiPoint, LineString, MultiLineString
import geopandas as gpd
import pandas as pd
import numpy as np


def snap_spatial_index(point_gdf: gpd.GeoDataFrame, line_gdf: gpd.GeoDataFrame, offset: int) -> gpd.GeoDataFrame:
    """This function snaps points to the closest point of a line based on spatial indexing

    Args:
        point_gdf (gpd.GeoDataFrame): geopandas GeoDataFrame with point geometry
        line_gdf (gpd.GeoDataFrame): geopandas GeoDataFrame with line geometry
        offset (int): Tolerance for point to be snipped to line in crs metrics

    Returns:
        gpd.GeoDataFrame: Point GeoDataFrame with updated locations snapped to lines, point outside the tolerance are deleted 
    """
    # Create bounding box for the points in offset distance in meters (that's the reason for the reprojection)
    station_bbox = point_gdf.bounds + [-offset, -offset, offset, offset]

    # Apply an operation to this station_bbox to get a list of the lines (sptially indexed) that overlap
    hits = station_bbox.apply(lambda row: list(line_gdf.sindex.intersection(row)), axis=1)
    tmp = pd.DataFrame({
        "pt_idx": np.repeat(hits.index, hits.apply(len)), 
        "line_i": np.concatenate(hits.values)
    })

    # Join back to the lines on line_i 
    tmp = tmp.join(line_gdf.reset_index(drop=True), on="line_i") 
    tmp = tmp.join(point_gdf.geometry.rename("point"), on="pt_idx") 
    tmp = gpd.GeoDataFrame(tmp, geometry="geometry", crs=point_gdf.crs) 

    # Calculate the distance between each line and its associated point feature
    tmp["snap_dist"] = tmp.geometry.distance(gpd.GeoSeries(tmp.point))

    # Discard and sort lines by distance to each point
    tmp = tmp.loc[tmp.snap_dist <= offset] 
    tmp = tmp.sort_values(by=["snap_dist"]) 

    # Find closest line to a point
    closest = tmp.groupby("pt_idx").first() 
    closest = gpd.GeoDataFrame(closest, geometry="geometry") 

    # Real Snapping
    pos = closest.geometry.project(gpd.GeoSeries(closest.point)) 
    new_pts = closest.geometry.interpolate(pos) 

    # Join back the new geometry to our original station  
    line_columns = []    
    snapped = gpd.GeoDataFrame(closest[line_columns],geometry=new_pts) 
    updated_points = point_gdf.drop(columns=["geometry"]).join(snapped) 
    updated_points = updated_points.dropna(subset=["geometry"]) 

    return updated_points 
    

def connect_points_spatial_index(point_gdf: gpd.GeoDataFrame, line_gdf: gpd.GeoDataFrame, offset: int, ) -> gpd.GeoDataFrame:
    """
    This function connects the stations points within the offset distance by a line and appends it to the line_gdf
    
    Args:
        point_gdf (gpd.GeoDataFrame): geopandas GeoDataFrame with point geometry
        line_gdf (gpd.GeoDataFrame): geopandas GeoDataFrame with line geometry
        offset (int): Tolerance for points to be connected by a line in crs metrics
    
    Returns:
        gpd.GeoDataFrame: Line GeoDataFrame with updated lines as connections between the points 
    """
    
    # Create bounding box for the points in offset distance in meters
    station_bbox = point_gdf.bounds + [-offset, -offset, offset, offset]

    # Apply an operation to this station_bbox to get a list of the points (sptially indexed) that overlap
    hits = station_bbox.apply(lambda row: list(point_gdf.sindex.intersection(row)), axis=1)
    tmp = pd.DataFrame({
        "pt_idx": np.repeat(hits.index, hits.apply(len)),
        "pt_i": np.concatenate(hits.values)
    })

    # Drop self intersections
    tmp = tmp[tmp["pt_idx"] != tmp["pt_i"]]

    # Join bakc to get the geometries
    tmp = tmp.join(point_gdf.reset_index(drop=True), on="pt_i") 
    tmp = tmp.join(point_gdf.geometry.rename("point"), on="pt_idx")
    
    # Create Linestrings connecting the stations
    tmp["line"] = tmp.apply(lambda row: LineString([row["geometry"], row["point"]]), axis=1)
    
    # Manage columns to be appended to the rails.gdf
    tmp = tmp.set_geometry('line')
    tmp = tmp.reset_index()
    tmp = tmp.drop(['index', 'pt_idx', 'pt_i', 'network', 'geometry', 'point'], axis=1)
    tmp = tmp.rename_geometry('geometry')
    tmp["name"] = ['change'] * tmp.shape[0]

    line_gdf = line_gdf.append(tmp, ignore_index=True)
    
    return line_gdf 


def split_line_spatial_index(point_gdf: gpd.GeoDataFrame, line_gdf: gpd.GeoDataFrame, offset: int) -> gpd.GeoDataFrame:
    """
    This function splits line features from line_gdf when they contain intermediate points from points_gdf within the offset distance
    
    Args:
        point_gdf (gpd.GeoDataFrame): geopandas GeoDataFrame with point geometry
        line_gdf (gpd.GeoDataFrame): geopandas GeoDataFrame with line geometry
        offset (int): Tolerance for points to work as split points for a line in crs metrics
    
    Returns:
        gpd.GeoDataFrame: Line GeoDataFrame with updated lines split by the points 
    """

    # Create bounding box for the points in offset distance in meters
    station_bbox = point_gdf.bounds + [-offset, -offset, offset, offset]

    # Apply an operation to this station_bbox to get a list of the lines (sptially indexed) that overlap
    hits = station_bbox.apply(lambda row: list(line_gdf.sindex.intersection(row)), axis=1)

    # Create a better datastructure to relate the points to their lines in tolerance distance
    tmp = pd.DataFrame({
        "pt_idx": np.repeat(hits.index, hits.apply(len)),   
        "line_i": np.concatenate(hits.values)
    })

    # Join bakc to get the geometries
    tmp = tmp.join(line_gdf.reset_index(drop=True), on="line_i") 
    tmp = tmp.join(point_gdf.geometry.rename("point"), on="pt_idx") 
    
    # Split the lines by the already snapped stations
    tmp["split_lines"] = tmp.apply(lambda row: split(row["geometry"], row["point"]), axis=1)
    tmp["num_features"] = tmp.apply(lambda row: len(row["split_lines"]), axis=1)
    tmp = tmp[tmp["num_features"]>1]

    # Create new GeoDataFrame for split lines
    split_lines_dic = {"name": [], "geometry": []}
    for i, row in tmp.iterrows():
        split_lines_dic["name"].append("split1")
        split_lines_dic["name"].append("split2")
        split_lines_dic["geometry"].append(row["split_lines"][0])
        split_lines_dic["geometry"].append(row["split_lines"][1])
    split_lines_df = pd.DataFrame (split_lines_dic, columns = ["name", "geometry"])
    split_lines_gdf = gpd.GeoDataFrame(split_lines_df, crs=line_gdf.crs)

    # Merge new split lines with original lines
    line_gdf = line_gdf.append(split_lines_gdf, ignore_index=True)

    return line_gdf