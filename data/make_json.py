import pandas as pd
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry
import json

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,   
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def fix_string(text):
    if "index.html#Counter" in text:
        text = text[:-18]
    if (text[-1:] != '/') and (text[-4:] != 'html'):
        text = text + '/'
    if ('https://plato.stanford.edu/' in text):
        return text
    elif ('//' in text):
        dummy = list(text)
        dummy = dummy[3:]
        text = "entries" + "".join(dummy)
    elif ('..' in text):
        # Delete '..' from text
        dummy = list(text)
        dummy = dummy[2:]
        text = "entries" + "".join(dummy)
        # Add entries before fixed text
    # Add 'https://plato.stanford.edu/'
    text = 'https://plato.stanford.edu/' + text
    text = text.lower() # lowering string letters
    return text

def load_page(url):
    url = fix_string(url)
    response = requests_retry_session().get(url, timeout=5)
    raw_html = response.text
    html = BeautifulSoup(raw_html, 'html.parser')
    return html

# Take out links from all tags
def take_links_from_tags(topics):
    # Define link list
    links = []
    for topic in topics:
        link = topic.find_parent('a')['href']
        # Add element to link list
        links.append(link)
    return links

def download_page_data(link):
    # Open the page
    page = load_page(link)
    
    # Find title of the page
    title = page.h1.string
    if title is None:
        strings = [string for string in page.h1.strings]
        title = ''.join(strings)

    # Find intro paragraph
    intro = page.find('p').get_text()
        
    # Find links to related articles
    rel = page.find(id='related-entries')
    links = rel.p.find_all('a')
    links = [link['href'] for link in links if link['href'] != 'index.html'] 
    links = [fix_string(text) for text in links]
    
    return (title, intro, links)

def find_intro(link):
    page = load_page(link)
    intro = page.find('p').get_text()
    return intro

# Load page of content
html = load_page('https://plato.stanford.edu/contents.html')

# Take out all 'strong' tags
topics = html.find_all('strong')


df = pd.DataFrame()
nodes = []
connections = []
link_title_table = {}
links = take_links_from_tags(topics)
links = [link for link in links]


for link in links:
    title, intro, related_links = download_page_data(link)
    link_title_table[fix_string(link)] = title
    nodes.append({"id": title, "intro": intro, "address": link})
    print(title) # For tracking purposes
    for related in related_links:
        row = {"source": title, "target": related}
        connections.append(row)

df = pd.DataFrame(connections)
df = df.replace(link_title_table)
connections = df.to_dict('records')

data = {"nodes": nodes, "links": connections}

# Exporting data to json file
print("Starting export")
json_str = json.dumps(data, indent=2)
with open("data.json", "w") as f:
    f.write(json_str)

print("Done!")