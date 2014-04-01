"""
Wintria.com listens on the dock/ directory for new 'Saved_Articles.txt' files
to be sent over via ssl from our crawlers (or this local machine if we
configure it so). It then opens the file, parses it, and saves the article
data in that file into the MySQL database.

We do it this way instead of directly making a database connection because
I just wanted to use django's ORM :).
"""
import codecs
import json
import re
import time
import pytz

from datetime import datetime, timedelta
from warnings import filterwarnings
from urlparse import urlparse
import MySQLdb as Database
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from wintria.article.models import Article, Source
from wintria.lib.source_data import get_desc, get_soup

MAX_ARCHIVE_COUNT = 1000000
input_fn = '/home/lucas/labs/news_dump/articles.json'


def purge_old():
    now = datetime.now()
    two_days_ago = now - timedelta(days=2)
    epoch = datetime(2000, 4, 20, 18, 4, 34, 44710)
    western = pytz.timezone('US/Pacific')

    two_days_ago = western.localize(two_days_ago)
    epoch = western.localize(epoch)

    count = 0

    # outdated = article.objects.filter(timestamp__range=[epoch, two_days_ago])
    # for a in outdated: # Delete all articles over 3 days old
    # RE-ENABLE This later, when we have more articles
    #    a.delete()
    #    count += 1

    overflown = Article.objects.order_by('-timestamp')[MAX_ARCHIVE_COUNT:]
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
    help = 'Opens up .json article files and sends the data to our db'

    def handle(self, *args, **options):
        filterwarnings('ignore', category=Database.Warning)
        ts = time.time()
        self.stdout.write('unpacking files and saving to db... ' +
                          datetime.fromtimestamp(ts).strftime(
                              '%Y-%m-%d %H:%M:%S'))
        total = 0
        count = 0
        dups = 0

        articles_file = codecs.open(input_fn, 'r', 'utf8')
        articles_string = articles_file.read()
        articles_file.close()
        articles_json = json.loads(articles_string)

        for article_dict in articles_json:
            total += 1
            # If a source matches the article, sync em.
            # If not, make a new source and sync em.
            domain = urlparse(article_dict['url']).netloc
            try:
                s = Source.objects.get(domain=domain)
            except Source.DoesNotExist:
                s = None

            if not s:
                print 'creating new source from %s' % domain

                if len(domain.split('.')) >= 2:
                    try:
                        url = 'http://' + domain
                        soup = get_soup(url)
                        desc = get_desc(soup)
                        # save_logo(soup, domain)
                        s = Source(
                            domain=domain,
                            description=desc
                        ).save()
                        # push_s3(s)
                    except IntegrityError, e:
                        print "Integrity error on source", str(e)
                    except Exception, e:
                        print "Save source err", str(e)
                else:
                    print "%s domain isn't valid" % domain

            if s:
                try:
                    _article = Article(
                        url=article_dict['url'],
                        title=article_dict['title'],
                        txt=article_dict['text'],
                        keywords=article_dict['keywords'],
                        source=s,
                        thumb_url=article_dict['img'],
                        has_img=0
                    )

                    url_obj = urlparse(article_dict['url'])
                    domain, scheme = url_obj.netloc, url_obj.scheme

                    if domain.startswith(u'www.'):
                        domain = domain[4:]
                    if scheme == u'https':
                        scheme = u'http'
                    f_url = scheme + u'://' + domain + url_obj.path

                    # Make sure article's canon form is not already present
                    # (without www. or https://)
                    # If we get a non existing error, we are good to go!
                    try:
                        __ = Article.objects.get(url=f_url)
                    except Article.DoesNotExist:
                        pass
                    except Exception, e:
                        print 'article unqiue excep', str(e)
                        continue
                    else:
                        dups += 1
                        continue  # skip saving!

                    _article.save()
                    count += 1

                except IntegrityError, e:  # catches the URL - Unique setting.
                    if e.args[0] == 1062:
                        dups += 1
                except Exception, e:
                    print 'Save article err:', str(e)
                    pass
            else:
                print 'Source + Article failed to save'
                try:
                    print 'for', article_dict['url']
                except Exception, e:
                    print '%s failed to print url' % str(e)

        self.stdout.write(str(count) + ' files unpacked and saved and we had '
                          + str(dups) + ' duplicate articles and we have ' +
                          str(total) + ' total incoming articles ' +
                          datetime.fromtimestamp(ts).
                          strftime('%Y-%m-%d %H:%M:%S'))
        purge_old()
