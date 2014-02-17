__author__ = 'Lucas Ou-Yang'

from django.core.management.base import BaseCommand, CommandError
import math
import Image
import ImageFile
import ImageOps
import cStringIO
import urllib2

from warnings import filterwarnings
import MySQLdb as Database

thumbnail_size = 70, 70

from Article.models import Source
from Wintria.settings import get_root_url

dest_thumb_url = '/home/wintrialucas/webapps/windjango/Wintria/Wintria/logo_static/logo_thumbs/'
def generate_thumb(url, domain):
    _file = cStringIO.StringIO(urllib2.urlopen(url, timeout=4).read())
    img = Image.open(_file)
    thumb = ImageOps.fit(img, thumbnail_size, Image.ANTIALIAS)
    thumb.save(dest_thumb_url + domain + '.png')

class Command(BaseCommand):
    filterwarnings('ignore', category = Database.Warning)

    help = 'Generates valid thumbnails for all source logos'

    def handle(self, *args, **options):
        domains = Source.objects.values_list('domain', flat=True)
        for d in domains:
            if d[-1] == '/':
                d = d[:-1]
            url = get_root_url() + '/static/logobank/' + d + '.png'
            try:
                generate_thumb(url, d)
            except Exception, e:
                print 'thumbnail error', str(e), d


if __name__ == '__main__':
    url = 'http://wintrialucas.webfactional.com/static/logobank/www.dailymail.co.uk.png'
    domain = 'www.dailymail.co.uk'
    generate_thumb(url, domain)


# def alt_thumb(url, domain):
#    _file = cStringIO.StringIO(urllib2.urlopen(url, timeout=4).read())
#    img = Image.open(_file)
#    img = prepare_image(img)
#    img.save(dest_thumb_url + domain + '.png')