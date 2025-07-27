import os
import numpy as np
import pandas as pd

from .file_system import get_data_path
from .timing import timer_start, timer_end
from .constants.amenity import AmenityByCategory
from .semantic import get_reranker_model, cross_similarity
from .vectordb import milvus_client

def infer_amenities(query: str, threshold=-0.9, reranker=None, verbose=True) -> list[str]:
    """
    Guess amenities based on a query string.

    Args:
        query (str): The query string to search for amenities.
        threshold (float): The minimum similarity score to consider an amenity relevant.
        reranker: Optional reranker model for cross-encoder predictions.
    """
    if verbose: t = timer_start("infer amenity")
    amenities = np.concatenate(list(AmenityByCategory.values()))
    similarities = cross_similarity(query, amenities, inverse=True, reranker=reranker)
    mask = similarities > threshold
    amenities = amenities[mask]
    amenities = list(map(str, amenities))
    if verbose: timer_end(t)
    return amenities

def ann_search(place: str, query: str, limit=30, client=None):
    """
    Perform approximate nearest neighbor search in the vector database.

    Args:
        place (str): The place identifier.
        query (str): The query string to search for.
        limit (int): The maximum number of results to return.
        client: Optional Milvus client instance. If None, a new client will be created.
    """
    if client is None: client = milvus_client(place)

    collection_name = "semantic"
    if not client.has_collection(collection_name):
        raise ValueError(f"Collection '{collection_name}' does not exist in the vector database.")
    client.load_collection(collection_name)

    results = client.search(
        collection_name=collection_name,
        query=query,
        limit=limit,
        output_fields=["name", "amenity", "text", "vector"],
        params={"metric_type": "L2"}
    )
    results = pd.DataFrame(data=results)
    print(results)
    return 



def semantic_search(place : str, query : str, limit=30, client = None, verbose=True):
    """
    Perform 
    """
    if client is None: client = milvus_client(place)
    results = ann_search(place, query, limit, client)
    
    reranker = get_reranker_model()
    reranker.rank(results, query, return_documents=True, show_progress_bar=verbose)

