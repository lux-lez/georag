import osmnx
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

def geolocate(place_name, user_agent="geo_checker"):
    geolocator = Nominatim(user_agent=user_agent)
    try:
        location = geolocator.geocode(place_name, timeout=10)
        return location
    except (GeocoderTimedOut, GeocoderServiceError):
        # Handle timeout or service errors gracefully
        return None

def get_features(place : str, tags : dict):
    place = place.strip()
    location = geolocate(place)
    if location == None:
        print(f"{place} not geocodable.")
        return None 
    features = osmnx.features_from_place(place, tags)
    return features


place = "Karlsruhe, Germany"
#place = "Umbabwe, Gacio"
tags = {"amenity" : ["restaurant"]}
features = get_features(place, tags)