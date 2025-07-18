import os
import numpy as np
import osmnx 
import shapely
import geojson
import geopandas

#  data_path = os.path.join( os.path.abspath(os.curdir), "data")


def get_placename(place : str) -> str:
    placename = place.replace(",", "").replace(" ", "_")
    return placename

def geoquery_place(place : str):

    # place path
    data_path = os.path.join( os.path.dirname(os.path.dirname(__file__)), "data")
    placename = get_placename(place)
    georef_path = os.path.join(data_path, placename)

    # check whether files exist
    os.makedirs(georef_path, exist_ok=True) 
    contents =  os.listdir(georef_path)
    
    
    # geo data files
    geometry_file = "geometry.geojson"
    restaurant_file = "restaurants.geojson"
    
    # Query OpenStreetMap for the place and get its geographical data
    if geometry_file in contents:
        with open(os.path.join(georef_path, geometry_file)) as f:
            polygon = shapely.geometry.shape(geojson.load(f))
    else:
        try:
            print(f"Querying OpenStreetMap for geometry of {place} ... \r", end="", flush=True)
            gdf = osmnx.geocode_to_gdf(place)

            if gdf.shape == 0: polygon = None
            elif gdf.shape[0] >= 1:
                print(f"Found geometry of {gdf["display_name"]} " + " " * 60)
                if gdf.shape[0] > 1: 
                    print(f"Multiple geometries available, using first one." + " "*30) 
                gdf = dict(gdf.iloc[0])

                # Get axis aligned bounding box
                bboxes = "bbox_" + np.asarray(["west", "east", "south", "north"]) 
                aabb = np.asarray([gdf[bbox] for bbox in bboxes])    
                print("Bounding box ", aabb)
                #TODO: save bounding box to file

                #TODO: search on wikipedia and gather data on place
                # save name, description and other stuff to file 
                
                # save polygon
                polygon = gdf["geometry"]
                with open(os.path.join(georef_path, geometry_file),"w") as f:
                    f.write(shapely.to_geojson(polygon))

        except Exception as e:
            print(f"\nError: {e}")
            print("Please check the place name and try again.")
            return 


    if restaurant_file in contents:
        # TODO load geopandas geodataframe from geojson file 
        with open(os.path.join(georef_path, restaurant_file), "r") as f:
            restaurants = geojson.load(f) # ...
        restaurants = geopandas.GeoDataFrame(restaurants)
    else:
        try:
            print(f"Querying OpenStreetMap for restaurants in {place} ... ", end="", flush=True)
            tags = {"amenity": "restaurant"}
            restaurants = osmnx.features_from_polygon(polygon, tags=tags)
            features = []
            for _, row in restaurants.iterrows():
                props = {}
                for key in restaurants.columns: 
                    if key in row and not (row[key] is np.nan or row[key] is None):
                        props[key] = row[key]
                    feature = geojson.Feature(geometry=row["geometry"], properties=props)
                    features.append(feature)
            with open(os.path.join(georef_path, restaurant_file), "w") as f:
                geojson.dump(geojson.FeatureCollection(features), f)
        except Exception as e:
            print("Error ", e)
            return 
    
    return restaurants

