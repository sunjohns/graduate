# -*- coding: utf-8 -*-
import json
import urllib, urllib2, urlparse
import re


class OAuth_Base():
    def __init__(self, kw):
        """self.oauth_type_id = kw.get('oauth_type_id', 0)
        self.oauth_type = kw.get('oauth_type', '')

        self.client_id = kw.get('client_id', '')
        self.client_secret = kw.get('client_secret', '')
        self.redirect_uri = kw.get('redirect_uri', '')
        self.scope = kw.get('scope', '')
        self.state = kw.get('state', '')

        self.url_authorize = kw.get('url_authorize', '')
        self.url_access_token = kw.get('url_access_token', '')
        self.url_open_id = kw.get('url_open_id', '')
        self.url_user_info = kw.get('url_user_info', '')
        self.url_email = kw.get('url_email', '')"""

        if not isinstance(kw, dict):
            raise Exception("arg is not dict type")

        for key, value in kw.items():
            setattr(self, key, value)

    def _get(self, url, data):
        """get请求"""
        request_url = '%s?%s' % (url, urllib.urlencode(data))
        response = urllib2.urlopen(request_url)
        return response.read()

    def _post(self, url, data):
        """post请求"""
        request = urllib2.Request(url, data=urllib.urlencode(data))
        response = urllib2.urlopen(request)
        # response = urllib2.urlopen(url, urllib.urlencode(data))
        return response.read()

    # 根据情况重写以下方法
    def get_auth_url(self):
        """获取授权页面的网址"""
        params = {'client_id': self.client_id,
                  'response_type': 'code',
                  'redirect_uri': self.redirect_uri,
                  'scope': self.scope,
                  'state': self.state}
        return '%s?%s' % (self.url_authorize, urllib.urlencode(params))

    def get_access_token(self, code):
        """根据code获取access_token"""
        pass

    def get_open_id(self):
        """获取用户的标识ID"""
        pass

    def get_user_info(self):
        pass

    def get_email(self):
        pass


class OAuth_Github(OAuth_Base):
    openid = ''

    def get_access_token(self, code):
        params = {'grant_type': 'authorization_code',
                  'client_id': self.client_id,
                  'client_secret': self.client_secret,
                  'code': code,
                  'redirect_uri': self.redirect_uri}

        # Github此处是POST请求
        response = self._post(self.url_access_token, params)

        # 解析结果
        result = urlparse.parse_qs(response, True)
        self.access_token = result['access_token'][0]
        return self.access_token

    def get_open_id(self):
        """获取用户的标识ID"""
        if not self.openid:
            # 若没有openid，则调用一下获取用户信息的方法
            self.get_user_info()

        return self.openid

    def get_user_info(self):
        """获取用户资料信息"""
        params = {'access_token': self.access_token, }
        response = self._get(self.url_user_info, params)

        result = json.loads(response)
        self.openid = result.get('id', '')
        return result

    def get_email(self):
        """获取邮箱"""
        params = {'access_token': self.access_token, }
        response = self._get(self.url_email, params)

        result = json.loads(response)
        return result[0]['email']
