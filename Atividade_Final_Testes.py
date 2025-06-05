import pandas as pd
import random
import sys
import json
import os

# Parâmetros
alpha = 0.5  # taxa de aprendizado
gamma = 0.9  # fator de desconto
epsilon = 0.2  # chance de explorar

# Inicializa a Tabela Q
# q_table = {
#     'seco': {'regar': 0.0, 'pouca_agua': 0.0, 'nao_regar': 0.0},
#     'ideal': {'regar': 0.0, 'pouca_agua': 0.0, 'nao_regar': 0.0},
#     'encharcado': {'regar': 0.0, 'pouca_agua': 0.0, 'nao_regar': 0.0},
# }

if os.path.exists('q_table_input.json'):
    with open('q_table_input.json', 'r') as f:
        q_table = json.load(f)
else:
    q_table = {
        'seco': {'regar': 0.0, 'pouca_agua': 0.0, 'nao_regar': 0.0},
        'ideal': {'regar': 0.0, 'pouca_agua': 0.0, 'nao_regar': 0.0},
        'encharcado': {'regar': 0.0, 'pouca_agua': 0.0, 'nao_regar': 0.0},
    }

# Carrega recompensas do arquivo JSON ou define padrão
if os.path.exists('recompensas.json'):
    with open('recompensas.json', 'r') as f:
        recompensas = json.load(f)
else:
    recompensas = {
        'seco': {'regar': 5, 'pouca_agua': 2, 'nao_regar': -1},
        'ideal': {'regar': -3, 'pouca_agua': 2, 'nao_regar': 5},
        'encharcado': {'regar': -5, 'pouca_agua': -1, 'nao_regar': 2},
    }

# Função de transição
def transicao(estado, acao):
    if estado == 'seco':
        if acao == 'regar': return 'ideal'
        elif acao == 'pouca_agua': return 'seco'
        else: return 'seco'
    elif estado == 'ideal':
        if acao == 'regar': return 'encharcado'
        elif acao == 'pouca_agua': return 'ideal'
        else: return 'seco'
    elif estado == 'encharcado':
        if acao == 'regar': return 'encharcado'
        elif acao == 'pouca_agua': return 'ideal'
        else: return 'ideal'

# Função de recompensa usando o dicionário carregado
def recompensa(estado, acao):
    if estado in recompensas and acao in recompensas[estado]:
        return recompensas[estado][acao]
    else:
        return 0  # padrão para recompensas não definidas

# Função para alterar o número de episódios (padrão 100)
def mudarRangeDeEpisodios():
    try:
        valor = float(sys.argv[1]) if len(sys.argv) > 1 else 100
        if not valor.is_integer():
            raise ValueError
        num_episodios = int(valor)
    except ValueError:
        print(f"Erro: '{sys.argv[1]}' não é um número inteiro válido.")
        sys.exit(1)
    return num_episodios

def obter_epsilon():
    try:
        valor = float(sys.argv[2]) if len(sys.argv) > 2 else 0.2
        if valor < 0.0 or valor > 1.0:
            raise ValueError
        return valor
    except ValueError:
        print(f"Erro: '{sys.argv[2]}' não é um valor válido para epsilon.")
        sys.exit(1)

numEpisodios = mudarRangeDeEpisodios()
epsilon = obter_epsilon()

# Histórico para análise
historico = []

# Execução dos episódios
for episodio in range(1, numEpisodios):
    estado = random.choice(['seco', 'ideal', 'encharcado'])

    for passo in range(1):  # Um passo por episódio
        if random.random() < epsilon:
            acao = random.choice(['regar', 'pouca_agua', 'nao_regar'])
        else:
            acao = max(q_table[estado], key=q_table[estado].get)

        prox_estado = transicao(estado, acao)
        r = recompensa(estado, acao)
        max_q_prox = max(q_table[prox_estado].values())
        q_atual = q_table[estado][acao]
        q_novo = q_atual + alpha * (r + gamma * max_q_prox - q_atual)
        q_table[estado][acao] = q_novo

        historico.append({
            'Episódio': episodio,
            'Estado': estado,
            'Ação': acao,
            'Recompensa': r,
            'Próximo estado': prox_estado,
            'Q(s,a)': round(q_novo, 2)
        })
        estado = prox_estado

# Cria a pasta 'htmlsFolder' se ela não existir
os.makedirs('htmlsFolder', exist_ok=True)

# Exibe a tabela final de Q-values com pandas
q_df = pd.DataFrame(q_table).T

# Salvar tabela Q como JSON para uso externo (interface gráfica)
with open('q_table.json', 'w') as file:
    json.dump(q_table, file)

print("Tabela Q salva como 'q_table.json'. Abra no navegador para visualizar.")

# Histórico
historico_df = pd.DataFrame(historico)

q_html = q_df.style.background_gradient(cmap="YlGn").to_html()

# Adicionar CSS manualmente
css = """
<style>
table {
    border-collapse: collapse;
    width: 80%;
    margin: 20px auto;
    font-family: Arial, sans-serif;
}

th, td {
    border: 2px solid #6495ED;
    text-align: center;
    padding: 10px;
}

th {
    background-color: #6495ED;
    color: white;
}

tr:nth-child(even) {
    background-color: #f2f2f2;
}
</style>
"""

# Salvar com o CSS embutido
with open("htmlsFolder/q_table.html", "w", encoding="utf-8") as f:
    f.write(css + q_html)

# Mostrar no terminal sem estilo
print(q_df)
   
# Mostra histórico das decisões (últimos 10)
historico_df = pd.DataFrame(historico)
historico_df.tail(10).to_html("htmlsFolder/historico.html")

print("Histórico salvo como 'htmlsFolder/historico.html'.")
print(historico_df.tail(10))