import os
import django
import matplotlib.pyplot as plt

# 1. Configuração do ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.models import Loja

def gerar_dashboards_regionais():
    lojas = Loja.objects.all()
    
    nomes_lojas = []
    lucros_potenciais = []
    investimento_estoque = []

    print("=" * 50)
    print("      TECHSTORE BI - RELATÓRIO CONSOLIDADO")
    print("=" * 50)

    for loja in lojas:
        lucro_total = 0
        estoque_total = 0
        
        # Percorre os produtos vinculados a esta loja
        produtos = loja.produtos.all()
        for p in produtos:
            # Lucro total = (Lucro Unitário * Quantidade em Estoque)
            lucro_total += float(p.calcular_margem_abs()) * p.estoque
            estoque_total += float(p.valor_total_estoque())
        
        nomes_lojas.append(loja.nome_da_loja)
        lucros_potenciais.append(lucro_total)
        investimento_estoque.append(estoque_total)

        print(f"FILIAL: {loja.nome_da_loja.ljust(15)} | LUCRO: R$ {lucro_total:>9.2f}")

    # --- CRIAÇÃO DOS GRÁFICOS ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('Performance Regional: Rio de Janeiro vs São Paulo', fontsize=16)

    # Gráfico 1: Lucro Potencial (Barras)
    cores = ['#003366', '#CC0000'] # Azul para RJ, Vermelho para SP
    ax1.bar(nomes_lojas, lucros_potenciais, color=cores)
    ax1.set_title('Lucro Potencial (Venda Total)')
    ax1.set_ylabel('R$')

    # Gráfico 2: Investimento em Estoque (Pizza)
    ax2.pie(investimento_estoque, labels=nomes_lojas, autopct='%1.1f%%', colors=cores, shadow=True)
    ax2.set_title('Distribuição de Investimento (% do Capital)')

    plt.tight_layout()
    print("\n[INFO] Exibindo dashboards... Feche a janela para continuar.")
    plt.show()

if __name__ == "__main__":
    gerar_dashboards_regionais()
    