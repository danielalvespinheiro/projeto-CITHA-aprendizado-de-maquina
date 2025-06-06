import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import seaborn as sns 

df = pd.read_csv('dados.csv', delimiter=';', decimal=',', encoding= 'UTF-8') 

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
#df.info() 

# Verificar valores ausentes 
# print("\nValores ausentes por coluna:") 
# print(df.isnull().sum())

# Resumo estatístico 
df.describe().T

def GerarGrafico1():
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

def GerarGrafico2():

    sns.scatterplot(data=df, x='temp_flor', y='produtividade', hue='ENSO', s=80, alpha=0.8) 
    plt.title('Temperatura durante floração vs. Produtividade', fontsize=14) 
    plt.xlabel('Temperatura média durante floração (°C)', fontsize=12) 
    plt.ylabel('Produtividade (kg/ha)', fontsize=12) 
    plt.legend(title='Evento ENSO')
    plt.tight_layout()
    plt.show() 

def GerarGrafico3():
    df.select_dtypes(include='number').hist(bins=15, figsize=(12,8)) 
    plt.suptitle("Distribuições das variáveis numéricas") 
    plt.show()

def GerarGrafico4():
    # Seleciona só as colunas numéricas relevantes 
    variaveis_numericas = df.select_dtypes(include='number') 
    # Calcula a matriz de correlação 
    correlacao = variaveis_numericas.corr() 
    # Heatmap 
    plt.figure(figsize=(10, 6)) 
    sns.heatmap( 
    correlacao, 
    annot=True, 
    fmt=".2f", 
    cmap='coolwarm', 
    linewidths=0.5, 
    square=True, 
    cbar_kws={"shrink": .8}, 
    vmin=-1, vmax=1 
    ) 
    plt.title('Matriz de Correlação entre Variáveis Numéricas') 
    plt.tight_layout() 
    plt.show()

def GerarGrafico5():
    # Seleciona as variáveis numéricas (sem o ano) 
    cols_plot = ['chuva_flor', 'chuva_colheita', 'chuva_total','anomalia_flor', 'temp_flor', 'umid_flor', 'produtividade'] 
    # Pairplot 
    sns.pairplot( 
    df[cols_plot], 
    corner=True, 
    # evita duplicação acima/abaixo da diagonal 
    diag_kind='hist', # ou 'kde' 
    plot_kws={'alpha': 0.7, 's': 40, 'edgecolor': 'k'} 
    ) 
    plt.suptitle("Matriz de Dispersão entre Variáveis", fontsize=14, y=1.02) 
    plt.show()

# 1. Chuva relativa durante floração 
df['chuva_relativa'] = df['chuva_flor'] / df['chuva_total'] 
 # 2. Binário: anomalia positiva ou não 
df['anomalia_bin'] = (df['anomalia_flor'] > 0).astype(int) 

 # 3. Codificar ENSO como variáveis dummies 
df = pd.get_dummies(df, columns=['ENSO'], drop_first=True) # cria ENSO_El Niño e ENSO_La Niña 
df.head(10)  
df.filter(like='ENSO').tail(10)

# 1. Definindo X e y
X = df.drop(columns=['produtividade', 'safra']) # safra é para classificação
y = df['produtividade'] 

# Lista de colunas numéricas
colunas_numericas = ['chuva_flor', 'chuva_colheita', 'chuva_total','anomalia_flor', 'temp_flor', 'umid_flor', 'chuva_relativa'] 

# Lista de colunas binárias
colunas_binarias = ['anomalia_bin', 'ENSO_La Niña', 'ENSO_Neutro'] 

from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
# 3. Criando o transformador
preprocessador = ColumnTransformer(transformers=[('num', StandardScaler(),
colunas_numericas),('bin', 'passthrough', colunas_binarias)]) 

from sklearn.model_selection import train_test_split
# 4. Separando treino e teste sem embaralhar (respeitando ordem temporal)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False) 

from sklearn.decomposition import PCA
# Aplica o ColumnTransformer (padronização)
X_padronizado = preprocessador.fit_transform(X)
# Aplica PCA com todos os componentes (não limita n_components ainda)
pca_full = PCA()
pca_full.fit(X_padronizado)
# Scree Plot

