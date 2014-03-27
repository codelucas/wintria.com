from django.shortcuts import render_to_response, RequestContext
from django.core.cache import cache

import random

from wintria.lib.google import goog_trends
from wintria.lib.io import (query_to_articles, articles_to_sources,
                            articles_to_related_keys)
from wintria.wintria.settings import get_root_url

VISITED_COOKIE = 'visited4'
QUERY_COOKIE = 'c_query'
QUERY_PARAM = 'query'



def render_with_context(request, template, cookies=[], kwargs={}):
    """
    Main 'inherited' view that every non-ajax view calls when returning
    a response. This view abstracts cookies, setting critical template vars
    like the root url, etc, render to response, etc. Cookies are passed in the
    form of a list of tuples.
    """
    kwargs['root_url'] = get_root_url()
    response = render_to_response(template, kwargs,
        context_instance=RequestContext(request))
    for tup in cookies:
        response.set_cookie(tup[0], tup[1])
    return response

def home(request):
    """
    Template returning search bar screen, users see this screen first
    """
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
    """
    screen displaying the crawled articles and sources
    """
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
