# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render_to_response
from blog.models import BlogArticles
def blog_title(request):
    blogs=BlogArticles.objects.all()
    return render_to_response("blog/title.html",{"blogs":blogs,'user':request.user})
def blog_article(request,article_id):
    article=BlogArticles.objects.get(id=article_id)
    pub=article.publish
    return render_to_response("blog/content.html",{"article":article,"publish":pub,'user':request.user})
