
import os
import argparse 

from .geo_query import geoquery_place
from .scrape_website import scrape_website

__all__ = ["geoquery_place", "scrape_website"]

#data_path = os.path.join( os.path.abspath(os.curdir), "data")
#data_path = os.path.join( os.path.dirname(__file__), "data")