import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("dados.csv", sep=';', decimal=',')

df.rename(columns={
'chuva_durante_floração_mm': 'chuva_flor',
'chuva_durante_colheita_mm': 'chuva_colheita',
'chuva_total_anual_mm': 'chuva_total',
'anomalia_chuva_floração_mm': 'anomalia_flor',
'temperatura_média_floração_C': 'temp_flor',
'umidade_relativa_média_floração_%': 'umid_flor',
'evento_ENSO': 'ENSO',
'produtividade_kg_por_ha': 'produtividade',
'produtividade_safra': 'safra'
}, inplace=True)

df['umid_flor'] = df['umid_flor'] / 100
df.set_index('ano', inplace=True)
df.head()

# Ver informações gerais do dataframe
# df.info()
# Verificar valores ausentes
# print("\nValores ausentes por coluna:")
# df.isnull().sum()
# Resumo estatístico
# df.describe().T

def ensoPordu():
    sns.set(style="whitegrid", palette="colorblind")
    sns.boxplot(
    data=df,
    x='ENSO',
    y='produtividade',
    order=['La Niña', 'Neutro', 'El Niño']
    )
    plt.title('Produtividade vs. Evento ENSO', fontsize=14)
    plt.xlabel('Evento ENSO', fontsize=12)
    plt.ylabel('Produtividade (kg/ha)', fontsize=12)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.tight_layout()
    plt.show()

# ensoPordu()

def tempProdut():
    sns.scatterplot(data=df, x='temp_flor', y='produtividade', \
                    hue='ENSO', s=80, alpha=0.8)
    plt.title('Temperatura durante floração vs. Produtividade', fontsize=14)
    plt.xlabel('Temperatura média durante floração (°C)', fontsize=12)
    plt.ylabel('Produtividade (kg/ha)', fontsize=12)
    plt.legend(title='Evento ENSO')
    df.select_dtypes(include='number').hist(bins=15, figsize=(12,8))
    plt.suptitle("Distribuições das variáveis numéricas")
    plt.show()

tempProdut()