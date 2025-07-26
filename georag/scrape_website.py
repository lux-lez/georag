import os
import yaml
import requests
import urllib.parse
from bs4 import BeautifulSoup
from tqdm import tqdm

from .utils import alphanumeric
from .file_system import get_data_path
from .constants.files import MediaCategories, MediaRules

# Exclude unwanted tags
def is_visible(tag, exclude_tags=[], exclude_keywords=[]):
    if tag.parent.name in exclude_tags:
        return False
    # Exclude by class or id keywords
    attrs = tag.parent.attrs
    for key in ['class', 'id']:
        if key in attrs:
            if any(any(word in v.lower() for word in exclude_keywords) for v in (attrs[key] if isinstance(attrs[key], list) else [attrs[key]])):
                return False
    return True

def get_media_sublink(link:str) -> str:
    format = ""
    all_formats = []
    global MediaCategories
    for l in MediaCategories.values(): 
        all_formats += l
    for ext in all_formats:
        if ext in link: 
            format = ext
    if format == "": return ""
    return link.split(format)[0] + format

def get_media_category(link:str) -> str:
    ext = os.path.splitext(link)[-1]
    for c in MediaCategories:
        if ext in MediaCategories[c]: 
            return c
    return ""



def download_file(url: str, save_path: str):
    """
    Download a file from a URL and save it to the specified path.

    Args:
        url (str): The URL of the file to download.
        save_path (str): The local file path to save the downloaded file.
    """
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def scrape_website(url : str, include_text=True, include_media=True, internal_only=True, verbose=True):
    """
    Scrape a website and return a dictionary with text elements and media links.

    Args:
        url (str): The URL to scrape.
        include_text (bool): Whether to include text elements.
        include_media (bool): Whether to include media/document links.
        internal_only (bool): If True, only return URLs from same domain name.
        verbose (bool): Whether to output 

    Returns:
        dict: {
            'title' [title, subtitle, etc. ... ]
            'text': [list of text elements ... ],                   #(optional)
            'media': [list of media/document URLs ... ]             #(optional)
            'links' [list of hyperlinks to other pages ... ]    #(optional)
        } 
    """

    # parse URL response 
    
    try:
        resp = requests.get(url, timeout=3)
    except Exception as e:
        if verbose: print("Could not open URL ", url)
        return 
    soup = BeautifulSoup(resp.text, 'html.parser')
    base_url = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(url))
    if verbose: print("Visited ", base_url)

    # Initialize result dictionary with title 
    result = {}
    if soup.title != None:
        result["title"] = soup.title.contents
    else:
        result["title"] = url.replace("https:", "").replace("/", "").split(".")[0].capitalize()

    # List of text elements
    if include_text:
        texts = []

        # Define tags and classes/ids to exclude
        exclude_tags = {'nav', 'footer', 'aside', 'form', 'header', 'script', 'style'}
        exclude_keywords = ['nav', 'footer', 'sidebar', 'login', 'signup', 'advert', 'ads', 'banner']

        # Try to find main content
        main_content = soup.find('main') or soup.find('article') or soup.find('section') or soup.body
        if main_content:

            # filter tags  
            for tag in main_content.find_all(string=True):
                content = tag.strip()
                if len(content) > 9 and " " in content: 
                    if content and is_visible(tag, exclude_tags, exclude_keywords):
                        texts.append(content)

        result['text'] = texts

    # List of media elements
    if include_media:
        media_links = set()

        # Images
        if include_media:    
            for img in soup.find_all('img', src=True):
                link = urllib.parse.urljoin(base_url, img['src'])
                if not internal_only or urllib.parse.urlparse(link).netloc == urllib.parse.urlparse(base_url).netloc:
                    media_links.add(link)        
    
    # List of references to other web pages 
    reference_links = set()

    # Documents and other media
    for a in soup.find_all('a', href=True):
        href = a['href']
        link = urllib.parse.urljoin(base_url, href)
        if not internal_only or urllib.parse.urlparse(link).netloc == urllib.parse.urlparse(base_url).netloc:
            
            # check if file is media
            media_sublink = get_media_sublink(link) 
            if media_sublink != "": 
                if include_media:
                    media_links.add(media_sublink)
            else: 
                reference_links.add(link)

    # Ensure media links have valid extension   
    if include_media:
        n_ignored = 0
        valid_media_links = []
        for link in media_links:
            s = get_media_sublink(link)
            if s != "":
                c = get_media_category(s)
                if c != "":
                    if MediaRules[c] == "save":
                        valid_media_links.append(s)
                    else:
                        n_ignored += 1
        media_links = valid_media_links

    # Add the results together
    if verbose: print(f"  Found {len(reference_links)} links ")
    result["links"] = list(reference_links)
    if include_media:
        if verbose: print(f"  Found {len(media_links)} media files (ignored {n_ignored}) ")
        result["media"] = list(media_links)        
    
    return result 


