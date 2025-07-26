# GeoRAG  

[Read the official documentation.](./docs/Documentation.md). Here is just the short version:

## Licence 

This software is released under GPLv3 licence. 

## Installation 

This software was built using Python. Here are the installation instructions.

```bash
python3 -m pip install -r requirements.txt 
```

## Usage 


<b>Interactive Mode</b>
Activate the virtual environment, then run the script without any parameters. 
```
python3 georag.py
```

<b>Parametric Mode</b>

You can also use the script with parameters. Available options are 
```
python3 georag.py [-h] [-q QUERY] [-b] [-s SEARCH] [-c CHAT] [-i] [-o OUT]
```

The different parameters are all optional. Here is a list 
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

## Examples

<b> Linux </b>

For the CLI interface run 
```bash
source .venv/bin/activate
python3 georag.py
```

Run an example with `sh run_example.sh`.

Run the tests with `sh run_tests.sh`.

To check the disk usage of the data directory per place run
```bash
du -hd1 data
```

## What is good

- pretty command line interface with interactive mode

- geographic amenity search using OSM tested for restaurants 

- recursive website text extraction   


## What is bad or still needs to be improved

- Instructions for Windows and macOS: installation, run and test 

- Rather slow, currently hardly any async or parallelization

- Redundancy in file system: currently optimized for rerunning smaller parts of the application, tradeoff is that overall memory is inefficiently used

- Still a lot of warnings are printed but seems to work anyway

