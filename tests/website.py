
import os, sys

## Ensure that georag.py can be imported 
#sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Ensure that georag.py in the parent directory can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from georag import scrape_website

print("# Testing Website scraper")
data_path = os.path.join( os.path.dirname(os.path.dirname(__file__)), "data")
print("Data path ", data_path)

for url in [
    "https://mahmouds.de/en/home-en/",
    "https://www.uuuhmami.com",
    "https://bellini-heidelberg.de/" ]:

    print("[] Scraping {url}")
    website_text = scrape_website("https://mahmouds.de/en/home-en/", markdown=True)
    output_path = os.path.join(data_path, "Heidelberg_Germany", "restaurants", "mahmouds")
    os.makedirs(output_path, exist_ok=True)
    with open(os.path.join(output_path, "description.md")) as f:
        f.write(website_text)
    print("Written to ", os.path.abspath(output_path) )