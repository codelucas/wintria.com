import feedparser

def goog_trends():
    useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:24.0) Gecko/20100101 Firefox/24.0'
    loc = 'http://www.google.com/trends/hottrends/atom/feed?pn=p1'

    try:
        listing = feedparser.parse(loc, agent=useragent)['entries']
    except Exception,e:
        print str(e), 'Error feedparsing'
        return []

    trends = []
    for item in listing:
        trends.append(item['title'])
    return trends
