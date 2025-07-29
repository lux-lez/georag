# GeoRAG

Geographical Retrieval Augmented Generation (GeoRAG) is an AI-powered search assistant that helps users find and recommend places such as restaurants, cafes, attractions, and shopping centers in a given city. GeoRAG combines semantic search using S-BERT embeddings, fast vector similarity search with Milvus, and natural language response generation using the Mistral 7B language model running in the cloud.

GeoRAG works by first retrieving relevant information from OpenStreetMap data, encoding place descriptions into vector embeddings, and storing them in a Milvus vector database. When a user asks a question, the system finds the most relevant places using semantic similarity, then generates a helpful, context-aware answer using the Mistral LLM.

GeoRAG software features:
- **Semantic Search:** Uses light-weight Sentence Transformers (S-BERT) to encode place descriptions and user queries for accurate matching.
- **Vector Database:** Stores and searches embeddings efficiently using Milvus.
- **LLM Integration:** Generates natural language answers with Mistral 7B, grounded in retrieved context.
- **Command-Line Interface:** Easy-to-use CLI for both interactive and parametric modes.

### Overview
1. Follow the [Installation instruction](#install) to setup the software. 
2. Jump right with the command line interface either in [interactive mode](#interactive), [parametric mode](#parametric) or [running from Python](#code).
3. Dive deeper and maybe even [contribute to the project](#contribute). 

### Usage 

Command line interface (CLI) purely runs in terminal. Pretty interface nevertheless. 

#### Mistral AI
Have your Mistral API key ready when using the program for the first time. 
Note that you can [sign up](https://auth.mistral.ai/ui/registration) for a free trial. Then you can [create a new key] (https://help.mistral.ai/en/articles/347464-how-do-i-create-api-keys-within-a-workspace).

Once you have entered it it will be stored under `.api_keys/mistralai.txt` so that you won't be asked again.

Note that additionally to printing the answer on the screen the results of each pipeline step are including the whole context are written to `requests/query_XYZ.md` where XYZ is the timestamp when the pipeline finished.

#### <a name="interactive"></a> Interactive Mode

Interactive mode. Input parameters at runtime.
```python3 georag.py```

Here is a "screenshot" of what the interface looks like.
```md
────────── GeoRAG ────────────────────────────────────────
Interactive interface

Place "Karlsruhe"
> Located place  Karlsruhe, Baden-Württemberg, Deutschland

Query "Best vegan restaurant"
[ ... ]

--- Answer: -----------
These restaurants are highly rated for their vegan options 
1. My heart beats vegan
2. The Corner 
------------------------------

Finished GeoRAG pipeline in 9.8s 
Continue? [Y/n]  ... 
```

#### <a name="parametric"></a> Parametric Mode
Give the two parameters for place and query.  
```md
usage: python3 -m georag [-h] place query

GeoRAG is geographically knowledgable AI search assistent.

positional arguments:
  place       where to search
  query       what to search for

options:
  -h, --help  show this help message and exit
```

### <a name="code"></a> Code interface
If you want to use the code in your python 

```python
from georag import pipeline as rag

# Single query
answer = rag("Karlsruhe", "Best vegan restaurant")
```
Note that everytime you run this function the whole database has to be reloaded which takes much longer than a single query.
For multiple queries it is better to use the following functionality.

```python
from georag import multi_pipeline as batch_rag

# Multiple queries
diets = ["vegan", "gluten-free", "halal"]
queries = [f"Find restaurants with {d} food." for d in diets]
answer_batch = batch_rag("Karlsruhe", queries )
```

(Note that you can also pass an optional parameter `name : str` to the pipeline functions which will save the log file with a proper name instead of some timestamp.)

### <a name="install"></a> Installation 

1. First create a virtual environment and activate it. (Optional, but strongly recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate
```
On Windows you have to call `.venv/bin/activate.bat` to [activate the virtual environment](https://docs.python.org/3/library/venv.html#how-venvs-work) instead of calling the source function.

2. Install the Python requirements
```bash
python3 -m pip install -r requirements.txt
```

Caveat; If you don't have a GPU that supports CUDA then run
```bash
pip cache purge
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

to clear the CUDA files and reinstall the CPU version of torch. Retry the installation steps from above afterwards.
