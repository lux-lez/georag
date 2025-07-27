import os
import numpy as np
import pandas as pd
import osmnx
from typing import Union
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from .file_system import get_data_path
from .constants.amenity import AmenityByCategory
from .timing import timer_start, timer_end

def geolocate(place_name, user_agent="geo_checker"):
    """ Geograohically locate a place using Nominatim.
    Args:
        place_name (str): The name of the place to geolocate.
        user_agent (str): User agent for Nominatim requests.
    Returns:
        Location object or None if geocoding fails.
    """
    geolocator = Nominatim(user_agent=user_agent)
    try:
        location = geolocator.geocode(place_name, timeout=10)
        return location
    except (GeocoderTimedOut, GeocoderServiceError):
        # Handle timeout or service errors gracefully
        return None

def geoquery(place : str, verbose=True) -> pd.DataFrame:
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
    location = geolocate(place, verbose=False)
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