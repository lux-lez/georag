# GeoRAG

<b> About </b>

GeoRAG is an AI-powered tool designed to help you discover real-world locations with ease. By leveraging semantic search and advanced language models, GeoRAG can intelligently "look things up" for you, going beyond simple keyword matching to understand your intent and preferences. Whether you're searching for the best restaurants, unique cafes, or hidden gems in your city, GeoRAG analyzes location data and descriptive information to provide tailored recommendations. Get ready to explore and find your new favorite spot with the help of cutting-edge AI technology!

--- 

## What does it do?

First search locations using OpenStreetMaps (OSM). 

<p>
Currently it can only be used for restaurants. 
</p>

#### Overview 

1. Follow the [Installation instruction](#install) to setup the software. 
2. Jump right in and [try it out](#usage).
3. You might want to [read on the invidual components](#components).
4. Dive deeper and maybe even [contribute to the project](#contribute). 

---

### <a name="usage"></a>How to use it? 

Command line interface (CLI) purely runs in terminal. Pretty interface nevertheless. 

<b>Interactive mode</b>     
All components will be easily accessible through a text based graphical interface. 
```python3 georag.py```

Here is a "screenshot" of what the interface looks like.

```
──────────── MENU ────────────────────

╭──────────────╮                 
│   GeoQuery   │                 
│   WebScrape  │                 
│   BuildIndex │                 
│ > SemSearch  │                 
│   ChatBot    │                 
│   Exit       │                 
╰──────────────╯                 
                                    
─────── SemSearch ────────────────────

What are you searching for?
: sushi
Selected place  Heidelberg_Germany [ ... ]
Performing semantic search.
Results:
                      name  similarity        LA                                               text
0    Sexy Fish & the Tiger    0.848772  0.794530  big  plates to share\nS E X Y  F I S H  P A R ...
1                  Keisari    0.884011  0.832136                       # Heidelberg – Keisari Sushi
2                     Choa    0.606753  0.861268  # CHOA Heidelberg â Asian Soulfood: Sushi, T...

Continue? [Y/n]
```

<b>Parametric Mode</b>

You can also use the script with parameters to selectively use specific components. Available options are 
```
python3 georag.py [-h] [-q QUERY] [-b] [-s SEARCH] [-c CHAT] [-i] [-o OUT]
```

The different parameters are all optional. Here is a list of which parameters control which components  
```
options:
  -h, --help           Show this documentation
  -q, --query QUERY    Place to query at
  -b, --build          Flag to build semantic index
  -s, --search SEARCH  Prompt for search
  -c, --chat CHAT      Open chat window (will overwrite interactive to always be true)
  -i, --interactive    Flag for interactive
  -o, --out OUT        Output path
```

### <a name="install"></a> How to install 

First create a virtual environment and activate it
```
python3 -m venv .venv
source .venv/bin/activate
```

Then install the requirements
```
python3 -m pip install -r requirements.txt
```

Caveat; If you don't have a GPU that supports CUDA then run 
```bash
pip cache purge
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```
to clear the CUDA files and reinstall the CPU version of torch. Retry the installation steps from above afterwards.  



--- 

#### <a name="usage"></a> Compontents 

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
    Use LLaMA-Index to chunk the documents, then we use an S-BERT model to encode the chunks. 
    In Milvus we create a semantic vector database. The search index is also stored in Milvus (not LLaMA-Index).

3. <b>SemanticSearch</b> semantic search on descriptions
    ```
    python3 georag.py -s "vegan restaurant with tofu dishes" 
    ```
    Optional arguments:
    - Output: `python3 georag.py -s "..." -o tofu.json`

    Non-optimizing behaviour as heuristic aproach to allow search diversity.
    By default filter out all candidates with similarity < 1% (as predicted by cross-encoder).

4. <b>ChatBot</b> chat in terminal with interactive interface
    ```
    python georag.py -c "I am looking for the best sushi restaurant near Europaplatz. Can you recommend any?"
    ```
    Optional arguments:
    - Output `python georag.py -c "..." -o myfavsushi.json` a new folder is created that stores the chat history.

<b>Data structure</b>

Folder per place
```
cache/   ...                                    # OSM cache
data/
    └── <place>/
        ├── geometry.geojson                    # OSM geometry
        ├── restaurants.geojson                 # OSM features 
        ├── vectors.npz                         # Encoded Latent Vectors 
        ├── vector.db                           # Milvus vector data base (+ semantic index)  
        ├── amenities.csv                       # List of amenities
        └── amenities/                          # Amenity data
                     ├── <restaurant 1>/ ... 
                     ├── <restaurant 2>/ ... 
                     └── ...
```

Folder per amenity
```
<restaurant>/
            ├── description.md          # Markdown list OSM tags
            ├── links.yaml              # URLs using in scraping  
            ├── website_1.md            # eg. a text scraped of a website  
            └── ... 
```

--- 

## <a name="contribute"></a> Contributing

### Software Licence 

Free open source published under GPLv3.

First release by Luca Lenz in 2025.

### Source Code structure

```
georag/
├── all_libraries.py       # import all dependencies (useful for testing)
├── utils.py               # no external dependencies
├── constants/             # text knowledge 
├── timing_decorators.py  
├── ...
│
│ # Entry point
├── __init__.py            # definition of exports 
├── cli_iterface.py        # decide which components to use 
│                          # (or full pipeline which uses all components in order)
│
│ # Loaders for AI models 
├── models/
│   ├── semantic.py        # cross and bi encoders
│   └── llm.py             # language model 
│
├── semantic_tools.py      # routines for semantic models  
│
│ # Pipeline components
├── 1. geo_query.py        # geographical query 
│                          # defines `GeoQuery` class which download `data/<place>/...`
│ 
├── 2. scrape_website.py   # download a text version and documents from a website URL  
│                          # follows unvisited links in `links.yaml` and save as eg. `website_123.yaml`
│
├── 3. build_database.py   # building vector database and semantic index with embedding
│                          # split into chunks and vectorize to `vectors.npz`
│                          # build vector index using Milvus and store to `vector.db`
│
├── 4. semantic_search.py  # use embedding and reranker to search database
│
└── 5. chat_bot.py         # chat interface, history and context managment
```
