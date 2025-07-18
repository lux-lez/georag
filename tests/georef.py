import os, sys

## Ensure that georag.py can be imported 
#sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Ensure that georag.py in the parent directory can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from georag import *

print("# Testing georag.py ...")
print("[] Test 1/3")
place_information("Karlsruhe, Germany")
print("\n")

print("[] Test 2/3")
place_information("Heidelberg-Südstadt, Heidelberg, Germany")
print("\n")

print("[] Test 3/3 (imaginary city, should fail)")
place_information("Umpalumpa, Germany")
print("\n")
