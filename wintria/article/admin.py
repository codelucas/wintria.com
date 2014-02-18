from django.contrib import admin
from models import Article, Source

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'thumb_url', 'timestamp', 'click_count',)
    list_filter = ('source',)
    ordering = ('-click_count', '-timestamp',)
    search_fields = ('title', 'url', 'timestamp',)

class SourceAdmin(admin.ModelAdmin):
    list_display = ('domain',)
    list_filter = ('domain',)
    ordering = ('domain',)
    search_fields = ('domain', 'description',)

admin.site.register(Article, ArticleAdmin)
admin.site.register(Source, SourceAdmin)