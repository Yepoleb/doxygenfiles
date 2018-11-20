import os
from os import path
import sys
from lxml import html
import urllib.parse
import requests

BLACKLIST = ["stdint.h"]

if len(sys.argv) < 2:
    print("Missing arguments!")
    print("Usage: {} <base_url> <directory>".format(sys.argv[0]))
    exit(1)

base_url = sys.argv[1]
code_dir = sys.argv[2]
os.makedirs(code_dir, exist_ok=True)

session = requests.Session()

list_url = urllib.parse.urljoin(base_url, "files.html")
list_bytes = session.get(list_url).content
list_tree = html.fromstring(list_bytes)
list_links = list_tree.xpath('.//table[@class="directory"]/tr/td[1]/a[1]/@href')

for file_link in list_links:
    print("Downloading", file_link)
    file_url = urllib.parse.urljoin(base_url, file_link)
    file_bytes = session.get(file_url).content
    file_tree = html.fromstring(file_bytes)

    file_title = file_tree.find('.//div[@class="title"]').text
    if file_title in BLACKLIST:
        continue

    lines = file_tree.findall('.//div[@class="fragment"]/div[@class="line"]')
    text = ""
    for line in lines:
        line_text = "".join(line.xpath(".//text()"))
        text += line_text[line_text.find("\xA0") + 1:] + "\n"

    with open(path.join(code_dir, file_title), "w") as file_out:
        file_out.write(text)
