import etl as e
import routing as r
import argparse
import time
import sys
import geopandas as gpd
import os
import shutil

DB_SCHEMA = "sa"
TABLE_RAIL = "railways"
TABLE_STAT = "stations"
TABLE_CITY = "cities"
TABLE_HERI = "heritage"
DOWNLOAD_DIR = "data/original"
PROCESSED_DIR = "data/processed"

# Create the filenames for folder data/original
fname_rail_original = e.create_fname(TABLE_RAIL, DOWNLOAD_DIR)
fname_station_original = e.create_fname(TABLE_STAT, DOWNLOAD_DIR)
fname_city_original = e.create_fname(TABLE_CITY, DOWNLOAD_DIR)
fname_heri_original = e.create_fname(TABLE_HERI, DOWNLOAD_DIR)

# Create the filenames for folder data/processed
fname_rail_processed= e.create_fname(TABLE_RAIL, PROCESSED_DIR)
fname_station_processed = e.create_fname(TABLE_STAT, PROCESSED_DIR)
fname_city_processed = e.create_fname(TABLE_CITY, PROCESSED_DIR)
fname_heri_processed = e.create_fname(TABLE_HERI, PROCESSED_DIR)


def extraction(config: dict, countries: str) -> None:
    """ Runs extraction

        Args:
            config (str): configuration dictionary
            country (str): The country where you want to travel in Europe in international spelling
    """
    
    e.info("EXTRACTION: START DATA EXTRACTION")
    url = config["url"]

    for country in countries:
        # Railway data from OSM
        if os.path.exists(f"{fname_rail_original}_{country}.geojson") == False:
            query_rail = e.query_rail(country)
            e.info(f"EXTRACTION: DOWNLOADING RAILS DATA IN {country}")
            rail_data = e.get_data(url, query_rail)
            e.save_as_json_geojson(rail_data, f"{fname_rail_original}_{country}")
        else:
            e.info(f"EXTRACTION OF RAILS DATA IN {country} HAS ALREADY BEEN DONE")
        
        # Station data from OSM
        if os.path.exists(f"{fname_station_original}_{country}.geojson") == False: 
            query_station = e.query_station(country)
            e.info(f"EXTRACTION: DOWNLOADING STATION DATA IN {country}")
            station_data = e.get_data(url, query_station)
            e.save_as_json_geojson(station_data, f"{fname_station_original}_{country}")
        else:
            e.info(f"EXTRACTION OF STATIONS DATA IN {country} HAS ALREADY BEEN DONE")

        # City data from OSM
        if os.path.exists(f"{fname_city_original}_{country}.geojson") == False: 
            query_city = e.query_city(country)
            e.info(f"EXTRACTION: DOWNLOADING CITY DATA IN {country}")
            city_data = e.get_data(url, query_city)
            e.save_as_json_geojson(city_data, f"{fname_city_original}_{country}")
        else:
            e.info(f"EXTRACTION OF CITY DATA IN {country} HAS ALREADY BEEN DONE")

        # Heritage data from OSM
        if os.path.exists(f"{fname_heri_original}_{country}.geojson") == False: 
            query_heri = e.query_heritage(country)
            e.info(f"EXTRACTION: DOWNLOADING HERITAGE DATA IN {country}")
            heri_data = e.get_data(url, query_heri)
            e.save_as_json_geojson(heri_data, f"{fname_heri_original}_{country}")
        else:
            e.info(f"EXTRACTION OF HERITAGE DATA IN {country} HAS ALREADY BEEN DONE")

        e.info(f"EXTRACTION: COMPLETED IN {country}")

    e.info("EXTRACTION: COMPLETED")


