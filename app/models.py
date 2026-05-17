from django.db import models
from django.contrib.auth.models import User

# --- 1. USUÁRIOS E PERFIS ---
class Perfil(models.Model):
    TIPO_PESSOA_CHOICES = [('PF', 'Pessoa Física'), ('PJ', 'Pessoa Jurídica')]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo_pessoa = models.CharField(max_length=2, choices=TIPO_PESSOA_CHOICES, default='PF')
    documento = models.CharField(max_length=18, unique=True, verbose_name="CPF/CNPJ")
    cep = models.CharField(max_length=9, verbose_name="CEP")
    endereco = models.CharField(max_length=255, verbose_name="Rua", blank=True, null=True)
    cidade = models.CharField(max_length=100, verbose_name="Cidade", blank=True, null=True)
    estado = models.CharField(max_length=2, verbose_name="Estado", blank=True, null=True)

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"

    def __str__(self):
        return f"{self.usuario.username} ({self.tipo_pessoa})"

# --- 2. ESTRUTURA DA LOJA ---
class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome

class Loja(models.Model):
    equipe = models.ManyToManyField(User, related_name='lojas_que_gerencio', blank=True)
    nome_da_loja = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    cep = models.CharField(max_length=9, verbose_name="CEP da Loja", default="00000-000")
    logo = models.ImageField(upload_to='lojas/', blank=True, null=True)

    def __str__(self):
        return self.nome_da_loja

class Produto(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, related_name='produtos')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço de Venda")
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço de Custo")
    estoque = models.PositiveIntegerField(default=0)
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True) 
    especificacoes = models.TextField(help_text="Ex: RAM, CPU")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self):
        return self.nome

    # --- ESTAS SÃO AS FUNÇÕES QUE ESTÃO FALTANDO ---

    def calcular_margem_abs(self):
        """Calcula o lucro bruto (Preço - Custo)"""
        return self.preco - self.preco_custo

    def calcular_margem_percentual(self):
        """Calcula a margem em %"""
        if self.preco > 0:
            return round(((self.preco - self.preco_custo) / self.preco) * 100, 2)
        return 0

    def valor_total_estoque(self):
        """Calcula o valor total investido no estoque atual"""
        return self.estoque * self.preco_custo

# --- 4. INTERAÇÃO E VENDAS ---
class Avaliacao(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='avaliacoes')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nota = models.PositiveSmallIntegerField()
    comentario = models.TextField()
    data_postagem = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Avaliações"

class Pedido(models.Model):
    comprador = models.ForeignKey(User, on_delete=models.CASCADE)
    data_pedido = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Pedido {self.id} - {self.comprador.username}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"