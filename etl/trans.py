import geojson
import json
import shapely.geometry as sg
import geopandas as gpd
import os

# This will be our module for the transformation functions

def open_json(filename):
    """
    This function loads in the json file stored by osm_download
    Args:
    filename:str = Filename where the data is stored
    Returns:
    A json file in dictionary format
    """
    with open(f"{filename}.json") as file1:
        data = json.load(file1)
    return data


# Besides the geometry columns we want to extract attributes of the OSM tags and store them in columns
# Therefore this function creates dictionaries for each tag from the raw OSM JSON and is afterwards 
# implemented in the big conversion function
def append_tags(element, new_element, desired_tags: list):
    """
    This function takes the desired tags and create a dictionary for every tag. 
    This dictionary is appended to an element of the conversion from Overpass json to gpd.geodataframe.
    Therefore each single dictionary gets its own coloumn
    
    Args:
        element: old element dictionary to take the information from
        new_element: new element dictionary to write the information in 
        desired_tags: list[str] list of strings containing the desired tags as columns in the gpd.gdf
    Return:
        new_element: dictionary with new tags
    """
    # Make a for loop for every tag in the list desired tags
    for tag in desired_tags:
        # condition: There must be a dictionary with tags AND the desired tag in it
        if ('tags' in element.keys()) and (tag in element['tags'].keys()): 
            new_element[tag] = element['tags'][tag]
        else:
            new_element[tag] = None
    return new_element


# Implement the conversion function from the raw OSM JSON file to a geopandas geodataframe
def overpass_json_to_gpd_gdf(overpass_json, desired_tags) -> gpd.GeoDataFrame:
    """
        This function takes a overpass json file containing nodes or ways and transforms it 
        into an geopandas geodataframe
        
        Args:
            desired_tags: list[str] containing tags to be new column in gpd.gdf
            
            overpass_json: a json dictionary containing a list of elements (noded or ways)
            
            For node elements each element is structured as following:
            [
             first_element,
             # this is an element:
             {'type': 'node', 
              'id': 25414208, 
              'lat': 38.7404678, 
              'lon': -9.1656799, 
              'tags': {'local_ref': '3',...},
             },
             last_element
             ]
             
            For the ways each element is structured as following:
            [
            first_element,
            # this is an element
            {'type': 'way',
             'geometry': [{'lat': lat, 'lon': lon}, {'lat': lat, 'lon': lon}],
             'tags': {'maxspeed': '190', ...}
            },
             last_element
            ]
            
        Returns:
            gpd.gdf: a geopandas geodataframe 
            
            Based on the conversion from a following list of dictionaries:
            [first_ element,
             # this is an element
             {'geometry': shape.object,
              'desired_tag1': 'value1',
              'desired_tag2': 'value2'
             },
             last_element
             ]
    """

    new_data = []
    for element in overpass_json['elements']:
        # create a new element dictionary which stands for one element
        new_element = {}
        
        # 1. This first part is for nodes of OSM
        if element['type'] == 'node':
            # create a new_geometry dictionary
            # data structure for new_geometry to be shaped with function shapely.geometry.shape() afterwards
            """
            [{
                'type': 'Point',
                'coordinates': (lon, lat)
            }]
            """
            new_geometry = {}
            # change 'type' to 'Point'
            new_geometry['type'] = 'Point'
            # create a new geometry point as tuple (lat, lon)    
            lon = element['lon']
            lat = element['lat']
            geometry = [(lon, lat)]
            new_geometry['coordinates'] = geometry
        
        # 2. This second part is for ways of OSM
        if element['type'] == 'way':
            # create a new_geometry dictionary
            # data structure for new_geometry to be shaped with function shapely.geometry.shape() afterwards
            """
            [{
                'type': 'LineString',
                'coordinates': [(lon, lat), (lon, lat)]
            }]
            """
            new_geometry = {}
            # change 'type' to 'LineString'
            new_geometry['type'] = 'Linestring'
            # create a list of geometries
            geometry = [] 
            for node in element['geometry']:
                lon = node['lon']
                lat = node['lat']
                geometry.append((lon, lat))
            new_geometry['coordinates'] = geometry
            
        # shape the new_geometry {'type': 'Linestring OR Point', 'coordinates': [(lat, lon) OR, (lat, lon)]} 
        # and append it as under the tag 'geometry' in the new_element dictionary
        new_element['geometry'] = sg.shape(new_geometry)

        # append atribute tags if available
        append_tags(element, new_element, desired_tags)

        # append each single new element (dict) to the new list of new elements [dict1, dict2]
        new_data.append(new_element)
    
    #transform it to a gpd geodataframe
    return gpd.GeoDataFrame(new_data, crs="EPSG:4326")


def save_as_shp(geodf: gpd.GeoDataFrame, fname: str) -> None:
    """
    This function saves a geopandas.Geodataframe as a shapefile

    Args:
        geodf (gpd.GeoDataFrame): The geodata
        fname (str): directory path to store the data 
    """

    geodf.to_file(driver = 'ESRI Shapefile', filename= f"{fname}")
    return