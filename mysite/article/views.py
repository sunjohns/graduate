# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,render_to_response
from django.contrib.auth.decorators import login_required
from article.models import ArticleColumn
from article.forms import  ArticleColumnForm
from django.http import  HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from article.forms import ArticlePostForm,ArticlePost
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from article.models import ArticleTag
from article.forms import ArticleTagForm
import json
from django.contrib.auth.models import User


# articles=ArticlePost.objects.all()
# pages = Paginator(articles, 10)
#
#
# print pages.count
# print pages.num_pages
# print pages.page_range
#
#
# articles_page = pages.page(1)
# print articles_page.number
# print articles_page.has_previous()
# print articles_page.has_next()


# Create your views here.
@login_required(login_url='/management/login/')
@csrf_exempt
def article_column(request):
    if request.method == "GET":
        columns = ArticleColumn.objects.filter(user=request.user)
        column_form = ArticleColumnForm()
        return render(request, "article/column/article_column.html", {"columns":columns, 'column_form':column_form})

    if request.method == "POST":
        column_name = request.POST['column']
        columns = ArticleColumn.objects.filter(user_id=request.user.id, column=column_name)
        if columns:
            return HttpResponse('2')
        else:
            ArticleColumn.objects.create(user=request.user, column=column_name)
            return HttpResponse("1")
@login_required(login_url='/management/login')
@require_POST
@csrf_exempt
def rename_article_column(request):
    column_name = request.POST["column_name"]
    column_id = request.POST['column_id']
    try:
        line = ArticleColumn.objects.get(id=column_id)
        line.column = column_name
        line.save()
        return HttpResponse("1")
    except:
        return HttpResponse("0")
@login_required(login_url='/management/login')
@require_POST
@csrf_exempt
def del_article_column(request):
    column_id = request.POST["column_id"]
    try:
        line = ArticleColumn.objects.get(id=column_id)
        line.delete()
        return HttpResponse("1")
    except:
        return HttpResponse("2")


@login_required(login_url='/management/login')
@csrf_exempt
def article_post(request):
    if request.method == "POST":
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            cd = article_post_form.cleaned_data
            try:
                new_article = article_post_form.save(commit=False)
                new_article.author = request.user
                new_article.column = request.user.article_column.get(id=request.POST['column_id'])
                new_article.save()
                tags = request.POST['tags']
                if tags:
                    for atag in json.loads(tags):
                        tag = request.user.tag.get(tag=atag)
                        new_article.article_tag.add(tag)

                return HttpResponse("1")
            except:
                return HttpResponse("2")
        else:
            return HttpResponse("3")
    else:
        article_post_form = ArticlePostForm()
        article_columns = request.user.article_column.all()
        article_tags = request.user.tag.all()
        return render(request, "article/column/article_post.html",
                      {"article_post_form": article_post_form, "article_columns": article_columns,
                       "article_tags": article_tags, "user": request.user})


@login_required(login_url='/management/login')
def article_list(request,username=None):
    # data={}
    # if username:
    #     user = User.objects.get(username=username)
    #     articles_title = ArticlePost.objects.filter(author=user)
    #     try:
    #         userinfo = user.userinfo
    #         data["userinfo"]=userinfo
    #         data["user"]=user
    #     except:
    #         userinfo = None
    # else:
    #     articles_title = ArticlePost.objects.all()
    #
    # #articles_title = ArticlePost.objects.all()
    # # paginator = Paginator(articles_title, 5)
    # # page = request.GET.get('page')
    # # try:
    # #     current_page = paginator.page(page)
    # #     articles = current_page.object_list
    # # except PageNotAnInteger:
    # #     current_page = paginator.page(1)
    # #     articles = current_page.object_list
    # # except EmptyPage:
    # #     current_page = paginator.page(paginator.num_pages)
    # #     articles = current_page.object_list
    # current_page = request.GET.get("page", 1)
    #
    # # articles = ArticlePost.objects.all()
    # pages = Paginator(articles_title, 7)
    # articles = pages.page(current_page)
    #
    # data["articles"] = articles
    # data["pages"] = pages
    #
    #
    #
    # return render(request, "article/column/article_list.html", data)






    """show blogs' list"""

    # 获取GET请求的参数，得到当前页码。若没有该参数，默认为1
    current_page = request.GET.get("page", 1)

    articles = ArticlePost.objects.all()
    pages = Paginator(articles, 7)  # 7个对象为1页，这个参数可以写在settings.py里面
    articles = pages.page(current_page)  # 获得当前页的数据




    return render_to_response('article/column/article_list.html',{"user":request.user,"articles":articles,"pages":pages})


@login_required(login_url='/management/login')
def article_detail(request, id, slug):
    article = get_object_or_404(ArticlePost, id=id, slug=slug)
    return render_to_response("article/column/article_detail.html", {"article":article,"user":request.user})


@login_required(login_url='/management/login')
@require_POST
@csrf_exempt
def del_article(request):
    article_id = request.POST['article_id']
    try:
        article = ArticlePost.objects.get(id=article_id)
        article.delete()
        return HttpResponse("1")
    except:
    	return HttpResponse("2")



@login_required(login_url='/management/login')
@csrf_exempt
def edit_article(request,article_id):
    if request.method == "GET":
        article_columns = request.user.article_column.all()
        article = ArticlePost.objects.get(id=article_id)
        this_article_form = ArticlePostForm(initial={"title":article.title})
        this_article_column = article.column
        return render(request, "article/column/edit_article.html", {"article":article, "article_columns":article_columns, "this_article_column":this_article_column, "this_article_form":this_article_form})
    else:
        redit_article = ArticlePost.objects.get(id=article_id)
        try:
            redit_article.column = request.user.article_column.get(id=request.POST['column_id'])
            redit_article.title = request.POST['title']
            redit_article.body = request.POST['body']
            redit_article.save()
            return HttpResponse("1")
        except:
            return HttpResponse("2")


@login_required(login_url='/management/login')
@csrf_exempt
def article_tag(request):
    if request.method == "GET":
        article_tags = ArticleTag.objects.filter(author=request.user)
        article_tag_form = ArticleTagForm()
        return render_to_response("article/tag/tag_list.html", {"article_tags":article_tags, "article_tag_form":article_tag_form, "user":request.user})

    if request.method == "POST":
        tag_post_form = ArticleTagForm(data=request.POST)
        if tag_post_form.is_valid():
            try:
                new_tag = tag_post_form.save(commit=False)
                new_tag.author = request.user
                new_tag.save()
                return HttpResponse("1")
            except:
                return HttpResponse("the data cannot be save.")
        else:
            return HttpResponse("sorry, the form is not valid.")


@login_required(login_url='/management/login')
@require_POST
@csrf_exempt
def del_article_tag(request):
    tag_id = request.POST['tag_id']
    try:
        tag = ArticleTag.objects.get(id=tag_id)
        tag.delete()
        return HttpResponse("1")
    except:
    	return HttpResponse("2")


