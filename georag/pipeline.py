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

def get_context(results: pd.DataFrame) -> str:
    ''' 
    Reformulate results data frame to context string
    '''
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
    '''Run the pipeline on multiple queries '''

    # Start Milvus and Mistral clients if not given 
    if client == None: _client = milvus_client(place)
    else: _client = client
    if llm_client == None: llm_client = start_llm_client()
    
    # Populate list of answers
    answers = []
    for i in tqdm(range(len(query)), desc="Processing queries"):
        q = query[i]
        if verbose: print(f"\nProcessing query: {q}")
        name_q = "" if name == "" else name + "_" + str(i)
        answer = pipeline(place, q, client=_client, llm_client=llm_client, verbose=False, name=name_q)
        answers.append(answer)
    if client == None and _client != None: _client.close() # don't forget to close connection
    return answers


def pipeline(place : str, query : str, results=None, context=None, question=None, answer=None, client = None, llm_client = None, verbose=True, name="") -> str:
    """
    Runs the GeoRAG pipeline for a single query:
    1. Performs a semantic search for the query in the given place (unless results are provided).
    2. Builds a context string from the search results (unless context is provided).
    3. Rephrases the query as a question for the LLM (unless question is provided).
    4. Asks the LLM for an answer using the question and context (unless answer is provided).
    5. Logs the process and results to a markdown file in the 'queries' directory.

    Args:
        place (str): The name of the place or dataset to search.
        query (str): The user's query string.
        results (pd.DataFrame, optional): Precomputed search results. If None, performs search.
        context (str, optional): Precomputed context string. If None, builds from results.
        question (str, optional): Precomputed question. If None, rephrases the query.
        answer (str, optional): Precomputed answer. If None, asks the LLM.
        client (optional): Milvus client instance. If None, a new one is created.
        llm_client (optional): LLM client instance. If None, a new one is created.
        verbose (bool, optional): If True, prints progress and answer.
        name (str, optional): Custom name for the output file. If empty, uses a timestamp.

    Returns:
        str: The answer generated by the LLM.
    """

    # Semantic search
    if type(results) == type(None):
        if client == None: _client = milvus_client(place)
        else: _client = client
        results = semantic_search(place, query, client=_client, verbose=verbose)
        if client == None: _client.close()
    if context == None:
        context = get_context(results)

    # Ask LLM
    if question == None:
        if llm_client == None: llm_client = start_llm_client()
        question = rephrase_question(query, llm_client=llm_client, verbose=verbose)
    if answer == None:
        if verbose: print("\n--- Answer: -----------" )
        answer = ask_llm_with_context(question, context, llm_client=llm_client, verbose=verbose)
        if verbose: print("-"*30 + "\n")

    # if no output was given, generate unique output name from timestamp 
    now = datetime.datetime.now()
    if name == "":
        stamp = str(now.timestamp()).replace(".","")
        name = "query_" + stamp 

    # Write log of what was done 
    filename = name + ".md"
    proj_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    query_path = os.path.join(proj_dir, "queries", filename)
    os.makedirs(os.path.dirname(query_path), exist_ok=True)
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

    # Save to file and return answer
    with open(query_path, "w") as f:
        f.write(msg)
    return answer