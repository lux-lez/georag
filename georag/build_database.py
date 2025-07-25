import os
import numpy as np
import sentence_transformers
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from tqdm import tqdm 

from .utils import *
from .geo_query import get_data_path
from .constants.files import AllowedDocumentExtensions

# Embedding (Bi-encoder)
_embedding = None
def get_embedding_model(verbose = True):
    global _embedding 
    if _embedding == None:
        model_name = "all-MiniLM-L6-v2"
        if verbose: print("Loading embedding ", model_name)
        _embedding = sentence_transformers.SentenceTransformer(model_name)
    return _embedding

# Reranker (Cross-encoder)
_reranker = None
def get_reranker_model(verbose = True):
    global _reranker 
    if _reranker == None:
        model_name = "cross-encoder/ms-marco-MiniLM-L6-v2"
        if verbose: print("Loading reranker ", model_name)
        _reranker = sentence_transformers.CrossEncoder(model_name)
    return _reranker

def build_database(place : str, verbose = True):
    
    # Load precomputed semantic vectors if they exist 
    path = get_data_path(place)
    vector_path = os.path.join(path, "vectors.npz")
    if os.path.isfile(vector_path):
        npz_file = np.load(vector_path)
        amenities = npz_file["amenity"]
        texts = npz_file["text"]
        vectors = npz_file["vector"]

    else:

        # Split documents into chunks
        document_path = os.path.join(path, "amenities" )
        documents = SimpleDirectoryReader(document_path, recursive=True, required_exts=AllowedDocumentExtensions)
        documents = documents.load_data()
        splitter = SentenceSplitter(chunk_size = 512, chunk_overlap=50)
        chunks = splitter.get_nodes_from_documents(documents, show_progress=verbose)

        # Calculate vectors
        embedding = get_embedding_model()
        n_latent =  embedding.get_sentence_embedding_dimension()
        amenities = []; texts = []; vectors = []
        chunk_iterations = range(len(chunks))
        if verbose: chunk_iterations = tqdm(chunk_iterations, desc="Embedding chunks")
        for i in chunk_iterations:
            chunk = chunks[i]

            # Read name of amenity
            amenity = os.path.split(os.path.split(chunk.metadata["file_path"])[-2])[-1]
            try:
                with open( os.path.join(document_path, amenity, "description.md") ) as f:
                    firstline = f.read().split("\n")[0]
                name = firstline.split("# ")[-1]
            except Exception as e:
                name = amenity
            
            # Calculate embedded vector
            text = chunk.text
            vector = embedding.encode_document(text)

            # append to list
            amenities.append(name)
            texts.append(text)
            vectors.append(vector)

        # Save to file
        if verbose: 
            print("Saving vectors to ", vector_path, " ... ", end="", flush=True)
        np.savez(vector_path, vector=vectors, text=texts, amenity=amenities)
        if verbose:
            print("Saved vectors to ", vector_path, " "*20)


    # Store in Milvus database
        
    #... 