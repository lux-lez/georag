try: 
    # Only these components are exported:
    from .cli import interface  
    from .search import save_query as search  
        # will use the semantic search and llm if no arguments are provided

except ModuleNotFoundError as e:
    print("Modules not found:", flush=True)
    print("\t", e)
    print("Have you activated the virtual environment?")
    exit(1)

