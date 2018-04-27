# coding:utf-8
from django.db import models
from django.contrib.auth.models import User



class OAuth_type(models.Model):
    """oauth type"""
    type_name = models.CharField(max_length=12)
    title = models.CharField(max_length=12)
    img = models.FileField(upload_to='static/img/connect')

    def __unicode__(self):
        return self.type_name

class OAuth_ex(models.Model):
    """User models ex"""
    user = models.ForeignKey(User)  # 和User关联的外键
    openid = models.CharField(max_length=64, default='')
    oauth_type = models.ForeignKey(OAuth_type, default=1)  # 关联账号的类型

    def __unicode__(self):
        return u'<%s>' % (self.user)
