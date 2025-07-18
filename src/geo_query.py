import os
import numpy as np
import osmnx 
import shapely
from shapely.geometry import shape  # <-- add this import
import geojson




def place_information(place : str):
    data_path = os.path.join( os.path.dirname(os.path.dirname(__file__)), "data")

    
    print("Geo reference for ", place)
    placename = place.replace(",", "").replace(" ", "_")
    georef_path = os.path.join(data_path, placename)
    os.makedirs(georef_path, exist_ok=True)
    is_empty = len( os.listdir(georef_path) ) == 0
    if not is_empty: pass # try to avoid re-querying        

    # Query OpenStreetMap for the place and get its geographical data
    print(f"Querying OpenStreetMap for {place} ... ", end="", flush=True)
    try:
        gdf = osmnx.geocode_to_gdf(place)
        if gdf.shape[0] != 1: 
            print(f"\nWarning! Found {gdf.shape[0]} geo matches")
        gdf = dict(gdf.iloc[0])
        print(f"\rFound {gdf["display_name"]} " + " " * 60)
    except Exception as e:
        print(f"\nError: {e}")
        print("Please check the place name and try again.")
        return 

    # Save the geographical data to a file
    # Save shape file
    output_name = f"geometry.geojson"
    already_exists = os.path.isfile(os.path.join(georef_path, output_name))
    if not already_exists:
        polygon = gdf["geometry"]
        with open(os.path.join(georef_path, output_name),"w") as f:
            f.write(shapely.to_geojson(polygon))
    else:
        with open(os.path.join(georef_path, output_name)) as f:
            polygon = shapely.geometry.shape(geojson.load(f))
    # TODO: check if file is corrupted 

    # Get axis aligned bounding box
    bboxes = "bbox_" + np.asarray(["west", "east", "south", "north"]) 
    aabb = np.asarray([gdf[bbox] for bbox in bboxes])    
    #TODO: save bounding box to file

    # Searh area for tags

    # Get restaurants in the area
    tags = {"amenity": "restaurant"}
    print(f"Querying OpenStreetMap for restaurants in {place} ... ", end="", flush=True)
    try:
        restaurants = osmnx.features_from_polygon(polygon, tags=tags)
        if restaurants.shape[0] == 0:
            print("\rNo restaurants found in the area.")
            return 
        else:
            print(f"\rFound {restaurants.shape[0]} restaurants." + " " *60)

            # Save restaurants to a GeoJSON file with additional properties
            output_name = f"restaurants.geojson"
            features = []
            for _, row in restaurants.iterrows():
                props = {}
                for key in ["name", "opening_hours", "website", "description"]:
                    if key in row and not (row[key] is np.nan or row[key] is None):
                        props[key] = row[key]
                feature = geojson.Feature(geometry=row["geometry"], properties=props)
                features.append(feature)
            with open(os.path.join(georef_path, output_name), "w") as f:
                geojson.dump(geojson.FeatureCollection(features), f)
    except Exception as e:
        print(f"\nError: {e}")
        print("Something went wrong.")
        return 
    
    return placename