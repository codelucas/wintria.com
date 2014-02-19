"""
"""
import json
from django.http import HttpResponse, Http404
from django.db.utils import IntegrityError

from wintria.lib.io import (query_to_articles, articles_to_sources,
                            articles_to_related_keys)
from wintria.article.models import Article
from wintria.article.templatetags.article_extras import jsonify
from wintria.wintria.views import (QUERY_COOKIE, render_with_context,
                                   QUERY_PARAM)
# from wintria.lib.summarize import SUMMARIZER

# Searches for crawlers by a tag input query, updates articles and crawlers.
SOURCE_DELIM = "&del"

def query_main(request):
    """
    Async calls to the server from the template via this method
    returns appropriate articles with an query input
    """
    if request.method == 'POST':
        if (QUERY_PARAM in request.POST) and request.POST[QUERY_PARAM].strip():
            query = request.POST[QUERY_PARAM].strip()
            articles = query_to_articles(query)
            sources = articles_to_sources(articles)

            related_keys = articles_to_related_keys(articles)

            source_obj = []
            for s in sources:
                source_obj.append({"id":SOURCE_DELIM.join([s.domain,
                                                           s.description,
                                                           s.get_small_thumb_url()])})
            source_obj = source_obj[:20]
            source_json = json.dumps(source_obj)
            updated_news = jsonify(articles)

            ret_json = json.dumps({"updated_news":updated_news,
                "source_json": source_json, 'related_keys':related_keys})

            response = HttpResponse(ret_json, mimetype="application/json")
            response.set_cookie(QUERY_COOKIE, query)
            return response

        return HttpResponse()

    else:
        raise Http404('What are you doing here?')

def single(request, id=None):
    """
    Retrieves and displays a single article, potential summary
    generation. We currently have a crude keyword generator
    """
    if id:
        try:
            article = Article.objects.filter(id=id)[0]
            article.click()
            #reg = r"\b)|(\b".join(article.get_keywords_list()[:95])
            #reg = r"(\b" + reg + r"\b)"
            #regex = re.compile(reg, re.I)
            # COLOR = ['red', 'blue', 'orange', 'violet', 'green']
            #COLOR = ['rgb(255, 113, 113)', 'rgb(128, 128, 255)',
            #         'rgb(255, 202, 105)', 'rgb(238, 139, 238)', 'rgb(125, 207, 125)']
            #TWITTER_URL = "https://twitter.com/search?q=%23"

            #summary = SUMMARIZER.keyword_summarize(
            #    article.get_keywords_list(), article.txt, 4)

            #i = 0
            #output = ""
            #m = None
            #for mtch in regex.finditer(summary):
            #    output += "".join([
            #        (summary[i:mtch.start()]),
            #        ("<a class='twitter_popup' href='"+TWITTER_URL+summary[mtch.start():mtch.end()]+"'>"),
            #        ("<span style='text-decoration:underline;'>"), #% COLOR[(mtch.lastindex-1) % len(COLOR)],
            #        ('#'+summary[mtch.start():mtch.end()]),
            #        ("</span></a>")
            #    ])
            #    i = mtch.end()
            #    m = mtch

            #if m: summary = "".join([output, summary[m.end():]])
            return render_with_context(request, 'single.html', kwargs={'article':article}) #, 'summary':summary})

        except IntegrityError:
            raise Http404

    raise Http404

