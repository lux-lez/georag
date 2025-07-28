try:
    from .geo import geolocate, geoquery
    from .vectordb import build_database
    from .search import semantic_search as search
    from .cli import interface as cli_interface
    #from .vectordb import build_vectordb
except ModuleNotFoundError as e:
    print("Modules not found:", flush=True)
    print("\t", e)
    print("Have you activated the virtual environment?")
    exit(1)

