import requests
import re
import pickle
import sys
from bs4 import BeautifulSoup

def getRealURL(response):
    tmp = response.text.replace('<link rel="canonical" href="', 'r@ndom}-=||').split('r@ndom}-=||')[-1]
    idx = tmp.find('"/>')
    real_link = tmp[:idx]
    return real_link

def getOriginalLinks(response):
    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    content = soup.find("div", {"id": "mw-content-text"})
    paragraphs = content.findChildren("div", recursive = False)[0].findChildren(recursive=False)
    for paragraph in paragraphs:
        if len(paragraph.findAll("span", {"id": "References"})) != 0:
            break
        if len(paragraph.findAll("span", {"id": "Notes"})) != 0:
            break
        if len(paragraph.findAll("span", {"id": "External_links"})) != 0:
            break
        for link in paragraph.findAll("a"):
            href = str(link.get('href'))
            match_wiki = re.match(r'/wiki/', href, re.M|re.I)
            match_colon = ':' in href
            if match_wiki and not match_colon:
                links.append(href.split("/wiki/")[1])
    return set(links)

def addLinks(queue, redirects, links, broken_links):
    try:
        response = requests.get("https://en.wikipedia.org/wiki/" + queue[0], timeout=1)
    except:
        print("Failed to load queue[0] page: https://en.wikipedia.org/wiki/" + queue[0])
        return None
    queue.pop(0)
    key = getRealURL(response).split("/wiki/")[1]
    redirects.update({key: key})
    if key not in links:
        print("Adding to list: " + key)
        f_links = []
        broken = []
        o_links = getOriginalLinks(response)
        for link in o_links:
            if link in redirects:
                value = redirects[link]
                f_links.append(value)
                if value not in links:
                    queue.append(value)
            else:
                new_response = None
                tries = 0
                worked = False
                while tries < 100:
                    try:
                        new_response = requests.get("https://en.wikipedia.org/wiki/" + link, timeout=1)
                        worked = True
                        break
                    except:
                        print("Failed to load page: https://en.wikipedia.org/wiki/" + link)
                        tries += 1
                if worked:
                    new_url = getRealURL(new_response)
                    value = new_url.split("/wiki/")[1]
                    f_links.append(value)
                    redirects.update({link: value})
                    if value not in links:
                        queue.append(value)
                else:
                    broken.append(value)
        links[key] = set(f_links)
        if len(broken) > 0:
            broken_links[key] = set(broken_links)
        print("Added to list: " + key)

queue = ['Niskayuna_High_School']
redirects = {}
links = {}
broken_links = {}
try:
    pkl_file = open('data.pkl', 'rb')
    data = pickle.load(pkl_file)
    queue = data[0]
    redirects = data[1]
    links = data[2]
    broken_links = data[3]
    pkl_file.close()
except:
    print("file not found")

iter = int(float(sys.argv[1])) if len(sys.argv) > 1 else 1
for _ in range(iter):
    addLinks(queue, redirects, links, broken_links)
    data_file = open('data.pkl', 'wb')
    pickle.dump((queue, redirects, links, broken_links), data_file)
    data_file.close();
