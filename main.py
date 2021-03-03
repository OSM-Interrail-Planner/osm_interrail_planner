import etl as e
import routing as r
import time
import sys
import geopandas as gpd
import os
import shutil

URL = "http://overpass-api.de/api/interpreter"
NAME_RAIL = "railways"
COLUMNS_RAIL = {"name": str}
NAME_STAT = "stations"
COLUMNS_STAT = {"name": str, "name:en": str, "network": str}
NAME_CITY = "cities"
COLUMNS_CITY = {"name": str, "name:en": str, "place": str, "population": str}
NAME_HERI = "heritage"
COLUMNS_HERI = {"name": str, "heritage": str}
NAME_NATU = "nature"
COLUMNS_NATU = {"name": str, "website": str}
DOWNLOAD_DIR = "data/original"
PROCESSED_DIR = "data/processed"
EPSG = "EPSG:32629"

# Create the filenames for folder data/original
fname_rail_original = e.create_fname(NAME_RAIL, DOWNLOAD_DIR)
fname_station_original = e.create_fname(NAME_STAT, DOWNLOAD_DIR)
fname_city_original = e.create_fname(NAME_CITY, DOWNLOAD_DIR)
fname_heri_original = e.create_fname(NAME_HERI, DOWNLOAD_DIR)
fname_natu_original = e.create_fname(NAME_NATU, DOWNLOAD_DIR)

# Create the filenames for folder data/processed
fname_rail_processed= e.create_fname(NAME_RAIL, PROCESSED_DIR)
fname_station_processed = e.create_fname(NAME_STAT, PROCESSED_DIR)
fname_city_processed = e.create_fname(NAME_CITY, PROCESSED_DIR)
fname_heri_processed = e.create_fname(NAME_HERI, PROCESSED_DIR)
fname_natu_processed = e.create_fname(NAME_NATU, PROCESSED_DIR)

def extraction(countries: list) -> None:
    """ Runs extraction of data from OpenStreetMap via Overpass API

        Args:
            country (list): The countries where you want to travel in Europe in international spelling
    """
    
    e.info("EXTRACTION: START DATA EXTRACTION")

    for country in countries:
        # Railway data from OSM
        if os.path.exists(f"{fname_rail_original}_{country}.geojson") == False:
            query_rail = e.query_rail(country)
            e.info(f"EXTRACTION: DOWNLOADING RAILS DATA IN {country}")
            rail_data = e.get_data(URL, query_rail, 'Railways', country)
            e.save_as_json_geojson(rail_data, f"{fname_rail_original}_{country}")
        else:
            e.info(f"EXTRACTION OF RAILS DATA IN {country} HAS ALREADY BEEN DONE")
        
        # Station data from OSM
        if os.path.exists(f"{fname_station_original}_{country}.geojson") == False: 
            query_station = e.query_station(country)
            e.info(f"EXTRACTION: DOWNLOADING STATION DATA IN {country}")
            station_data = e.get_data(URL, query_station, 'Stations', country)
            e.save_as_json_geojson(station_data, f"{fname_station_original}_{country}")
        else:
            e.info(f"EXTRACTION OF STATIONS DATA IN {country} HAS ALREADY BEEN DONE")

        # City data from OSM
        if os.path.exists(f"{fname_city_original}_{country}.geojson") == False: 
            query_city = e.query_city(country)
            e.info(f"EXTRACTION: DOWNLOADING CITY DATA IN {country}")
            city_data = e.get_data(URL, query_city, 'City', country)                
            e.save_as_json_geojson(city_data, f"{fname_city_original}_{country}")
        else:
            e.info(f"EXTRACTION OF CITY DATA IN {country} HAS ALREADY BEEN DONE")

        # Heritage data from OSM
        if os.path.exists(f"{fname_heri_original}_{country}.geojson") == False: 
            query_heri = e.query_heritage(country)
            e.info(f"EXTRACTION: DOWNLOADING HERITAGE DATA IN {country}")
            heri_data = e.get_data(URL, query_heri, 'Heritage', country)
            e.save_as_json_geojson(heri_data, f"{fname_heri_original}_{country}")
        else:
            e.info(f"EXTRACTION OF HERITAGE DATA IN {country} HAS ALREADY BEEN DONE")

        # Nature data from OSM
        if os.path.exists(f"{fname_natu_original}_{country}.geojson") == False: 
            query_natu = e.query_nature(country)
            e.info(f"EXTRACTION: DOWNLOADING NATURE DATA IN {country}")
            natu_data = e.get_data(URL, query_natu, 'Natural Parks', country)
            e.save_as_json_geojson(natu_data, f"{fname_natu_original}_{country}")
        else:
            e.info(f"EXTRACTION OF NATURE DATA IN {country} HAS ALREADY BEEN DONE")

        e.info(f"EXTRACTION: COMPLETED IN {country}")

    e.info("EXTRACTION: COMPLETED")


