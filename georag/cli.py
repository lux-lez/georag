# Command 
import os, sys
from random import randint
from argparse import ArgumentParser
import rich, rich.prompt, rich.console, rich_menu

from .geo import geolocate
#from .search import infer_amenities

def welcome(console = None):
    if console == None: console = rich.console.Console()
    console.rule("GeoRAG")

def yes_or_no(prompt : str) -> bool:
    """Ask yes or no question (boolen, default answer yes)"""
    answer = input(f"{prompt} [Y/n]")
    answer = answer.lower().strip()
    return not answer.startswith("n")

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

def menu(choices : list[str], title="Menu") -> int:
    m = rich_menu.Menu(*choices, title=title)
    choice = str(menu.ask())
    idx = choices.index(choice)
    return idx

def check_place(place : str, console=None):
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


def interactive_place(console=None) -> str:
    if console == None: console = rich.console.Console()
    place = None
    while place == None:
        p = console.input("Place ")
        p = check_place(p, console)
        if p != None: place = p 
    return place

def interactive_query(console=None):
    if console == None: console = rich.console.Console()
    q = console.input("Query ")
    #amenities = infer_amenities(q)
    #if len(amenities) == 0: 
    #    print("Matched Aamenities ", ", ".join(amenities))
    return q


def interactive_interface(console=None):
    if console == None: console = rich.console.Console()
    console.print("Interactive interface")
    place = interactive_place()
    query = interactive_query()
    console.print("...")


def parametric_interface(place : str, query : str, console=None):
    print("Parametric interface")
    place = check_place(place)
    console.print("...")

def interface(console=None):
    console = rich.console.Console()
    welcome(console=console)
    argv = [a for a in sys.argv if a != ""][1:]
    if len(argv) == 0: 
        interactive_interface(console=console)
    else:
        args = parse_args()
        parametric_interface(args["place"], args["query"], console=console)
