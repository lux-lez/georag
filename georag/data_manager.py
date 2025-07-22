import numpy as np
import os
import shapely
import geojson
import geopandas

def alphanumeric(name) -> str:
    '''
    Alphanumeric representation (ie. a-z or A-Z or 0-9 ) of a string.
    Useful for saving files as alphanumeric strings are guaranteed to be file system compatible across distributions.
    '''

    name = str(name) 

    # Replace accented and special characters with ASCII equivalents
    replacements = {
        "ä": "a", "Ä": "a", "ã": "a", "å": "a", "á": "a", "à": "a", "â": "a", "æ": "ae",
        "õ": "o", "ö": "o", "ó": "o", "ò": "o", "ô": "o", "ø": "o", "Ô": "I",
        "é": "e", "è": "e", "ê": "e", "ë": "e", "É": "E", "È": "E", "Ê": "E", "Ë": "E",
        "í": "i", "ì": "i", "î": "i", "ï": "i", "Í": "i", "Ì": "I", "Î": "I", "Ï": "I",
        "ñ": "n", "Ñ": "n",
        "ç": "c", "Ç": "c",
        "ß": "ss",
        "ú": "u", "ù": "u", "û": "u", "ü": "u", "Ú": "u", "Ù": "U", "Û": "U", "Ü": "U"
    }
    for orig, repl in replacements.items():
        name = name.replace(orig, repl)

    # Seperators    
    for sep in [" ", ".", ","]:
        name = name.replace(sep, "_")
    while "__" in name:
        name = name.replace("__", "_")

    # Filter alphanumeric digits 
    name  = "".join(filter(
        lambda x: x in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-",
        np.asarray([*name])
    ))

    return name

# Data paths

def get_data_path(place : str):
    proj_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(proj_dir, "data", alphanumeric(place))

def get_feature_path(place : str, name : str):
    return os.path.join( get_data_path(place), "features", alphanumeric(name) )
