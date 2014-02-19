"""
"""
from django.core.management.base import BaseCommand
from PIL import Image, ImageOps
import cStringIO
import urllib2

from warnings import filterwarnings
import MySQLdb as Database

from wintria.article.models import Source
from wintria.wintria.rename_this_to_settings import get_root_url, PROJECT_ROOT

thumbnail_size = 70, 70
dest_thumb_url = PROJECT_ROOT + 'wintria/wintria/logo_static/logo_thumbs/'

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
