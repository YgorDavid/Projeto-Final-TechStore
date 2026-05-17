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