from django.core.management.base import BaseCommand
from django.db.models import Count

# from wintria.lib.io import queryset_iterator
from wintria.article.models import Article


"""
This file exists because I fucked up the keyword deserialization in
the previous port of Wintria from webfaction to Digitalocean.

I saved the keywords var as a python json string instead of
a u'@@' delimited string as was supposed to.
"""


"""
def queryset_iterator(queryset, chunksize=1000):
    # Churn qs into a generator to save memory
    sz = 100000000000
    last_sz = queryset[0].num_articles
    while sz > last_sz:
        for row in queryset.filter(num_articles__lt=sz)[:chunksize]:
            sz = row.num_articles
            yield row
        gc.collect()
"""


import gc  # garbage collector
import json
import ast


def queryset_iterator(queryset, chunksize=1000):
    """
    Iterate over a Django Queryset ordered by the primary key
    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.
    Note that the implementation of the iterator does not support
    ordered query sets.
    """
    first_pk = queryset.order_by('pk')[0].pk
    pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('-pk')
    # pk = queryset[0].pk
    while pk > first_pk:
        for row in queryset.filter(pk__lt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()


class Command(BaseCommand):

    def handle(self, *args, **options):
        # prioritize sources witht the most articles
        # articles = Article.objects.order_by('-pk')
        gen = queryset_iterator(Article.objects)
        cnt = 0
        LIMIT = 10
        for a in gen:
            keys = a.keywords
            if keys and keys[0] == '[' and keys[-1] == ']':
                obj_keys = ast.literal_eval(keys)
                old_keys = obj_keys
                new_keys = u'@@'.join(obj_keys)
                a.keywords = new_keys
                a.save()
                print 'saved', old_keys, 'as', a.keywords, \
                    'on timestamp:', a.timestamp
            else:
                print 'skipping article because keys already fixed:', keys
            cnt += 1
            if cnt == LIMIT:
                break
        print 'end'
