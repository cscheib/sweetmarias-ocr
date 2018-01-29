#!/usr/bin/env python

# Written by: Chris Scheib

# functions:
#   - category_parse(category_uri) - returns list of URIs to each variety
#   - variety_parse(variety_uri)  - returns URI to image
#   - variety_name(variety_uri)  - returns name of variety
#   - get_image(image_uri) - returns image as Bytes object
#   - variety_score(image_bytes) - returns score as an integer or maybe float(?)


import requests
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import re
from io import BytesIO

baseurl = "https://www.sweetmarias.com"
category = "/category/good-for-espresso"
debug = False

def category_parse(category_uri):
    variety_list = []

    category_page = requests.get(baseurl + category_uri)
    soup = BeautifulSoup(category_page.text, 'html.parser')
    for item in soup.findAll('div', class_='item'):
        coffee = item.find('div', class_='meta-container')
        variety_name = coffee.find('h3').find('a').text # currently unused
        variety_cost = coffee.find('i').text # currently unused
        variety_uri  = coffee.find('h3').find('a')["href"]
        variety_list.append(variety_uri)
    return variety_list

# TODO: change return to some form of structured data with all info

def variety_parse(variety_uri):
    variety_page = requests.get(baseurl + variety_uri)
    soup = BeautifulSoup(variety_page.text, 'html.parser')
    images = soup.findAll("li",class_="four columns mobile-two")
    image_uri = "http:" + images[-1].find("a")["href"]
    return image_uri

# This function assumes the last list item (li) contains the tasting score image

def variety_score(score_image):
    image_text = pytesseract.image_to_string(score_image)
    if debug:
        print("=---------=")
        print(image_text)
        print("=---------=")
    score_regex = re.compile('Score:* (\d+)')
    match = score_regex.search(image_text)
    if match:
        score = match.group(1)
        return score
    else:
        return "Unable to parse using OCR"

def variety_name(variety_uri):
    variety_page = requests.get(baseurl + variety_uri)
    soup = BeautifulSoup(variety_page.text, 'html.parser')
    title = soup.find("title")
    return title.text

def get_image_uri(image_uri):
    r = requests.get(image_uri)
    image_content =  Image.open(BytesIO(r.content))
    return image_content

def get_image_file(image_file):
    image_content = Image.open(image_file)
    return image_content

########################

for coffee in category_parse(category):
    if debug:
        print("Variety URI: " + coffee)
        print("Image URI: " + variety_parse(coffee))
        print("Variety Score: " + variety_score(get_image_uri(variety_parse(coffee))))
        print("Variety Name: " + variety_name(coffee))
        print("=================")
    else:
        print("Variety Name: " + variety_name(coffee))
        print("Score: " + variety_score(get_image_uri(variety_parse(coffee))))
        print("=================")
