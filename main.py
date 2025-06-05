from nicegui import ui
import subprocess
import random
import json
import os

# Carrega recompensas do arquivo JSON ou usa padrão
if os.path.exists('recompensas.json'):
    with open('recompensas.json', 'r') as f:
        recompensas = json.load(f)
else:
    recompensas = {
        'seco': {'regar': 5, 'pouca_agua': 2, 'nao_regar': -1},
        'ideal': {'regar': -3, 'pouca_agua': 2, 'nao_regar': 5},
        'encharcado': {'regar': -5, 'pouca_agua': -1, 'nao_regar': 2},
    }

if os.path.exists('q_table_input.json'):
    with open('q_table_input.json', 'r') as f:
        epislon = json.load(f)
else:
    q_table = {
    'seco': {'regar': 0.0, 'pouca_agua': 0.0, 'nao_regar': 0.0},
    'ideal': {'regar': 0.0, 'pouca_agua': 0.0, 'nao_regar': 0.0},
    'encharcado': {'regar': 0.0, 'pouca_agua': 0.0, 'nao_regar': 0.0},
    }

# Carrega a q_table do arquivo JSON
with open('q_table.json', 'r') as file:
    q_table = json.load(file)

def salvar_recompensas():
    try:
        with open('recompensas.json', 'w') as f:
            json.dump(recompensas, f, indent=4)
        ui.notify('Recompensas salvas com sucesso!')
    except Exception as e:
        ui.notify(f'Erro ao salvar recompensas: {e}')

def salvar_epsilon():
    try:
        with open('epsilon.json', 'w') as f:
            json.dump({'epsilon': q_table}, f, indent=4)
        ui.notify('Valor de epsilon salvo com sucesso!')
    except Exception as e:
        ui.notify(f'Erro ao salvar epsilon: {e}')

# Contêineres globais para alternar entre as telas
container_menu = None
container_tela1 = None
container_tela2 = None
container_tela3 = None
caminho_imagem_menu = 'logo.png'

# Mensagens aleatórias para o menu
mensagens_menu = [
    "Seja bem-vindo ao sistema!",
    "Explore as funcionalidades com facilidade.",
    "Hoje é um ótimo dia para aprender!",
    "A tecnologia está ao seu alcance.",
]

# Função para alternar entre telas
def mostrar_tela(tela):
    global container_menu, container_tela1, container_tela2

    # Esconde todos os contêineres
    container_menu.style('display: none')
    container_tela1.style('display: none')
    container_tela2.style('display: none')
    container_tela3.style('display: none')

    # Mostra apenas o contêiner correspondente
    tela.style('display: flex')

# Função para criar a primeira tela
def criar_tela1():
    global container_tela1

    with container_tela1:
        # Contêiner global para armazenar a exibição dinâmica
        container_dinamico = ui.column()

        def executar_e_exibir():
            # Obtém o número de episódios do campo de entrada
            num_episodios = campo_episodios.value
            if num_episodios is None or num_episodios < 100:
                ui.notify('Por favor, insira um número inteiro maior ou igual a 100.')
                return

            # Limpa o conteúdo anterior, se existir
            container_dinamico.clear()

            try:
                # Executa o script de aprendizado por reforço com o número de episódios
                subprocess.run(['python', 'Atividade_Final_Testes.py', str(num_episodios)], check=True)

                # Carrega os arquivos HTML gerados
                with open('htmlsFolder/q_table.html', 'r', encoding='utf-8') as f:
                    q_table_html = f.read()
                with open('htmlsFolder/historico.html', 'r', encoding='utf-8') as f:
                    historico_html = f.read()

                # Atualiza o contêiner com os novos conteúdos
                with container_dinamico:
                    ui.label('Tabela de Resultados:').classes('text-sm mt-4')
                    ui.html(q_table_html).classes('w-full overflow-auto')
                    ui.label('Histórico de Decisões (últimos 10)').classes('text-sm mt-4') 
                    ui.html(historico_html).classes('w-full overflow-auto')
            except subprocess.CalledProcessError as e:
                ui.notify(f'Erro ao executar o script: {e}')
            except FileNotFoundError:
                ui.notify('Arquivos HTML não encontrados. Verifique se o script foi executado corretamente.')

        # Interface da Tela 1
        ui.label('Digite o número de episódios:').classes('text-sm mt-4')
        campo_episodios = ui.number(label='Número de episódios (minimo 100)', value=100, min=100).classes('w-full')
        with ui.row().classes('gap-4 mt-4'):  # Define um contêiner horizontal com espaçamento entre os botões
            ui.button('Executar Algoritmo e Exibir Resultados', on_click=executar_e_exibir).classes('text-sm px-3 py-2')
            ui.button('Voltar ao Menu', on_click=lambda: mostrar_tela(container_menu)).classes('text-sm px-3 py-2')


