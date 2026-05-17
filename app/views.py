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
# --- IMPORTS DE INTERFACE E AUTENTICAÇÃO ---
from django.shortcuts import render, redirect 
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm 
from django.contrib import messages
from django import forms
from .models import Perfil, Loja, Produto 

# --- IMPORTS DE ENGENHARIA DE DADOS E BI ---
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import io
import base64

# --- SEGURANÇA ---
from django.contrib.admin.views.decorators import staff_member_required

# --- FUNÇÃO AUXILIAR DE BI ---
def exportar_grafico_para_base64():
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    imagem_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    return imagem_base64

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
    
    favoritos_ids = []

    if request.user.is_authenticated:
        favoritos_ids = list(Favorito.objects.filter(usuario=request.user).values_list('produto_id',flat=True))

    context = {
    'usuario': request.user.username,
    'produtos': produtos,
    'categorias_choices': categorias_choices,
    'categoria_selecionada': categoria_selecionada,
    'form': form,
    'form_avaliacao': form_avaliacao,
    'q': q,
    'favoritos_ids': favoritos_ids,
}
    
    return render(request, 'produtos.html', context)

def detalhe_produto(request, produto_id):

    produto = get_object_or_404(
        Produto,
        id=produto_id
    )

    return render(
        request,
        'detalhe_produto.html',
        {
            'produto': produto
        }
    )

@login_required
def favoritar_produto(request, produto_id):

    produto = get_object_or_404(
        Produto,
        id=produto_id
    )

    favorito = Favorito.objects.filter(
        usuario=request.user,
        produto=produto
    )

    if favorito.exists():
        favorito.delete()

    else:
        Favorito.objects.create(
            usuario=request.user,
            produto=produto
        )

    return redirect('produtos')

@login_required
def lista_favoritos(request):
    favoritos = Favorito.objects.filter(usuario=request.user).select_related('produto')

    return render(request,'favoritos.html',{'favoritos': favoritos})

@login_required
def alternar_favorito(request, produto_id):
    produto = get_object_or_404(Produto,id=produto_id)

    favorito_existente = Favorito.objects.filter(usuario=request.user,produto=produto)

    if favorito_existente.exists():
        favorito_existente.delete()
        favoritado = False

    else:
        Favorito.objects.create(
            usuario=request.user,
            produto=produto
        )

        favoritado = True

    return JsonResponse({'status': 'success','favoritado': favoritado})

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
# --- 1. FORMULÁRIO DE CADASTRO ---
class CadastroForm(UserCreationForm):
    documento = forms.CharField(
        label="CPF ou CNPJ",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000-00'})
    )
    cep = forms.CharField(
        label="CEP",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'})
    )

    def clean_documento(self):
        doc = ''.join(filter(str.isdigit, self.cleaned_data.get('documento', '')))
        if len(doc) not in [11, 14]:
            raise forms.ValidationError("Digite um CPF ou CNPJ válido.")
        return doc

# --- 2. VIEWS ---

def home_view(request):
    context = {'nome_empresa': 'TechStore'}
    return render(request, 'home.html', context)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            usuario = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
            if usuario:
                login(request, usuario)
                return redirect('home')
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})

