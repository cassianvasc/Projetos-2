from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .forms import PostCreateform, UpdatePostForm