# auto_map = AutoComplete.get_mapper()
"""
@csrf_exempt
def autocomplete(request, q=''):
    resp = []

    if auto_map.get(q):
        results = auto_map[q][:15]
        for r in results:
            dd = {}
            dd['value'] = r
            dd['tokens'] = dd['value'].split(' ')
            resp.append(dd)

    resp = json.dumps(resp)
    return HttpResponse(resp, mimetype="application/json")

# Swaps a crawler (adds one or removes one). Updates the news. Crawler updating is done via frontend.
@csrf_exempt
def swapSource(request):
    if request.method == 'POST':
        s_dict = change_and_get_sources(request.COOKIES.get(COOKIE_KEYS["Sources"], None),
            impacted=request.POST['domain'], action=request.POST["intent"])
        sources = s_dict["sources"]
        source_string = s_dict["source_str"]
        articles = sources_to_articles(sources)
        for a in articles: a.domain = "hii"
        # impacted_source = Source.objects.get(domain=request.POST['domain'])

        updated_news = jsonify(articles)
        # Nested json, take our already jsonified model list
        # and use it as a value in an outer json object.
        ret_json = json.dumps({"updated_news" : updated_news})

        response = HttpResponse(ret_json, mimetype = "application/json")
        response.set_cookie(COOKIE_KEYS["Sources"], source_string)
        return response
    else:
        raise Http404('What are you doing here?')

# The whole purpose of this GET port is to aid
# the NewsEngine uniquifier. For some reason, a lot
# of duplicate articles never get caught until we save into mysql...

from datetime import timedelta, datetime
import pytz
PASSWD = "thewintriastartup"
@csrf_exempt
def article_exists(request):
    if request.method == 'POST':# and 'password' in request.POST:
        if 'password' not in request.POST or request.POST['password'] != PASSWD:
            raise Http404

        now = datetime.now()
        ago = now - timedelta(days=2)         # 2 days will be our safe range
        western = pytz.timezone('US/Pacific') # Get timezone, localize both
        ago = western.localize(ago)
        now = western.localize(now)
        #articles = article.objects.filter(timestamp__range=[ago, now]).values_list('url', flat=True)
        articles = article.objects.values_list('url', flat=True)
        DEL=u'$$'
        articles=DEL.join(articles)
        jsoned = json.dumps({'articles':articles})
        return HttpResponse(jsoned, mimetype="application/json")
    raise Http404

import re
COLOR = ['red', 'blue', 'orange', 'violet', 'green']
#text = Graham says that Perl is cooler than Java and Python than Perl. In some circles, maybe. Graham uses the example of Slashdot, written in Perl. But what about Advogato, written in C? What about all of the cool P2P stuff being written in all three of the languages? Considering that Perl is older than Java, and was at one time the Next Big Language, I think you would have a hard time getting statistical evidence that programmers consider Perl "cooler" than Java, except perhaps by virtue of the fact that Java has spent a few years as the "industry standard" (and is thus uncool for the same reason that the Spice Girls are uncool) and Perl is still "underground" (and thus cool, for the same reason that ambient is cool). Python is even more "underground" than Perl (and thus cooler?). Maybe all Graham has demonstrated is that proximity to Lisp drives a language underground. Except that he's got the proximity to Lisp argument backwards too.
regex = re.compile(r"(\blisp\b)|(\bpython\b)|(\bperl\b)|(\bjava\b)|(\bc\b)", re.I)

i = 0; output = "&lt;html&gt;"
for m in regex.finditer(text):
    output += "".join([text[i:m.start()],
            "&lt;strong&gt;&lt;span style='color:%s'&gt;" % COLOR[m.lastindex-1],
            text[m.start():m.end()],
            "&lt;/span&gt;&lt;/strong&gt;"])
    i = m.end()
print "".join([output, text[m.end():], "&lt;/html&gt;"])

import re
COLOR = ['red', 'blue', 'orange', 'violet', 'green']
text = '''Graham says that Perl is cooler than Java and Python than Perl.
In some circles, maybe. Graham uses the example of Slashdot, written in Perl.
But what about Advogato, written in C? What about all of the cool P2P stuff being written
in all three of the languages? Considering that Perl is older than Java, and was
at one time the Next Big Language, I think you would have a hard time getting statistical
evidence that programmers consider Perl "cooler" than Java, except perhaps by virtue of the
fact that Java has spent a few years as the "industry standard" (and is thus uncool for
the same reason that the Spice Girls are uncool) and Perl is still "underground" (and
thus cool, for the same reason that ambient is cool). Python is even more "underground"
than Perl (and thus cooler?). Maybe all Graham has demonstrated is that proximity to
Lisp drives a language underground. Except that he's got the proximity to Lisp argument
backwards too.'''
regex = re.compile(r"(\blisp\b)|(\bpython\b)|(\bperl\b)|(\bjava\b)|(\bc\b)", re.I)
i = 0; output = "&lt;html&gt;"
for m in regex.finditer(text):
    output += "".join([text[i:m.start()],
                       "&lt;strong&gt;&lt;span style='color:%s'&gt;" % COLOR[m.lastindex-1],
                       text[m.start():m.end()],
                       "&lt;/span&gt;&lt;/strong&gt;"])
    i = m.end()
print "".join([output, text[m.end():], "&lt;/html&gt;"])

"""