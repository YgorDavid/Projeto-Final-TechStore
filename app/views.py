from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CadastroForm, AvaliacaoForm, UserUpdateForm, PerfilUpdateForm, ProdutoForm
from .models import *
from .carrinho import Carrinho

def detalhe_carrinho(request):
    carrinho = Carrinho(request)
    return render(request, 'carrinho.html', {'carrinho': carrinho})


def carrinho_adicionar(request, produto_id):
    carrinho = Carrinho(request)
    produto = get_object_or_404(Produto, id=produto_id)
    carrinho.adicionar(produto=produto)
    return redirect('detalhe_carrinho')


def carrinho_remover(request, produto_id):
    carrinho = Carrinho(request)
    produto = get_object_or_404(Produto, id=produto_id)
    carrinho.remover(produto)
    return redirect('detalhe_carrinho')

@login_required
def finalizar_compra(request):
    carrinho = Carrinho(request)

    context = {
        'carrinho': carrinho
    }

    return render(request, 'finalizar_compra.html', context)

    # aqui você pode salvar pedido no banco depois
    carrinho.limpar()  # se existir esse método

def home_view(request):
    produtos = Produto.objects.all()
    context = {
        'nome_empresa': 'TechStore',
        'produtos': produtos
    }
    return render(request, 'home.html', context)

@login_required
def produtos_view(request):
    form = ProdutoForm()
    form_avaliacao = AvaliacaoForm()
    
    if request.method == 'POST' and 'adicionar_produto' in request.POST:
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save(commit=False)
            loja_do_usuario = request.user.lojas_que_gerencio.first()
            if loja_do_usuario:
                produto.loja = loja_do_usuario
                produto.save()
                return redirect('produtos')
            else:
                form.add_error(None, 'Você precisa ter uma loja para adicionar produtos.')
    
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
            messages.success(request, f"Conta criada com sucesso para {user.username}! Faça o seu login.")
            return redirect('login')
        
        else:
            messages.error(request, "Erro ao criar conta. Verifique se os dados estão corretos (Senhas iguais, CPF válido, etc).")
            return render(request, 'cadastro.html', {'form': form})
        
    else:
        form = CadastroForm()
    return render(request, 'cadastro.html', {'form': form})

    
def logout_view(request):
    logout(request)
    messages.info(request, "Você saiu com sucesso.")
    return redirect('login')