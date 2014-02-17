__author__ = 'louyang'

#from django.core.management.base import BaseCommand, CommandError
from urllib2 import Request, HTTPError, URLError, build_opener
from httplib import InvalidURL
#from lib.io import queryset_iterator
import urllib
import StringIO
import math
import Image
import ImageFile
import os
#from Article.models import Article

chunk_size = 1024
thumbnail_size = 90, 90

from lib import s3

def clean_url(url):
    """url quotes unicode data out of urls"""
    #url = unicode(url, 'utf8')
    url = url.encode('utf8')
    url = ''.join([urllib.quote(c) if ord(c) >= 127 else c for c in url])
    return url

def image_to_str(image):
    s = StringIO.StringIO()
    image.save(s, image.format)
    s.seek(0)
    return s.read()

def str_to_image(s):
    s = StringIO.StringIO(s)
    s.seek(0)
    image = Image.open(s)
    return image

def prepare_image(image):
    image = square_image(image)
    image.thumbnail(thumbnail_size, Image.ANTIALIAS) # this one is inplace
    return image

def image_entropy(img):
    """calculate the entropy of an image"""
    hist = img.histogram()
    hist_size = sum(hist)
    hist = [float(h) / hist_size for h in hist]
    return -sum([p * math.log(p, 2) for p in hist if p != 0])

def square_image(img):
    """if the image is taller than it is wide, square it off. determine
    which pieces to cut off based on the entropy pieces."""
    x,y = img.size
    while y > x:
        # slice 10px at a time until square
        slice_height = min(y - x, 10)

        bottom = img.crop((0, y - slice_height, x, y))
        top = img.crop((0, 0, x, slice_height))

        #remove the slice with the least entropy
        if image_entropy(bottom) < image_entropy(top):
            img = img.crop((0, 0, x, y - slice_height))
        else:
            img = img.crop((0, slice_height, x, y))

        x,y = img.size

    return img

def fetch_url(url, referer=None, retries=1, dimension=False):

    cur_try = 0
    nothing = None if dimension else (None, None)
    url = clean_url(url)

    if not url.startswith(('http://', 'https://')):
        return nothing

    while True:
        try:
            req = Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (compatible; MSIE 9.0; '
                                         'AOL 9.7; AOLBuild 4343.19; Windows NT 6.1; '
                                         'WOW64; Trident/5.0; FunWebProducts)')
            if referer:
                req.add_header('Referer', referer)

            opener = build_opener()
            open_req = opener.open(req, timeout=5)

            # if we only need the dimension of the image, we may not
            # need to download the entire thing
            if dimension:
                content = open_req.read(chunk_size)
            else:
                content = open_req.read()

            content_type = open_req.headers.get('content-type')

            if not content_type:
                return nothing

            if 'image' in content_type:
                p = ImageFile.Parser()
                new_data = content
                while not p.image and new_data:
                    try:
                        p.feed(new_data)
                    except IOError, e: # jpg error on some computers
                        print(str(e))
                        p = None
                        break
                    new_data = open_req.read(chunk_size)
                    content += new_data

                if p is None:
                    return nothing
                # return the size, or return the data
                if dimension and p.image:
                    return p.image.size
                elif dimension:
                    return nothing
            elif dimension:
                # expected an image, but didn't get one
                return nothing

            return content_type, content

        except (URLError, HTTPError, InvalidURL), e:
            cur_try += 1
            if cur_try >= retries:
                print('error while fetching: %s referer: %s' % (url, referer))
                print(str(e))
                return nothing
        finally:
            if 'open_req' in locals():
                open_req.close()


def thumbnail(url):
    content_type, image_str = fetch_url(url)
    if image_str:
        image = str_to_image(image_str)
        try:
            image = prepare_image(image)
        except IOError, e:
            # can't read interlaced PNGs, ignore
            if 'interlaced' in e.message:
                return None
        return image, url
    return None, None

'''
class Command(BaseCommand):

    def handle(self, *args, **options):
        articles = queryset_iterator(Article.objects.all())
        os.chdir('/home/wintrialucas/webapps/windjango/Wintria/dock/')

        for a in articles:
            try:
                key = a.thumbnail_key()
                img, img_url = thumbnail(a.thumb_url)
                local = key + '.jpg'
                if img is None:
                    continue
                try:
                    img.save(local)
                except IOError, e: # converting to jpg causes errors sometimes
                    print 'caught error'
                    img.convert('RGB').save(local)

                abs_pth = os.path.abspath(local)
                _ = s3.upload_img(abs_pth, key) # uploads and returns dest url
                os.remove(abs_pth)


            except Exception,e:
                print('%s fail to save img %s' % (str(e), a.url))
                #a.has_img = False
                #a.save()
                continue

'''
import base64
import hashlib
def thumbnail_key(url):
    return base64.urlsafe_b64encode(hashlib.md5(url).digest())

import codecs
if __name__ == '__main__':
    os.chdir('/Users/louyang/Dropbox/Programming/WebDev/Wintria/Article/management/commands/')
    f = codecs.open('urls2.txt', 'r+', encoding='utf8')
    lines = f.read().split('\r\n')
    lines = lines[::-1]

    cnt = 0
    for line in lines:
        cnt += 1
        if cnt % 2000 == 0:
            print cnt
        try:
            dat = line.split(' ')
            if len(dat) != 2:
                print 'not size 2?'
                continue
            article_url, img_url = dat[0], dat[1]
            key = thumbnail_key(article_url)
            img, img_url = thumbnail(img_url)
            local = key + '.jpg'
            if img is None:
                continue
            try:
                img.save(local)
            except IOError, e: # converting to jpg causes errors sometimes
                print 'caught error'
                img.convert('RGB').save(local)

            abs_pth = os.path.abspath(local)
            _ = s3.upload_img(abs_pth, key) # uploads and returns dest url
            os.remove(abs_pth)

        except Exception, e:
            print(str(e))
            continue


    f.close()
