import json
import shapely.geometry as sg
import geopandas as gpd
import osm2geojson as o2g


def open_json(filename: str):
    """
    This function loads in the json file stored in data/original 

    Args:
        filename(str): Filename where the data is stored
    Returns:
        A json file in dictionary format
    """
    with open(f"{filename}.json") as file1:
        data = json.load(file1)
    return data


# Besides the geometry columns we want to extract attributes of the OSM tags and store them in columns
# Therefore this function creates dictionaries for each tag from the raw OSM JSON and is afterwards 
# implemented in the big conversion function
def append_tags(element: dict, new_element: dict, desired_tags: dict):
    """
    This function takes the desired tags and creates a dictionary for every tag. 
    This dictionary is appended to an element of the conversion from Overpass json to gpd.geodataframe.
    Therefore each single dictionary gets its own coloumn
    
    Args:
        element: one old element dictionary of OSM-Json to take the information from
        new_element: new element dictionary to write the information in 
        desired_tags: list[str] list of strings containing the desired tags as columns in the gpd.gdf
    Return:
        new_element: dictionary with new tags
    """
    for tag in desired_tags.keys():
        # condition: There must be a dictionary with tags AND the desired tag in it
        if ('tags' in element.keys()) and (tag in element['tags'].keys()): 
            value = element['tags'][tag] # element['tags']['population'] = string 80 000
            # if the tag/column is going to be converted to a float -> delete empty spaces of string
            if desired_tags[tag] == 'float':
                new_element[tag] = value.replace(" ", "")
            else:
                new_element[tag] = value
        else:
            pass
    return new_element


