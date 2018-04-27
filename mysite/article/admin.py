# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from django.contrib import admin
from article.models import ArticleColumn
class ArticleColumnAdmin(admin.ModelAdmin):
    list_display = ('column','created','user')
    list_filter = ('column',)
admin.site.register(ArticleColumn,ArticleColumnAdmin)
