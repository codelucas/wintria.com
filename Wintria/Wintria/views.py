from django.shortcuts import render_to_response, RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from lib.google import goog_trends
from lib.io import query_to_articles, articles_to_sources, articles_to_related_keys
from Wintria.settings import get_root_url
from django.core.cache import cache
import random

VISITED_COOKIE = 'visited4'
QUERY_COOKIE = 'c_query'
QUERY_PARAM = 'query'

def render_with_context(request, template, cookies=[], kwargs={}):
    '''main 'inherited' view that every non-ajax view calls when returning
    a response. This view abstracts cookies, setting critical template vars
    like the root url, etc, render to response, etc. Cookies are passed in the
    form of a list of tuples.'''

    kwargs['root_url'] = get_root_url()

    response = render_to_response(template, kwargs,
        context_instance=RequestContext(request))

    for tup in cookies:
        response.set_cookie(tup[0], tup[1])

    return response

def home(request):
    '''template returning search bar screen, users see this screen first'''

    if cache.get('g_trends', default=False):
        g_trends = cache.get('g_trends')
    else:
        g_trends = goog_trends()
        # one day timeout
        if g_trends:
            cache.set('g_trends', g_trends, timeout=86400)

    if len(g_trends) > 5: # random trends
        g_trends = random.sample(g_trends, 5)

    return render_with_context(request, 'home.html', cookies=[ (VISITED_COOKIE, True) ],
                               kwargs={'cur_articles' : None, 'cur_sources' : None,
                                       'trending':g_trends})

def search(request):
    '''screen displaying the crawled articles and sources'''
    if not request.COOKIES.get(VISITED_COOKIE, False):
        return home(request)

    if (QUERY_PARAM in request.GET) and request.GET[QUERY_PARAM].strip():
        query = request.GET[QUERY_PARAM].strip()
    else:
        query = request.COOKIES.get(QUERY_COOKIE, False)
        if not query:
            query = "news"

    # cookies = [ (QUERY_COOKIE, query) ]

    articles = query_to_articles(query)
    related_keys = articles_to_related_keys(articles)
    sources = articles_to_sources(articles)[:20]

    return render_with_context(request, 'search.html', cookies=[ (QUERY_COOKIE, query) ],
                               kwargs={'cur_articles' : articles, 'cur_sources' : sources,
                                       'related_keys':related_keys})

def story(request):
    return render_with_context(request, 'story.html', kwargs={})

def about(request):
    return render_with_context(request, 'about.html', kwargs={})

def wintria_2(request):
    return render_with_context(request, 'wintria_2.html', kwargs={})

def thanks(request):
    return render_with_context(request, 'support.html', kwargs={})


'''
def daily(request):

        'top articles':
        top=Source.objects.annotate(article_count=Count('article')).order_by('-article_count').filter(article_count__gte=10)[:10]

    top_sources=Source.objects.annotate(article_count=Count('article')).\
        order_by('-article_count').filter(article_count__gte=10)[:10]
    full_tags = ""
    if ('tags' in request.GET) and request.GET['tags'].strip():
        tags = request.GET['tags'].split(',')
        tags = [ tag.strip() for tag in tags ]
        articles = tags_to_articles(tags)
        sources = articles_to_sources(articles)

    try: found_count = articles.count()
    except TypeError: found_count = 0

    if sort == "newest":
        articles.sort(key=lambda x: x.timestamp, reversed=True)
    else:
        articles.sort(key=lambda x: x.click_count, reversed=True)

    paginator = Paginator(articles, 7)
    pageNumber = request.GET.get('page')
    try: paginatedPage = paginator.page(pageNumber)
    except PageNotAnInteger: pageNumber = 1
    except EmptyPage: pageNumber = paginator.num_pages
    articles = paginator.page(pageNumber)

    unpaged_url = re.split("&page", request.get_full_path())[0]

    return render_with_context(request, 'archives.html', {'articles' : articles,
        'sort' : sort, "full_tags" : full_tags, "unpaged_url" : unpaged_url,
        "found_count" : found_count})

def about(request):
    return render_with_context(request, 'story.html')


'''


"""
def streams(request, sort="hotness"):
    order = "-timestamp"
    if sort == "hotness": order = "-hotness"

    sources = Source.objects.order_by(order)

    owned_sources = []
    if request.COOKIES.get(SOURCES_COOKIE, None):
        owned_sources = re.split(' ', request.COOKIES.get(SOURCES_COOKIE, None))
    num_owned_sources = len(owned_sources)

    for source in sources:
        source.set_hotness()
        if owned_sources and (source.domain in owned_sources):
            source.owned = True
        else:
            source.owned = False

    paginator = Paginator(sources, 7)
    pageNumber = request.GET.get('page')
    try: paginatedPage = paginator.page(pageNumber)
    except PageNotAnInteger: pageNumber = 1
    except EmptyPage: pageNumber = paginator.num_pages
    sources = paginator.page(pageNumber)

    return render_with_context(request, 'streams.html', {'sources' : sources,
        'sort' : sort, 'num_owned_sources': num_owned_sources})
"""


"""
def search(request):
    articles = []
    if ('query' in request.GET) and request.GET['query'].strip():
        articles = query_to_articles(request.GET['query'])
    try:
        found_count = articles.count()
    except TypeError:
        found_count = 0

    paginator = Paginator(articles, 7)
    pageNumber = request.GET.get('page')
    try: paginatedPage = paginator.page(pageNumber)
    except PageNotAnInteger: pageNumber = 1
    except EmptyPage: pageNumber = paginator.num_pages
    articles = paginator.page(pageNumber)

    return render_with_context(request, 'archives.html', {"articles" : articles,
        "numresults" : found_count})
"""
