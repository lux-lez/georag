import numpy as np
from .models.semantic import get_reranker_model

#semantic filter S
#   y = S(x) := max(T, f(x))

def cross_similarity(query:str, documents:list[str], reranker=None):
    """
    Cross-encoder predicts the logits and is converted to probability space. 
    Similarity is just an affine linear transform of the probability to scale to negative values.  
    """
    if reranker == None:
        _reranker = get_reranker_model()
    else:
        _reranker = reranker
    pairs = [[query, doc] for doc in documents]    
    scores = _reranker.predict(pairs)
    prob = 1.0 / ( 1.0 + np.exp(-scores) ) 
    similarity = 2.0 * prob - 1.0 # affine transform                    
                                  #   0% : probability <->  similarity -1.0 )
                                  #  50% : probability <->  similarity  0.0 )    
                                  # 100% : probability <->  similarity +1.0 )
    
    return similarity 


def semantic_line_filter(query : str, text : str, delim="\n", min_similarity = -0.01):
    reranker = get_reranker_model()
    lines = [line for line in text.split(delim) if len(line.strip()) > 3] 
    similarity = cross_similarity(query, lines)
    filtered_text = delim.join(lines[similarity >= min_similarity])
    return filtered_text

