"""
"""
import os
import sys
import urllib
import urllib2
import json
from urlparse import urlparse

ACCT_KEY = 'lOy/DHCCQA1e8fjX4U7AUd7/qNRKaRCUX/NTYMyioH0'
USR_NAME = '27e67155-f7a2-45e1-ac4d-d952a1d1f70f'

def extract_bing(topic):
    if len(topic) > 4 and topic[-4:] != 'logo':
        topic =  topic + ' ' + 'logo'
    topic = "'" + topic + "'"
    quoted_query = urllib.quote(topic)

    root_url = "https://api.datamarket.azure.com/Bing/Search/"
    search_url = root_url + "Image?$format=json&Query=" + quoted_query

    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, search_url, USR_NAME, ACCT_KEY)

    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)

    data_dict = urllib2.urlopen(search_url).read()
    data_dict = json.loads(data_dict)
    data_dict = data_dict['d']
    data_dict = data_dict['results']
    return data_dict[0]['Thumbnail']['MediaUrl']

EXTENSIONS = [
    'com',
    'co',
    'us',
    'net',
    'org',
    'mil',
    'gov',
    'edu',
    'store',
    'web',
    'de',
    'uk',
    'ru',
    'cn',
    'se',
    'jp'
]

def name_from_domain(domain):
    chunked = domain.split('.')
    if chunked[0] == 'www':
        chunked = chunked[1:]
    chunked = chunked[:-1]
    for EX in EXTENSIONS:
        for i,chunk in enumerate(chunked):
            if EX == chunk:
                del chunked[i]
    return ' '.join(chunked)

def extract_bing_url(domain):
    new_logo = None
    try:
        #domain = urlparse(url).netloc
        name = name_from_domain(domain)
        new_logo = extract_bing(name)
        print new_logo
    except Exception,e:
        print 'bing raw extract err', str(e)
        pass
    return new_logo
