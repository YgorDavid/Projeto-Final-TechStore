from decimal import Decimal
from .models import Produto


class Carrinho:
    def __init__(self, request):
        self.session = request.session
        carrinho = self.session.get('carrinho')

        if not carrinho:
            carrinho = self.session['carrinho'] = {}

        self.carrinho = carrinho

    def adicionar(self, produto, quantidade=1):
        produto_id = str(produto.id)

        if produto_id not in self.carrinho:
            self.carrinho[produto_id] = {
                'quantidade': 0,
                'preco': str(produto.preco)
            }

        self.carrinho[produto_id]['quantidade'] += quantidade
        self.salvar()

    def remover(self, produto):
        produto_id = str(produto.id)

        if produto_id in self.carrinho:
            del self.carrinho[produto_id]
            self.salvar()

    def limpar(self):
        self.session['carrinho'] = {}
        self.session.modified = True

    def salvar(self):
        self.session.modified = True

    def __iter__(self):
        produto_ids = self.carrinho.keys()
        produtos = Produto.objects.filter(id__in=produto_ids)

        carrinho_copia = self.carrinho.copy()

        for produto in produtos:
            carrinho_copia[str(produto.id)]['produto'] = produto

        for item in carrinho_copia.values():
            item['preco'] = Decimal(item['preco'])
            item['total'] = item['preco'] * item['quantidade']

            yield item

    def get_total_preco(self):
        return sum(
            Decimal(item['preco']) * item['quantidade']
            for item in self.carrinho.values()
        )

    def __len__(self):
        return sum(item['quantidade'] for item in self.carrinho.values())