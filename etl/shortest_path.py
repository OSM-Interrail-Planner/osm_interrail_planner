from shapely.ops import nearest_points
from shapely.geometry import Point, MultiPoint
import pprint as pp
import geopandas as gpd


def city_to_station(file_city, file_station, list_input_city):
    """[summary]

    Args:
        file_city ([type]): [description]
        file_station ([type]): [description]
        list_input_city ([type]): [description]
    """
    # First, open shapefiles as GeoDataFrames
    gdf_city = gpd.read_file(file_city)
    gdf_station = gpd.read_file(file_station)
    

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

#file_city = "data\processed\cities\cities.shp"
#file_station = "data\processed\stations\stations.shp"
#list_input_city = ["Lisboa", "Ericeira", "Beja"]

#city_to_station(file_city, file_station, list_input_city) 