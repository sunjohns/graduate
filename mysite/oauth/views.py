# coding:utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.core.urlresolvers import reverse  # url逆向解析

from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from django.conf import settings

# OAuth应用相关模块
from oauth.oauth_client import OAuth_Github
from oauth.models import OAuth_ex, OAuth_type
#from oauth.forms import BindEmail


#from user_ex.views import get_active_code, send_active_email
import time
import uuid


def github_login(request):
    """登录前的认证"""
    oauth_github = OAuth_Github(settings.OAUTH_GITHUB_CONFIG)

    # 获取 得到Authorization Code的地址
    url = oauth_github.get_auth_url()

    return HttpResponseRedirect(url)


def github_check(request):
    """登录之后，会跳转到这里"""
    request_code = request.GET['code']
    oauth_github = OAuth_Github(settings.OAUTH_GITHUB_CONFIG)


    # 获取access_token
    try:
        access_token = oauth_github.get_access_token(request_code)
    except Exception as e:
        data = {}
        data['message'] = u'登录出错，请稍后重试<br>(辅助信息%s)”' % str(e)
        data['goto_url'] = '/'
        data['goto_time'] = 3000
        data['goto_page'] = True
        return render_to_response('message.html', data)

    # 获取用户信息
    infos = oauth_github.get_user_info()
    open_id = str(infos.get('id', ''))
    nickname = infos.get('login', '')

    # 检查id是否存在
    githubs = OAuth_ex.objects.filter(openid=open_id, oauth_type=oauth_github.oauth_type_id)

    # 获取邮箱
    if githubs:
        # 存在则获取对应的用户，并登录
        _login_user(request, githubs[0].user)
        return HttpResponseRedirect('/')
    else:
        # 不存在，则尝试获取邮箱
        try:
            # 获取得到邮箱则直接绑定
            email = oauth_github.get_email()
        except Exception as e:
            # 获取不到即跳转到绑定用户
            url = '%s?open_id=%s&nickname=%s&oauth_type=%s' % (
                reverse('bind_email'),
                open_id,
                nickname,
                oauth_github.oauth_type)
            return HttpResponseRedirect(url)

        # 获取到邮箱，直接绑定
        # 判断是否存在对应的用户(我这里的用户名就是邮箱，根据你的实际情况参考)
        users = User.objects.filter(username=email)

        if users:
            # 存在则绑定和登录
            user = users[0]
        else:
            # 不存在则直接注册并登录
            user = User(username=email, email=email)
            pwd = str(uuid.uuid1())  # 生成随机密码
            user.set_password(pwd)
            user.is_active = True  # 真实邮箱来源，则认为是有效用户
            user.save()

        # 添加绑定记录
        oauth_type = OAuth_type.objects.get(id=oauth_github.oauth_type_id)
        oauth_ex = OAuth_ex(user=user, openid=open_id, oauth_type=oauth_type)
        oauth_ex.save()

        # 更新昵称
        if not user.first_name:
            user.first_name = nickname
            user.save()

        _login_user(request, user)

        data = {}
        data['goto_url'] = '/'
        data['goto_time'] = 3000
        data['goto_page'] = True
        data['message'] = u'登录并绑定成功'
        return render_to_response('message.html', data)


def _login_user(request, user):
    """直接登录用户"""
    # 设置backend，绕开authenticate验证
    setattr(user, 'backend', 'django.contrib.auth.backends.ModelBackend')
    login(request, user)