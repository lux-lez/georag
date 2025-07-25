# GeoRAG

GeoRAG lets you assist search for real places by letting an AI "look things up" for you. 

## How does it work?


First search locations using OpenStreetMaps (OSM). 
Then build an index for location descriptions using LLaMA-index. 
Load the index into a vector database with file and chunk references using Milvus. 


<p>
Currently it can only be used for restaurants. 
</p>

## How to install 

First create a virtual environment
```
python3 -m venv .venv
```

Then install the requirements
```
python3 -m pip install -r requirements.txt
```

## How to use it? 

Command line interface (CLI)

```
python3 georag.py --help
```


<b>Interactive mode</b>
```
python3 georag.py
```

--- 

### Compontents 

Here is a list of all the software features included in this project with an example of how to use:

1. <b>GeoQuery</b> search OSM, build semantic index and update vector database
    ```
    python3 georag.py -q "Karlsruhe, Germany" 
    ```

2. <b>WebScrape</b> recursive information retrieval from website and markdown rendering
    ```
    python3 georag.py -w "https://derkuchenladen.de/" 
    ```
    Optional arguments:
    - Output: `python3 georag.py -w "..." -o description.kuchenladen_berlin.md`

3. <b>BuildIndex</b> build semantic vector database for document text chunks
    ```
    python3 georag.py -b
    ```

3. <b>SemanticSearch</b> semantic search on descriptions
    ```
    python3 georag.py -s "vegan restaurant with tofu dishes" 
    ```
    Optional arguments:
    - Output: `python3 georag.py -s "..." -o tofu.json`

4. <b>ChatBot</b> chat in terminal with interactive interface
    ```
    python georag.py -c "I am looking for the best sushi restaurant near Europaplatz. Can you recommend any?"
    ```
    Optional arguments:
    - Output `python georag.py -c "..." -o myfavsushi.json` a new folder is created that stores the chat history.


--- 

## Contribute 

<b>Source Code structure</b>

```
georag/
├── __init__.py         # definition of exports 
├── all_libraries.py    # import all dependencies (useful for testing)
├── utils.py            # no external dependencies
│
├── cli_iterface.py     # decide which components to use 
│                       # (or full pipeline which uses all components in order)
│
│ #Components
├── 1. geo_query.py        # geographical query 
├── 2. scrape_website.py   # download a text version and documents from a website URL  
├── 3. build_database.py   # building vector database and semantic index with embedding
├── 4. semantic_search.py  # use embedding and reranker to search database
├── 5. llm_interface.py    # chat interface, history and context managment
└── ...
```
