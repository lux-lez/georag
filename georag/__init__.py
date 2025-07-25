
import os
import sys
import argparse 

from .geo_query import *
from .scrape_website import *

def parse_args():
    a = argparse.ArgumentParser(
        prog = "GeoRAG",
        description="",
        epilog="",
    )
    a.add_argument("-q", "--query")
    return a.parse_args()

def run():
    print(sys.argv)
    args = parse_args()
    done_something = False
    print("Args ", args)
    if type(args.query) == str and len(args.query.strip()) > 3:
        print("Geo query ", args.query)
        q = GeoQuery("restaurant", args.query)
        if q != None: done_something = True
    
    if not done_something:
        print("Nothing to be done.")

#TODO: only export relevant functions
# __all__ = [ "GeoQuery" ... ]