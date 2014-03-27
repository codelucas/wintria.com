from django.conf.urls import patterns, include, url
from django.contrib import admin
# admin.autodiscover()

handler404 = 'wintria.lib.error_views.custom_404'
handler500 = 'wintria.lib.error_views.custom_500'

urlpatterns = patterns('',
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^obfuscateddfsdafsajsdlf23940523131f'
        r'dfddsdsadfafewewefrfgs2934hfdhksbhvfs/', include(admin.site.urls)),
)

urlpatterns += patterns('wintria.article.views',
    url(r'^api/query_main/$', 'query_main'),
    url(r'^(?P<id>(\d+))/(.+)/$', 'single'),
    url(r'^(?P<id>(\d+))/$', 'single'),
)

urlpatterns += patterns('wintria.wintria.views',
    url(r'^$', 'home'),
    url(r'^search/$', 'search'),
    url(r'^story/$', 'story'),
    url(r'^about/$', 'about'),
    url(r'^2\.0/$', 'wintria_2'),
    url(r'^thanks/$', 'thanks'),

    # url(r'^streams/$', 'streams'),
    # url(r'^streams/(?P<sort>\w+)/$', 'streams'),
    # url(r'^daily/$', 'daily'),
    # url(r'^daily/(?P<sort>\w+)/$', 'daily'),
)

urlpatterns += patterns('wintria.wintriauser.views',
    url(r'^feedback/$', 'send_feedback'),
    url(r'^thanks_for_all_the_fish/$', 'thanks_for_all_the_fish')
)
