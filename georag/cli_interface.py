import os
from random import randint
from argparse import ArgumentParser
import rich, rich.prompt, rich.console, rich_menu
 
#from .utils import alphanumeric

from .file_system import get_data_path
from .geo_query import GeoQuery
from .scrape_website import visit_websites
from .build_database import build_database
from .semantic_search import semantic_search

Actions = ["query", "build", "search", "chat"]

def yes_or_no(prompt : str) -> bool:
    """Ask yes or no question (boolen, default answer yes)"""
    answer = input(f"{prompt} [Y/n]")
    answer = answer.lower().strip()
    return not answer.startswith("n")

def stall():
    """Ask whether to quit the application"""
    if not yes_or_no("Continue?"): exit()

def select_place() -> str:
    """ Select a downloads place from the data folder """ 
    data_path = get_data_path("")[:-1]
    places = [d for d in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, d))]
    if len(places) == 0:
        print("No places found. Run the GeoQuery first."); return ""
    menu = rich_menu.Menu(*places, title="Select place")
    place = str(menu.ask())
    print("Selected place ", place)
    return place

def parse_args() -> dict:

    # Parser
    a = ArgumentParser(
        prog = "georag",
        description="GeoRAG is an restaurant decision assistant.",
        epilog="(C) 2025 GPLv3 by Luca Lenz",
    )
    # In scope of project just limited to restaurants

    # Main actions 
    a.add_argument("-q", "--query",                            help="Place to query at")                          
    a.add_argument("-b", "--build",       action='store_true', help="Flag to build semantic index")        
    a.add_argument("-s", "--search",                           help="Prompt for search")               
    a.add_argument("-c", "--chat",                             help="Open chat window (will overwrite interactive to always be true)") 
    a.add_argument("-i", "--interactive", action='store_true', help="Flag for interactive") 
    a.add_argument("-o", "--out",                              help="Output path")           
    # TODO: Write documentation compatible with --help
    args = a.parse_args()

    # convertNamespace to dictionary
    argnames = [
        k for k in dir(args) 
        if not (k.startswith("_") or k.endswith("_"))
    ]
    args = {k : getattr(args, k) for k in argnames}

    return args

def georag_cli():
    """ TODO: docs 
    ...
    """
    args = parse_args()
    console = rich.console.Console()

    noargs = args["query"] == None and not args["build"] and args["search"] == None and not args["chat"] 
    if noargs: 
        interactive_welcome()
    else:
        if sum([args[k] != None for k in ["query", "search", "chat"]]) > 1:
            if args["out"] != None: 
                print("Warning, output parameter was inconsitently used and will be ignored.")
                args["out"] = None

        place = ""        
        if args["query"] != None:
            place = args["query"].strip()
            if len(place) > 3:
                console.rule("GeoQuery")
                q = GeoQuery("restaurant", place)
        
        if args["build"]:
            if place == "": 
                place = select_place()
            build_database(place)
    
        if args["search"] != None:
            console.rule("SemSearch")
            print("Semantic search for:")
            print("\t", args["search"])
            if place == "": 
                place = select_place()
            answer = semantic_search(place, args["search"])
            print("Results")
            print(answer)
    
        
        if args["chat"] != None:
            args["interactive"] = True
            done_something = True
            console.rule("ChatBot")
            print("Chat bot not implemented yet.")
        
        if not args["interactive"]:
            print("Finished GeoRAG task.")
        else:
            interactive_welcome()

def interactive_welcome():
    finished = False
    while not finished:
        menu = rich_menu.Menu("GeoQuery", "WebScrape", "BuildIndex", "SemSearch", "ChatBot", "Exit")
        match menu.ask():
            case "GeoQuery": 
                interactive_geoquery()
            case "WebScrape":
                interactive_webscrape()
            case "BuildIndex":
                interactive_buildindex()
            case "SemSearch":
                interactive_semsearch() 
            case "ChatBot":
                print("TODO: ChatBot")
            case "Exit":
                finished = True ; exit()
        
_place_examples = [
    "Karlsruhe, Germany",
    "Melbourne, Australia",
    "Helsinki, Finland",
    "Ouagadougou, Burkina Faso",
    "Marseille, France",
    "Pompei, Italy",
    "Mumbai, India",
    # ... 
]
def interactive_geoquery():
    console = rich.console.Console()
    console.rule("GeoQuery")
    console.print(f"Geographical query for restaurants by place. (eg. {_place_examples[randint(0, len(_place_examples)-1)]})")
    place = rich.prompt.Prompt.ask("Place to query")
    place = place.strip()
    q = GeoQuery("restaurant", place)
    stall() ; interactive_welcome()

def interactive_webscrape():
    console = rich.console.Console()
    console.rule("WebScrape")

    data_path = get_data_path("")[:-1]
    places = [d for d in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, d))]
    if len(places) == 0:
        console.print("No places found. Run the GeoQuery first."); return 
    menu = rich_menu.Menu(*places, title="Select place")
    place = str(menu.ask())
    visit_websites(place)
    stall() ; interactive_welcome()


def interactive_buildindex():
    console = rich.console.Console()
    console.rule("BuildIndex")

    place = select_place()

    path = get_data_path(place)
    force_update = False
    if os.path.isfile( os.path.join(path, "vector.db") ):
        force_update = yes_or_no("Milvus database already exists. Force update?")
    build_database(place, overwrite=force_update)

    stall() ; interactive_welcome()


def interactive_semsearch():
    console = rich.console.Console()
    console.rule("SemSearch")

    # Ask for semantic query 
    query = rich.prompt.Prompt.ask("What are you searching for?\n")
    
    # Select a place 
    data_path = get_data_path("")[:-1]
    places = [d for d in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, d))]
    if len(places) == 0:
        console.print("No places found. Run the GeoQuery first."); return 
    menu = rich_menu.Menu(*places, title="Select place")
    place = str(menu.ask())
    print("Selected place ", place)

    results = semantic_search(place, query)
    print("Results:")
    print(results)
    stall() ; interactive_welcome()