import os
import numpy as np
import pandas as pd
import time, datetime
import pdb

from .utils import alphanumeric
from .file_system import get_data_path
from .timing import timer_start, timer_end
from .constants.amenity import AmenityByCategory
from .semantic import get_embedding_model,get_reranker_model, cross_similarity, semantic_line_filter
from .vectordb import milvus_client
from .llm import start_llm_client, rephrase_question

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

def ann_search(place: str, query: str, limit=30, client=None, embedding=None):
    """
    Perform approximate nearest neighbor search in the vector database.

    Args:
        place (str): The place identifier.
        query (str): The query string to search for.
        limit (int): The maximum number of results to return.
        client: Optional Milvus client instance. If None, a new client will be created.
    """
    if client == None: _client = milvus_client(place)
    else: _client = client
    if embedding == None: embedding = get_embedding_model()

    collection_name = "semantic"
    if not _client.has_collection(collection_name):
        raise ValueError(f"Collection '{collection_name}' does not exist in the vector database.")
    _client.load_collection(collection_name)

    query_vector = embedding.encode_query(query)
    t = timer_start("ANN search")
    results = _client.search(
        collection_name=collection_name,
        data=[query_vector],
        limit=limit,
        output_fields=["name", "amenity", "text"],
    )[0]
    data = [ {"id" : r["id"], "ann_distance" : r["distance"], **r["entity"]} for r in results ]
    df = pd.DataFrame(data)    
    timer_end(t)

    if client == None: _client.close()
    
    return df



def semantic_search(place : str, query : str, limit=30, client = None, verbose=True):
    """
    Perform semantic search
    """

    if client == None: _client = milvus_client(place)
    else: _client = client
    results = ann_search(place, query, limit, _client)
    if client == None: _client.close()
    
    reranker = get_reranker_model()
    if verbose: t = timer_start("reranking")
    texts = reranker.rank(query, results["text"], top_k=10, return_documents=True)
    df = pd.DataFrame(texts)
    if verbose: timer_end(t)

    #for i in range(df.shape[0]):
    #    df[i, "text"] = semantic_line_filter(query, df["text"][i], reranker=reranker, verbose=verbose)
    
    results = results.iloc[df["corpus_id"]]
    results["similarity"] = 1.0 / (1.0 + np.exp(-df["score"])) * 2.0 - 1.0
    
    return results
