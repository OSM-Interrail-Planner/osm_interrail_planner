import etl as e
import argparse
import time
import sys


DB_SCHEMA = "sa"
TABLE_RAIL = "railways"
TABLE_STAT = "stations"
TABLE_CITY = "cities"
DOWNLOAD_DIR = "data/original"
PROCESSED_DIR = "data/processed"



def extraction(config: dict) -> None:
    """ Runs extraction

        Args:
            config (str): configuration dictionary
    """
    e.info("EXTRACTION: START DATA EXTRACTION")
    url = config["url"]

    # Setting the queries for overpass API 
    query_rail = e.query_rail("Portugal")
    query_station = e.query_station("Portugal")
    query_city = e.query_city("Portugal")

    # Calling the queries in the get_data from API function
    e.info("EXTRACTION: DOWNLOADING RAILS DATA")

    n = 0
    while n < 10:

        try:
            rail_data = e.get_data(url, query_rail)
            
        except:
            n += 1
            print(f"download attempt: {n}")

        else:
            break


    e.info("EXTRACTION: DOWNLOADING STATION DATA")

    n = 0
    while n < 10:

        try:
            station_data = e.get_data(url, query_station)
        
        except:
            n += 1
            print(f"download attempt: {n}")

        else:
            break

    
    e.info("EXTRACTION: DOWNLOADING CITY DATA")

    n = 0
    while n < 10:
        
        try:
            city_data = e.get_data(url, query_city)


        except:
            n += 1
            print(f"download attempt: {n}")
            
        else:
            break
    

    

    # Saving data with file names rail, station, city
    fname_rail = config["fname_rail"]
    fname_rail = f"{DOWNLOAD_DIR}/{fname_rail}"
    e.info("EXTRACTION: SAVING RAIL DATA AS JSON/GEOJSON")
    e.save_as_json_geojson(rail_data, fname_rail)

    fname_station = config["fname_station"]
    fname_station = f"{DOWNLOAD_DIR}/{fname_station}"
    e.info("EXTRACTION: SAVING STATION DATA AS JSON/GEOJSON")
    e.save_as_json_geojson(station_data, fname_station)

    fname_city = config["fname_city"]
    fname_city = f"{DOWNLOAD_DIR}/{fname_city}"
    e.info("EXTRACTION: SAVING STATION DATA AS JSON/GEOJSON")
    e.save_as_json_geojson(city_data, fname_city)
    
    e.info("EXTRACTION: COMPLETED")

def transformation(config: dict) -> None:
    """Runs transformation

    Args:
        config (dict): [description]
    """
    e.info("TRANSFORMATION: START TRANSFORMATION")
    e.info("TRANSFORMATION: READING DATA")
    fname = config["fname"]
    df = e.read_csv(f"{DOWNLOAD_DIR}/{fname}")
    e.info("TRANSFORMATION: DATA READING COMPLETED")
    e.info("TRANSFORMATION: DATA SUBSETTING")
    cols = config["columns"]

    # Select only the rows in the analysis period
    # What happens if there is no data in this period?
    # What should we do in that case?
    start_date = config["period"]["start_date"]
    end_date = config["period"]["end_date"]
    df = df.loc[(start_date <= df["pickup_datetime"]) & (df["dropoff_datetime"] <= end_date)]

    # This is a simple transformation, but simple transformations
    # can be quite tricky. Consider what happens if there is
    # a column in cols not present in df?
    # How can we save that?
    df = df[cols]
    e.info("TRANSFORMATION: SUBSETTING DONE")
    e.info("TRANSFORMATION: SAVING TRANSFORMED DATA")
    e.write_csv(df, fname=f"{PROCESSED_DIR}/{fname}", sep=",")
    e.info("TRANSFORMATION: SAVED")
    e.info("TRANSFORMATION: COMPLETED")


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
        df = e.read_csv(f"{PROCESSED_DIR}/{fname}")
        e.info("LOAD: DATA READ")
        e.info("LOAD: INSERTING DATA INTO DATABASE")
        db.insert_data(df, DB_SCHEMA, TABLE, chunksize=chunksize)
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
    config = e.read_config(config_file)
    #msg = time_this_function(extraction, config=config)
    #e.info(msg)
    extraction(config)
    #transformation(config)
    #load(config, chunksize=10000)
    #msg = time_this_function(transformation, config=config)
    #e.info(msg)
    #msg = time_this_function(load, config=config, chunksize=1000)
    #e.info(msg)


if __name__ == "__main__":
    config_file = parse_args()
    main(config_file)
