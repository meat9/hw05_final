import datetime as dt
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404

from .models import Post, Group, User, Comment, Follow
from django.contrib.auth.decorators import login_required





def profile_follow(request, username):
    folloing = request.user.Follow.author
    x = Follow.objects.all()[0].user.id
    print (x)
