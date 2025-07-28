import os
import pymilvus
from tqdm import tqdm
import pandas as pd

from .geo import geolocate
from .file_system import get_data_path
from .timing import timer_start, timer_end

def milvus_client(place : str, verbose=True) -> pymilvus.MilvusClient:
    """
    Create a Milvus client for the vector database of a given place.
    Args:
        place (str): The name of the place to connect to.
        verbose (bool): Whether to print connection information.
    Returns:
        pymilvus.MilvusClient: The Milvus client connected to the vector database.
    
    Don't forget to close the client after use!
    """
    location = geolocate(place)
    if location != None: place = location.address
    if place == None:  
        if verbose: print(f"Could not geolocate {place}.") 
        return None
    db_path = os.path.join(get_data_path(place), "vector.db")
    if not os.path.isfile(db_path):
        if verbose: print(f"Vector database for {place} does not exist at {db_path}.")
    
    try:
        print("\nStarting Milvus client for", place)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        client = pymilvus.MilvusClient(db_path)
        print("Got milvus client ", client)
        return client
    except Exception as e:
        print("Error in database ")
        print(e)

def milvus_init(client : pymilvus.MilvusClient, place : str, n_latent : int, overwrite = False, verbose=True):
    """
    Initialize a Milvus database for a given place.
    
    Args:
        place (str): The name of the place to initialize the database for.
        n_latent (int): The dimensionality of the vectors.
        verbose (bool): Whether to print progress messages.
    """
    
    collection_name = "semantic"
    if client.has_collection(collection_name):
        if not overwrite:
            if verbose: print("Collection", collection_name, "already exists. Skipping initialization.")
            return client
        else:
            if verbose: print("Overwriting collection ", collection_name)
            client.drop_collection(collection_name=collection_name)
    
    # Create schema
    schema = client.create_schema()
    schema.add_field("id",      pymilvus.DataType.INT64,         is_primary=True)
    schema.add_field("name",    pymilvus.DataType.VARCHAR,       max_length=64)
    schema.add_field("amenity", pymilvus.DataType.VARCHAR,       max_length=64)
    schema.add_field("text",    pymilvus.DataType.VARCHAR,       max_length=512)
    schema.add_field("vector",   pymilvus.DataType.FLOAT_VECTOR, dim=n_latent)

    # Create collection
    index_params = client.prepare_index_params()
    index_params.add_index(field_name="vector", index_type="AUTOINDEX", metric_type="L2")
    
    client.create_collection(
        collection_name=collection_name,
        dimension=n_latent,
        schema=schema,
        index_params=index_params
    )
    
    if verbose: print(f"Collection '{collection_name}' initialized with {n_latent} dimensions.")
    return client

def milvus_populate(client : pymilvus.MilvusClient, data: pd.DataFrame, verbose=True):
    """
    Populate the Milvus database with data.
    
    Args:
        client (pymilvus.MilvusClient): The Milvus client to use for the operation.
        data (pd.DataFrame): DataFrame containing the data to insert.
        verbose (bool): Whether to print progress messages.
    """
    if verbose: t = timer_start("inserting vectors")
    
    collection_name = "semantic"
    if not client.has_collection(collection_name):
        raise ValueError(f"Collection '{collection_name}' does not exist in the vector database.")
    
    client.load_collection(collection_name)
    
    # Insert data
    data_iterator = range(len(data))
    if verbose: data_iterator = tqdm(data_iterator, desc="Inserting")
    for i in data_iterator:
        row = dict(data.iloc[i])
        client.insert(
            collection_name=collection_name,
            data={"id" : i, "name" : row["name"], "amenity" : row["amenity"], "text" : row["description"], "vector" : row["vector"]}
        )

    if verbose: timer_end(t)
    return client 
