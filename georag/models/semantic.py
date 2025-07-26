import sentence_transformers # SBERT 

# Embedding (Bi-encoder)
def get_embedding_model(verbose = True):
    model_name = "all-MiniLM-L6-v2"
    embedding = sentence_transformers.SentenceTransformer(model_name)
    return embedding

# Reranker (Cross-encoder)
def get_reranker_model(verbose = True):
    model_name = "cross-encoder/ms-marco-MiniLM-L6-v2"
    reranker = sentence_transformers.CrossEncoder(model_name)
    return reranker