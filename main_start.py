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
DOWNLOAD_DIR = "data/original"
PROCESSED_DIR = "data/processed"

# Create the filenames for folder data/original
fname_rail_original = e.create_fname(TABLE_RAIL, DOWNLOAD_DIR)
fname_station_original = e.create_fname(TABLE_STAT, DOWNLOAD_DIR)
fname_city_original = e.create_fname(TABLE_CITY, DOWNLOAD_DIR)

# Create the filenames for folder data/processed
fname_rail_processed= e.create_fname(TABLE_RAIL, PROCESSED_DIR)
fname_station_processed = e.create_fname(TABLE_STAT, PROCESSED_DIR)
fname_city_processed = e.create_fname(TABLE_CITY, PROCESSED_DIR)


def extraction(config: dict) -> None:
    """ Runs extraction

        Args:
            config (str): configuration dictionary
    """
    if os.path.exists(DOWNLOAD_DIR):
        e.info("EXTRACTION HAS ALREADY BEEN DONE")
        return None

    e.info("EXTRACTION: START DATA EXTRACTION")
    url = config["url"]

    # Setting the queries for overpass API 
    query_rail = e.query_rail("Portugal")
    query_station = e.query_station("Portugal")
    query_city = e.query_city("Portugal")

    # Calling the queries in the get_data from API function
    e.info("EXTRACTION: DOWNLOADING RAILS DATA")
    rail_data = e.get_data(url, query_rail)

    e.info("EXTRACTION: DOWNLOADING STATION DATA")
    station_data = e.get_data(url, query_station)
   
    e.info("EXTRACTION: DOWNLOADING CITY DATA")
    city_data = e.get_data(url, query_city)
    
    # Saving data with file names rail, station, city
    e.info("EXTRACTION: SAVING RAIL DATA AS JSON/GEOJSON")
    e.save_as_json_geojson(rail_data, fname_rail_original) 

    e.info("EXTRACTION: SAVING STATION DATA AS JSON/GEOJSON")
    e.save_as_json_geojson(station_data, fname_station_original)

    e.info("EXTRACTION: SAVING STATION DATA AS JSON/GEOJSON")
    e.save_as_json_geojson(city_data, fname_city_original)
    
    e.info("EXTRACTION: COMPLETED")


def network_preprocessing(config: dict) -> None:
    """Runs transformation

    Args:
        config (dict): [description]
    """
    if os.path.exists(PROCESSED_DIR):
        e.info("PREPROCESSING HAS ALREADY BEEN DONE")
        return None

    e.info("PREPROCESSING: STARTED")
        
    # Reading the .json files for rail, stations, city from the folder data/original
    rail_json = e.open_json(fname_rail_original)
    station_json = e.open_json(fname_station_original)
    city_json = e.open_json(fname_city_original)

    # Convert the OSM JSON to a gpd.GeoDataFrame and store in the folder data/processed as shapefile
    e.info("PREPROCSSING: DATA CONVERSION STARTED")

    cols_station = config["columns_station"]
    station_gdf = e.overpass_json_to_gpd_gdf(station_json, cols_station)
    station_gdf = e.reproject(station_gdf, "EPSG:32629")

    cols_rails = config["columns_rail"]
    rail_gdf = e.overpass_json_to_gpd_gdf(rail_json, cols_rails)
    rail_gdf = e.reproject(rail_gdf, "EPSG:32629")

    cols_city = config["columns_city"]
    city_gdf = e.overpass_json_to_gpd_gdf(city_json, cols_city)
    city_gdf = e.reproject(city_gdf, "EPSG:32629")

    # Preprocess data to make it routable
    e.info("PREPROCSSING: PREPARE ROUTABLE NETWORK")
        # snap stations to rail
    e.info("PREPROCESSING: SNAP_STATIONS_TO_RAIL")
    station_gdf = r.snap_with_spatial_index(station_gdf, rail_gdf, 50)
        # connect station for changing in rail_gdf
    e.info("PREPROCESSING: CONNECT STATIONS")
    rail_gdf = r.connect_stations(station_gdf, "name" ,rail_gdf)
        # split rails at nearest station
    e.info("PREPROCESSING: SPLIT_TO_SEGMENTS")
    rail_gdf = r.split_line_by_nearest_points(rail_gdf, station_gdf)

    # save as shapefiles
    e.save_as_shp(station_gdf, fname_station_processed)
    e.save_as_shp(rail_gdf, fname_rail_processed)
    e.save_as_shp(city_gdf, fname_city_processed)

    e.info("PREPROCESSING: COMPLETED")

def routing(list_input_city):

    # First, open shapefiles as GeoDataFrames
    city_gdf = gpd.read_file(fname_city_processed)
    station_gdf = gpd.read_file(fname_station_processed)   
    rail_gdf = gpd.read_file(fname_rail_processed)

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


def load(config: dict, chunksize: int=1000) -> None:
    """Runs load

    Args:
        config (dict): configuration dictionary
        chunksize (int): the number of rows to be inserted at one time
    """
    try:
        fname = config["fname"]
        db = e.DBController(**config["database"])
        e.info("LOAD: READING DATA")
        #df = e.read_csv(f"{PROCESSED_DIR}/{fname}")
        e.info("LOAD: DATA READ")
        e.info("LOAD: INSERTING DATA INTO DATABASE")
        #db.insert_data(df, DB_SCHEMA, TABLE, chunksize=chunksize)
        e.info("LOAD: DONE")
    except Exception as err:
        e.die(f"LOAD: {err}")


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
    
    country = e.inputs_country()
    list_input_city = e.inputs_city()

    # Perform the extraction
    extraction(config)
    #msg = time_this_function(extraction, config=config)
    #e.info(msg)

    #Perform the transformation
    network_preprocessing(config)
    #msg = time_this_function(transformation, config=config)
    #e.info(msg)
    
    routing(list_input_city)

    #load(config, chunksize=10000)
    #msg = time_this_function(load, config=config, chunksize=1000)
    #e.info(msg)


if __name__ == "__main_start__":
    config_file = parse_args()
    main(config_file)