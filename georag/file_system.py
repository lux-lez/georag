import os 
import time, datetime 

from .utils import alphanumeric 

# Data paths
def get_data_path(place : str):
    proj_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    name = alphanumeric(place)
    return os.path.join(proj_dir, "data", name)

def vectordb_exists(place : str):
    path = get_data_path(place)
    vec_filename = "vector.db"
    vec_path = os.path.join(path, vec_filename)
    return os.path.isdir(vec_path)

