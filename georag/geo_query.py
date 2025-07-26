import os
import osmnx
import geopandas, geojson, shapely
import pandas as pd
import numpy as np
import time 
import yaml
from tqdm import tqdm

from .utils import alphanumeric
from .file_system import get_data_path
from .constants.tags import TagsPerCategory


def unique_exclude_empty(v, dtype="<U128"):
    v = np.asarray(v, dtype=dtype)
    v = np.unique(v)
    v = v[v != "nan"]
    v = v[v != ""]
    return v

def description_from_dict(d: dict, description=None, bullet:str = "-") -> dict:
    """
    Build a categorized description dictionary from a flat dictionary of tags.

    This function organizes the contents of a dictionary `d` (typically OSM tags)
    into a structured dictionary grouped by semantic categories (e.g., 'about', 'contact', etc.).
    Each category contains a set of formatted strings describing the tag and its value.
    Only non-empty and non-"nan" values are included.

    Args:
        d (dict): Dictionary of tags (key-value pairs), e.g., from an OSM feature.
        description (dict, optional): Existing description dictionary to update. 
            If None, a new dictionary is created.
        bullet (str, optional): bullet point in list (markdown compatible by default)

    Returns:
        dict: A dictionary where keys are category names (str) and values are sets of 
        formatted strings describing the tags in that category.
    """

    # Empty in, empty out 
    if description is None: description = {}
    if len(d.keys()) == 0: return description
    
    # loop over tag categories
    for category, tags in TagsPerCategory.items():
        if category not in description:
            description[category] = set()
        
        # loop over tags in that category
        for tag in tags:
            if tag in d:
                str_tag = str(d[tag])
                if str_tag not in ["", "nan"]:

                    # Only use the part after the last colon for display
                    tag_display = tag.split(":")[-1] if ":" in tag else tag

                    # write as markdown list 
                    line = " ".join([bullet, tag_display, d[tag]])
                    description[category].add(line)
    return description


def get_address(**kwargs) -> str:
    """
    Build a human-readable address string from available keyword arguments.
    Handles combination of missing fields appropriately.

    Args: (optional)
        street, housenumber, city, postcode, countryplace, floor, housename,  ...
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
        - amenity : str                what are you searching for? (currently only tested with "restaurant")
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
        if verbose: print("Downloading ", self.place, " to ", self.path)
        os.makedirs( self.path, exist_ok=True )

        # Initialize private variables
        self.geometry = self.get_geometry()
        self.features = self.get_features()
        self.amenities = self.get_amenities()

        #self.visit_links()

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
            if type(self.features) == type(None): 
                print("No features found.") ; return None
            names = unique_exclude_empty(self.features.name, dtype="<U128")
            
            # Prepare lists to collect column data
            address_list = []
            website_list = []

            # Find addresses, website URLs
            addr_fields = [c.replace("addr:", "") for c in self.features.columns if c.startswith("addr:") ]

            # Iterate over all feature names
            iterations = range(len(names))
            if self.verbose: 
                iterations = tqdm(iterations, desc="Searching addresses" )
            for i in iterations:
                name = names[i]
                mask = self.features.name == name
                path_i = os.path.join(self.path, "amenities", alphanumeric(name))
                os.makedirs(path_i, exist_ok=True)

                # get list of website URLs
                websites_1 = unique_exclude_empty(self.features["website"][ mask ],  dtype="<U128")
                websites_2 = unique_exclude_empty(self.features["contact:website"][ mask ], dtype="<U128")
                websites = np.concatenate([websites_1, websites_2])
                websites = [w for w in websites if w != "" and (w.startswith("http") or w.startswith("www"))] 
                websites = "\n".join(websites)
                
                website_list.append(websites)
                
                website_file = "links.yaml"
                website_path = os.path.join(path_i, website_file)
                if not os.path.isfile(website_path):
                    with open(website_path, "w") as f:
                        text = yaml.dump({"unvisited" : websites.split("\n")})
                        f.write(text)

                # get list of addresses from data 
                addr_df = self.features[ ["addr:" + field for field in addr_fields ] ][mask]            
                addr_entries = []
                for j in range(addr_df.shape[0]):
                    d = dict(addr_df.iloc[j])
                    d = {k : d["addr:" + k] for k in addr_fields}
                    addr_entries.append(get_address(**d))
                addr_entries = unique_exclude_empty(addr_entries)
                address = "\n".join(addr_entries)
                address_list.append(address)               
            
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
                        desc_parts.extend(sorted(description[category]))
                
                # Write description to file
                description_file = "description.md"
                description_path = os.path.join(path_i, description_file)
                description = "\n".join(["# " + name, address, "", *desc_parts])
                with open(description_path, "w") as f:
                    f.write(description)
            
            # Assign lists to DataFrame columns at once
            df = pd.DataFrame({
                "name" : names,
                "website": website_list,
                "address" : address_list
            })

            # Information on data gap
            if self.verbose:
                empty_rate = np.mean( np.logical_and(df["address"] == "", df["website"] == ""))
                print(str(round(empty_rate * 100.0, 2)) + "%" + " of entries have neither website nor address")
            
            # Save to file
            df.to_csv( amenity_path )
            
        self.amenities = df
        return df
