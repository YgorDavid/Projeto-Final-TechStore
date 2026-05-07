# Create your views here.

from django.shortcuts import render
from .models import *

def home_view(request):
    context = {
    }

    return render(request,'home.html', context)