def network_preprocessing(config: dict, countries) -> None:
    """Runs transformation

    Args:
        config (dict): [description]
    """
    if os.path.exists(f"{fname_rail_processed}") and os.path.exists(f"{fname_city_processed}") and os.path.exists(f"{fname_station_processed}"):
        
        city_all_gdf = gpd.read_file(fname_city_processed)
        all_cities_list = e.all_cities_list(city_all_gdf)

        e.info("PREPROCESSING HAS ALREADY BEEN DONE")

        return all_cities_list

    e.info("PREPROCESSING: STARTED")

    # create general gpd.GeoDataFrame
    rail_all_gdf = gpd.GeoDataFrame()
    station_all_gdf = gpd.GeoDataFrame()
    city_all_gdf = gpd.GeoDataFrame()
    heri_all_gdf = gpd.GeoDataFrame()

    for country in countries:    
        # Reading the .json files for rail, stations, city from the folder data/original
        rail_json = e.open_json(f"{fname_rail_original}_{country}")
        station_json = e.open_json(f"{fname_station_original}_{country}")
        city_json = e.open_json(f"{fname_city_original}_{country}")
        heri_json = e.open_json(f"{fname_heri_original}_{country}")

        # Convert the OSM JSON to a gpd.GeoDataFrame and store in the folder data/processed as shapefile
        e.info(f"PREPROCSSING: DATA CONVERSION FOR {country} STARTED")

        cols_station = config["columns_station"]
        station_gdf = e.overpass_json_to_gpd_gdf(station_json, cols_station)
        station_gdf = e.reproject(station_gdf, "EPSG:32629")
        station_all_gdf = station_all_gdf.append(station_gdf, ignore_index=True)

        cols_rails = config["columns_rail"]
        rail_gdf = e.overpass_json_to_gpd_gdf(rail_json, cols_rails)
        rail_gdf = e.reproject(rail_gdf, "EPSG:32629")
        rail_all_gdf = rail_all_gdf.append(rail_gdf, ignore_index=True)

        cols_city = config["columns_city"]
        city_gdf = e.overpass_json_to_gpd_gdf(city_json, cols_city)
        city_gdf = e.reproject(city_gdf, "EPSG:32629")
        city_all_gdf = city_all_gdf.append(city_gdf, ignore_index=True)

        cols_heri = config["columns_heri"]
        heri_gdf = e.overpass_json_to_gpd_gdf(heri_json, cols_heri)
        heri_gdf = e.reproject(heri_gdf, "EPSG:32629")
        heri_all_gdf = heri_all_gdf.append(heri_gdf, ignore_index=True)

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
    e.save_as_shp(station_all_gdf, fname_station_processed)
    e.save_as_shp(rail_all_gdf, fname_rail_processed)
    e.save_as_shp(city_all_gdf, fname_city_processed)
    e.save_as_shp(heri_all_gdf, fname_heri_processed)

    e.info("PREPROCESSING: COMPLETED")

    all_cities_list = e.all_cities_list(city_all_gdf)

    return all_cities_list


def routing(list_input_city):

    # First, open shapefiles as GeoDataFrames
    city_gdf = gpd.read_file(fname_city_processed)
    station_gdf = gpd.read_file(fname_station_processed)   
    rail_gdf = gpd.read_file(fname_rail_processed)
    heri_gdf = gpd.read_file(fname_heri_processed)

    # connecting the input city list to the nearest station
    gdf_input_stations = r.city_to_station(city_gdf, station_gdf, list_input_city)

    e.info("ROUTING: SOLVING TSP STARTED")
    #solving the travelling sales man problem ("TSP")
    dict_distance_matrix = r.create_distance_matrix(gdf_input_stations, rail_gdf, mirror_matrix=True)
    plan_output = r.tsp_calculation(dict_distance_matrix)

    # create GeoDataFrame ot of the plan_output
    best_route = r.merge_tsp_solution(dict_distance_matrix, plan_output, crs="EPSG:32629")
    e.info("ROUTING: SOLVING TSP COMPLETED")
    
    e.save_as_shp(best_route, 'data/best_route')

    shutil.make_archive('data/best_route', 'zip', 'data/best_route')

    # select cities in proximity
    close_cities = r.points_on_way(city_gdf, best_route, list_input_city, 5000, crs="EPSG:32629")
    e.save_as_shp(close_cities, 'data/close_cities')

    # select heritages in proximity
    close_heris = r.points_on_way(heri_gdf, best_route, [], 5000, crs="EPSG:32629")
    e.save_as_shp(close_heris, 'data/close_heris')


def parse_args() -> str:
    """ Reads command line arguments

        Returns:
            the name of the configuration file
    """
    parser = argparse.ArgumentParser(description="GPS: ETL working example")
    parser.add_argument("--config_file", required=True, help="The configuration file")
    args = parser.parse_args()
    return args.config_file

def time_this_function(func, **kwargs) -> str:
    """ Times function `func`

        Args:
            func (function): the function we want to time

        Returns:
            a string with the execution time
    """
    import time
    t0 = time.time()
    func(**kwargs)
    t1 = time.time()
    return f"'{func.__name__}' EXECUTED IN {t1-t0:.3f} SECONDS"

def main(config_file: str) -> None:
    """Main function for ETL

    Args:
        config_file (str): configuration file
    """
    # Read the config file
    config = e.read_config(config_file)
    
    countries = e.inputs_country()

    # Perform the extraction
    extraction(config, countries)
    #msg = time_this_function(extraction, config=config)
    #e.info(msg)

    #Perform the transformation
    all_cities_list = network_preprocessing(config, countries)
    #msg = time_this_function(transformation, config=config)
    #e.info(msg)
    
    list_input_city = e.inputs_city(all_cities_list)

    routing(list_input_city)


if __name__ == "__main__":
    config_file = parse_args()
    main(config_file)