def GerarGrafico6():
    plt.plot(range(1, len(pca_full.explained_variance_ratio_)+1),
    pca_full.explained_variance_ratio_, marker='o')
    plt.title('Scree Plot - Variância Explicada por Componente')
    plt.xlabel('Componente Principal')
    plt.ylabel('Proporção da Variância')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    # Mostrar numericamente
    for i, v in enumerate(pca_full.explained_variance_ratio_):
        print(f"PC{i+1}: {v:.2%}") 

# Aplica PCA com 2 componentes
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_padronizado)

# Cria df_PCA com componentes e variáveis-alvo
df_PCA = pd.DataFrame(X_pca, columns=['PC1', 'PC2'], index=X.index)
df_PCA['produtividade'] = df['produtividade']
df_PCA['safra'] = df['safra']

def GerarGrafico7():
    sns.scatterplot(data=df_PCA, x='PC1', y='PC2', hue='safra', s=80, alpha=0.8)
    plt.title('PCA - Componentes Principais coloridos por Safra')
    plt.xlabel('Componente Principal 1')
    plt.ylabel('Componente Principal 2')
    plt.legend(title='Safra')
    plt.tight_layout()
    plt.show() 

from sklearn.linear_model import LinearRegression, Ridge
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error, r2_score 

# Pipeline: pré-processador + modelo
pipeline_original = make_pipeline(preprocessador, LinearRegression())
# Treinamento
pipeline_original.fit(X_train, y_train)
# Previsão
y_pred_orig = pipeline_original.predict(X_test)
# Avaliação
mse_orig = mean_squared_error(y_test, y_pred_orig)
rmse_orig = mse_orig ** 0.5
r2_orig = r2_score(y_test, y_pred_orig)

# print(f"[Regressão linear] RMSE: {rmse_orig:.2f} | R²: {r2_orig:.2%}") 

# Pipeline com regularização L2 (Ridge)
lambda_regressao = 1 # testar vários valores para lambda
pipeline_ridge = make_pipeline(preprocessador, Ridge(alpha=lambda_regressao)) 

# Treinamento
pipeline_ridge.fit(X_train, y_train)
# Previsão
y_pred_ridge = pipeline_ridge.predict(X_test)
# Avaliação
mse_ridge = mean_squared_error(y_test, y_pred_ridge)
rmse_ridge = mse_ridge ** 0.5
r2_ridge = r2_score(y_test, y_pred_ridge)

# print(f"[Regularização Ridge (L²) | λ = {lambda_regressao}] RMSE:{rmse_ridge:.2f} | R²: {r2_ridge:.2%}")

# Definindo X e y com base no df_PCA
X_pca = df_PCA[['PC1', 'PC2']]
y_pca = df_PCA['produtividade']
# Divisão temporal (como fizemos antes)
X_pca_train, X_pca_test, y_pca_train, y_pca_test = train_test_split(X_pca,
y_pca, test_size=0.2, shuffle=False)
# Modelo linear simples com PCA
modelo_pca = LinearRegression()
modelo_pca.fit(X_pca_train, y_pca_train)
# Previsão
y_pred_pca = modelo_pca.predict(X_pca_test)
# Avaliação
rmse_pca = mean_squared_error(y_pca_test, y_pred_pca) ** 0.5
r2_pca = r2_score(y_pca_test, y_pred_pca)

# print(f"[PCA + Regressão linear] RMSE: {rmse_pca:.2f} | R²: {r2_pca:.2%}")

# Modelo com Ridge sobre PCA
lambda_regressao = 1 # testar vários valores para lambda
modelo_pca_ridge = Ridge(alpha=lambda_regressao)
modelo_pca_ridge.fit(X_pca_train, y_pca_train)
# Previsão
y_pred_pca_ridge = modelo_pca_ridge.predict(X_pca_test)
# Avaliação
rmse_pca_ridge = mean_squared_error(y_pca_test, y_pred_pca_ridge) ** 0.5
r2_pca_ridge = r2_score(y_pca_test, y_pred_pca_ridge)

# print(f"[PCA + Regularização Ridge (L²) | λ = {lambda_regressao}] RMSE:{rmse_pca_ridge:.2f} | R²: {r2_pca_ridge:.2%}") 

