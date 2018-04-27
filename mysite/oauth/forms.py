from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from oauth.models import OAuth_ex


class BindEmail(forms.Form):
    """bind the openid to email"""
    qq_openid = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'qq_openid'}))
    qq_nickname = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'qq_nickname'}))
    email = forms.EmailField(label=u'注册邮箱',
                             widget=forms.EmailInput(
                                 attrs={'class': 'form-control', 'id': 'email', 'placeholder': u'请输入您注册用的邮箱'}))
    pwd = forms.CharField(label=u'用户密码', max_length=36,
                          widget=forms.PasswordInput(
                              attrs={'class': 'form-control', 'id': 'pwd', 'placeholder': u'若尚未注册过，该密码则作为用户密码'}))

    # 验证邮箱
    def clean_email(self):
        qq_openid = self.cleaned_data.get('qq_openid')
        email = self.cleaned_data.get('email')
        users = User.objects.filter(email=email)

        if users:
            # 判断是否被绑定了
            if OAuth_ex.objects.filter(user=users[0]):
                raise ValidationError(u'该邮箱已经被绑定了')
        return email

    # 验证密码
    def clean_pwd(self):
        email = self.cleaned_data.get('email')
        pwd = self.cleaned_data.get('pwd')

        users = User.objects.filter(email=email)
        if users:
            # 若用户存在，判断密码是否正确
            user = authenticate(username=email, password=pwd)
            if user is not None:
                return pwd
            else:
                return ValidationError(u'密码不正确，不能绑定')