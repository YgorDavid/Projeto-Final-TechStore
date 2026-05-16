import os
import django
import matplotlib.pyplot as plt

# --- CONFIGURAÇÃO DO AMBIENTE DJANGO ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.models import Produto 

# MÓDULO DE INTELIGÊNCIA LOGÍSTICA E FINANCEIRA

def identificar_regiao_por_cep(cep):
    """Retorna o Estado baseado no primeiro dígito do CEP."""
    if not cep:
        return "Outras Regiões"
    cep_limpo = str(cep).replace("-", "").strip()
    primeiro_digito = cep_limpo[0]
    
    if primeiro_digito in ['0', '1']:
        return "São Paulo"
    elif primeiro_digito == '2':
        return "Rio de Janeiro"
    elif primeiro_digito == '3':
        return "Minas Gerais"
    else:
        return "Outras Regiões"

# --- ÁREA DE PROCESSAMENTO (CONEXÃO COM O BANCO REAL) ---
if __name__ == "__main__":
    print("--- CONECTANDO AO BANCO DE DADOS DJANGO ---")
    
    # Buscamos todos os produtos cadastrados
    produtos_reais = Produto.objects.all()
    
    if not produtos_reais.exists():
        print("Nenhum produto cadastrado no banco de dados ainda!")
        exit()
        
    print("--- AGRUPANDO LUCRO POTENCIAL POR REGIÃO ---")
    lucro_por_regiao = {}
    
    for produto in produtos_reais:
        preco_venda = float(produto.preco)
        preco_custo = float(produto.preco_custo)
        quantidade_estoque = int(produto.estoque)
        
        valor_frete = 15.00
        lucro_unitario = preco_venda - preco_custo - valor_frete
        lucro_total_produto = lucro_unitario * quantidade_estoque
        
        # INSTÂNCIA DINÂMICA: Puxa o CEP da loja vinculada ao produto
        try:
            cep_loja = produto.loja.cep  # Acessa o CEP através do relacionamento
            regiao = identificar_regiao_por_cep(cep_loja)
        except AttributeError:
            # Caso o produto não tenha loja vinculada, evita que o script quebre
            regiao = "São Paulo"
        
        if regiao in lucro_por_regiao:
            lucro_por_regiao[regiao] += lucro_total_produto
        else:
            lucro_por_regiao[regiao] = lucro_total_produto

    # Mostra o resultado em texto no terminal
    for regiao, total_lucro in lucro_por_regiao.items():
        print(f"Região: {regiao:15} | Lucro Potencial em Estoque: R$ {total_lucro:.2f}")

    print("\n--- GERANDO COMPONENTE VISUAL REAL ---")
    print("Abrindo o painel de Dashboards... Feche a janela do gráfico para encerrar.")

    # --- MONTAGEM DO MATPLOTLIB ---
    estados = list(lucro_por_regiao.keys()) 
    lucros = list(lucro_por_regiao.values()) 
    
    plt.figure(figsize=(8, 5))
    
    # Cores personalizadas: Azul escuro para a primeira barra, Vermelho para a segunda (padrão elegante)
    cores = ['navy', 'crimson', 'darkgreen', 'orange'][:len(estados)]
    
    plt.bar(estados, lucros, color=cores, edgecolor='black', width=0.4)
    
    plt.title("KPI Financeiro: Lucro Real do Estoque por Região", fontsize=14, fontweight='bold')
    plt.xlabel("Regiões (Faturamento por Filial)", fontsize=12)
    plt.ylabel("Lucro Total em Estoque (R$)", fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Adiciona os valores no topo de cada barra para dar o toque premium final
    for i, valor in enumerate(lucros):
        plt.text(i, valor + (max(lucros) * 0.01), f"R$ {valor:,.2f}", ha='center', va='bottom', fontweight='bold')
        
    plt.tight_layout()
    plt.show()
    