# Command 
import os, sys
from random import randint
from argparse import ArgumentParser
import rich, rich.prompt, rich.console, rich_menu

from .geo import geolocate
from .search import semantic_search
from .timing import timer_start, timer_end
from .vectordb import build_database
#from .search import infer_amenities
from .pipeline import pipeline

def yes_or_no(prompt : str) -> bool:
    """Ask yes or no question (boolen, default answer yes)"""
    answer = input(f"{prompt} [Y/n]")
    answer = answer.lower().strip()
    return not answer.startswith("n")

def menu(choices : list[str], title="Menu") -> int:
    """Ask for a choice from the options in a list
    Args: list of choices
    Returns: index of choice 
    """
    m = rich_menu.Menu(*choices, title=title)
    choice = str(menu.ask())
    idx = choices.index(choice)
    return idx


def parse_args() -> dict:

    # Parser
    a = ArgumentParser(
        prog = "georag",
        description="GeoRAG is geographically knowledgable AI search assistent.",
        epilog="(C) 2025 GPLv3 by Luca Lenz",
    )
    # In scope of project just limited to restaurants
    a.add_argument("place", type=str, help="where")
    a.add_argument("query", type=str, help="what")
    args = a.parse_args()

    # convertNamespace to dictionary
    argnames = [
        k for k in dir(args) 
        if not (k.startswith("_") or k.endswith("_"))
    ]
    args = {k : getattr(args, k) for k in argnames}

    return args


def check_place(place : str, console=None):
    """Check if place is geolocateable and if so returns address"""
    if console == None: console = rich.console.Console()
    location = geolocate(place)
    if location == None: 
        console.print("Place ", place, " is not geolocatable. Please try again.")
        return None
    else:
        found_place = True
        place = location.address
        print("Located place ", place)
    return place


def run_all(place, query, console=None, client=None, verbose=True ):
    """Run everything"""
    print("Running pipeline")
    if client == None: _client = build_database(place)
    else: _client = client  

    if _client != None: 
        t = timer_start("GeoRAG pipeline")
        pipeline(place, query, client=_client, verbose=verbose)
        timer_end(t)

    if client == None and _client != None: _client.close()

def parametric_interface(console=None):
    if console == None: console = rich.console.Console()
    args = parse_args()
    place, query = args["place"], args["query"]
        
    print("Parametric interface")
    place = check_place(place)
    if place != None:
        run_all(place, query)

def interactive_interface(console=None):
    if console == None: console = rich.console.Console()
    console.print("Interactive interface")

    console.rule("Enter Place")
    place = None
    while place == None:
        p = console.input("Place ")
        p = check_place(p, console)
        if p != None: place = p 
    
    console.rule("Ask Question")
    finished = False 
    while not finished:
        client = build_database(place)
        query = console.input("Query ")
        run_all(place, query, client=client)
        finished = not yes_or_no("Continue?")
    client.close()

def interface(console=None):
    if console == None: console = rich.console.Console()
    console.rule("GeoRAG")
    argv = [a for a in sys.argv if a != ""][1:]
    if len(argv) == 0: 
        interactive_interface(console=console)
    else:
        parametric_interface(console=console)
