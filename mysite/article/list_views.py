from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http.response import HttpResponse
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from article.models import ArticlePost, ArticleColumn
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import redis
from django.conf import  settings
from article.models import Comment
from article.forms import CommentForm
from django.db.models import Count



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


r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

def article_titles(request, username=None):
    data={}
    if username:
        user = User.objects.get(username=username)
        articles_title = ArticlePost.objects.filter(author=user)
        try:
            userinfo = user.userinfo
            data["userinfo"]=userinfo
            data["user"]=user
        except:
            userinfo = None
    else:
        articles_title = ArticlePost.objects.all()

    #articles_title = ArticlePost.objects.all()
    # paginator = Paginator(articles_title, 5)
    # page = request.GET.get('page')
    # try:
    #     current_page = paginator.page(page)
    #     articles = current_page.object_list
    # except PageNotAnInteger:
    #     current_page = paginator.page(1)
    #     articles = current_page.object_list
    # except EmptyPage:
    #     current_page = paginator.page(paginator.num_pages)
    #     articles = current_page.object_list
    current_page = request.GET.get("page", 1)

    # articles = ArticlePost.objects.all()
    pages = Paginator(articles_title, 7)
    articles = pages.page(current_page)

    data["articles"] = articles
    data["pages"] = pages

    if username:
        return render(request, "article/list/author_articles.html",data)

    return render(request, "article/list/article_titles.html", data)


@login_required(login_url='/management/login/')
def article_detail(request, id, slug):
    article = get_object_or_404(ArticlePost, id=id, slug=slug)
    total_views = r.incr("article:{}:views".format(article.id))
    r.zincrby('article_ranking', article.id, 1)

    article_ranking = r.zrange('article_ranking', 0, -1, desc=True)[:10]
    article_ranking_ids = [int(id) for id in article_ranking]
    most_viewed = list(ArticlePost.objects.filter(id__in=article_ranking_ids))
    most_viewed.sort(key=lambda x: article_ranking_ids.index(x.id))

    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.article = article
            new_comment.save()
    else:
        comment_form = CommentForm()

    article_tags_ids = article.article_tag.values_list("id", flat=True)
    similar_articles = ArticlePost.objects.filter(article_tag__in=article_tags_ids).exclude(id=article.id)
    similar_articles = similar_articles.annotate(same_tags=Count("article_tag")).order_by('-same_tags', '-created')[:4]

    return render(request,"article/list/article_detail.html",
                  context = {"article": article, "total_views": total_views, "most_viewed": most_viewed,
                   "comment_form": comment_form, "similar_articles": similar_articles, "user": request.user})

@csrf_exempt
@require_POST
@login_required(login_url='/management/login/')
def like_article(request):
    article_id = request.POST.get("id")
    action = request.POST.get("action")
    if article_id and action:
        try:
            article = ArticlePost.objects.get(id=article_id)
            if action == "like":
                article.users_like.add(request.user)
                return HttpResponse("1")
            else:
                article.users_like.remove(request.user)
                return HttpResponse("2")
        except:
            return HttpResponse("no")


@csrf_exempt
@require_POST
@login_required(login_url='/management/login/')
def like_article(request):
    article_id = request.POST.get("id")
    action = request.POST.get("action")
    if article_id and action:
        try:
            article = ArticlePost.objects.get(id=article_id)
            if action=="like":
                article.users_like.add(request.user)
                return HttpResponse("1")
            else:
                article.users_like.remove(request.user)
                return HttpResponse("2")
        except:
            return HttpResponse("no")



def search(request):
        wd = request.GET.get("wd")
        if not wd:
            return HttpResponse("<h1>404</h1>search not exist")
        else:
            articles = ArticlePost.objects.filter(title__icontains=wd)
            if articles:
                # return data
                current_page = request.GET.get("page", 1)
                pages = Paginator(articles, 7)
                articles = pages.page(current_page)
                return render_to_response('article/column/article_search.html', {"articles":articles,"wd":wd,"pages":pages,"user":request.user})
            else:
                return HttpResponse("<h1>404</h1>search not exist")





