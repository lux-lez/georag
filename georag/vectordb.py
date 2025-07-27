import os
import numpy as np 
import pandas as pd 
from tqdm import tqdm 
import pymilvus
from typing import Union

from .geo import geolocate, geoquery
from .constants.amenity import AmenityByCategory
from .semantic import get_embedding_model
from .file_system import get_data_path
from .timing import timer_start, timer_end
from .milvus import milvus_client, milvus_init, milvus_populate



def load_vectors(place : str, verbose = True) -> Union[pd.DataFrame, None]:
    ''' Load pre-computed vectors from a .npz file.
    Args:
        place (str): The name of the place to load vectors for.
        verbose (bool): Whether to print progress messages.
    Returns:
        A pandas dataframe with columns "name", "amenity", "description", and "vector",
        or None if the file does not exist.
    '''
    path = get_data_path(place)
    data_path = os.path.join(path, "vectors.npz") 
    if not os.path.isfile(data_path): return None
    else:
        if verbose: t = timer_start("loading compressed vector data (.npz)")
        data = np.load(data_path)
        data = {k: data[k] for k in ["name", "amenity", "description", "vector"]}  # Convert to dictionary
        n = len(data["name"])
        if verbose: 
            timer_end(t)
            print("Found existing vector data with", n, "entries from", len(np.unique(data["amenity"])), "amenities")
        return data

def encode_vectors(texts : list[str], embedding = None, verbose=True) -> list[np.array]:
    """
    Encode a list of texts into vectors using the embedding model.
    
    Args:
        txt (list[str]): List of texts to encode.
        embedding: Optional embedding model. If None, the default model will be used.
    
    Returns:
        list[np.array]: List of encoded vectors.
    """
    if embedding is None: embedding = get_embedding_model()
    vectors = []
    veciterator = range(len(texts))
    if verbose: veciterator = tqdm(veciterator, desc="Encoding")
    for i in veciterator:
        text = texts[i]
        vector = embedding.encode_document(text)
        vectors.append(vector)
    return vectors


def build_database(place : str, overwrite : bool = False, verbose=True):

    # Load existing vector database if available
    data = load_vectors(place, verbose=verbose)
    if data == None:
        data = geo_search(place, verbose=verbose)
        vectors = encode_vectors(data["description"], verbose=verbose)
        data["vector"] = vectors

        # Save vectors to file
        if verbose: t = timer_start("saving compressed semantic vectors (.npz)")
        path = get_data_path(place)
        data_path = os.path.join(path, "vectors.npz") 
        np.savez(data_path, **data)
        if verbose: timer_end(t)
        
        # Print some data
        if verbose: 
            n = len(data["name"]) ; m = len(np.unique(data["amenity"]))
            print("Found existing vector data with", n, "entries from", m, "amenities")
    
    # Milvus client
    client = milvus_client(place, verbose=verbose)
    if client == None:
        raise ValueError("Could not connect to Milvus client. Please check your setup.")
    
    # Copy data to Milvus 
    n_latent = len(data["vector"][0]) 
    milvus_init(client, place, n_latent, overwrite=overwrite, verbose=verbose)
    milvus_populate(client, pd.DataFrame(data), verbose=verbose)
    
    # Print collection stats
    if verbose:
        collection_name = "semantic"
        print("Collection", collection_name)
        stats = client.get_collection_stats(collection_name)
        print("\n".join([ "   " +  str(k) + " : " + str(v) for k,v in stats.items() ]))

    # Close the connection
    client.close()
        

