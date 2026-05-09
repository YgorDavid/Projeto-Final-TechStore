# Create your views here.

from django.shortcuts import render, redirect 
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import *

def home_view(request):
    context = {
        'nome_empresa': 'TechStore'
    }

    return render(request,'home.html', context)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            usuario = authenticate(username=username, password=password)
            
            if usuario is not None:
                login(request, usuario)
                return redirect('home') # Certifique-se que a rota da home se chama 'home' no urls.py
            else:
                messages.error(request, "Usuário ou senha inválidos.  Tente novamente!")
        else:
            messages.error(request, "Informações inválidas. Tente novamente!")
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})
   
def cadastro_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            return render(request, 'cadastro.html', {
                'form': CustomUserCreationForm(),
                'mostrar_bem_vindo': True,
                'email_usuario': user.email,
                'nome_usuario': user.username,
            })
    else:
        form = CustomUserCreationForm()
    return render(request, 'cadastro.html', {'form': form})
    
def logout_view(request):
    logout(request)

    return redirect('login')

    # sincronização total 09/05