import os
import pandas as pd
import datetime

from .milvus import milvus_client
from .llm import start_llm_client, rephrase_question, ask_llm, ask_llm_with_context
from .semantic import semantic_line_filter
from .search import semantic_search

def pipeline(place, query, results=None, context=None, question=None, answer=None, client = None, llm_client = None, verbose=True):
    
    if type(results) == type(None):
        if client == None: _client = milvus_client(place)
        else: _client = client
        results = semantic_search(place, query, client=_client)
        if client == None: _client.close()

    if question == None:
        if llm_client == None: llm_client = start_llm_client()
        question = rephrase_question(query, llm_client=llm_client, verbose=verbose)

    if context == None:
        context = []
        for i, (name, text) in enumerate(zip(results.name, results.text)):
            info = str(i) + ". " + name + ":\n"
            info += "\n".join(["  "+l for l in text.split("\n")])
            context.append(info)
        context = "\n\n".join(context)

    if answer == None:
        print("\n--- Answer: -----------" )
        answer = ask_llm_with_context(question, context, llm_client=llm_client, verbose=verbose)
        print("-"*30 + "\n")

    # get time stamp
    now = datetime.datetime.now()
    stamp = str(now).replace(".","")

    # Output file name
    filename = "query_" + stamp + ".md"
    proj_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    query_path = os.path.join(proj_dir, "queries", filename)
    os.makedirs(os.path.dirname(query_path), exist_ok=True)

    # Write log 
    msg = "\n".join([
        "# GeoRAG Log", ""
        f"Time: {str(now)}", ""
        f"Place: {place}",     
        f"Query: {query}", ""
        f"Question: {question}",
        f"Results: {", ".join(results.name)}",
        f"Answer: {answer}", "\n\n", 
        f"Context:\n{context}",

    ])

    # Write to file
    with open(query_path, "w") as f:
        f.write(msg)