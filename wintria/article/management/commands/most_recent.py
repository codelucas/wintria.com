"""
Get the 10 most recent article's titles and id's to
make sure our extractor is working.
"""
from django.core.management.base import BaseCommand, CommandError

from wintria.article.models import Article
from wintria.wintria.settings import PROJECT_ROOT

from warnings import filterwarnings
import MySQLdb as Database


class Command(BaseCommand):
    help = 'Get the 10 most recent article\'s titles and id\'s \
            to make sure our extractor is working.'

    def handle(self, *args, **options):
        filterwarnings('ignore', category = Database.Warning)
        articles = Article.objects.order_by('-timestamp')[:10]
        for a in articles:
            print 'id:', a.id, 'title:', a.title, 'date:', \
                a.timestamp, 'keywords:', a.keywords