# Simulação dos dados para plotagem
lambdas = [0.1, 1, 10, 100, 1000, 10000, 30000, 100000, 300000, 1000000]
def GerarGrafico8():
    rmse_sem_pca = [71.19, 68.30, 54.97, 34.91, 26.38, 25.61, 25.56, 25.55,25.54, 25.54]
    rmse_com_pca = [43.25, 42.98, 40.61, 31.20, 25.97, 25.57, 25.55, 25.54, 25.54, 25.54]
    plt.plot(lambdas, rmse_sem_pca, marker='o', label='Sem PCA')
    plt.plot(lambdas, rmse_com_pca, marker='s', label='Com PCA')
    plt.xscale('log')
    plt.xlabel("λ (log scale)")
    plt.ylabel("RMSE")
    plt.title("Comparação do RMSE em função de λ (Ridge)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show() 

def GerarGrafico9():
    # R² para cada lambda (sem e com PCA)
    r2_sem_pca = [-8.48, -7.72, -4.65, -1.28, -0.30, -0.23, -0.2221, -0.2206, -0.2201, -0.2200]
    r2_com_pca = [-2.50, -2.45, -2.08, -0.82, -0.2616, -0.2230, -0.2209, -0.2202,-0.2200, -0.2199]
    plt.plot(lambdas, r2_sem_pca, marker='o', label='Sem PCA')
    plt.plot(lambdas, r2_com_pca, marker='s', label='Com PCA')
    plt.xscale('log')
    plt.xlabel("λ (log scale)")
    plt.ylabel("R²")
    plt.title("Comparação do R² em função de λ (Ridge)")
    plt.grid(True) 
    plt.legend()
    plt.tight_layout()
    plt.show() 

def plot_modelos_para_variavel(x_var, X, y, scaler, pca_model, modelo_linear,
                               modelo_ridge, modelo_pca, modelo_pca_ridge):
    
    x_index = X.columns.get_loc(x_var)
    x_vals = np.linspace(X[x_var].min(), X[x_var].max(), 100)
    X_mean = X.mean().to_numpy()
    X_input = np.tile(X_mean, (100, 1))
    X_input[:, x_index] = x_vals
    X_input_df = pd.DataFrame(X_input, columns=X.columns) # ⬅ usa os mesmos nomes
    X_input_scaled = scaler.transform(X_input_df)
    X_input_pca = pca_model.transform(X_input_scaled)

    y_linear = modelo_linear.predict(X_input_scaled)
    y_ridge = modelo_ridge.predict(X_input_scaled)
    y_pca = modelo_pca.predict(X_input_pca)
    y_pca_ridge = modelo_pca_ridge.predict(X_input_pca)

    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=X[x_var], y=y, color='red', label='Dados reais', s=50, edgecolor='black')

    plt.plot(x_vals, y_linear, label='Linear', linestyle='-', color='blue')
    plt.plot(x_vals, y_ridge, label='Ridge (λ=1.000.000)', linestyle='--', color='orange')
    plt.plot(x_vals, y_pca, label='PCA + Linear', linestyle='-.', color='green')
    plt.plot(x_vals, y_pca_ridge, label='PCA + Ridge (λ=100.000)', linestyle=':', color='purple')

    plt.xlabel(x_var)
    plt.ylabel('Produtividade (kg/ha)')
    plt.title(f'Comparação de modelos — {x_var}')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# 1. Reconstrução de X e y
X = df[[
'chuva_flor', 'chuva_colheita', 'chuva_total',
'anomalia_flor', 'temp_flor', 'umid_flor', 'chuva_relativa'
]]
y = df['produtividade']

# 2. Padronização
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 3. PCA
pca_model = PCA(n_components=2)
X_pca = pca_model.fit_transform(X_scaled)

# Converte o array PCA em DataFrame com nomes
df_pca = pd.DataFrame(X_pca, columns=['PC1', 'PC2'], index=df.index)
df[['PC1', 'PC2']] = df_pca

# 4. Modelos treinados separadamente
modelo_linear = LinearRegression().fit(X_scaled, y)
modelo_ridge = Ridge(alpha=1e6).fit(X_scaled, y)
modelo_pca = LinearRegression().fit(X_pca, y)
modelo_pca_ridge = Ridge(alpha=1e5).fit(X_pca, y)

