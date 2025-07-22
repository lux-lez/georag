import os
import time
import numpy as np
import pandas as pd
import osmnx 
import shapely
import geojson
import geopandas
from tqdm import tqdm

from .data_manager import alphanumeric, get_data_path, get_feature_path


def unique_exclude_empty(v, dtype="<U128"):
    v = np.asarray(v, dtype=dtype)
    v = np.unique(v)
    v = v[v != "nan"]
    v = v[v != ""]
    return v

tags_per_category = {
    "about": [
        'name', 'amenity', 'note', 'alt_name', 'description', 'source:addr', 'cuisine',
        'cuisine:description', 'operator', 'note:en', 'reg_name', 'official_name',
        'created_by', 'old_name', 'old_operator', 'branch', 'brand', 'brand:wikidata',
        'brand:wikipedia', 'short_name', 'source', 'image', 'wikidata', 'designation',
        'loc_name', 'name:de', 'name:zh', 'name:note', 'fixme', 'old_name_1',
        'old_name_2', 'old_name:1', 'old_name:1890-2010', 'old_name:2010-2017',
        'old_name:2017-2018', 'old_name:2018-2021', 'disused:amenity', 'disused:name',
        'ref', 'ref:vatin', 'operation', 'mapillary', 'theme', 'description:de'
    ],
    "contact": [
        'phone', 'email', 'contact:email', 'contact:facebook', 'contact:phone',
        'contact:fax', 'fax', 'contact:instagram', 'contact:tiktok', 'contact:youtube',
        'operator:type', 'contact:mobile', 'contact:whatsapp', 'disused:contact:website'
    ],
    "food": [
        'website:menu', 'diet:vegetarian', 'diet:non-vegetarian', 'diet:vegan',
        'diet:halal', 'lunch', 'lunch:menu', 'lunch:warm', 'diet:gluten_free',
        'diet:kosher', 'diet:organic', 'organic', 'running_sushi', 'buffet',
        'check_date:diet:vegan', 'check_date:diet:vegetarian', 'all_you_can_eat',
        'all_you_can_eat:type', 'oven'
    ],
    "booking": [
        'reservation', 'opening_hours', 'opening_hours:kitchen', 'opening_hours:signed',
        'check_date:opening_hours', 'check_date', 'kitchen_hours', 'start_date',
        'indoor_seating', 'outdoor_seating', 'outdoor_seating:capacity', 'beer_garden',
        'indoor', 'room', 'reservation:website', 'opening_hours:url', 'website:reservation',
        'service_times', 'opening_date'
    ],
    "payment": [
        'payment:cards', 'payment:cash', 'payment:contactless', 'payment:credit_cards',
        'payment:girocard', 'payment:mastercard', 'payment:visa', 'payment:maestro',
        'payment:mastercard:min_payment', 'payment:others', 'payment:visa:min_payment',
        'payment:debit_cards', 'payment:apple_pay', 'payment:mastercard_contactless',
        'payment:qr_code', 'payment:american_express', 'payment:diners_club',
        'payment:credit_card', 'payment:google_pay', 'payment:electronic_purses',
        'payment:cryptocurrencies', 'payment:konzernausweis', 'payment:v_pay'
    ],
    "access": [
        'wheelchair', 'toilets:wheelchair', 'toilets', 'level', 'toilets:access',
        'drive_in', 'drive_through', 'access', 'access:description', 'wheelchair:description',
        'wheelchair:description:de', 'max_level', 'min_level', 'addr:floor', 
        'addr:subdistrict', 'addr:housename', 'min_age', 'layer', 'ele', 'height',
        'source:height', 'level:ref'
    ],
    "catering": [
        'takeaway', 'delivery', 'delivery:partner', 'delivery:brand', 'delivery:covid19'
    ],
    "atmosphere": [
        'smoking', 'bar', 'brewery', 'microbrewery', 'brewery:wikidata', 'craft_beer',
        'cocktails', 'panoramax', 'table_service', 'self_service', 'highchair', 'highchai',
        'kids_area', 'kids_area:fee', 'kids_area:outdoor', 'kids_area:supervised',
        'indoor_slide', 'seating', 'seats', 'seats:indoor', 'seats:outdoor'
    ],
    "toilets": [
        'toilets:female', 'toilets:male', 'toilets:unisex', 'toilets:disposal',
        'toilets:menstrual_products', 'changing_table', 'changing_table:location',
        'changing_table:count', 'changing_table:fee'
    ],
    "internet": [
        'internet_access', 'internet_access:fee', 'internet_access:ssid', 'wifi',
        'internet_access:operator'
    ],
    "misc": [
        'shop', 'old_name', 'air_conditioning', 'dog', 'roof:colour', 'roof:levels',
        'roof:shape', 'roof:material', 'building', 'building:levels', 'building:part',
        'craft', 'sport', 'currency:EUR', 'currency:others', 'tourism', 'source:outline',
        'lastcheck', 'surveillance', 'designation'
    ]
}

