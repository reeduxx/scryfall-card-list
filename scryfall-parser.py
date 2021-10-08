#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
    A small Python project that fetches lists of cards by set from the Scryfall API (https://scryfall.com/docs/api)
'''

import argparse
import csv
import inspect
import requests
from requests.exceptions import HTTPError
import sys
from xml.dom import minidom
from xml.etree import ElementTree

__author__ = 'Brighton Ulery'
__credits__ = ['Brighton Ulery']
__license__ = 
__version__ = '0.0.1'
__maintainer__ = 'Brighton Ulery'
__email__ = 'brighton.ulery@gmail.com'
__status__ = 'Dev'
    
class SetNotFoundError(Exception):
    def __init__(self, msg):
        try:
            ln = sys.exc_info()[-1].tb_lineno
        except AttributeError:
            ln = inspect.currentframe().f_back.f_lineno
        self.args = "{0.__name__} (line {1}): {2}".format(type(self), ln, msg), sys.exit(self)
    
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('set', help = 'The set from which you want to pull cards from')
    parser.add_argument('-e', '--ext', help = 'The file extension you wish to write to', default='txt')
    args = parser.parse_args()
    return args

def main():
    inputs = parse_args()
    names = parse_api(inputs.set)
    names.sort()
    print('Writing', len(names), 'card names. . .')
    write_to_file(inputs.set, inputs.ext, names)

def parse_api(set):
    print('Checking set code. . .')
    
    if(set not in fetch_sets()):
        raise SetNotFoundError('Other error occurred: Invalid set code: ' + set)
        
    api = 'https://api.scryfall.com/cards/search?order=set&q=e%3A' + set + '&unique=prints'
    print('Fetching card list. . .')
    
    try:
        names = []
        response = requests.get(api)
        response.raise_for_status()
        jsonResponse = response.json()
        
        for card in jsonResponse['data']:
            for k, v in card.items():
                if k == 'name':
                    names.append(v)
        
        if(jsonResponse['has_more']):
            names.extend(parse_pages(jsonResponse['next_page']))
        
        return names
    
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

def parse_pages(page):
    names = []
    response = requests.get(page)
    response.raise_for_status()
    jsonResponse = response.json()
    
    for card in jsonResponse['data']:
        for k, v in card.items():
            if k == 'name':
                names.append(v)
    
    if(jsonResponse['has_more']):
        names.extend(parse_pages(jsonResponse['next_page']))
    
    return names

def write_to_file(set, ext, names):
    filename = set + '.' + ext
    
    match ext:
        case 'csv':
            file = open(filename, 'w', newline='')
            csvWriter = csv.writer(file)
        
            for name in names:
                csvWriter.writerow([name])
                
        case 'xml':
            file = open(filename, 'w')
            cards = ElementTree.Element('cards')
            
            for name in names:
                ElementTree.SubElement(cards, 'card').text= name
            
            data = minidom.parseString(ElementTree.tostring(cards, encoding = 'unicode')).toprettyxml()
            file.write(data)
    
        case _:
            file = open(filename, 'w')
        
            for name in names:
                file.write(name + '\n')
    
    print('Cards written to:', set + '.' + ext)
    file.close()

def fetch_sets():
    try:
        sets = []
        api = 'https://api.scryfall.com/sets'
        response = requests.get(api)
        response.raise_for_status()
        jsonResponse = response.json()
        
        for set in jsonResponse['data']:
            for k, v in set.items():
                if k == 'code':
                    sets.append(v)
    
        return sets
        
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

if __name__ == '__main__':
    main()