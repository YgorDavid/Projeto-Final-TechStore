from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    TIPO_PESSOA_CHOICES = [
        ('PF', 'Pessoa Física'),
        ('PJ', 'Pessoa Jurídica'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    foto = models.ImageField(upload_to='perfil_fotos/', null=True, blank=True)
    tipo_pessoa = models.CharField(max_length=2, choices=TIPO_PESSOA_CHOICES, default='PF')
    documento = models.CharField(max_length=18, unique=True, verbose_name="CPF/CNPJ")
    telefone = models.CharField(max_length=20, null=True, blank=True)
    cep = models.CharField(max_length=9, verbose_name="CEP")
    endereco = models.CharField(max_length=255, verbose_name="Rua", blank=True, null=True)
    cidade = models.CharField(max_length=100, verbose_name="Cidade", blank=True, null=True)
    estado = models.CharField(max_length=2, verbose_name="Estado", blank=True, null=True)
    
    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"

    def __str__(self):
        return f"{self.usuario.username} ({self.tipo_pessoa})"

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
    logo = models.ImageField(upload_to='lojas/', blank=True, null=True)

    def __str__(self):
        return self.nome_da_loja

class Produto(models.Model):
    CATEGORIA_CHOICES = [
        ('smartphones', 'Smartphones'),
        ('notebooks', 'Notebooks'),
        ('acessorios', 'Acessórios'),
        ('outros', 'Outros'),
    ]
    
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, related_name='produtos')
    categoria = models.CharField(
    max_length=50, 
    choices=CATEGORIA_CHOICES, 
    null=True, 
    blank=True
)
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    
    # Campos Financeiros
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    estoque = models.PositiveIntegerField(default=0)
    imagem = models.ImageField(upload_to='produtos/') 
    especificacoes = models.TextField(help_text="Ex: RAM, CPU, Versão do Software")

    # --- KPIs de Custo e Financeiros (Jorge) ---
    def calcular_margem_abs(self):
        """Retorna o lucro em Reais (Preço - Custo)"""
        return self.preco - self.preco_custo

    def calcular_margem_percentual(self):
        """Retorna a margem em porcentagem"""
        if self.preco > 0:
            margem = (self.calcular_margem_abs() / self.preco) * 100
            return round(margem, 2)
        return 0

    def valor_total_estoque(self):
        """KPI Logístico: Quanto dinheiro tenho parado neste produto"""
        return self.preco_custo * self.estoque

    def __str__(self):
        return self.nome

class Avaliacao(models.Model):
    NOTAS_CHOICES = [
        (1, '⭐ (1) Ruim'),
        (2, '⭐⭐ (2) Regular'),
        (3, '⭐⭐⭐ (3) Bom'),
        (4, '⭐⭐⭐⭐ (4) Muito Bom'),
        (5, '⭐⭐⭐⭐⭐ (5) Excelente'),
    ]

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='avaliacoes')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nota = models.PositiveSmallIntegerField(choices=NOTAS_CHOICES)
    comentario = models.TextField()
    data_postagem = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Avaliações"
        unique_together = ('usuario', 'produto') 

    def __str__(self):
        return f"Nota {self.nota} para {self.produto} por {self.usuario.username}"

class Pedido(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('enviado', 'Enviado'),
        ('cancelado', 'Cancelado'),
    ]
    comprador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    data_pedido = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
