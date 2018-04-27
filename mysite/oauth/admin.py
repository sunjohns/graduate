# coding:utf-8
from django.contrib import admin
from oauth.models import OAuth_ex, OAuth_type


# Register your models here.
class OAuthTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_name', 'title', 'img')


class OAuthAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'openid', 'oauth_type')


admin.site.register(OAuth_ex, OAuthAdmin)
admin.site.register(OAuth_type, OAuthTypeAdmin)
