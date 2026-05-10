from django.shortcuts import render, redirect 
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm 
from django.contrib import messages
from .forms import CustomUserCreationForm
# Importe os modelos que for usar na home conforme a lógica do Ygor
from .models import Produto, Categoria 

def home_view(request):
    produtos = Produto.objects.all()
    context = {
        'nome_empresa': 'TechStore',
        'produtos': produtos
    }
    return render(request, 'home.html', context)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            return redirect('home')
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def cadastro_view(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            # 1. Salva o usuário principal (Auth do Django)
            user = form.save()
            return render(request, 'cadastro.html', {
                'form': CustomUserCreationForm(), 
                'mostrar_bem_vindo': True,
                'nome_usuario': user.username,
                'email_usuario': user.email,
            })
        else:
            messages.error(request, "Erro no cadastro. Verifique os dados.")
    else:
        form = CadastroForm()
    return render(request, 'cadastro.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')
    