def visit_link(links_path: str, out_path: str = "", verbose=True):
    '''
    Visit one unvisited link from a scraped website. 

    Args:
        links_path (str): path to unified resource links file (.yaml file)
        out_path   (str): path to output (optional)
    '''

    # by default save to same folder as links file
    if out_path == "":
        out_path = str(os.path.dirname(links_path))

    ext = os.path.splitext(links_path)[-1]

    # load yaml file
    if ext == ".yaml":
        try:
            with open(links_path, "r") as f:
                links_yaml = yaml.safe_load(f.read())

            if "unvisited" not in links_yaml or not links_yaml["unvisited"]:
                unvisited_links = []
            else:
                unvisited_links = links_yaml["unvisited"]

            if verbose:
                print(f"Visiting {1 if unvisited_links else 0} link(s).")

            new_media = []
            new_links = []

            # Only visit the first unvisited link
            if unvisited_links:
                link = unvisited_links[0]
                if link.startswith("http") or link.startswith("www"):
                    # Visit website and get contents
                    result = scrape_website(link, verbose=verbose)
                    if result is not None:
                        # Write website text to markdown file
                        n_websites = len([
                            f for f in os.listdir(out_path)
                            if f.startswith("website_") and f.endswith(".md")
                        ])
                        result_path = os.path.join(out_path, "website_" + str(n_websites + 1) + ".md")
                        markdown = "# " + " ".join(result["title"]) + "\n\n" + "\n".join(result["text"])
                        with open(result_path, "w") as f:
                            f.write(markdown)

                        # Save URLs for hyperlinks and media files
                        new_links.extend(result["links"])
                        new_media.extend(result["media"])

                        # Download media files if they don't exist yet
                        for media in new_media:
                            media_path = os.path.join(out_path, os.path.split(media)[-1])
                            if not os.path.isfile(media_path):
                                download_file(media, media_path)

            # Get already visited links
            visited_links = links_yaml.get("visited", [])

            # Move the visited link from unvisited to visited
            if unvisited_links:
                visited_links.append(unvisited_links[0])
                visited_links = list(set(visited_links))  # remove duplicates

            # Set new links to unvisited, excluding already visited
            updated_unvisited_links = [
                link for link in new_links
                if link not in visited_links
            ]
            # Add the remaining unvisited links (except the first, which was just visited)
            if len(unvisited_links) > 1:
                updated_unvisited_links.extend(unvisited_links[1:])

            with open(links_path, "w") as f:
                f.write(yaml.dump({"unvisited": updated_unvisited_links, "visited": visited_links}))

        except Exception as e:
            print("YAML parsing error in ", links_path)
            print(e)
            return None

    else:
        raise ValueError(f"Links must be .yaml file. Received {ext} instead.")


def visit_websites(place : str, verbose=True):
    '''
    Loop over all amenities and scrape the websites.

    Args:
        place : str - which geographical place (either name or alphanumeric string) 
    '''

    # geo query if files don't exists
    path = get_data_path( alphanumeric(place) )
    if not os.path.isdir(path):
        q = GeoQuery(place)

    # iterate over amenities
    amenities_path = os.path.join(path, "amenities")
    amenities = [d for d in os.listdir(amenities_path) if os.path.isdir(os.path.join(amenities_path, d))]
    iterations = range(len(amenities))
    if verbose: iterations = tqdm(iterations, desc="Scraping")
    for i in iterations:
        amenity = amenities[i]

        # Visit links 
        links_path = os.path.join(amenities_path, amenity, "links.yaml")
        visit_link(links_path, verbose=False)