import shapely.geometry as sg
from shapely.ops import nearest_points, split
from shapely.geometry import Point, MultiPoint, MultiLineString
import pprint as pp
import geopandas as gpd


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


def snap_stations_to_rails(station_gdf: gpd.GeoDataFrame, rail_gdf: gpd.GeoDataFrame):
    """ 
    Snap the stations to the nearest node in the nearest railway

    Args:
        stations_gdf (Geo-DataFrame): The Stations Geo-DataFrame
        rails_gdf (Geo-DataFrame): The rails Geo-DataFrame
    """
    stations_to_split = station_gdf.geometry.unary_union
    rails_to_split = rail_gdf.geometry.unary_union
    for i in range(len(stations_to_split)):
        rails_to_split.interpolate(rails_to_split.project(station_gdf.geometry[i])).wkt
    station_gdf['geometry'] = station_gdf.apply(lambda row: rails_to_split.interpolate(rails_to_split.project(row.geometry)), axis=1)
    return(station_gdf,stations_to_split,rails_to_split)

def gdf_to_segments(stations_to_split: MultiPoint, rails_to_split: MultiLineString):
    """
    Split rails segments based on the stations points

    Args:
        stations_to_split (MultiPoint): The nodes of the stations to 
        rails_to_split (MultiLineString): A MultiLineString for the rails
    """
    # returns GeometryCollection
    rails_geometry =  split(rails_to_split, stations_to_split)
    # transform Geometry Collection to GeoDataFrame
    segments = [feature for feature in rails_geometry]
    rail_segments_gdf = gpd.GeoDataFrame(
        list(range(len(segments))), geometry=segments)
    rail_segments_gdf.columns = ['name','geometry']
    return(rail_segments_gdf)


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

    Muilti_Station = MultiPoint(gdf_station['geometry'])

    output_gdf = gpd.GeoDataFrame()
    for i, row in gdf_city.iterrows():
        city_point = row['geometry']
        city_name = row['name']

        near_point = nearest_points(city_point, Muilti_Station) # output = [city point, station point]
        
        near_station = gdf_station[gdf_station['geometry'] == near_point[1]]
        near_station = gpd.GeoDataFrame(near_station)
        near_station['city'] = ''
        near_station["city"] = city_name

        output_gdf = output_gdf.append(near_station)

    print(output_gdf)

    return output_gdf