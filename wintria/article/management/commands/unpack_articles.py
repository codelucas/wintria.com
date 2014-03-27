"""
Wintria.com listens on the dock/ directory for new 'Saved_Articles.txt' files
to be sent over via ssl from our crawlers (or this local machine if we configure it so).
It then opens the file, parses it, and saves the article data in that file into
the MySQL database.

We do it this way instead of directly making a database connection because
I just wanted to use django's ORM :).
"""
import os
import codecs
import re
import time
import pytz
import gc

from datetime import datetime, timedelta
from warnings import filterwarnings
from urlparse import urlparse
import MySQLdb as Database
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from wintria.article.models import Article, Source
from wintria.lib.source_data import get_desc, get_soup, save_logo, push_s3
from wintria.wintria.settings import PROJECT_ROOT

MAX_ARCHIVE_COUNT = 1000000
INPUT_FILE = 'Saved_Articles.txt'

INPUT_NAME = PROJECT_ROOT + 'wintria/dock/' + INPUT_FILE
LOC_DIR = PROJECT_ROOT + 'wintria/dock/'

PROPERTY_DELIMITER = u";;"
ARTICLE_DELIMITER = u"\$\$"

def purge_old():
    now = datetime.now()
    two_days_ago = now - timedelta(days=2)
    epoch = datetime(2000, 4, 20, 18, 4, 34, 44710)
    western = pytz.timezone('US/Pacific')

    two_days_ago = western.localize(two_days_ago)
    epoch = western.localize(epoch)

    count = 0

    # outdated = article.objects.filter(timestamp__range=[epoch, two_days_ago])
    # for a in outdated: # Delete all articles over 3 days old # RE-ENABLE This later, when we have more articles
    #    a.delete()
    #    count += 1

    overflown = Article.objects.order_by('-pk')[MAX_ARCHIVE_COUNT:]
    for a in overflown:
        a.delete()
        count += 1
    print count, "Articles have been deleted from the DB to meet the", \
        MAX_ARCHIVE_COUNT, "article Cap"

def open_delimited(filename, delimiter, chunksize=1024, *args, **kwargs):
    with codecs.open(filename, *args, **kwargs) as infile:
        remainder = ''
        for chunk in iter(lambda: infile.read(chunksize), ''):
            pieces = re.split(delimiter, remainder+chunk)
            for piece in pieces[:-1]:
                yield piece
            remainder = pieces[-1]
        if remainder:
            yield remainder

class Command(BaseCommand):
    help = 'Manages incoming Saved_Articles.txt files'

    def handle(self, *args, **options):
        filterwarnings('ignore', category=Database.Warning)
        ts = time.time()
        self.stdout.write('unpacking files and saving to db... ' +
                          datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))

        total, count, dups = 0, 0, 0
        files = os.listdir(LOC_DIR)

        if INPUT_FILE not in files:
            self.stdout.write(INPUT_FILE + ' has not arrived yet!')
            return

        # Parses line by line
        for a in open_delimited(INPUT_NAME, ARTICLE_DELIMITER, 1024, encoding='utf-8'):
            total += 1

            dat = a.split(PROPERTY_DELIMITER)
            if len(dat) != 6:
                self.stdout.write('length not 6')
                continue

            # If a source matches the article, sync em.
            # If not, make a new source and sync em.
            domain = urlparse(dat[0]).netloc

            try:
                s = Source.objects.get(domain=domain)
            except Source.DoesNotExist:
                s = None

            if not s:
                print 'creating new source from %s' % domain

                if len(domain.split('.')) >= 2:
                    try:
                        url = 'http://'+domain
                        soup = get_soup(url)
                        desc = get_desc(soup)
                        save_logo(soup, domain)

                        s = Source(
                                domain=domain,
                                description=desc
                            ).save()

                        push_s3(s)

                    except IntegrityError, e:
                        print "Integrity error on source", str(e)
                    except Exception, e:
                        print str(e)
                else:
                    print "%s domain isn't valid" % domain

            if s:
                try:
                    _article=Article(
                        url=dat[0],
                        title=dat[1],
                        txt=dat[2],
                        keywords=dat[3],
                        source=s,
                        thumb_url=dat[4], # Any non-url strings will become u'None'
                        has_img=int(dat[5])
                    )
                    # Canon form
                    url_obj=urlparse(dat[0]) # dat[0] is the url
                    domain, scheme = url_obj.netloc, url_obj.scheme
                    if domain.startswith(u'www.'):
                        domain = domain[4:]
                    if scheme == u'https':
                        scheme = u'http'
                    f_url = scheme + u'://' + domain + url_obj.path

                    # Make sure incoming article's canon form is not already present
                    # (without www. or https://)
                    # If we get a non existing error, we are good to go!
                    try:
                        _dup = Article.objects.get(url=f_url)
                    except Article.DoesNotExist:
                        pass
                    except Exception, e:
                        print 'article unqiue excep', str(e)
                        continue
                    else:
                        dups += 1
                        continue # skip saving!

                    _article.save()
                    count += 1

                except IntegrityError, e: # catches the URL - Unique setting.
                    if e.args[0] == 1062:
                        dups += 1
                except Exception, e:
                    print 'Regular ex: ', str(e)
                    pass
            else:
                print 'no source!?'
                try:
                    'for ', dat[0]
                except Exception,e:
                    print '%s failed to even print dat[0]' % str(e)

            # gc.collect()

        os.remove(INPUT_NAME)
        self.stdout.write(str(count) + ' files successfully unpacked and saved and we had '
                          + str(dups) + ' duplicate articles and we have ' + str(total) +
                          ' total incoming articles ' +
                          datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
        purge_old()
