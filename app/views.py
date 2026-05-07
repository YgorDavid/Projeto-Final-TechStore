# Create your views here.

from django.shortcuts import render
from .models import *

def home_view(request):
    context = {
        'nome_empresa': 'TechStore'
    }

    return render(request,'home.html', context)

def login_view(request):
    context = {
    }

    return render(request,'login.html', context)

def cadastro_view(request):
    context = {
    }
    
    return render(request, 'cadastro.html', context)

def logout_view(request):
    context = {
    }
    
    return render(request, context)