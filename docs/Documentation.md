# GeoRAG

Geographical Retrieval Augmented Generation

### Overview
1. Follow the [Installation instruction](#install) to setup the software. 
2. Jump right with the command line interface either in [interactive_mode](#interactive) or [parametric_mode](#parametric).
3. Dive deeper and maybe even [contribute to the project](#contribute). 

### Usage 

Command line interface (CLI) purely runs in terminal. Pretty interface nevertheless. 

#### <a name="interactive"></a> Interactive Mode

Interactive mode, requires no parameters.
```python3 georag.py```

Here is a "screenshot" of what the interface looks like.
```md
────────── GeoRAG ────────────────────────────────────────
Interactive interface
Place "Karlsruhe"
Located place  Karlsruhe, Baden-Württemberg, Deutschland
Query "Best vegan restaurant"
...
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
