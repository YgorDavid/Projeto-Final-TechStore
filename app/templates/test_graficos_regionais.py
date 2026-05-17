import os
import django
import matplotlib.pyplot as plt

# 1. Configura o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.models import Loja, Produto

def gerar_graficos_rj_sp():
    lojas = Loja.objects.all()
    
    nomes_lojas = []
    totais_estoque = []

    # Coletando os dados reais que você cadastrou
    for loja in lojas:
        total = 0
        for p in loja.produtos.all():
            total += float(p.valor_total_estoque())
        
        nomes_lojas.append(loja.nome_da_loja)
        totais_estoque.append(total)

    # Criando a figura para os dois gráficos
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Análise Regional TechStore: RJ vs SP', fontsize=16)

    # --- GRÁFICO DE BARRAS ---
    cores = ['#003366', '#CC0000'] # Azul (RJ) e Vermelho (SP)
    bars = ax1.bar(nomes_lojas, totais_estoque, color=cores)
    ax1.set_title('Investimento Total por Unidade')
    ax1.set_ylabel('Valor em R$')
    
    # Coloca o valor em cima da barra
    for bar in bars:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval, f'R$ {yval:,.2f}', va='bottom', ha='center')

    # --- GRÁFICO DE PIZZA ---
    ax2.pie(totais_estoque, labels=nomes_lojas, autopct='%1.1f%%', colors=cores, startangle=140)
    ax2.set_title('Participação no Capital Total')

    plt.tight_layout()
    
    print("Gerando gráficos de visualização...")
    plt.show()

if __name__ == "__main__":
    gerar_graficos_rj_sp()