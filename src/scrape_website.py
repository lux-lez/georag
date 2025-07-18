import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

MediaFormats = [
    '.txt', '.md',
    '.pdf', '.doc', '.docx', 
    '.mp3', '.mp4', '.avi', '.mov', 
    '.zip', '.rar', '.7z', 
    '.png', '.jpg', '.jpeg', '.gif', '.svg'
]

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


def scrape_website(url : str, include_text=True, include_media=True, internal_only=False, markdown=True):
    """
    Scrape a website and return a dictionary with text elements and media links.

    Args:
        url (str): The URL to scrape.
        include_text (bool): Whether to include text elements.
        include_media (bool): Whether to include media/document links.
        internal_only (bool): If True, only return internal URLs.
        markdown (bool): If True write output as a text.

    Returns:
        dict: {
            'title' [title, subtitle, etc. ... ]
            'text': [list of text elements ... ],               
            'media': [list of media/document URLs ... ]             #(optional)
            'reference' [list of hyperlinks to other pages ... ]    #(optional)
        }
    """

    # parse URL response 
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    base_url = "{0.scheme}://{0.netloc}".format(urlparse(url))
    print("Base URL ", base_url)
    result = {"title" : soup.title.contents}

    # List of text elements
    if include_text:
        texts = []

        # Define tags and classes/ids to exclude
        exclude_tags = {'nav', 'footer', 'aside', 'form', 'header', 'script', 'style'}
        exclude_keywords = ['nav', 'footer', 'sidebar', 'login', 'signup', 'advert', 'ads', 'banner']

        # Try to find main content
        main_content = soup.find('main') or soup.find('article') or soup.find('section') or soup.body

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
                link = urljoin(base_url, img['src'])
                if not internal_only or urlparse(link).netloc == urlparse(base_url).netloc:
                    media_links.add(link)

    # List of references to other web pages 
    reference_links = set()

    # Documents and other media (pdf, doc, mp4, etc.)
    for a in soup.find_all('a', href=True):
        href = a['href']
        link = urljoin(base_url, href)
        if not internal_only or urlparse(link).netloc == urlparse(base_url).netloc:
            if include_media and any(href.lower().endswith(ext) for ext in MediaFormats):                    
                media_links.add(link)
            else: 
                reference_links.add(link)

    # Add the results together
    result['reference'] = list(reference_links)
    if include_media:
        result['media'] = list(media_links)        
    
    # Wrap result in markdown
    if markdown:
        result = "\n\n".join([
            "# " + " ".join(result["title"]),
            "\n".join(result["text"]),
            "## Reference\n" + "\n".join(result["reference"]) 
        ] + ([] if not include_media else [
            "## Media\n" + "\n".join(result["media"])
        ]))
    return result

website = scrape_website("https://mahmouds.de/en/home-en/", markdown=True)