# ATENÇÃO AQUI É A FORMA DE PLOTAR A FUNÇÃO MODELOS PARA VARIÁVEIS
# plot_modelos_para_variavel('temp_flor', X, y, scaler, pca_model, modelo_linear, modelo_ridge, modelo_pca, modelo_pca_ridge) 

#### Curva 1D da função custo
def plot_funcao_custo_1D(x_var, X, y, intervalo=(-200, 200), pontos=200):
    """
    Plota a função de custo J(θ₁) para uma regressão univariada com a
    variável x_var.
    """
    x = X[x_var].values
    y = y.values
    m = len(y)

    # Centraliza x para eliminar o intercepto implicitamente
    x_centralizado = x - x.mean()
    theta1_vals = np.linspace(intervalo[0], intervalo[1], pontos)
    custos = [(1 / (2 * m)) * np.sum((theta1 * x_centralizado - y) ** 2) for theta1 in theta1_vals]

    plt.figure(figsize=(8, 5))
    plt.plot(theta1_vals, custos)
    plt.xlabel("θ₁")
    plt.ylabel("J(θ₁)")
    plt.title(f"Função de Custo - {x_var} (x centralizado)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# FORMA DE PLOTAR A FUNÇÃO CUSTO 1D
# plot_funcao_custo_1D('temp_flor', X, y) 

"""#### Superfície 2D da função custo"""
from itertools import combinations
from mpl_toolkits.mplot3d import Axes3D
def plot_funcao_custo_2D(x_vars, X, y, range_theta=(-200, 200), pontos=100):
    """
    Plota a superfície da função de custo J(θ₁, θ₂) para duas variáveis.
    """
    x1 = X[x_vars[0]].values
    x2 = X[x_vars[1]].values
    y = y.values
    m = len(y)

    # Matriz de entrada com intercepto
    X_mat = np.vstack([np.ones(m), x1, x2]).T

    # Geração de grid de θ₁ e θ₂ (intercepto θ₀ fixado em 0 para simplificação)
    theta1_vals = np.linspace(range_theta[0], range_theta[1], pontos)
    theta2_vals = np.linspace(range_theta[0], range_theta[1], pontos)

    J_vals = np.zeros((pontos, pontos))
    for i in range(pontos):
        for j in range(pontos):
            theta = np.array([0, theta1_vals[i], theta2_vals[j]]) # θ₀ = 0
            h = X_mat @ theta
            J_vals[j, i] = (1 / (2 * m)) * np.sum((h - y) ** 2)
    
    # Superfície
    T1, T2 = np.meshgrid(theta1_vals, theta2_vals)
    fig = plt.figure(figsize=(10, 6))

    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(T1, T2, J_vals, cmap='viridis', edgecolor='none', alpha=0.9)
    ax.set_xlabel(f"θ₁ ({x_vars[0]})")
    ax.set_ylabel(f"θ₂ ({x_vars[1]})")
    ax.set_zlabel("J(θ)")
    ax.set_title(f"Superfície da Função de Custo — {x_vars[0]} e {x_vars[1]}")

    plt.tight_layout()
    fig.subplots_adjust(right=0.5)
    plt.show()

# FUNÇÃO PARA PLOTAR O CUSTO 2D
# plot_funcao_custo_2D(['temp_flor', 'chuva_flor'], X, y)

"""#### Superfície 2D da função custo com PCA"""
def plot_funcao_custo_2D_PCA(X_pca, y, range_theta=(-200, 200), pontos=100):
    """
    Plota a superfície da função de custo J(θ₁, θ₂) usando os componentes
    principais PC1 e PC2.
    39
    """
    pc1 = X_pca[:, 0]
    pc2 = X_pca[:, 1]
    m = len(y)

    # Matriz de entrada com intercepto
    X_mat = np.vstack([np.ones(m), pc1, pc2]).T

    # Grid de valores de θ₁ e θ₂
    theta1_vals = np.linspace(range_theta[0], range_theta[1], pontos)
    theta2_vals = np.linspace(range_theta[0], range_theta[1], pontos)
    J_vals = np.zeros((pontos, pontos))

    for i in range(pontos):
        for j in range(pontos):
            theta = np.array([0, theta1_vals[i], theta2_vals[j]])
            h = X_mat @ theta
            J_vals[j, i] = (1 / (2 * m)) * np.sum((h - y) ** 2)

    # Superfície 3D
    T1, T2 = np.meshgrid(theta1_vals, theta2_vals)
    fig = plt.figure(figsize=(10, 6))

    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(T1, T2, J_vals, cmap='viridis', edgecolor='none', alpha=0.9)
    ax.set_xlabel("θ₁ (PC1)")
    ax.set_ylabel("θ₂ (PC2)")
    ax.set_zlabel("J(θ)")
    ax.set_title("Superfície da Função de Custo — Componentes Principais (PCA)")

    fig.subplots_adjust(right=0.85)
    plt.show()

# FUNÇÃO PARA PLOTAR O CUSTO 2D PCA (ELE É 3D E PODEMOS MECHER NELE)
# plot_funcao_custo_2D_PCA(X_pca, y)
"""
Fique Alerta!
Repare que a superfície da função de custo no espaço PC1 × PC2 é
quase simétrica, isso acontece porque o PCA gera variáveis ortogonais
entre si, o que elimina a multicolinearidade e como resultado, o
gradiente desce de forma mais eficiente, sem precisar "ziguezaguear"
por vales inclinados. 
"""

def plot_residuos(y_true, y_pred, titulo):
    """
    Plota os resíduos de um modelo específico.
    """
    residuos = y_true - y_pred
    plt.figure(figsize=(8, 4))
    plt.scatter(y_pred, residuos, color='royalblue', alpha=0.7)
    plt.axhline(0, color='red', linestyle='--')

    plt.xlabel("Previsão")
    plt.ylabel("Resíduo")

    plt.title(f"Resíduos — {titulo}")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    print("\n")

# FUNÇÃO DE PLOTE DE RESIDOS
# Previsões

# y_pred_linear = modelo_linear.predict(X_scaled)
# y_pred_ridge = modelo_ridge.predict(X_scaled)
# y_pred_pca = modelo_pca.predict(X_pca)
# y_pred_pca_ridge = modelo_pca_ridge.predict(X_pca)

 # Gráficos de resíduos

# plot_residuos(y, y_pred_linear, "Regressão Linear")
# plot_residuos(y, y_pred_ridge, "Regressão Regularizada (λ = 1.000.000)")
# plot_residuos(y, y_pred_pca, "PCA + Regressão Linear")
# plot_residuos(y, y_pred_pca_ridge, "PCA + Regularizada (λ = 100.000)") 

# 1. Mapeia a variável alvo (safra)
mapa_safra = {'baixa': 0, 'media': 1, 'alta': 2}
df['safra_num'] = df['safra'].map(mapa_safra)

# 2. Define variáveis preditoras (mesmas da regressão)
X_class = df[['chuva_flor', 'chuva_colheita', 'chuva_total', 'anomalia_flor', 'temp_flor', 'umid_flor', 'chuva_relativa']] 

y_class = df['safra_num']
# 3. Padronização
scaler_class = StandardScaler()
46
X_class_scaled = scaler_class.fit_transform(X_class)
# 4. PCA (opcional — será usado para um dos modelos)
pca_class = PCA(n_components=2)

X_class_pca = pca_class.fit_transform(X_class_scaled)

# 5. Divisão treino/teste
X_train_class, X_test_class, y_train_class, y_test_class = train_test_split(X_class_scaled, y_class, test_size=0.3, random_state=42, stratify=y_class)
X_train_pca, X_test_pca, _, _ = train_test_split(X_class_pca, y_class, test_size=0.3, random_state=42, stratify=y_class)

from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier

# 1. Modelo com variáveis originais
modelo_classico = OneVsRestClassifier(LogisticRegression(max_iter=1000))
modelo_classico.fit(X_train_class, y_train_class)

# 2. Modelo com PCA
modelo_pca_class = OneVsRestClassifier(LogisticRegression(max_iter=1000))
modelo_pca_class.fit(X_train_pca, y_train_class) 

from sklearn.metrics import confusion_matrix, accuracy_score, f1_score, classification_report

def plotar_curva_roc_multiclasse(y_true, y_score, classes, titulo="Modelo"):
    from sklearn.preprocessing import label_binarize
    from sklearn.metrics import roc_curve, auc
    from itertools import cycle

    y_bin = label_binarize(y_true, classes=classes)
    n_classes = y_bin.shape[1]
    fpr, tpr, roc_auc = {}, {}, {}

    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_bin[:, i], y_score[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])
        fpr["micro"], tpr["micro"], _ = roc_curve(y_bin.ravel(), y_score.ravel())
        roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])
    # Plot
    plt.figure(figsize=(8, 6))
    colors = cycle(['#1f77b4', '#ff7f0e', '#2ca02c'])

    for i, color in zip(range(n_classes), colors):
        plt.plot(fpr[i], tpr[i], color=color, lw=2, label=f'Classe {i} (AUC = {roc_auc[i]:.2f})')

    plt.plot(fpr["micro"], tpr["micro"], color='black', linestyle='--', label=f"Média micro (AUC = {roc_auc['micro']:.2f})")
    plt.plot([0, 1], [0, 1], 'k--', lw=1)

    plt.xlabel("Taxa de Falsos Positivos (FPR)")
    plt.ylabel("Taxa de Verdadeiros Positivos (TPR)")

    plt.title(f"Curva ROC Multiclasse — {titulo}")
    plt.legend(loc="lower right")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Função de avaliação completa