# Função para criar a segunda tela (uma terceira funcionalidade)
def criar_tela2():
    global container_tela2, recompensas

    with container_tela2:
        ui.label('Configuração de Recompensas').classes('text-h5 mb-2')

        if not recompensas:
            ui.label('A tabela de recompensas está vazia ou não foi carregada.').classes('text-red-500')
            return

        for estado, acoes in recompensas.items():
            ui.label(f'Estado: {estado}').classes('text-sm mt-4 mb-2')
            for acao, valor in acoes.items():
                def atualizar_recompensa(v, estado=estado, acao=acao):
                    recompensas[estado][acao] = v

                ui.number(
                    label=f'Ação: {acao}',
                    value=valor,
                    on_change=lambda e, est=estado, ac=acao: atualizar_recompensa(e.value, est, ac)
                ).classes('w-full mb-2')

        ui.button('Salvar Recompensas', on_click=salvar_recompensas).classes('mt-4')
        ui.button('Voltar ao Menu', on_click=lambda: mostrar_tela(container_menu)).classes('mt-4')# Função para criar o menu principal

def criar_tela3():
    global container_tela3, estados, acoes, inputs_q_table, container_dinamico

    estados = ['seco', 'ideal', 'encharcado']
    acoes = ['regar', 'pouca_agua', 'nao_regar']
    inputs_q_table = {}  # Dicionário para armazenar os inputs

    with container_tela3:
        ui.label('Configuração Manual da Q-Table').classes('text-h5 mb-2')

        # Campos de entrada para configurar os valores da Q-Table
        for estado in estados:
            ui.label(f'Valores para o estado: {estado}').classes('text-sm mt-4 mb-2')
            inputs_q_table[estado] = {}
            for acao in acoes:
                inputs_q_table[estado][acao] = ui.number(label=acao, value=0.0).classes('w-full mb-2')

        # Configurações adicionais
        ui.label('Digite o valor de epsilon (Pode deixar ele vazio, não afeta diretamente no resultado): ').classes('text-sm mt-4')
        def executar_algoritmo():
            q_table_valores = {
                estado: {acao: inputs_q_table[estado][acao].value for acao in acoes}
                for estado in estados
            }

            with open('q_table_input.json', 'w') as f:
                json.dump(q_table_valores, f, indent=4)

            epsilon = campo_epsilon.value

            with open('epsilon.json', 'w') as f:
                json.dump({'epsilon': epsilon}, f, indent=4)

            ui.notify('Q-Table salvos com sucesso!')
        campo_epsilon = ui.number(label='Epsilon', value=0.0, min=0.0, max=1.0, step=0.01).classes('w-full')
        ui.button('Salvar epsilon', on_click=executar_algoritmo).classes('mt-4')

        # Botão para executar o algoritmo
        def executar_algoritmo():
            # Coleta os valores da Q-Table configurada
            q_table_valores = {
                estado: {acao: inputs_q_table[estado][acao].value for acao in acoes}
                for estado in estados
            }

            # Salva os valores em um arquivo JSON
            with open('q_table_input.json', 'w') as f:
                json.dump(q_table_valores, f, indent=4)

            # Obtém os valores de epsilon
            epsilon = campo_epsilon.value

            # Limpa o container dinâmico
            container_dinamico.clear()

            try:
                # Executa o script externo
                # Carrega os resultados dos arquivos gerados
                with open('htmlsFolder/q_table.html', 'r', encoding='utf-8') as f:
                    q_table_html = f.read()
                with open('htmlsFolder/historico.html', 'r', encoding='utf-8') as f:
                    historico_html = f.read()

            except FileNotFoundError:
                ui.notify('Arquivos HTML não encontrados. Verifique a execução do script.')

        # Botões para executar e voltar ao menu
        ui.button('Voltar ao Menu', on_click=lambda: mostrar_tela(container_menu)).classes('mt-4')

        # Contêiner dinâmico para exibir os resultados
        container_dinamico = ui.column()

def criar_menu():
    global container_menu

    with container_menu:
        mensagem = random.choice(mensagens_menu)
        ui.image(caminho_imagem_menu).classes('w-1/2 mx-auto mb-4')
        ui.label(mensagem).classes('text-h4')
        ui.button('Exibir Tabela', on_click=lambda: mostrar_tela(container_tela1)).classes('mt-4')
        ui.button('Alterar recompensas', on_click=lambda: mostrar_tela(container_tela2)).classes('mt-4')
        ui.button('Alterar epsilon', on_click=lambda: mostrar_tela(container_tela3)).classes('mt-4')

# Contêineres principais para as telas
container_menu = ui.column().style('display: flex')
container_tela1 = ui.column().style('display: none')
container_tela2 = ui.column().style('display: none')
container_tela3 = ui.column().style('display: none')

# Cria cada tela
criar_menu()
criar_tela1()
criar_tela2()
criar_tela3()
# Executa a interface
ui.run()
