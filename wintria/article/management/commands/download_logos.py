from django.core.management.base import BaseCommand
from django.db.models import Count

from wintria.lib.source_data import get_soup, save_logo
from wintria.article.models import Source

import gc


def queryset_iterator(queryset, chunksize=1000):
    """
    Churn qs into a generator to save memory
    """
    sz = 100000000000
    last_sz = queryset[0].num_articles
    while sz > last_sz:
        for row in queryset.filter(num_articles__lt=sz)[:chunksize]:
            sz = row.num_articles
            yield row
        gc.collect()


class Command(BaseCommand):

    def handle(self, *args, **options):
        # prioritize sources witht the most articles
        sources = Source.objects.annotate(num_articles=Count('article')).\
            order_by('-num_articles')
        sources_generator = queryset_iterator(sources)
        failed = 0
        cnt = 0
        LIMIT = 2000
        for s in sources_generator:
            try:
                url = 'http://' + s.domain
                soup = get_soup(url)
                save_logo(soup, s.domain)
            except Exception, e:
                print('%s fail to save img %s' % (str(e), s.domain))
                failed += 1
                continue
            cnt += 1
            if cnt == LIMIT:
                break
        print 'saved all source logos, with %d failures' % failed
