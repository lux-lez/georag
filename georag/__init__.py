
print(f"Running georag/__init__.py as {__name__}\r", end="", flush=True)

from .geo import geolocate, geoquery
from .search import semantic_search as search

from .cli import interface as cli_interface
#from .vectordb import build_vectordb
if __name__ == "__main__": print(f"Finished georag/__init__.py as {__name__}")