def network_preprocessing(countries: list) -> None:
    """This function is based on the packages etl (trans.py) and routing (preprocessing.py). It transforms json data
    and prepares a routable network. The data is stored as shapefiles in data/processed

    Args:
        countries (list): List of destination countries 
    """

    # create a string for country names to use in saving
    countries = list(countries)
    countries.sort()
    fname_country = "_".join(countries)

    # check if preprocessed data for the composition of countries exists already
    if os.path.exists(f"data/processed/z_database/{fname_country}") == True:
        e.info("PREPROCESSING HAS ALREADY BEEN DONE FOR THESE COUNTRIES")
        e.info("GETTING DATA FOR THESE COUNTRIES FROM PREPROCESSING STORAGE")
        # read and save the found combination in processed folder structure (like a update of processed/cites...)
        station_all_gdf = gpd.read_file(f"data/processed/z_database/{fname_country}/station")
        e.save_as_shp(station_all_gdf, fname_station_processed)

        rail_all_gdf = gpd.read_file(f"data/processed/z_database/{fname_country}/rail")
        e.save_as_shp(rail_all_gdf, fname_rail_processed)

        city_all_gdf = gpd.read_file(f"data/processed/z_database/{fname_country}/city")
        e.save_as_shp(city_all_gdf, fname_city_processed)

        heri_all_gdf = gpd.read_file(f"data/processed/z_database/{fname_country}/heri")
        e.save_as_shp(heri_all_gdf, fname_heri_processed)

        natu_all_gdf = gpd.read_file(f"data/processed/z_database/{fname_country}/natu")
        e.save_as_shp(natu_all_gdf, fname_natu_processed)

        city_all_gdf = city_all_gdf[city_all_gdf.name  != "nan"]
        all_cities_list = e.all_cities_list(city_all_gdf)

        return all_cities_list

    e.info("PREPROCESSING: STARTED")

    # create general gpd.GeoDataFrame
    rail_all_gdf = gpd.GeoDataFrame()
    station_all_gdf = gpd.GeoDataFrame()
    city_all_gdf = gpd.GeoDataFrame()
    heri_all_gdf = gpd.GeoDataFrame()
    natu_all_gdf = gpd.GeoDataFrame()

    for country in countries:  

        # Reading the .json files for rail, stations, city from the folder data/original
        rail_json = e.open_json(f"{fname_rail_original}_{country}")
        station_json = e.open_json(f"{fname_station_original}_{country}")
        city_json = e.open_json(f"{fname_city_original}_{country}")
        heri_json = e.open_json(f"{fname_heri_original}_{country}")
        natu_json = e.open_json(f"{fname_natu_original}_{country}")

        # Convert the OSM JSON to a gpd.GeoDataFrame and store in the folder data/processed as shapefile
        e.info(f"PREPROCSSING: DATA CONVERSION FOR {country} STARTED")

        station_gdf = e.convert_to_gdf(station_json, COLUMNS_STAT, ['Point', 'MultiPoint'])
        station_gdf = e.reproject(station_gdf, EPSG)
        if country == 'Greece' or country == 'North Macedonia':
            station_gdf["name"] = station_gdf["name:en"]
        station_all_gdf = station_all_gdf.append(station_gdf, ignore_index=True)

        rail_gdf = e.convert_to_gdf(rail_json, COLUMNS_RAIL, ['LineString', 'MulitLineString'])
        rail_gdf = e.reproject(rail_gdf, EPSG)
        rail_all_gdf = rail_all_gdf.append(rail_gdf, ignore_index=True)

        city_gdf = e.convert_to_gdf(city_json, COLUMNS_CITY, ['Point', 'MultiPoint'])
        city_gdf = e.reproject(city_gdf, EPSG)
        if country == 'Greece' or country == 'North Macedonia':
            city_gdf["name"] = city_gdf["name:en"]
        city_all_gdf = city_all_gdf.append(city_gdf, ignore_index=True)

        heri_gdf = e.overpass_json_to_gpd_gdf(heri_json, COLUMNS_HERI, ['Point', 'MultiPoint'])
        heri_gdf = e.reproject(heri_gdf, EPSG)
        heri_all_gdf = heri_all_gdf.append(heri_gdf, ignore_index=True)

        natu_gdf = e.convert_to_gdf(natu_json, COLUMNS_NATU, [])
        natu_gdf = e.reproject(natu_gdf, EPSG)
        natu_gdf = e.way_to_polygon(natu_gdf)
        natu_all_gdf = natu_all_gdf.append(natu_gdf, ignore_index=True)

    e.info("PREPROCSSING: MERGED ALL COUNTRIES")

    # Preprocess data to make it routable
    e.info("PREPROCESSING: START PREPARING ROUTABLE NETWORK")
        # snap stations to rail
    e.info("PREPROCESSING: SNAP STATIONS TO RAIL")
    station_all_gdf = r.snap_spatial_index(point_gdf=station_all_gdf, line_gdf=rail_all_gdf, offset=50)
        # connect station for changing in rail_gdf
    e.info("PREPROCESSING: CONNECTING STATIONS")
    rail_all_gdf = r.connect_points_spatial_index(point_gdf=station_all_gdf, line_gdf=rail_all_gdf, offset=500)
        # split rails at nearest station
    e.info("PREPROCESSING: SPLITTING TO SEGMENTS")
    rail_all_gdf = r.split_line_spatial_index(point_gdf=station_all_gdf, line_gdf=rail_all_gdf, offset=2)
    e.info("PREPROCESSING: ROUTABLE NETWORK COMPLETED")

    # save as shapefiles
    os.makedirs(f"data/processed/z_database/{fname_country}")
    e.save_as_shp(station_all_gdf, f"data/processed/z_database/{fname_country}/station")
    e.save_as_shp(station_all_gdf, fname_station_processed)
    e.save_as_shp(rail_all_gdf, f"data/processed/z_database/{fname_country}/rail")
    e.save_as_shp(rail_all_gdf, fname_rail_processed)
    e.save_as_shp(city_all_gdf, f"data/processed/z_database/{fname_country}/city")
    e.save_as_shp(city_all_gdf, fname_city_processed)
    e.save_as_shp(heri_all_gdf, f"data/processed/z_database/{fname_country}/heri")
    e.save_as_shp(heri_all_gdf, fname_heri_processed)
    e.save_as_shp(natu_all_gdf, f"data/processed/z_database/{fname_country}/natu")
    e.save_as_shp(natu_all_gdf, fname_natu_processed)

    e.info("PREPROCESSING: COMPLETED")

    city_all_gdf = city_all_gdf[city_all_gdf.name  != "nan"]
    all_cities_list = e.all_cities_list(city_all_gdf)
    
    return all_cities_list


