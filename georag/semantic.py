import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder # SBERT 

from .timing import timer_start, timer_end

# Embedding (Bi-encoder)
def get_embedding_model(verbose = True): 
    try:
        model_name = "all-MiniLM-L6-v1" # v2 model caused memory leaks
        embedding = SentenceTransformer(model_name)
        return embedding
    except Exception as e:
        if verbose: 
            print("Could not load embedding.")
            print(e); exit(1)

# Reranker (Cross-encoder)
def get_reranker_model(verbose = True):
    try:
        model_name = "cross-encoder/msmarco-MiniLM-L6-en-de-v1" 
        reranker = CrossEncoder(model_name)
        return reranker
    except Exception as e:
        if verbose: 
            print("Could not load reranker.")
            print(e); exit(1)

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


def semantic_line_filter(query : str, text : str, delim="\n", min_similarity = -0.99, reranker=None, verbose=True):
    if reranker == None: reranker = get_reranker_model()
    if verbose: t = timer_start("filtering lines")
    lines = [line for line in text.split(delim) if len(line.strip()) > 3] 
    similarity = cross_similarity(query, lines)
    mask = similarity >= min_similarity
    s = []
    for i in np.where(mask)[0]:
        s.append(lines[i])
    if verbose: timer_end(t)
    return delim.join(s)     
