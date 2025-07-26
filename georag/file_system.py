import os 

from .utils import alphanumeric 

# Data paths
def get_data_path(place : str):
    proj_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    name = alphanumeric(place)
    return os.path.join(proj_dir, "data", name)