def description_from_dict(d: dict, description=None):
    if description is None:
        description = {}
    if len(d.keys()) == 0:
        return description
    else:
        for category, tags in tags_per_category.items():
            if category not in description:
                description[category] = set()
            for tag in tags:
                if tag in d:
                    str_tag = str(d[tag])
                    if str_tag not in ["", "nan"]:
                        # Only use the part after the last colon for display
                        tag_display = tag.split(":")[-1] if ":" in tag else tag
                        entry = f"- {tag_display} {d[tag]}"
                        description[category].add(entry)
    return description


def get_address(**kwargs) -> str:
    """
    Build a human-readable address string from available keyword arguments.
    Handles missing fields gracefully.
    """
    kwargs = {k : str(kwargs[k]) for k in kwargs if str(kwargs[k]) != "nan"}

    # Address parts in order of specificity
    parts = []

    # Optional: floor, housename, housenumber, street
    if "floor" in kwargs and kwargs["floor"]:
        parts.append(f'Floor {kwargs["floor"]}')
    if "housename" in kwargs and kwargs["housename"]:
        parts.append(kwargs["housename"])
    if "housenumber" in kwargs and kwargs["housenumber"]:
        if "street" in kwargs and kwargs["street"]:
            parts.append(f'{kwargs["street"]} {kwargs["housenumber"]}')
        else:
            parts.append(kwargs["housenumber"])
    elif "street" in kwargs and kwargs["street"]:
        parts.append(kwargs["street"])

    # Optional: postcode and city (combine if both exist)
    city = kwargs.get("city", "")
    postcode = kwargs.get("postcode", "")
    if postcode and city:
        parts.append(f"{postcode} {city}")
    elif postcode:
        parts.append(postcode)
    elif city:
        parts.append(city)

    # Optional: place (e.g. village), suburb, subdistrict
    locality = []
    for key in ["place", "suburb", "subdistrict"]:
        if key in kwargs and kwargs[key]:
            locality.append(kwargs[key])
    if locality:
        parts.append(", ".join(locality))

    # Optional: country
    if "country" in kwargs and kwargs["country"]:
        parts.append(kwargs["country"])


    # Join all parts, removing empty ones
    address = ", ".join([p for p in parts if p])
    return address

