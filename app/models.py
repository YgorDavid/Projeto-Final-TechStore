from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True) # Importante para URLs amigáveis

    class Meta:
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome

class Loja(models.Model):
    # Relaciona a Loja aos Usuários (equipe) para o Controle de Acesso
    equipe = models.ManyToManyField(User, related_name='lojas_que_gerencio', blank=True)
    nome_da_loja = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    logo = models.ImageField(upload_to='lojas/', blank=True, null=True)

    def __str__(self):
        return self.nome_da_loja

class Produto(models.Model):
    # Relacionamentos com Chave Estrangeira
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, related_name='produtos')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    
    # Informações do Produto
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.PositiveIntegerField(default=0)
    imagem = models.ImageField(upload_to='produtos/') # Essencial para o visual na Aula 20
    
    # Especificações Técnicas (Diferencial Tech)
    especificacoes = models.TextField(help_text="Ex: RAM, CPU, Versão do Software")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

class Avaliacao(models.Model):
    # Relacionamento para o Sistema de Reviews (Sugestão do projeto)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='avaliacoes')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nota = models.IntegerField(choices=[(i, i) for i in range(1, 6)]) # Nota de 1 a 5[cite: 1]
    comentario = models.TextField()
    data_postagem = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"

class Pedido(models.Model):
    # Opções de status para o Feedback e Lógica (Requisito B e C)
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

    def __str__(self):
        return f"Pedido #{self.id} - {self.comprador.username}"

class ItemPedido(models.Model):
    # Relaciona o Pedido aos Produtos (Chaves Estrangeiras)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2) # Preço no momento da compra

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"
    
# Faltou o custo