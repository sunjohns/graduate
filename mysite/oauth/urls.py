from django.conf.urls import include, url
from oauth import views as oauth_views

urlpatterns = [
    url(r'^github_login/$', oauth_views.github_login, name='github_login'),
    url(r'^github_check/$', oauth_views.github_check, name='github_check'),
]