import re

from wintria.article.models import Article

MAX_ARTICLE_QUERY = 150
ARTICLES_PER_CYCLE = 200

def num_words(txt):
    return len(txt.split(' '))

def articles_to_related_keys(articles):
    dd={}
    for a in articles:
        keys = a.get_keywords_list()
        for k in keys:
            if k in dd:
                dd[k] += 1
            else:
                dd[k] = 1

    common_keys = sorted(dd.items(), key=lambda x:x[1], reverse=True)[:12]
    return [ tup[0] for tup in common_keys ]

def strip_articles(articles):
    """
    Strips articles of useless fields for home. We safe-unique based
    on titles over 3 words long, since many checks are failing for now.
    """
    uniq_title={}
    ret = []
    for article in articles:
        if (num_words(article.title)<4) or (article.title not in uniq_title):
            if article.title not in uniq_title:
                uniq_title[article.title] = True

            article.txt = None
            article.timestamp = None
            article.click_count = None
            article.keywords = u'@@'.join(article.get_keywords_list(limit=20))
            ret.append(article)
    return ret

def prepare_memekey(text):
    """
    Memcached does not allow control chars or white spaces
    """
    if text:
        # unicode invalid characters
        RE_XML_ILLEGAL = u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
                         u'|' + \
                         u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
                          (unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                           unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                           unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                           )
        text = re.sub(RE_XML_ILLEGAL, "", text)
        # ascii control characters
        text = re.sub(r"[\x01-\x1F\x7F]", "", text)
        text = "_".join(text.split()) # remove all whitepsace
    return text

from django.core.serializers import serialize
import json

query_key = lambda x: prepare_memekey('main_q_%s' % x)[:250]

def query_to_articles(q):
    retrieved = Article.search.query(q).order_by('-@weight', '-@id')
    retrieved._limit = MAX_ARTICLE_QUERY

    ret_articles = strip_articles(retrieved)
    return ret_articles

def articles_to_sources(articles):
    """
    The blow code generates a 2 level nested tuple structure
    oops, cant use tuples, we are mutating vals
    """
    source_hash = {}
    for a in articles:

        if a.source.domain not in source_hash:
            source_hash[a.source.domain] = [a.source, 1]
        else:
            source_hash[a.source.domain][1] += 1

    source_hash = sorted(source_hash.items(),
                         key=lambda x: x[1][1], reverse=True)

    # if tup[1] > 3] # only keep sources, in sorted order
    return [ tup[0] for _domain, tup in source_hash ]


import gc # garbage collector

def queryset_iterator(queryset, chunksize=1000):
    """
    Iterate over a Django Queryset ordered by the primary key
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


def convert_to_datum(autocom_results, tag_all):
    """
    here is an example of a twitter datum
    [
      {
        "value": "West Side Story",
        "tokens": [
          "West",
          "Side",
          "Story"
        ]
      },
      {
        "value": "Lawrence of Arabia",
        "tokens": [
          "Lawrence",
          "of",
          "Arabia"
        ]
      }
    ]
    """
    base = []
    for r in autocom_results:
        try:
            dd = {}
            dd['value'] = r
            if tag_all:
                dd['tokens'] = dd['value'].split(' ') 
            else:
                dd['tokens'] = [ dd['value'] ] 
            base.append(dd)
        except Exception,e:
            pass

    return base # not in string form