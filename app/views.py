from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .forms import CadastroForm, AvaliacaoForm, UserUpdateForm, PerfilUpdateForm, ProdutoForm
from .models import *
from .carrinho import Carrinho


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
                messages.error(request, "Erro ao adicionar produto. Verifique os dados.")

        elif 'adicionar_avaliacao' in request.POST:
            form_avaliacao = AvaliacaoForm(request.POST)
            if form_avaliacao.is_valid():
                avaliacao = form_avaliacao.save(commit=False)
                avaliacao.usuario = request.user
                avaliacao.save()
                messages.success(request, "Avaliação enviada com sucesso!")
                return redirect('produtos')

    produtos = Produto.objects.all()

    q = request.GET.get('q', '').strip()
    if q:
        produtos = produtos.filter(nome__icontains=q)

    categoria_selecionada = request.GET.get('categoria', '').strip()
    if categoria_selecionada:
        produtos = produtos.filter(categoria=categoria_selecionada)

    preco_min = request.GET.get('preco_min')
    if preco_min:
        try:
            produtos = produtos.filter(preco__gte=float(preco_min))
        except ValueError:
            pass

    preco_max = request.GET.get('preco_max')
    if preco_max:
        try:
            produtos = produtos.filter(preco__lte=float(preco_max))
        except ValueError:
            pass

    categorias_choices = getattr(Produto, 'CATEGORIA_CHOICES', [])

    context = {
        'usuario': request.user.username,
        'produtos': produtos,
        'categorias_choices': categorias_choices,
        'categoria_selecionada': categoria_selecionada,
        'form': form,
        'form_avaliacao': form_avaliacao,
        'q': q,
    }
    
    return render(request, 'produtos.html', context)

def lista_favoritos(request):
    favoritos = Favorito.objects.filter(usuario=request.user).select_related('produto')
    produtos = [fav.produto for fav in favoritos] 
    
    return render(request, 'favoritos.html', {'produtos': produtos})

def alternar_favorito(request, produto_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'login_required'}, status=401)
        
    produto = get_object_or_404(Produto, id=produto_id)
    favorito_existente = Favorito.objects.filter(usuario=request.user, produto=produto)

    if favorito_existente.exists():
        favorito_existente.delete()
        favoritado = False
    else:
        Favorito.objects.create(usuario=request.user, produto=produto)
        favoritado = True

    return JsonResponse({'status': 'success', 'favoritado': favoritado})

def detalhe_carrinho(request):
    """Exibe os itens atualmente presentes no carrinho."""
    carrinho = Carrinho(request)
    return render(request, 'carrinho.html', {'carrinho': carrinho})

def carrinho_adicionar(request, produto_id):
    """Adiciona ou decrementa um produto controlando rigidamente o limite de estoque disponível."""
    carrinho = Carrinho(request)
    produto = get_object_or_404(Produto, id=produto_id)
    
    quantidade = 1
    override = False
    
    if request.method == 'POST':
        quantidade = int(request.POST.get('quantidade', 1))
        override = request.POST.get('override', 'False') == 'True'
        
    quantidade_no_carrinho = 0
    for item in carrinho:
        item_produto = item.get('produto') if isinstance(item, dict) else getattr(item, 'produto', None)
        if item_produto and item_produto.id == produto.id:
            quantidade_no_carrinho = item.get('quantidade', 0) if isinstance(item, dict) else getattr(item, 'quantidade', 0)
            break

    quantidade_final = quantidade if override else (quantidade_no_carrinho + quantidade)

    if quantidade_final > produto.estoque:
        messages.error(
            request, 
            f'Não é possível adicionar mais unidades de "{produto.nome}". '
            f'Você já tem {quantidade_no_carrinho} un. no carrinho e o estoque máximo é de {produto.estoque} un.'
        )
        return redirect(request.META.get('HTTP_REFERER', 'produtos'))
        
    carrinho.adicionar(produto=produto, quantidade=quantidade, override_quantidade=override)
    
    if override:
        messages.warning(request, f'"{produto.nome}" foi removido do seu carrinho!')
    else:
        messages.success(request, f'"{produto.nome}" foi adicionado ao seu carrinho!')
    
    return redirect(request.META.get('HTTP_REFERER', 'produtos'))


def carrinho_remover(request, produto_id):
    """Remove completamente um produto do carrinho (Botão da Lixeira)."""
    carrinho = Carrinho(request)
    produto = get_object_or_404(Produto, id=produto_id)
    
    carrinho.remover(produto)
    
    messages.warning(request, f'"{produto.nome}" foi removido do seu carrinho!')
    return redirect('detalhe_carrinho')


@login_required
def finalizar_compra(request):
    """Processa o checkout preenchendo automaticamente os dados do perfil do usuário."""
    carrinho = Carrinho(request)

    if len(carrinho) == 0:
        messages.info(request, 'Seu carrinho está vazio. Adicione produtos antes de finalizar.')
        return redirect('detalhe_carrinho')

    try:
        perfil = request.user.perfil
    except Exception:
        perfil = None

    if request.method == 'POST':
        nome_cliente = request.POST.get('nome')
        email_cliente = request.POST.get('email')
        telefone = request.POST.get('telefone')
        endereco = request.POST.get('endereco')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')
        cep = request.POST.get('cep')
        metodo_pagamento = request.POST.get('pagamento')

        pedido = Pedido.objects.create(
            comprador=request.user,
            total=carrinho.get_total_preco(),
            status='pendente'
        )

        for item in carrinho:
            ItemPedido.objects.create(
                pedido=pedido,
                produto=item['produto'],
                preco=item['preco'],
                quantidade=item['quantidade']
            )

        carrinho.limpar()  
        messages.success(request, f'Pedido #{pedido.id} realizado com sucesso!')
        return redirect('produtos')  

    context = {
        'carrinho': carrinho,
        'perfil': perfil
    }
    return render(request, 'finalizar_compra.html', context)

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

@login_required
def atendimento_view(request):
    perfil = getattr(request.user, 'perfil', None) 
    return render(request, 'atendimento.html', {'perfil': perfil})
