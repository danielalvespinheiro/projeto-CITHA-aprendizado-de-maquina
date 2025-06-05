from nicegui import ui
import subprocess

# Contêiner global para armazenar a exibição dinâmica
container_dinamico = None

def executar_e_exibir():
    global container_dinamico

    # Obtém o número de episódios do campo de entrada
    num_episodios = campo_episodios.value
    if num_episodios is None or num_episodios < 100:
        ui.notify('Por favor, insira um número inteiro maior ou igual a 100.')
        return

    # Limpa o conteúdo anterior, se existir
    if container_dinamico:
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
            ui.label('Tabela de Resultados:').classes('text-h5')
            ui.html(q_table_html).classes('w-full overflow-auto')
            ui.label('Histórico de Decisões (últimos 10)').classes('text-h5 mt-4')
            ui.html(historico_html).classes('w-full overflow-auto')

    except subprocess.CalledProcessError as e:
        ui.notify(f'Erro ao executar o script: {e}')
    except FileNotFoundError:
        ui.notify('Arquivos HTML não encontrados. Verifique se o script foi executado corretamente.')

# Contêiner inicial para organizar a interface
with ui.column() as container_principal:
    ui.label('Digite o número de episódios:')
    campo_episodios = ui.number(label='Número de episódios', value=100, min=100).classes('w-full')
    ui.button('Executar Algoritmo e Exibir Resultados', on_click=executar_e_exibir)
    # Define o contêiner dinâmico
    container_dinamico = ui.column()

# Executa a interface
ui.run()
