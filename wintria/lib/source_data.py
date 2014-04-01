"""
"""
import re
import urllib2
import urllib
import os
from urlparse import urlparse

from BeautifulSoup import BeautifulSoup

from wintria.lib.bing_logo_extract import extract_bing_url
from wintria.lib import s3
from wintria.lib.imaging import thumbnail
from wintria.article.models import NO_DESC
from wintria.wintria.settings import PROJECT_ROOT

def url_exists(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'                                                                 # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'                                                                         # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'                                                # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'                                                        # ...or ipv6
        r'(?::\d+)?'                                                                          # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    c_regex = re.compile(regex)
    return (c_regex.search(url) != None)

def is_img(url):
    return ('.jpg' in url) or ('.png' in url) or ('.jpeg' in url) or ('.gif' in url)\
        or ('.bmp' in url) or ('.tiff' in url)

LINKS_W_IMGS = ['meta', 'link', 'og', 'img', 'a']
IMG_KEYWORDS = ['logo', 'thumb']
USER_AGENT = "Mozilla/5.0"

def url_into_query(url):
    url = urlparse(url).netloc
    url = url.split('.')
    if url[0] == 'www' or url[0] == 'www2': # cut out useless www super-domain
        url = url[1:]
    url = ' '.join(url)
    return url

def get_desc(soup):
    if not soup:
        print 'err, no soup, can\'t access desc, logo'
        return NO_DESC
    meta_desc = soup.find('meta', {'name':'description'})
    fb_desc = soup.find('meta', {'property':'og:description'})
    desc = None
    try:
        if meta_desc and meta_desc['content'].strip():
            desc = meta_desc['content']
        elif fb_desc and fb_desc['content'].strip():
            desc = fb_desc['content']
    except Exception, e:
        desc = None

    if not desc:
        desc = NO_DESC
    return desc

def get_logo(soup):
    fb_img = soup.find('meta', {'property':'og:image'})
    if fb_img and url_exists(fb_img['content']) and is_img(fb_img['content']):
        return fb_img['content']

    icon = soup.find('link', {'rel':'icon'})
    if icon and url_exists(icon['href']) and is_img(icon['href']):
        return icon['href']

    icon = soup.find('link', {'rel':'img_src'})
    if icon and url_exists(icon['href']) and is_img(icon['href']):
        return icon['href']

    return None

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

def get_soup(url):
    req = urllib2.Request(url, headers=hdr)
    try: con = urllib2.urlopen( req, timeout=3 )
    except Exception, e:
        print 'error opening url', str(e), 'at', url
        return None
    try: soup = BeautifulSoup(con.read())
    except Exception, e:
        print str(e), "Error with trying to open beautifulsoup, trying to query on", url
        return None
    return soup

def save_to_disk(url, domain):
    try: urllib.urlretrieve(url, PROJECT_ROOT + 'wintria/wintria/templates/static/logobank/' +
                                 domain + '.png')
    except Exception, e:
        print str(e), 'error downloading', domain, '\'s logo'

def save_logo(soup, domain):
    img_url = None
    if soup:
        img_url = get_logo(soup)
    if not img_url:
        img_url = extract_bing_url(domain)
    if img_url:
        print 'downloading logo for ...', domain
        save_to_disk(img_url, domain)
    else:
        pass

def push_s3(s):
    try:
        key = s.thumbnail_key()
        img, img_url = thumbnail(s.get_logo_url())
        local = key + '.jpg'
        if img is None:
            return
        try:
            img.save(local)
        except IOError: # converting to jpg causes errors sometimes
            print 'caught error'
            img.convert('RGB').save(local)

        abs_pth = os.path.abspath(local)
        print s3.upload_img(abs_pth, key, bucket='wintria-source-images')
        os.remove(abs_pth)

    except Exception, e:
        print('%s fail to save img %s' % (str(e), s.domain))
        return

if __name__ == '__main__':
    soup = get_soup('http://huffingtonpost.com')
    print get_desc(soup)
