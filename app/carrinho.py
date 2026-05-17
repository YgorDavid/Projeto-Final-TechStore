from decimal import Decimal
from .models import Produto

class Carrinho:
    def __init__(self, request):
        self.session = request.session
        carrinho = self.session.get('carrinho')

        if not carrinho:
            carrinho = self.session['carrinho'] = {}

        self.carrinho = carrinho

    def adicionar(self, produto, quantidade=1, override_quantidade=False):
        """
        Adiciona um produto ao carrinho ou atualiza sua quantidade.
        """
        produto_id = str(produto.id)

        if produto_id not in self.carrinho:
            self.carrinho[produto_id] = {
                'quantidade': 0,
                'preco': str(produto.preco)
            }

        if override_quantidade:
            self.carrinho[produto_id]['quantidade'] = quantidade
        else:
            self.carrinho[produto_id]['quantidade'] += quantidade

        self.salvar()

    def remover(self, produto):
        """
        Remove um produto do carrinho.
        """
        produto_id = str(produto.id)

        if produto_id in self.carrinho:
            del self.carrinho[produto_id]
            self.salvar()

    def limpar(self):
        """
        Esvazia o carrinho por completo.
        """
        self.session['carrinho'] = {}
        self.session.modified = True

    def salvar(self):
        """
        Marca a sessão como modificada para garantir que seja salva.
        """
        self.session.modified = True

    def __iter__(self):
        """
        Itera sobre os itens do carrinho, buscando os produtos no banco de dados
        e calculando os subtotais de forma segura.
        """
        produto_ids = self.carrinho.keys()
        produtos = Produto.objects.filter(id__in=produto_ids)
        
        produtos_map = {str(p.id): p for p in produtos}
        
        stale_ids = []

        for produto_id, item in self.carrinho.items():
            produto = map_produto = produtos_map.get(produto_id)
            
            if produto:
                item_context = item.copy()
                item_context['produto'] = produto
                item_context['preco'] = Decimal(item['preco'])
                item_context['total'] = item_context['preco'] * item_context['quantidade']
                yield item_context
            else:
                stale_ids.append(produto_id)

        if stale_ids:
            for pid in stale_ids:
                del self.carrinho[pid]
            self.salvar()

    def get_total_preco(self):
        """Calcula a soma de todos os subtotais dos itens do carrinho"""
        return sum(Decimal(item['preco']) * item['quantidade'] for item in self.carrinho.values())

    def __len__(self):
        """
        Retorna a quantidade total de itens (soma das quantidades).
        """
        return sum(item['quantidade'] for item in self.carrinho.values())