class GeoQuery:
    ''' GeoQuery
    Geographical data search using OpenStreetMaps (OSM).
    Downloads GeoJSON files if you specify what and where you are searching.

    Arguments:
        - amenity : str                what are you searching for? 
        - place   : str                where should it be?
        - name    : str (optional)     data folder name (will use alphanumeric version of place descriptor by default)
        - verbose : bool (optional)    adjust output  

    For example the following command will download all the restaurants in Karlsruhe.    
    ```python
    q = GeoQuery("restaurant", "Karlsruhe, Germany")
    ```

    Notice that when rerunning the script the data is already downloaded.
    If the download is corrupt make sure to delete the broken files before rerunning.  
    '''

    def __init__(self, amenity : str, place : str, name : str = "", verbose : bool = True):
        self.verbose = verbose
        self.place = place 
        self.tags={"amenity" : amenity}
        
        if name == "": 
            self.name = alphanumeric(place)
        else:
            self.name = name

        # Initialize directory
        self.path = get_data_path(place)
        print(self.place, ">", self.name, "@", self.path)
        os.makedirs( self.path, exist_ok=True )

        # Initialize private variables
        self.geometry = self.get_geometry()
        self.features = self.get_features()
        self.amenities = self.get_amenities()


    def get_geometry(self, geometry_file = "geometry.geojson") -> shapely.Polygon:

        # Use stored value
        if hasattr(self, "geometry"): 
            if self.geometry != None: 
                return self.geometry

        # Load from file if exists
        geometry_path = os.path.join(self.path, geometry_file)
        if os.path.isfile(geometry_path):
            if self.verbose:
                print("Loading geometry for ", self.place)
            with open(geometry_path, "r") as f:
                geometry = shapely.geometry.shape(geojson.load(f))

        # Otherwise query OpenStreetMap (OSM)
        else:
            try:
                if self.verbose:
                    print(f"Searching for {self.place} ... \r", end="", flush=True)
                
                # Get geometry from first entry in GeoDataFrame
                gdf = osmnx.geocode_to_gdf(self.place)
                if self.verbose: 
                    print(f"Got ", gdf.shape[0], f" geometry file(s) for {self.place}" + " "*50)
                gdf = dict(gdf.iloc[0])
                geometry = gdf["geometry"]                    
                
                # Save to file
                print(f"Saving geometry of {self.place} to {geometry_path}")
                with open(geometry_path, "w") as f:
                    f.write(shapely.to_geojson(geometry))

            # Query failed
            except Exception as e:
                if self.verbose:
                    print(f"Geometry for {self.place} could not be found.")
                    print("(", e, ")") 
                return None
    
        self.geometry = geometry
        return geometry

    def get_features(self, feature_file="restaurants.geojson") -> geopandas.GeoDataFrame:

        # Use stored value
        if hasattr(self, "features"):
            if self.features != None: 
                return self.features

        # Load from file if exists
        feature_path = os.path.join(self.path, feature_file)
        if os.path.isfile(feature_path):

            # Timed runs of GeoDataFrame loader 

            if self.verbose:
                print("Loading features GeoJSON file... \r", end="", flush=True)
            t0 = time.time_ns()
            with open(feature_path, "r") as f:
                features = geojson.load(f)
            t1 = time.time_ns()
            if self.verbose and t1-t0 > 1e6: 
                print("Loaded GeoJSON in ", (t1-t0) * 1e-9, "s." + " "*30)
            
            t0 = time.time_ns()
            if self.verbose:
                print("Building GeoDataFrame... \r", end="", flush=True)
            features = geopandas.GeoDataFrame([features[i]["properties"] for i in range( len(features.features))])
            t1 = time.time_ns()
            if self.verbose and t1-t0 > 1e6:
                print("Built GeoDataFrame in ", (t1-t0) * 1e-9, "s." + " "*30)
            

        # Otherwise, search in OSM
        else:
            if self.verbose:
                tag_list = list(self.tags.values())
                tag_list = tag_list[0:min(len(tag_list)-1, 10)]
                tag_list = ", ".join(tag_list) 
                print(f"Searching {self.place} for {tag_list} ... \r", end = "", flush=True)

            # Saving geometry
            geometry = self.geometry
            print("Geometry ", type(geometry))
            try:
                features = osmnx.features_from_polygon(geometry, tags=self.tags)  
                
                # write to json object
                feature_list = []
                for _, row in features.iterrows():
                        props = {}
                        for key in features.columns: 
                            if key in row and not (row[key] is np.nan or row[key] is None):
                                props[key] = row[key]
                            feature = geojson.Feature(geometry=row["geometry"], properties=props)
                            feature_list.append(feature)
                
                # Number of unique names
                if self.verbose:
                    names = unique_exclude_empty( features.name )
                    print(f"Found {len(names)} feature results.")

                print(f"Saving features of {self.place} to {feature_path}")
                with open(feature_path, "w") as f:
                    geojson.dump(geojson.FeatureCollection(feature_list), f)

            except Exception as e:
                if self.verbose: 
                    print(f"Features for {self.place} could not be found.")
                    print("(", e, ")")
                return None 

        self.features = features
        return features


    def get_amenities(self, amenity_file="amenities.csv") -> pd.DataFrame:

        # Use buffered resource data frame
        if hasattr(self, "amenities") and self.amenities != None:
            return self.amenities

        # Load  from file
        amenity_path = os.path.join(self.path, amenity_file)
        if os.path.isfile(amenity_path):
            if self.verbose:
                print("Loading from CSV.")
            df = pd.read_csv(amenity_path)

        else:
            # Find unique feature names
            names = unique_exclude_empty(self.features.name, dtype="<U128")
            df = pd.DataFrame({"name": names})
            
            # Prepare lists to collect column data
            address_list = []
            website_list_final = []

            # Find addresses, website URLs
            addr_fields = [c.replace("addr:", "") for c in self.features.columns if c.startswith("addr:") ]

            # Iterate over all feature names
            iterations = range(len(names))
            if self.verbose: 
                iterations = tqdm(iterations, desc="Searching addresses" )
            for i in iterations:
                name = names[i]
                mask = self.features.name == name

                # get list of website URLs
                website_list = unique_exclude_empty(self.features["website"][ mask ],  dtype="<U128")
                website_list2 = unique_exclude_empty(self.features["contact:website"][ mask ], dtype="<U128")
                websites = "\n".join(np.concatenate([website_list, website_list2]))
                website_list_final.append(websites)

                # get list of addresses from data 
                addr_df = self.features[ ["addr:" + field for field in addr_fields ] ][mask]            
                addr_entries = []
                for j in range(addr_df.shape[0]):
                    d = dict(addr_df.iloc[j])
                    d = {k : d["addr:" + k] for k in addr_fields}
                    addr_entries.append(get_address(**d))
                addr_entries = unique_exclude_empty(addr_entries)
                address_list.append("\n".join(addr_entries))
            
                # More information as markdown text
                selected = self.features[mask]
                description = {}
                for j in range(np.sum(mask)):
                    d = dict(selected.iloc[j])
                    description = description_from_dict(d, description=description)
                # Join unique entries for each category, preserving order
                desc_parts = []
                for category in description:
                    if description[category]:
                        desc_parts.append("### " + category.capitalize())
                        # Sort for deterministic output
                        desc_parts.extend(sorted(description[category]))
                
                # Write description to file
                description_file = "description.md"
                description_path = os.path.join(self.path, "amenities", alphanumeric(name), description_file)
                os.makedirs(os.path.dirname(description_path), exist_ok=True)
                description = "\n".join(desc_parts)
                with open(description_path, "w") as f:
                    f.write(description)
            
            # Assign lists to DataFrame columns at once
            df["website"] = website_list_final
            df["address"] = address_list

            # Information on data gap
            if self.verbose:
                empty_rate = np.mean( np.logical_and(df["address"] == "", df["website"] == ""))
                print(str(round(empty_rate * 100.0, 2)) + "%" + " of entries have neither website nor address")
            
            # Save to file
            df.to_csv( amenity_path )
            
        self.amenities = df
        return df

