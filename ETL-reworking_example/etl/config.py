import yaml
from .logs import die


def read_config(fname: str) -> dict:
    """ Reads the configuration file

    Args:
        fname (str): the configuration file

    Returns:
        dict: a dictionary with the configuration
    """
    try:
        with open(fname) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
    except yaml.YAMLError as err:
        die(err)
    return data
