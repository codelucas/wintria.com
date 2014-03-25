"""
"""
from django.db import models
from django.utils import timezone
from djangosphinx import SphinxSearch

import math
import hashlib
import base64

from wintria.wintria.settings import get_root_url
from wintria.lib.img_utils import is_bad_url
from wintria.lib.custom_time import time_diff_raw

NO_DESC = 'No Description Provided'

class Source(models.Model):
    domain = models.CharField("Domain", max_length=150, primary_key=True)
    description = models.CharField("Description", max_length=1000, default=NO_DESC)
    # hotness = models.FloatField("Hotness", default=0, editable=False)

    def thumbnail_key(self):
        return base64.urlsafe_b64encode(hashlib.md5(self.domain).digest())

    def get_small_thumb_url(self, secure=False):
        if secure:
            return ('https://wintria-source-images.s3-us-west-2.amazonaws.com/%s'
                    % self.thumbnail_key())
        return ('http://wintria-source-images.s3-us-west-2.amazonaws.com/%s'
                % self.thumbnail_key())

    def get_thumb_url(self):
        return get_root_url()+'/static/logo_thumbs/'+self.domain+'.png'

    def get_logo_url(self):
        return get_root_url()+'/static/logobank/'+self.domain+'.png'

    def save(self, *args, **kwargs):
        if self.description is None:
            self.description = NO_DESC

        # newlines break the frontend js
        self.description = self.description.replace('\r\n', ' ').replace('\n', ' ')
        super(Source, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.domain

    class Meta:
        verbose_name_plural = "Sources"

class Article(models.Model):
    url = models.URLField("Origin URL", unique=True)
    title = models.CharField("Title", max_length=200)
    txt = models.CharField("Body Text", max_length=10000)
    keywords = models.CharField("Text Keywords", max_length=3000)
    timestamp = models.DateTimeField("Timestamp", default=timezone.now, editable=False)
    has_img = models.BooleanField(default=True)

    source = models.ForeignKey(Source, null=True, on_delete=models.SET_NULL)
    click_count = models.IntegerField("Clicked Count", default=1, editable=False)
    thumb_url = models.URLField("Thumbnail url") # Any non-url strings will become u'None'

    def __unicode__(self):
        return self.title[:100]

    def save(self, *args, **kwargs):
        img_404 = '/static/images/well_no_img.jpg'
        if is_bad_url(self.thumb_url):
            if is_bad_url(self.source.get_logo_url()):
                self.thumb_url = img_404
            else:
                self.thumb_url = self.source.get_logo_url()

        super(Article, self).save(*args, **kwargs)

    def thumbnail_key(self):
        return base64.urlsafe_b64encode(hashlib.md5(self.url).digest())

    def thumb_img(self, secure=False):
        if secure:
            return ('https://wintria-article-images.s3-us-west-2.amazonaws.com/%s'
                    % self.thumbnail_key())
        return ('http://wintria-article-images.s3-us-west-2.amazonaws.com/%s'
                % self.thumbnail_key())

    # Returns raw seconds of existence
    def getRawAge(self):
        return time_diff_raw(self.timestamp)

    def click(self):
        self.click_count = self.click_count + 1
        self.save()

    def get_hotness(self):
        clicks = self.click_count
        order = math.log10(max(abs(clicks), 1))
        sign = 1 if clicks > 0 else -1 if clicks < 0 else 0
        time = self.getRawAge() - 1134028003
        return round(order + sign * time / 45000, 7)

    def get_keywords_list(self, limit=25):
        return self.keywords.split(u'@@')[:limit]

    def get_template_keywords(self, limit=3):
        keys = [ ''.join(k.split()) for k in self.keywords.split(u'@@') ]
        return keys[:limit]

    search = SphinxSearch(
        weights = { # individual field weighting, this is optional
            'title': 100,
            'txt': 90,
            'keywords': 100,
        }
    )
