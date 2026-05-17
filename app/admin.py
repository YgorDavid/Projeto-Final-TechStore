from django.contrib import admin
from .models import Perfil, Categoria, Loja, Produto, Avaliacao, Pedido, ItemPedido

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'preco_custo', 'exibir_margem_abs', 'exibir_margem_pct', 'exibir_valor_estoque', 'estoque')
    list_filter = ('categoria', 'loja')
    search_fields = ('nome', 'descricao')

    def exibir_margem_abs(self, obj):
        return f"R$ {obj.calcular_margem_abs():.2f}"
    exibir_margem_abs.short_description = 'Lucro (R$)'

    def exibir_margem_pct(self, obj):
        return f"{obj.calcular_margem_percentual()}%"
    exibir_margem_pct.short_description = 'Margem (%)'

    def exibir_valor_estoque(self, obj):
        return f"R$ {obj.valor_total_estoque():.2f}"
    exibir_valor_estoque.short_description = 'Total em Estoque'

admin.site.register(Perfil)
admin.site.register(Categoria)
admin.site.register(Loja)
admin.site.register(Avaliacao)
admin.site.register(Pedido)
admin.site.register(ItemPedido)