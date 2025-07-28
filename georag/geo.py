import os
import numpy as np
import pandas as pd
import osmnx
from typing import Union
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from collections import namedtuple

from .utils import alphanumeric
from .file_system import get_data_path
from .constants.amenity import AmenityByCategory
from .timing import timer_start, timer_end

def geolocate(place_name, user_agent="geo_checker"):
    """ Geograohically locate a place using Nominatim.
    Needs internet connection to run if the place has not been downloaded yet.
    Args:
        place_name (str): The name of the place to geolocate.
        user_agent (str): User agent for Nominatim requests.
    Returns:
        Location object or None if geocoding fails.
    """
    try:
        place = place_name.split(",")[0]
        place = alphanumeric(place).split("_")[0]
        proj_path = os.path.dirname(os.path.dirname(__file__))
        data_path = os.path.join(proj_path, "data")
        for f in os.listdir(data_path):
            f_path = os.path.join(data_path, f) 
            if os.path.isdir(f_path):
                if f.split("_")[0] == place:
                    vecdb_path = os.path.join(data_path, f, "vectors.npz")
                    if os.path.isfile(vecdb_path):
                        nt = namedtuple('LocalLocator', ['address'])
                        return nt(f.replace("_", ", "))
    except Exception as e: pass
    

    geolocator = Nominatim(user_agent=user_agent)
    try:
        location = geolocator.geocode(place_name, timeout=5)
        return location
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print("Geolocate error:")
        print(e)
        return None

def geoquery(place : str, verbose=True) -> tuple[pd.DataFrame, list[str]]:
    """
    Search for amenities in a given place using OSMnx and return a DataFrame with their features.
    Args:
        place (str): The name of the place to search for amenities.
        verbose (bool): Whether to print progress messages.
        Returns:
            pd.DataFrame: A DataFrame containing the features of the amenities found in the place.
            
    """
    # Download features of all amenities 
    amenities = list( map(str, np.concatenate(list(AmenityByCategory.values()) ) ))
    if verbose:
        print("Downloading features for", len(amenities), "amenities in", place)
        t = timer_start("geo feature query")
    
    # Geolocate the place
    location = geolocate(place)
    if location != None: place = location.address
    if place == None:
        if verbose: print(f"{place} not geolocatable.")
        return None 
    if verbose: print(f"Geo feature query for {place}")
    tags = {"amenity" : amenities}
    features = osmnx.features_from_place(place, tags)
    features = features[ features.name == features.name ] # filter out NaN names
    n = features.shape[0]
    if verbose: timer_end(t); print("\r\rFound", n, "entries.")

    # Drop irrelevant feature columns 
    names = list(features.name)
    amenities = list(features.amenity)
    for k in ["geometry", "amenity", "type", "ele"]:
        if k in features.columns:
            features = features.drop(columns=k)
    
    # Save list of columns
    columns = list(features.columns)
    path = get_data_path(place)
    with open(os.path.join(path, "geo_columns.csv"), "w") as f:
        f.write(", ".join(columns))

    # Markdown version of columns, very fast to generate
    texts = []
    for i in range(n):
        row = dict(features.iloc[i])
        row = { k : v for k,v in row.items() if v == v }
        text = "\n".join( list(map("  ".join, row.items())) )
        text = f"# {names[i]}\n{amenities[i]}\n" + text
        texts.append(text)
    
    # Store in DataFrame
    return  pd.DataFrame({
        "name" : names,
        "amenity" : amenities,
        "description" : texts,
    })