def avaliar_modelo_classificacao(nome, y_true, y_pred, y_prob=None, classes=[0, 1, 2]):
    # Matriz de confusão
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=['Baixa', 'Média', 'Alta'], yticklabels=['Baixa', 'Média', 'Alta'])
    plt.xlabel("Predito")
    plt.ylabel("Real")

    plt.title(f"Matriz de Confusão — {nome}", pad=12)
    plt.tight_layout()
    plt.show()
    
    # Métricas textuais
    print(f"\nAvaliação — {nome}")
    print("Acurácia:", accuracy_score(y_true, y_pred))
    print("F1-score (macro):", f1_score(y_true, y_pred, average='macro'))
    print("\nRelatório de Classificação:")
    print(classification_report(y_true, y_pred, target_names=['Baixa', 'Média', 'Alta'], zero_division=0))

    # Curva ROC (opcional)
    if y_prob is not None:
        plotar_curva_roc_multiclasse(y_true, y_prob, classes, titulo=nome) 


# Previsões e probabilidades
y_pred_classico = modelo_classico.predict(X_test_class)
y_prob_classico = modelo_classico.predict_proba(X_test_class)

# Avaliação completa
# FUNÇÃO PARA AVALIAR MODELO CLASSICO 
# avaliar_modelo_classificacao("Modelo Sem PCA", y_test_class, y_pred_classico, y_prob_classico) 

