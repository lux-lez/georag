import os
import numpy as np
import pandas as pd
import datetime
from typing import Union
from tqdm import tqdm
import pdb

from .milvus import milvus_client
from .llm import start_llm_client, rephrase_question, ask_llm, ask_llm_with_context
from .semantic import semantic_line_filter
from .search import semantic_search

def get_context(results: pd.DataFrame):
    context = []
    similarity = np.asarray( results["similarity"] ) * 100.0
    texts = np.asarray( results["text"] )
    names = np.asarray( results["name"] )
    for i in range(len(names)):
        info = str(i) + ". " + names[i] + "\n"
        info += "similarity : " + str(similarity[i]) + "%\n"
        lines = texts[i].split("\n")[1:]
        info += "\n".join([" " + l for l in lines])
        context.append(info)
    context = "\n\n".join(context)
    return context

def multi_pipeline(place : str, query : list[str], client = None, llm_client = None, verbose=True, name=""):
    if client == None: _client = milvus_client(place)
    else: _client = client
    if llm_client == None: llm_client = start_llm_client()
    results = []
    
    for i in tqdm(range(len(query)), desc="Processing queries"):
        q = query[i]
        if verbose: print(f"\nProcessing query: {q}")
        name_q = "" if name == "" else name + "_" + str(i)
        res = pipeline(place, q, client=_client, llm_client=llm_client, verbose=False, name=name_q)
        results.append(res)
    return results


def pipeline(place : str, query : str, results=None, context=None, question=None, answer=None, client = None, llm_client = None, verbose=True, name="") -> str:
    
    if type(results) == type(None):
        if client == None: _client = milvus_client(place)
        else: _client = client
        results = semantic_search(place, query, client=_client, verbose=verbose)
        if client == None: _client.close()
    if context == None:
        context = get_context(results)

    if question == None:
        if llm_client == None: llm_client = start_llm_client()
        question = rephrase_question(query, llm_client=llm_client, verbose=verbose)

    if answer == None:
        if verbose: print("\n--- Answer: -----------" )
        answer = ask_llm_with_context(question, context, llm_client=llm_client, verbose=verbose)
        if verbose: print("-"*30 + "\n")

    # unique output name from 
    now = datetime.datetime.now()
    if name == "":
        stamp = str(now.timestamp()).replace(".","")
        name = "query_" + stamp 
    
    filename = name + ".md"
    proj_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    query_path = os.path.join(proj_dir, "queries", filename)
    os.makedirs(os.path.dirname(query_path), exist_ok=True)

    # Write log 
    msg = "\n\n".join([
        "# GeoRAG Log", 
        f"Time: {str(now)}", 
        f"Place: {place}",    
        f"Query: {query}", 
        f"Question: {question}",
        f"Results: {", ".join(results.name)}",
        f"Answer: {answer}", "", 
        f"Context:\n{context}",
    ])

    # Write to file
    with open(query_path, "w") as f:
        f.write(msg)
    
    return answer