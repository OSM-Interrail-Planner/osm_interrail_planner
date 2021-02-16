import shapely.geometry as sg
from shapely.ops import nearest_points, split
from shapely.geometry import Point, MultiPoint, MultiLineString
import pprint as pp
import geopandas as gpd
import pandas as pd
import numpy as np


def snap_with_spatial_index(point_gdf, line_gdf):
    # 3. Create bounding box for the points in offset distance in meters (that's the reason for the reprojection)
    offset = 100
    station_bbox = point_gdf.bounds + [-offset, -offset, offset, offset]
    #print(station_bbox)

    # 4. Now, we can apply an operation to this station_bbox to find get a list of the lines that overlap:
    hits = station_bbox.apply(lambda row: list(line_gdf.sindex.intersection(row)), axis=1)
    #print(hits)

    # 5. Create a better datastructure to relate the station points to their rails in tolerance distance
    tmp = pd.DataFrame({
        # index of points table
        "pt_idx": np.repeat(hits.index, hits.apply(len)),    
        # ordinal position of line - access via iloc later
        "line_i": np.concatenate(hits.values)
    })
    #print(tmp)

    # 6. Join back to the lines on line_i
        # we use reset_index() to give us the ordinal position of each line
    tmp = tmp.join(line_gdf.reset_index(drop=True), on="line_i")
        # Join back to the original points to get their geometry and rename the point geometry as "point"
    tmp = tmp.join(point_gdf.geometry.rename("point"), on="pt_idx")
        # Convert back to a GeoDataFrame, so we can do spatial ops
    tmp = gpd.GeoDataFrame(tmp, geometry="geometry", crs=point_gdf.crs)
    #print(tmp)

    # 7. Now we calculate the distance between each line and its associated point feature
    tmp["snap_dist"] = tmp.geometry.distance(gpd.GeoSeries(tmp.point))
    #print(tmp)

    # 8. Discard and sort by line bs distance to each point
        # Discard any lines that are greater than tolerance from points
    tmp = tmp.loc[tmp.snap_dist <= offset]
        # Sort on ascending snap distance, so that closest goes to top
    tmp = tmp.sort_values(by=["snap_dist"])

    # 9. Find closest line to a point
        # group by the index of the points and take the first, which is the closest line 
    closest = tmp.groupby("pt_idx").first()
        # construct a GeoDataFrame of the closest lines
    closest = gpd.GeoDataFrame(closest, geometry="geometry")
    #print(closest)

    # 10. Real Snapping: 
        # Position of nearest point from start of the line
    pos = closest.geometry.project(gpd.GeoSeries(closest.point))
        # Get new point location geometry
    new_pts = closest.geometry.interpolate(pos)

    # 11. Join back the new geometry to our original station
        # Identify the columns we want to copy from the closest line to the point, such as a line ID.
    line_columns = []
        # Create a new GeoDataFrame from the columns from the closest line and new point geometries (which will be called "geometries")
    snapped = gpd.GeoDataFrame(closest[line_columns],geometry=new_pts)
        # Join back to the original points:
    updated_points = point_gdf.drop(columns=["geometry"]).join(snapped)
        # You may want to drop any that didn't snap, if so:
    updated_points = updated_points.dropna(subset=["geometry"])

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


def split_line_by_nearest_points(gdf_line, gdf_points):
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

    # snap and split coords on line
    # returns GeometryCollection
    split_line = split(line, coords)

    # transform Geometry Collection to GeoDataFrame
    segments = [feature for feature in split_line]

    gdf_segments = gpd.GeoDataFrame(
        list(range(len(segments))), geometry=segments, crs=gdf_points.crs)
    gdf_segments.columns = ['index', 'geometry']

    return gdf_segments


def city_to_station(gdf_city, gdf_station, list_input_city):
    """[summary]

    Args:
        file_city ([type]): [description]
        file_station ([type]): [description]
        list_input_city ([type]): [description]
    """

    # Filtering the city GeoDataFrame(gdf_city) to match only the cities of interest (list_input_city).
    
    new = gdf_city["name"].isin(list_input_city) # -> create a boolean
    gdf_city = gdf_city[new]
    
    # calculate nearest_points() between each city in gdf_city and gdf_stations

    Multi_Station = MultiPoint(gdf_station['geometry'])
    output_gdf = gpd.GeoDataFrame()
    for i, row in gdf_city.iterrows():
        city_point = row['geometry']
        city_name = row['name']

        near_point = nearest_points(city_point, Multi_Station) # output = [city point, station point]
        
        near_station = gdf_station[gdf_station['geometry'] == near_point[1]]
        near_station = gpd.GeoDataFrame(near_station)
        near_station['city'] = ''
        near_station["city"] = city_name

        output_gdf = output_gdf.append(near_station)

    print(output_gdf)

    return output_gdf

# FOR TESTING
#city_gdf = gpd.read_file("data/processed/cities")
#station_gdf = gpd.read_file("data/snapped_station")   
#input_list_cities = ['Lisboa', 'Sines', 'Faro']

#city_to_station(city_gdf, station_gdf, input_list_cities)