def routing(list_input_city: list):
    """This function is based on the package routing. It finds the best route between the input cities and corresponding
    cultural sites, nature parks and close cities on the way. Everything is saved as shapefiles in data/route

    Args:
        list_input_city (list): List of input cities
    """
    # Check if there is still final route data and delete it
    if os.path.exists("data/route") == True:
        shutil.rmtree("data/route")
        os.makedirs("data/route")

    # Open shapefiles as GeoDataFrames
    city_gdf = gpd.read_file(fname_city_processed)
    station_gdf = gpd.read_file(fname_station_processed)   
    rail_gdf = gpd.read_file(fname_rail_processed)
    heri_gdf = gpd.read_file(fname_heri_processed)
    natu_gdf = gpd.read_file(fname_natu_processed)

    # connecting the input city list to the nearest station
    gdf_input_stations = r.city_to_station(city_gdf, station_gdf, list_input_city)

    e.info("ROUTING: SOLVING TSP STARTED")
    # solving the travelling sales man problem ("TSP")
    dict_distance_matrix = r.create_distance_matrix(gdf_input_stations, rail_gdf, mirror_matrix=True)
    # if no path could be found return the error city 
    if "error_city" in dict_distance_matrix.keys():
        return dict_distance_matrix

    plan_output = r.tsp_calculation(dict_distance_matrix)

    # create GeoDataFrame ot of the plan_output
    best_route = r.merge_tsp_solution(dict_distance_matrix, plan_output, crs=EPSG)
    e.info("ROUTING: SOLVING TSP COMPLETED")
    
    e.save_as_shp(best_route, 'data/route/best_route')

    # select cities in proximity
    close_cities = r.features_on_way(city_gdf, best_route, list_input_city, 5000, crs=EPSG)
    try:
        e.save_as_shp(close_cities, 'data/route/close_cities')
    except: e.info("no close cities on your best route")

    # select heritages in proximity
    close_heris = r.features_on_way(heri_gdf, best_route, [], 5000, crs=EPSG)
    try:
        e.save_as_shp(close_heris, 'data/route/close_heris')
    except: e.info("no close heritage sites on your best route")

    # select nature in proximity
    close_natus = r.features_on_way(natu_gdf, best_route, [], 20000, crs=EPSG)
    try:
        e.save_as_shp(close_natus, 'data/route/close_natus')
    except: e.info("no close natural parks on your best route")

    # select stations on the way
    #close_stations = r.features_on_way(station_gdf, best_route, [], 2000, crs=EPSG)
    #try:
    #    e.save_as_shp(close_stations, 'data/route/close_stations')
    #except: e.info("no close stations on your best route")

    return dict_distance_matrix