# def geoquery_place(place : str):

#     # place path
#     data_path = os.path.join( os.path.dirname(os.path.dirname(__file__)), "data")
#     placename = get_placename(place)
#     georef_path = os.path.join(data_path, placename)

#     # check whether files exist
#     os.makedirs(georef_path, exist_ok=True) 
#     contents =  os.listdir(georef_path)
    
    
#     # geo data files
#     geometry_file = "geometry.geojson"
    
#     # Query OpenStreetMap for the place and get its geographical data
#     if geometry_file in contents:
#         with open(os.path.join(georef_path, geometry_file)) as f:
#             polygon = shapely.geometry.shape(geojson.load(f))
#     else:
#         try:
#             print(f"Querying OpenStreetMap for geometry of {place} ... \r", end="", flush=True)
#             gdf = osmnx.geocode_to_gdf(place)

#             if gdf.shape == 0: polygon = None
#             elif gdf.shape[0] >= 1:
#                 print(f"Found geometry of {gdf["display_name"]} " + " " * 60)
#                 if gdf.shape[0] > 1: 
#                     print(f"Multiple geometries available, using first one." + " "*30) 
#                 gdf = dict(gdf.iloc[0])

#                 # Get axis aligned bounding box
#                 bboxes = "bbox_" + np.asarray(["west", "east", "south", "north"]) 
#                 aabb = np.asarray([gdf[bbox] for bbox in bboxes])    
#                 print("Bounding box ", aabb)
#                 #TODO: save bounding box to file
                
#                 # save polygon
#                 polygon = gdf["geometry"]
#                 with open(os.path.join(georef_path, geometry_file),"w") as f:
#                     f.write(shapely.to_geojson(polygon))

#         except Exception as e:
#             print(f"\nError: {e}")
#             print("Please check the place name and try again.")
#             return 

#     # Restaurant features
#     restaurant_file = "restaurants.geojson"
#     if restaurant_file in contents:
#         # TODO load geopandas geodataframe from geojson file 
        
#         with open(os.path.join(georef_path, restaurant_file), "r") as f:
#             restaurants = geojson.load(f) # ...        
#         restaurants = geopandas.GeoDataFrame([restaurants[i]["properties"] for i in range( len(restaurants.features))])
#     else:
#         try:
#             print(f"Querying OpenStreetMap for restaurants in {place} ... ", end="", flush=True)
#             tags = {"amenity": "restaurant"}
#             restaurants = osmnx.features_from_polygon(polygon, tags=tags)
#             features = []
#             for _, row in restaurants.iterrows():
#                 props = {}
#                 for key in restaurants.columns: 
#                     if key in row and not (row[key] is np.nan or row[key] is None):
#                         props[key] = row[key]
#                     feature = geojson.Feature(geometry=row["geometry"], properties=props)
#                     features.append(feature)
#             with open(os.path.join(georef_path, restaurant_file), "w") as f:
#                 geojson.dump(geojson.FeatureCollection(features), f)
#         except Exception as e:
#             print("Error ", e)
#             return 
    
#     print("Columns ", restaurants.columns)
#     for name, website in tqdm( np.asarray(restaurants[["name", "website"]]), desc="Scraping websites." ):
#         if type(website) == str: 
#             dirname = get_placename(name) 
#             dirpath = os.path.join(georef_path, "webpages", dirname)
#             os.makedirs(dirpath, exist_ok=True)
            
#             website_file = os.path.join(dirpath, "website.md")
#             if not os.path.isfile(website_file):
#                 markdown = scrape_website(website)
#                 if type(markdown) == str and len(markdown) > 5:
#                     with open(website_file, "w") as f:
#                         f.write(markdown)
#                 else:
#                     #Search web for this
#                     pass
#     return restaurants