# Implement the conversion function from the raw OSM JSON file to a geopandas geodataframe
def overpass_json_to_gpd_gdf(overpass_json: dict, desired_tags: dict, geometry_list: list) -> gpd.GeoDataFrame:
    """
    This function takes a overpass json file containing nodes or ways and transforms it 
    into an geopandas geodataframe
        
    Args:
        desired_tags (list): Containing tags to be new column in gpd.gdf
        overpass_json: A json dictionary containing a list of elements (noded or ways)
        geometry (list): List of accepted geometry types (Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon)

        For OSM node elements each element is structured as following:
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
             
        For OSM ways each element is structured as following:
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
        
        # 1. This part is for nodes of OSM
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
        
        # 2. This part is for ways of OSM
        if element['type'] == 'way' and 'center' not in element.keys():
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

        # 3. This part is for polygons of relation of OSM
        if element['type'] == 'relation' and 'center' not in element.keys():
            # create a new_geometry dictionary
            # data structure for new_geometry to be shaped with function shapely.geometry.shape() afterwards
            """
            [{
                'type': 'Polygon',
                'coordinates': [(lon, lat), (lon, lat)]
            }]
            """
            new_geometry = {}
            # change 'type' to 'LineString'
            new_geometry['type'] = 'Polygon'
            # create a list of geometries
            geometry = []
            for member in element['members']:
                if member['type'] == 'way':
                    for node in member['geometry']:
                        lon = node['lon']
                        lat = node['lat']
                        geometry.append((lon, lat))
            new_geometry['coordinates'] = geometry

        # 4. This part is for ways and relations with a center point
        if (element['type'] == 'way' and 'center' in element.keys()) or (element['type'] == 'relation' and 'center' in element.keys()):
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
            lon = element['center']['lon']
            lat = element['center']['lat']
            geometry = [(lon, lat)]
            new_geometry['coordinates'] = geometry
            
        # Shape the new_geometry {'type': 'Linestring OR Point', 'coordinates': [(lat, lon) OR, (lat, lon)]} 
        # and append it as under the tag 'geometry' in the new_element dictionary
        if new_geometry['type'] == 'Polygon':
            new_element['geometry'] = sg.Polygon(new_geometry['coordinates'])
        else:
            new_element['geometry'] = sg.shape(new_geometry)

        # Append atribute tags if available
        append_tags(element, new_element, desired_tags)

        # Append each single new element (dict) to the new list of new elements [dict1, dict2]
        new_data.append(new_element)
    
    # Transform it to a gpd geodataframe
    gdf = gpd.GeoDataFrame(new_data, crs="EPSG:4326")

    # Subset the data frame to only contain accepted geometries
    if geometry_list != []:
        gdf['geom_type'] = gdf.apply(lambda row: row["geometry"].geom_type, axis=1)
        new = gdf['geom_type'].isin(geometry_list)
        gdf = gdf[new]
        gdf = gdf.drop(['geom_type'], axis=1)

    return gdf


def convert_to_gdf(json_file: dict, desired_tags: dict, geometry_list: list) -> gpd.GeoDataFrame:
    """This function converts an Overpass json to gpd. GeoDataFrame with the desired attributes

    Args:
        json_file (json): Raw data json from OSM
        desired_tags (dict): OSM tags which should be included as columns in the GeoDataFrame
        geometry (list): List of accepted geometry types (Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon)

    Returns:
        gpd.GeoDataFrame
    """
    shape = o2g.json2shapes(json_file)
    shape_gdf = gpd.GeoDataFrame(shape, geometry = "shape", crs="EPSG:4326")

    # create function for extracting the desired OSM tags into GeoDataFrame columns
    def extract_value(row, key):
        try:
            value = row["properties"]["tags"][key]
        except:
            value = 'nan'
        
        return value

    # iterate over all desired tags
    for tag in desired_tags.keys():
        shape_gdf[tag] = shape_gdf.apply(lambda row: extract_value(row, tag), axis=1)
    
    shape_gdf = shape_gdf.rename_geometry('geometry')
    shape_gdf = shape_gdf.drop(["properties"], axis=1)

    # Subset the data frame to only contain accepted geometries
    if geometry_list != []:
        shape_gdf['geom_type'] = shape_gdf.apply(lambda row: row["geometry"].geom_type, axis=1)
        new = shape_gdf['geom_type'].isin(geometry_list)
        shape_gdf = shape_gdf[new]
        shape_gdf = shape_gdf.drop(['geom_type'], axis=1)

    return shape_gdf


def way_to_polygon(geo_df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """This function converts possible LineStrings and MultiLineStrings into Polygons and Multipolygons

    Args:
        geo_df (gpd.GeoDataFrame): GeoDataFrame with the LineStrings and MultiLineStrings as geometry

    Returns:
        gpd.GeoDataFrame: GeoDataFrame with the Polygons and Multipolygons as geometry
    """
    # create a function for checking the geometry type of a GeoDataFrame row
    def check_geom_type(row):
        if row["geometry"].geom_type == 'LineString':
            try:
                geo = sg.Polygon(list(row["geometry"].coords))
            except:
                geo = None
            return geo
        else:
            return row["geometry"]

    geo_df["geometry"] = geo_df.apply(lambda row: check_geom_type(row), axis=1)
    geo_df = geo_df[geo_df["geometry"]!=None]

    return geo_df


def reproject(geodf: gpd.GeoDataFrame, epsg: str) -> gpd.GeoDataFrame:
    """This function reprojects a GeoDataFrame to the given EPSG-Code

    Args:
        geodf (gpd.GeoDataFrame): Input GeoDataFrame
        epsg (str): EPSG-Code in format: "EPSG:NUMBER"

    Returns:
        gpd.GeoDataFrame: Reprojected GeoDataFrame
    """

    return geodf.to_crs(crs=epsg)


def save_as_shp(geo_df: gpd.GeoDataFrame, fname: str) -> None:
    """
    This function saves a geopandas.Geodataframe as a shapefile

    Args:
        geodf (gpd.GeoDataFrame): The geodata
        fname (str): directory path to store the data 

    Returns:
        gpd.GeoDataFrame
    """
    geo_df.to_file(driver = 'ESRI Shapefile', filename= f"{fname}")


def all_cities_list(city_gdf: gpd.GeoDataFrame) -> list:
    """
    function to extract a list of citys from cities GeoDataFrame

    Args:
        city_gdf (gpd.GeoDataFrame): The merged gdf of all cities of the countries
    
    Returns:
        An alphabetically sorted list of all city names
    """
    city_gdf = city_gdf.replace(to_replace= "/", value= ";", regex=True)
    all_cities_list = list(city_gdf['name'])
    return all_cities_list