# Previsões e probabilidades com PCA
y_pred_pca = modelo_pca_class.predict(X_test_pca)
y_prob_pca = modelo_pca_class.predict_proba(X_test_pca) 

# Avaliação completa
# FUNÇÃO PARA AVALIAR MODELO COM PCA
# avaliar_modelo_classificacao("Modelo com PCA", y_test_class, y_pred_pca, y_prob_pca)

from matplotlib.colors import ListedColormap
def plot_fronteira_decisao_2D(X_pca, y_true, modelo, titulo="Fronteiras de Decisão (PCA)"):
    """
    Plota as fronteiras de decisão do modelo treinado no plano PC1 vs PC2.
    """
    h = 0.02 # Passo da malha 
    
    # Geração da malha de pontos
    x_min, x_max = X_pca[:, 0].min() - 1, X_pca[:, 0].max() + 1
    y_min, y_max = X_pca[:, 1].min() - 1, X_pca[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

    # Predição sobre a malha
    Z = modelo.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    # Paleta de cores
    cmap_light = ListedColormap(['#FFAAAA', '#AAFFAA', '#AAAAFF'])
    cmap_bold = ['red', 'green', 'blue']

    # Gráfico
    plt.figure(figsize=(8, 6))
    plt.contourf(xx, yy, Z, cmap=cmap_light, alpha=0.5)
    scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=y_true, cmap = ListedColormap(cmap_bold), edgecolor='k', s=60)

    plt.xlabel("PC1")
    plt.ylabel("PC2")

    plt.title(titulo)
    plt.legend(handles=scatter.legend_elements()[0], labels=['Baixa',  'Média', 'Alta'])
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
# Aplicar para os dados do PCA e o modelo treinado com PCA
plot_fronteira_decisao_2D(X_class_pca, y_class, modelo_pca_class, titulo="Fronteiras de Decisão — PCA + Regressão Logística") 
