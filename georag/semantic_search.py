import os
import numpy as np
from pymilvus import MilvusClient
import pandas as pd


from .utils import alphanumeric
from .file_system import get_data_path
from .models.semantic import get_embedding_model, get_reranker_model

def semantic_search(place : str, query : str, min_similarity=0.01, max_results = 30, verbose=True, client=None):
    """
    Args:
        max_results (int) - highest number of expected results 
        similarity_threshold (float) - minimal predicted reranker similarity to accept candidate (should be between 0 and 1)
    """
    
    # get semantic models
    embedding = get_embedding_model()
    reranker = get_reranker_model()


    
    if client == None:
        name = alphanumeric(place)
        db_path = os.path.join(get_data_path(name), "vector.db")
        if verbose: print("Opening Milvus Lite client @", db_path)
        _client = MilvusClient(db_path)
    else:
        _client = client

    # Semantic search: ANN using Milvus
    collection_name = "semantic"
    if verbose: print("Performing semantic search.")
    q = embedding.encode_query(query)
    results = _client.search(
        collection_name=collection_name,
        data = [q],
        anns_field="vector",
        output_fields = ["amenity", "text"],
        limit = max_results * 2
    )
    if client == None: _client.close()

    # unpack results of ANN search
    results = results[0]
    amenities = [r["entity"]["amenity"] for r in results]
    texts = [r["entity"]["text"] for r in results]
    pairs = [[query, chunk] for chunk in texts]

    # similarity scores from semantic models
    la_scores = [ r["distance"] for r in results] 
    logit_scores = reranker.predict(pairs)
    prob_scores = 1.0 / (1 + np.exp(-logit_scores))
    similarity = 2.0 * prob_scores - 1.0 

    df = pd.DataFrame({"name" : amenities, "similarity" : similarity, "LA" : la_scores, "text" : texts})
    df = df[ df["similarity"] > min_similarity ] 
    return df 

