from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CadastroForm, AvaliacaoForm, UserUpdateForm, PerfilUpdateForm, ProdutoForm
from .models import *


def home_view(request):
    produtos = Produto.objects.all()
    
    avaliacoes_top = Avaliacao.objects.filter(nota=5)
    
    context = {
        'nome_empresa': 'TechStore',
        'produtos': produtos,
        'avaliacoes': avaliacoes_top
    }
    
    return render(request, 'home.html', context)

@login_required
def produtos_view(request):
    form = ProdutoForm()
    form_avaliacao = AvaliacaoForm()

    if request.method == 'POST':
        if 'adicionar_produto' in request.POST:
            form = ProdutoForm(request.POST, request.FILES)
            
            if form.is_valid():
                novo_produto = form.save(commit=False)
                
                loja_do_usuario = Loja.objects.filter(equipe=request.user).first()
                
                if not loja_do_usuario:
                    loja_do_usuario = Loja.objects.create(
                        nome_da_loja=f"Loja de {request.user.username}",
                        descricao="Criada automaticamente pelo sistema ao adicionar o primeiro produto."
                    )
                    loja_do_usuario.equipe.add(request.user)
                
                novo_produto.loja = loja_do_usuario
                novo_produto.save()
                
                messages.success(request, "Produto adicionado com sucesso!")
                return redirect('produtos')
            else:
                print("ERROS DO FORMULÁRIO:", form.errors)
                messages.error(request, "Erro ao adicionar produto. Verifique os dados.")

    if request.method == 'POST' and 'adicionar_avaliacao' in request.POST:
        form_avaliacao = AvaliacaoForm(request.POST)
        if form_avaliacao.is_valid():
            avaliacao = form_avaliacao.save(commit=False)
            avaliacao.usuario = request.user
            avaliacao.save()
            return redirect('produtos')
    
    produtos = Produto.objects.all()
    q = request.GET.get('q')
    if q:
        produtos = produtos.filter(nome__icontains=q)
    
    categoria_id = request.GET.get('categoria')
    categoria_selecionada = None
    if categoria_id:
        try:
            categoria_selecionada = int(categoria_id)
            produtos = produtos.filter(categoria_id=categoria_selecionada)
        except ValueError:
            pass
    
    preco_min = request.GET.get('preco_min')
    if preco_min:
        try:
            preco_min = float(preco_min)
            produtos = produtos.filter(preco__gte=preco_min)
        except ValueError:
            pass
    
    preco_max = request.GET.get('preco_max')
    if preco_max:
        try:
            preco_max = float(preco_max)
            produtos = produtos.filter(preco__lte=preco_max)
        except ValueError:
            pass
    
    context = {
        'usuario': request.user.username,
        'produtos': produtos,
        'categorias': Categoria.objects.all(),
        'categoria_selecionada': categoria_selecionada,
        'form': form,
        'form_avaliacao': form_avaliacao,
    }
    
    return render(request, 'produtos.html', context)

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
            
            tipo_perfil = form.cleaned_data.get('tipo_pessoa')
            nome_loja_digitado = form.cleaned_data.get('nome_da_loja')
            
            if tipo_perfil == 'PJ' and nome_loja_digitado:
                nova_loja = Loja.objects.create(
                    nome_da_loja=nome_loja_digitado,
                    descricao=f"Loja de {user.username}"
                )
                nova_loja.equipe.add(user)
            
            messages.success(request, f"Conta criada com sucesso para {user.username}! Faça o seu login.")
            return redirect('login')
        
        else:
            print("ERROS DE VALIDAÇÃO DO CADASTRO:", form.errors)
            for campo, erros in form.errors.items():
                for erro in erros:
                    messages.error(request, f"Erro no campo {campo}: {erro}")
            
            return render(request, 'cadastro.html', {'form': form})
        
    else:
        form = CadastroForm()
    return render(request, 'cadastro.html', {'form': form})

    
def logout_view(request):
    logout(request)
    messages.info(request, "Você saiu com sucesso.")
    return redirect('login')

def atendimento_view(request):
    return render(request, 'atendimento.html')
