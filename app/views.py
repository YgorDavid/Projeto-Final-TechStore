from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CadastroForm, AvaliacaoForm, UserUpdateForm, PerfilUpdateForm
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

@login_required(login_url='login')
def dashboard_view(request):
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = PerfilUpdateForm(request.POST, request.FILES, instance=perfil)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            perfil_instance = p_form.save(commit=False)
            
            num = p_form.cleaned_data.get('numero')
            rua = p_form.cleaned_data.get('endereco')
            
            if num and rua:
                perfil_instance.endereco = f"{rua} - Nº {num}"
            elif rua:
                perfil_instance.endereco = rua
                
            perfil_instance.save()
            
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            return redirect('dashboard')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = PerfilUpdateForm(instance=perfil)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'perfil': perfil
    }
    return render(request, 'dashboard.html', context)

# def detalhe_produto_view(request, pk):
#     produto = get_object_or_404(Produto, pk=pk)
#     avaliacoes = produto.avaliacoes.all()
    
#     context = {
#         'produto': produto,
#         'avaliacoes': avaliacoes
#     }
    
#     return render(request, 'detalhe_produto.html', context)

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
            
            messages.success(request, f"Seja bem-vindo, {user.username}! Login realizado com sucesso.")
            
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
            user = form.save()
            
            messages.success(request, f"Conta criada com sucesso para {user.username}! Faça o seu login abaixo.")
            
            return redirect('login') 
        else:
            return render(request, 'cadastro.html', {'form': form})
    else:
        form = CadastroForm()
    return render(request, 'cadastro.html', {'form': form})

    
def logout_view(request):
    logout(request)
    messages.info(request, "Você saiu com sucesso.")
    return redirect('login')

