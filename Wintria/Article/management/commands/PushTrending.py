__author__ = 'louyang'

from django.core.management.base import BaseCommand, CommandError
from Article.models import Article
from lib.io import convert_to_datum
from lib.google import goog_trends
import feedparser
from warnings import filterwarnings
import MySQLdb as Database
import codecs
import json


class Command(BaseCommand):
    help = 'Gathers trending topics from our own data + ' \
           'Google\'s data, pushes up to .json static files'

    def handle(self, *args, **options):
        filterwarnings('ignore', category = Database.Warning)

        dd = {}
        articles = Article.objects.order_by('-timestamp')[:300]
        for a in articles:
            keys = a.get_keywords_list()
            for k in keys:
                if k in dd:
                    dd[k] += 1
                else:
                    dd[k] = 1

        common_keys = sorted(dd.items(), key=lambda x:x[1], reverse=True)[:150]
        g_trends = goog_trends()

        # factor length in, many 'bad' short keys, like AP, U.S., etc.
        common_keys = sorted(common_keys, key=lambda x:len(x[0]), reverse=True)[:20]

        # uniquify the terms between our terms and googles, we dont want dupes
        g_lower = [ t.lower() for t in g_trends ]
        our_trends = [ tup[0] for tup in common_keys if tup[0].lower() not in g_lower ]

        trends = g_trends# + our_trends

        new_datum = convert_to_datum(trends, tag_all=False) # not in string form

        prefetch_file = 'prefetch.json'
        target_url = '/home/wintrialucas/webapps/windjango/Wintria/Wintria/autocomplete_static/autocomplete/'+prefetch_file

        try:
            f = codecs.open(target_url, 'r+', encoding='utf-8') # overwrite each time
        except IOError, e:
            f = open(target_url, 'w+') # file does not exist, so we make one
            f.close()
            f = codecs.open(target_url, 'r+', encoding='utf-8')


        raw_dat = f.read() # json, but in twitters 'datum' format
        f.close()

        try:
            old_datum = json.loads(raw_dat)
            new_vals =  [ dic_d['value'] for dic_d in new_datum ] # keep the old & new unique
            old_datum = [ dat for dat in old_datum if dat['value'] not in new_vals ]
        except Exception, e:
            print 'empty file or corrupt format', str(e)
            old_datum = []

        datum = new_datum + old_datum
        uniq_terms = {}
        uniq_datum = []
        for d in datum:
            if d['value'] not in uniq_terms:
                uniq_terms[d['value']] = True
                uniq_datum.append(d)

        uniq_datum = uniq_datum[:130] # keep some old results, because we don't have good proprietary grabber
        uniq_datum = json.dumps(uniq_datum)

        print 'pushing the following trends:', uniq_datum

        f = codecs.open(target_url, 'w+', encoding='utf-8')
        f.write(uniq_datum)
        f.close()

        print 'finished pushing trends'

