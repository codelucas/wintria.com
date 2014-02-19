"""
"""
import os
from django.core.management.base import BaseCommand

from wintria.lib.io import queryset_iterator
from wintria.lib.imaging import thumbnail
from wintria.lib import s3
from wintria.article.models import Source
from wintria.wintria.rename_this_to_settings import PROJECT_ROOT

chunk_size = 1024
thumbnail_size = 40, 40

class Command(BaseCommand):

    def handle(self, *args, **options):
        sources = queryset_iterator(Source.objects.all())
        os.chdir(PROJECT_ROOT + 'wintria/dock/')

        for s in sources:
            try:
                key = s.thumbnail_key()
                img, img_url = thumbnail(s.get_logo_url())
                local = key + '.jpg'
                if img is None:
                    print s.domain, 'does not have an img'
                    continue
                try:
                    img.save(local)
                except IOError: # converting to jpg causes errors sometimes
                    print 'caught error'
                    img.convert('RGB').save(local)

                abs_pth = os.path.abspath(local)
                print s3.upload_img(abs_pth, key, bucket='wintria-source-images') # uploads and returns dest url
                os.remove(abs_pth)

            except Exception, e:
                print('%s fail to save img %s' % (str(e), s.domain))
                continue

