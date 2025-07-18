# GeoRAG

GeoRAG lets you assist search for real places by letting an AI "look things up" for you. 

## How does it work?

First search locations using OpenStreetMaps (OSM). 
Then build an index for location descriptions using LLaMA-index. 
Load the index into a vector database with file and chunk references using Milvus. 

An example for cafees and restaurants in Karlsruhe is provided. 

## How to use it? 

Command line interface (CLI)


<b>Interactive mode</b>
```
python georag.py
```

<b>Indexing</b> search OSM, build semantic index and update vector database
```
python georag.py -i "restaurants in Karsruhe" 
```

<b>Query</b> directly in terminal
```
python georag.py -q "I am looking for the best sushi restaurant in Europaplatz."
```
If you set the output flag eg. `python georag.py -q "..." -o myfavsushi` a new folder is created that stores the query and result inside.
