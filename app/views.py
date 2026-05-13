from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CadastroForm, AvaliacaoForm
from .models import *

def home_view(request):
    produtos = Produto.objects.all()
    context = {
        'nome_empresa': 'TechStore',
        'produtos': produtos
    }
    return render(request, 'home.html', context)

def produtos_view(request):
    context = {
        
    }

    return render(request,'produtos.html', context)

@login_required
def avaliar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.usuario = request.user
            avaliacao.produto = produto
            avaliacao.save()
            
            return redirect('detalhe_produto', pk=produto.id)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            print(form.errors) 
            messages.error(request, "Usuário ou senha inválidos.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def cadastro_view(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            return render(request, 'cadastro.html', {'mostrar_bem_vindo': True, 'nome_usuario': user.username})
        else:
            return render(request, 'cadastro.html', {'form': form, 'mostrar_bem_vindo': False})
    else:
        form = CadastroForm()
    return render(request, 'cadastro.html', {'form': form})

    
def logout_view(request):
    logout(request)
    messages.info(request, "Você saiu com sucesso.")
    return redirect('login')

