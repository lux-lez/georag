import os
from random import randint
from argparse import ArgumentParser
import rich, rich.prompt, rich.console, rich_menu
 
#from .utils import alphanumeric

from .geo_query import GeoQuery, visit_links
from .build_database import build_database

Actions = ["query", "build", "search", "chat"]

def parse_args() -> dict:

    # Parser
    a = ArgumentParser(
        prog = "georag",
        description="GeoRAG is an restaurant decision assistant.",
        epilog="(C) 2025 GPLv3 by Luca Lenz",
    )
    # In scope of project just limited to restaurants

    # Main actions 
    a.add_argument("-q", "--query",                            help="Place to query at")                             # Place to query at
    a.add_argument("-b", "--build",       action='store_true', help="Flag to build semantic index")        # Flag to build semantic index
    a.add_argument("-s", "--search",                           help="Prompt for search")                            # Prompt for search
    a.add_argument("-c", "--chat",                             help="Open chat window (will overwrite interactive to always be true)")                              # Open chat window (will overwrite interactive to always be true) 
    a.add_argument("-i", "--interactive", action='store_true', help="Flag for interactive")  # Flag for interactive
    a.add_argument("-o", "--out",                              help="Output path")                               # Output path
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
    if noargs: interactive_welcome()
    else:
        done_something = False
        if sum([args[k] != None for k in ["query", "search", "chat"]]) > 1:
            if args["out"] != None: 
                print("Warning, output parameter was inconsitently used and will be ignored.")
                args["out"] = None

        place = ""        
        if args["query"] != None:
            place = args["query"].strip()
            if len(place) > 3:
                done_something = True
                console.rule("GeoQuery")
                q = GeoQuery("restaurant", place)
        
        if args["build"]:
            if place == "": 
                if args["interactive"]:
                    done_something = True
                    console.rule("BuildIndex")
                    interactive_buildindex()
                else:
                    print("No place provided.")
                    exit()
        
        if args["search"] != None:
            done_something = True
            console.rule("SemSearch")
            print("Semantic search for ", args["search"])
        
        if args["chat"] != None:
            args["interactive"] = True
            done_something = True
            console.rule("ChatBot")
            print("Chat bot not implemented yet.")
        
        if args["interactive"]:
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
                interactive_semsearch()  # Call the function
            case "ChatBot":
                print("TODO: ChatBot")
            case "Exit":
                finished = True
        
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

def interactive_webscrape():
    console = rich.console.Console()
    console.rule("WebScrape")

    data_path = os.path.join( os.path.dirname( os.path.dirname(__file__) ), "data")
    places = [d for d in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, d))]
    if len(places) == 0:
        console.print("No places found. Run the GeoQuery first."); return 
    menu = rich_menu.Menu(*places, title="Select place")
    place = str(menu.ask())
    visit_links(place)


def interactive_buildindex():
    console = rich.console.Console()
    console.rule("BuildIndex")
    data_path = os.path.join( os.path.dirname( os.path.dirname(__file__) ), "data")
    places = [d for d in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, d))]
    if len(places) == 0:
        console.print("No places found. Run the GeoQuery first."); return 
    menu = rich_menu.Menu(*places, title="Select place")
    place = str(menu.ask())
    build_database(place)

def interactive_semsearch():
    console = rich.console.Console()
    console.rule("SemSearch")
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    places = [d for d in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, d))]
    if len(places) == 0:
        console.print("No places found. Run the GeoQuery first."); return 

    query = rich.prompt.Prompt.ask("Search for")
    menu = rich_menu.Menu(*places, title="Select place")
    place = str(menu.ask())
    # TODO: Implement semantic search logic here
    print(f"Semantic search for '{query}' in '{place}'")

