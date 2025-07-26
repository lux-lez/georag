import os
import numpy as np
import sentence_transformers
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from tqdm import tqdm 
from pymilvus import MilvusClient
from pymilvus import Collection, DataType

from .utils import alphanumeric
from .file_system import get_data_path
from .constants.files import AllowedDocumentExtensions
from .models.semantic import get_embedding_model

def build_database(place : str, overwrite=False, verbose = True):
    
    # Load precomputed semantic vectors if they exist 
    path = get_data_path(place)
    vector_path = os.path.join(path, "vectors.npz")

    if os.path.isfile(vector_path):
        if verbose: 
            print("Loading precomputed semantics from ", vector_path)
        npz_file = np.load(vector_path)
        amenities = npz_file["amenity"]
        texts = npz_file["text"]
        vectors = npz_file["vector"]
    

    else:
        if verbose:
            print("Chunking documents...")

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
        if verbose: chunk_iterations = tqdm(chunk_iterations, desc="Encoding")
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

    # Store in Milvus Lite database
    db_path = os.path.join(path, "vector.db") 
    client = MilvusClient(db_path)
    n_latent = len(vectors[0])
    if client == None:
        print("Milvus client could not be created.") ; return 

    collection_name = "semantic"

    if overwrite and client.has_collection(collection_name):
        if verbose: print("Overwriting collection ", collection_name)
        client.drop_collection(collection_name=collection_name)

    if not client.has_collection(collection_name):  
        
        schema = client.create_schema()
        schema.add_field("chunk",   DataType.INT64,        is_primary = True)
        schema.add_field("amenity", DataType.VARCHAR,      max_length = 64)
        schema.add_field("text",    DataType.VARCHAR,      max_length = 512)
        schema.add_field("vector",  DataType.FLOAT_VECTOR, dim = n_latent)

        index_params =  client.prepare_index_params()
        index_params.add_index(field_name="vector", index_type="AUTOINDEX", metric_type="L2")

        collection = client.create_collection(
            collection_name = collection_name,
            dimension = n_latent,
            schema = schema,
            index_params = index_params
        )
        if verbose:
            print("Collection ", collection_name)
            stats = client.get_collection_stats(collection_name)
            print("\n".join([ str(k) + ":" + str(v) for k,v in stats.items() ]))

        
        data_iterator = range(len(vectors))
        if verbose: data_iterator = tqdm(data_iterator, desc="Inserting")
        for i in data_iterator:
            data = {"chunk" : i, "amenity" : amenities[i], "text" : texts[i], "vector" : vectors[i]}
            client.insert(collection_name=collection_name, data=[data])    
    
    client.close()

    # TODO: analyse data statistics
    #       how diverse is data?

    # TODO: (optional) visualization
    #       use 2D PCA to find a pointcloud of semantic positioning of the restaurants based on semantic similarity (in embedding space)
    #       Idea: use color to indicate mismatch between reranker and embedding 
    #       Q: Can sentance be found from embedding that describes PCA component basis ? 
    #       Q: What is PCA coefficient covariance distribution?
