from django.contrib import admin
from .models import Perfil, Categoria, Loja, Produto, Avaliacao, Pedido, ItemPedido

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    # Colunas que aparecerão na lista de produtos
    list_display = ('nome', 'preco', 'preco_custo', 'exibir_margem_abs', 'exibir_margem_pct', 'exibir_valor_estoque', 'estoque')
    
    # Filtros laterais para facilitar a vida do gerente
    list_filter = ('categoria', 'loja')
    
    # Campo de busca
    search_fields = ('nome', 'descricao')

    # Funções para exibir os KPIs que você criou no models.py
    def exibir_margem_abs(self, obj):
        return f"R$ {obj.calcular_margem_abs()}"
    exibir_margem_abs.short_description = 'Lucro (R$)'

    def exibir_margem_pct(self, obj):
        return f"{obj.calcular_margem_percentual()}%"
    exibir_margem_pct.short_description = 'Margem (%)'

    def exibir_valor_estoque(self, obj):
        return f"R$ {obj.valor_total_estoque()}"
    exibir_valor_estoque.short_description = 'Total em Estoque'

# Mantendo o registro da Avaliação que já estava lá
admin.site.register(Avaliacao)
admin.site.register(Categoria)
admin.site.register(Loja)