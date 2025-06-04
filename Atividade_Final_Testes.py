import random
import pandas as pd

# Parâmetros
alpha = 0.5 # taxa de aprendizado
gamma = 0.9 # fator de desconto
epsilon = 0.2 # chance de explorar

# Inicializa a Tabela Q
q_table = {
    'seco': {'regar': 0.0, 'pouca_agua': 0.0, 'nao_regar': 0.0},
    'ideal': {'regar': 0.0, 'pouca_agua': 0.0, 'nao_regar': 0.0},
    'encharcado': {'regar': 0.0, 'pouca_agua': 0.0, 'nao_regar': 0.0},
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

# Função de recompensa
def recompensa(estado, acao):
    if estado == 'seco':
        if acao == 'regar': return 5
        elif acao == 'pouca_agua': return 2
        else: return -1
    elif estado == 'ideal':
        if acao == 'nao_regar': return 5
        elif acao == 'pouca_agua': return 2
        else: return -3
    elif estado == 'encharcado':
        if acao == 'nao_regar': return 2
        elif acao == 'pouca_agua': return -1
        else: return -5

# Registro
historico = []

# Episódios
for episodio in range(1, 51):
    estado = random.choice(['seco', 'ideal', 'encharcado'])

    for passo in range(1): # Um passo por episódio
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

# Mostra a tabela final de Q-values
q_df = pd.DataFrame(q_table).T

# Salvar a tabela como HTML com gradiente
q_df.style.background_gradient(cmap="YlGn").to_html("q_table.html")
print("Tabela Q salva como 'q_table.html'. Abra no navegador para visualizar.")

# Mostrar no terminal sem estilo
print(q_df)

# Mostra histórico das decisões (últimos 10)
historico_df = pd.DataFrame(historico)
historico_df.tail(10).to_html("historico.html")

print("Histórico salvo como 'historico.html'.")
print(historico_df.tail(10))