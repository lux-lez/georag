import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder # SBERT 

# Embedding (Bi-encoder)
def get_embedding_model(verbose = True): 
    model_name = "all-MiniLM-L6-v1" # v2 model caused memory leaks
    embedding = SentenceTransformer(model_name)
    return embedding

# Reranker (Cross-encoder)
def get_reranker_model(verbose = True):
    model_name = "cross-encoder/msmarco-MiniLM-L6-en-de-v1" 
    reranker = CrossEncoder(model_name)
    return reranker

def cross_similarity(query:str, documents:list[str], inverse=False, reranker=None):
    """
    Cross-encoder predicts the logits and is converted to probability space. 
    Similarity is just an affine linear transform of the probability to scale to negative values.  
    """
    if reranker == None: reranker = get_reranker_model()
    if inverse: pairs = [[doc, query] for doc in documents]
    else:       pairs = [[query, doc] for doc in documents]    
    scores = reranker.predict(pairs)
    prob = 1.0 / ( 1.0 + np.exp(-scores) ) 
    similarity = 2.0 * prob - 1.0 # affine transform                    
                                  #   0% : probability <->  similarity -1.0 )
                                  #  50% : probability <->  similarity  0.0 )    
                                  # 100% : probability <->  similarity +1.0 )
    
    return similarity 

