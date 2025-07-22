
## Ensure that georag.py can be imported 
import os, sys
base_path = os.path.dirname(os.path.dirname(__file__)); sys.path.append(base_path)

from georag import *


print("# Testing georag.py ...")
places = [
    "Karlsruhe, Germany",
    "Heidelberg, Germany",
    "Berlin, Germany"
]
for i,place in enumerate(places):
    print(f"[] Test {i+1}/{len(places)}")
    GeoQuery("restaurant", place)
    print("\n")
