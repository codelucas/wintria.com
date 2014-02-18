"""
Generate lists of news urls for personal use or research
Input a number of the amount of urls wanted
"""
import gc 
import os
import codecs

from django.core.management.base import BaseCommand
from wintria.article.models import Article

PARENT_DIR = os.path.abspath(os.path.dirname(__file__))

def queryset_iterator(queryset, chunksize=1000):
    """
    Iterate  over a Django Queryset ordered by the primary key.
    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    """
    pk = 0
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()

class Command(BaseCommand):

    def handle(self, *args, **options):

        file_path = os.path.join(PARENT_DIR, 'urls.txt')
        if os.path.exists(file_path):
            os.remove(file_path)

        articles = queryset_iterator(Article.objects.all())
        CAP = 100000 #int(options['num'])
        interval = min(10000, (CAP / 10))

        current_str = u''
        index = 0
        for a in articles:
            if index >= CAP:
                print 'breaking %d articles' % CAP
                break
            try:
                if index % interval == 0:
                    fn = codecs.open(file_path, 'a', 'utf8')
                    fn.write(current_str)
                    fn.close()
                    current_str = u''
                else:
                    current_str += a.url + u'\r\n'
                index += 1
            except Exception, e:
                print '%s failed url %s' % (str(e), a.url)
                continue

        fn = codecs.open(file_path, 'a', 'utf8')
        fn.write(current_str)
        fn.close()
        print 'finished at %d articles' % index