def cadastro_view(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            doc = form.clean_documento()
            tipo = 'PF' if len(doc) == 11 else 'PJ'
            Perfil.objects.create(usuario=user, tipo_pessoa=tipo, documento=doc, cep=form.cleaned_data.get('cep'))
            messages.success(request, f"Conta {tipo} criada com sucesso.")
            return redirect('login')
    else:
        form = CadastroForm()
    return render(request, 'cadastro.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def atendimento_view(request):
    perfil = getattr(request.user, 'perfil', None) 
    return render(request, 'atendimento.html', {'perfil': perfil})
def produtos_view(request):
    context = {'lista_produtos': Produto.objects.all()} 
    return render(request, 'produtos.html', context)

@staff_member_required
def dashboard_bi_view(request):
    """
    View consolidada: KPIs + Gráfico de Barras + Gráfico de Pizza + Ranking
    """
    # 1. BUSCA DE DADOS
    lojas = Loja.objects.all()
    produtos = Produto.objects.all()
    
    # --- LÓGICA PARA O GRÁFICO DE BARRAS (Regionais) ---
    nomes_lojas = []
    valores_lucro_loja = []
    for loja in lojas:
        lucro_loja = sum(float(p.calcular_margem_abs()) * p.estoque for p in loja.produtos.all())
        nomes_lojas.append(loja.nome_da_loja)
        valores_lucro_loja.append(lucro_loja)

    # --- LÓGICA PARA O GRÁFICO DE PIZZA (Categorias - Opção B) ---
    categorias_lucro = {}
    for p in produtos:
        # Verifica se o produto tem categoria, senão marca como 'Geral'
        cat = p.categoria if hasattr(p, 'categoria') and p.categoria else "Geral"
        lucro_total_produto = float(p.calcular_margem_abs()) * p.estoque
        categorias_lucro[cat] = categorias_lucro.get(cat, 0) + lucro_total_produto

    # --- GERANDO GRÁFICO DE BARRAS ---
    plt.figure(figsize=(10, 5))
    plt.style.use('dark_background')
    plt.bar(nomes_lojas, valores_lucro_loja, color='#58a6ff') 
    plt.title('LUCRO POR REGIONAL', color='#58a6ff')
    grafico_barras = exportar_grafico_para_base64()
    plt.close()

    # --- GERANDO GRÁFICO DE PIZZA ---
    plt.figure(figsize=(7, 7))
    plt.style.use('dark_background')
    plt.pie(categorias_lucro.values(), labels=categorias_lucro.keys(), autopct='%1.1f%%', colors=['#58a6ff', '#51cf66', '#ff7b72'])
    plt.title('MIX DE LUCRO POR CATEGORIA', color='#51cf66')
    grafico_pizza = exportar_grafico_para_base64()
    plt.close()

    # --- RANKING (Opção A) ---
    produtos_ranking = sorted(produtos, key=lambda p: float(p.calcular_margem_abs()), reverse=True)[:5]

    # 5. ENTREGA PARA O HTML
    context = {
        'grafico': grafico_barras,
        'grafico_pizza': grafico_pizza, # Nova variável enviada
        'total_geral': sum(valores_lucro_loja),
        'total_lojas': lojas.count(),
        'produtos_lucrativos': produtos_ranking,
    }
    
    return render(request, 'admin/dashboard_bi.html', context)
@staff_member_required
def dashboard_logistica_view(request):
    # 1. Pegamos todos os produtos do banco de dados
    produtos = Produto.objects.all()
    
    # 2. Calculamos o Capital Imobilizado
    # (Preço de custo que você pagou multiplicado pela quantidade que tem guardada)
    capital_total = sum(float(p.preco_custo) * p.estoque for p in produtos)
    
    # 3. Criamos uma lista apenas com produtos que estão com estoque baixo (menos de 5)
    estoque_critico = [p for p in produtos if p.estoque < 5]
    
    # 4. Criamos o Gráfico de Saúde do Estoque
    # Vamos contar quantos produtos estão em cada situação
    qtd_critico = len([p for p in produtos if p.estoque < 5])
    qtd_atencao = len([p for p in produtos if 5 <= p.estoque <= 10])
    qtd_saudavel = len([p for p in produtos if p.estoque > 10])

    plt.figure(figsize=(8, 5))
    plt.style.use('dark_background')
    
    categorias = ['Crítico (<5)', 'Atenção (5-10)', 'Saudável (>10)']
    contagem = [qtd_critico, qtd_atencao, qtd_saudavel]
    cores = ['#ff7b72', '#f1e05a', '#51cf66'] # Vermelho, Amarelo, Verde

    plt.bar(categorias, contagem, color=cores)
    plt.title('SAÚDE DO INVENTÁRIO (QUANTIDADE)', color='#58a6ff', pad=20)
    
    # Transformamos o gráfico em imagem para o HTML entender
    grafico_estoque = exportar_grafico_para_base64()
    plt.close()

    # 5. Enviamos tudo para o novo template que vamos criar
    context = {
        'estoque_critico': estoque_critico,
        'capital_total': capital_total,
        'grafico_estoque': grafico_estoque,
        'total_pecas': sum(p.estoque for p in produtos)
    }
    return render(request, 'admin/dashboard_logistica.html', context)
