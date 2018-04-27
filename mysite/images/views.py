# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from django.views.decorators.csrf import csrf_exempt
from images.forms import ImageForm
from images.models import Image

@login_required(login_url='/management/login/')
@csrf_exempt
@require_POST
def upload_image(request):
    form = ImageForm(data=request.POST)
    if form.is_valid():
        try:
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.save()
            return JsonResponse({'status':"1"})
        except:
            return JsonResponse({'status':"0"})


@login_required(login_url='/management/login/')
def list_images(request):
    images = Image.objects.filter(user=request.user)
    return render_to_response('image/list_images.html', {"images": images, "user": request.user})


@login_required(login_url='/management/login/')
@require_POST
@csrf_exempt
def del_image(request):
    image_id = request.POST['image_id']
    try:
        image = Image.objects.get(id=image_id)
        image.delete()
        return JsonResponse({'status':"1"})
    except:
        return JsonResponse({'status':"2"})

@login_required(login_url='/management/login/')
def falls_images(request):
    images = Image.objects.all()
    return render(request, 'image/falls_images.html', {"images": images})