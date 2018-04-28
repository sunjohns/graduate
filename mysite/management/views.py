# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render,render_to_response
from django.core.urlresolvers import reverse


# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from management.forms import LoginForm, RegistrationForm, UserProfileForm, UserInfoForm, UserForm
from management.models import UserProfile, UserInfo
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def user_login(request):
	if request.method == "POST":
		login_form = LoginForm(request.POST)
		if login_form.is_valid():
			cd = login_form.cleaned_data
			user = authenticate(username=cd['username'], password=cd['password'])
			if user:
				login(request,user)
				return HttpResponseRedirect('/')
			else:
				return HttpResponse("Sorry, Your username or password is not right.")
		else:
			return HttpResponse("Invalid login")

	if request.method == "GET":
		login_form = LoginForm()
		return render_to_response("management/login.html", {"form":login_form,"user":request.user})
def register(request):
    if request.method == "POST":
        user_form = RegistrationForm(request.POST)
        userprofile_form = UserProfileForm(request.POST)
        if user_form.is_valid()*userprofile_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            new_profile = userprofile_form.save(commit=False)
            new_profile.user = new_user
            new_profile.save()
            UserInfo.objects.create(user=new_user)
            return HttpResponseRedirect("/management/login")
        else:
            return HttpResponse("sorry, your can not register.")
    else:
        user_form = RegistrationForm()
        userprofile_form = UserProfileForm()
        return render_to_response("management/register.html", {"form": user_form, "profile":userprofile_form})

@login_required(login_url='/management/login/')
def myself(request):
    user = User.objects.get(username=request.user.username)
    userprofile = UserProfile.objects.get(user=user)
    userinfo = UserInfo.objects.get(user=user)
    return render_to_response("management/myself.html", {"user": user, "userinfo": userinfo, "userprofile": userprofile})


@login_required(login_url='/management/login/')
def myself_edit(request):
    user = User.objects.get(username=request.user.username)
    userprofile = UserProfile.objects.get(user=request.user)
    userinfo = UserInfo.objects.get(user=request.user)

    if request.method == "POST":
        user_form = UserForm(request.POST)
        userprofile_form = UserProfileForm(request.POST)
        userinfo_form = UserInfoForm(request.POST)
        if user_form.is_valid() * userprofile_form.is_valid() * userinfo_form.is_valid():
            user_cd = user_form.cleaned_data
            userprofile_cd = userprofile_form.cleaned_data
            userinfo_cd = userinfo_form.cleaned_data
            user.email = user_cd['email']
            userprofile.birth = userprofile_cd['birth']
            userprofile.phone = userprofile_cd['phone']
            userinfo.school = userinfo_cd['school']
            userinfo.company = userinfo_cd['company']
            userinfo.profession = userinfo_cd['profession']
            userinfo.address = userinfo_cd['address']
            userinfo.aboutme = userinfo_cd['aboutme']
            user.save()
            userprofile.save()
            userinfo.save()
        return HttpResponseRedirect('/management/my-information/')
    else:
        user_form = UserForm(instance=request.user)
        userprofile_form = UserProfileForm(initial={"birth":userprofile.birth, "phone":userprofile.phone})
        userinfo_form = UserInfoForm(initial={"school":userinfo.school, "company":userinfo.company, "profession":userinfo.profession, "address":userinfo.address, "aboutme":userinfo.aboutme})
        return render(request, "management/myself_edit.html", {"user_form":user_form, "userprofile_form":userprofile_form, "userinfo_form":userinfo_form})


@login_required(login_url='/management/login/')
def my_image(request):
    if request.method == 'POST':
        img = request.POST['img']
        userinfo = UserInfo.objects.get(user=request.user.id)
        userinfo.photo = img
        userinfo.save()
        return HttpResponse("1")
    else:
        return render_to_response('management/imagecrop.html',)
