import os
import webbrowser
from threading import Timer
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# 1. Carregar os dados
caminho_csv = r'C:\Users\gasiq\Documents\Aula Python\visualizacao_dados_avancada\cleaned\ecommerce_estatistica.csv'
df = pd.read_csv(caminho_csv)

# Inicializar a aplicação Dash
app = Dash(__name__)

# Preparar opções únicas de Gênero para o filtro interativo
generos_disponiveis = ['Todos'] + sorted(df['Gênero'].dropna().unique().tolist())

# 2. Layout da Aplicação Web
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'margin': '20px', 'backgroundColor': '#f9f9f9', 'padding': '20px'}, children=[
    html.H1("Dashboard Interativo - Estatísticas de E-commerce", style={'textAlign': 'center', 'color': '#333'}),
    
    # Filtro interativo (alimenta o Input do Callback)
    html.Div(style={'width': '40%', 'margin': '0 auto 30px auto'}, children=[
        html.Label("Filtrar por Gênero:", style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='filtro-genero',
            options=[{'label': g, 'value': g} for g in generos_disponiveis],
            value='Todos',
            clearable=False
        )
    ]),

    # Linha 1: Histograma e Dispersão 3D
    html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-between'}, children=[
        html.Div(dcc.Graph(id='grafico-histograma'), style={'width': '49%', 'marginBottom': '20px'}),
        html.Div(dcc.Graph(id='grafico-dispersao-3d'), style={'width': '49%', 'marginBottom': '20px'}),
    ]),

    # Linha 2: Mapa de Calor e Gráfico de Barras
    html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-between'}, children=[
        html.Div(dcc.Graph(id='grafico-heatmap'), style={'width': '49%', 'marginBottom': '20px'}),
        html.Div(dcc.Graph(id='grafico-barras'), style={'width': '49%', 'marginBottom': '20px'}),
    ]),

    # Linha 3: Gráfico de Pizza e Densidade
    html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-between'}, children=[
        html.Div(dcc.Graph(id='grafico-pizza'), style={'width': '49%', 'marginBottom': '20px'}),
        html.Div(dcc.Graph(id='grafico-densidade'), style={'width': '49%', 'marginBottom': '20px'}),
    ]),

    # Linha 4: Gráfico de Regressão (Largura total)
    html.Div(style={'width': '100%'}, children=[
        dcc.Graph(id='grafico-regressao')
    ])
])

# 3. Callback para atualizar todos os gráficos interativamente
@app.callback(
    [
        Output('grafico-histograma', 'figure'),
        Output('grafico-dispersao-3d', 'figure'),
        Output('grafico-heatmap', 'figure'),
        Output('grafico-barras', 'figure'),
        Output('grafico-pizza', 'figure'),
        Output('grafico-densidade', 'figure'),
        Output('grafico-regressao', 'figure')
    ],
    [Input('filtro-genero', 'value')]
)
def atualizar_graficos(genero_selecionado):
    # Filtragem dos dados
    if genero_selecionado == 'Todos':
        dff = df.copy()
    else:
        dff = df[df['Gênero'] == genero_selecionado]

    # 1. Histograma (Frequência de Notas)
    fig_hist = px.histogram(
        dff.dropna(subset=['Nota']),
        x='Nota',
        nbins=10,
        title='Histograma - Frequência de Notas dos Produtos',
        color_discrete_sequence=['green']
    )
    fig_hist.update_traces(marker_line_color='black', marker_line_width=1, opacity=0.8)
    fig_hist.update_layout(yaxis_title='Frequência')

    # 2. Gráfico de Dispersão 3D (Nota x Preço x Desconto)
    dados_3d = dff[['Nota', 'Preço', 'Desconto', 'Gênero']].dropna()
    fig_3d = px.scatter_3d(
        dados_3d,
        x='Nota',
        y='Preço',
        z='Desconto',
        color='Gênero',
        opacity=0.7,
        title='Dispersão 3D: Nota, Preço e Desconto'
    )

    # 3. Mapa de Calor (Correlação Nota, Preço e Desconto)
    dados_corr = dff[['Nota', 'Preço', 'Desconto']].dropna().corr()
    fig_heatmap = px.imshow(
        dados_corr,
        text_auto='.2f',
        color_continuous_scale='RdBu_r',
        zmin=-1, zmax=1,
        title='Mapa de Calor - Correlação entre Variáveis'
    )

    # 4. Gráfico de Barras Horizontais (Vendas por Gênero)
    dados_bar = df[['Gênero', 'Qtd_Vendidos_Cod']].dropna()
    vendas_genero = dados_bar.groupby('Gênero', as_index=False)['Qtd_Vendidos_Cod'].sum()
    fig_barras = px.bar(
        vendas_genero,
        x='Qtd_Vendidos_Cod',
        y='Gênero',
        orientation='h',
        title='Quantidade de Vendas por Gênero (Total Geral)',
        color_discrete_sequence=['#a770ee']
    )
    fig_barras.update_layout(xaxis_title='Qtd_Vendidos')

    # 5. Gráfico de Pizza (Distribuição por Temporada)
    dados_pizza = dff['Temporada'].dropna().value_counts().reset_index()
    dados_pizza.columns = ['Temporada', 'Contagem']
    fig_pizza = px.pie(
        dados_pizza,
        names='Temporada',
        values='Contagem',
        title='Distribuição de Produtos por Temporada'
    )
    fig_pizza.update_traces(textposition='inside', textinfo='percent+label')

    # 6. Gráfico de Densidade (Representado via Histograma Marginal / Violino em Plotly Express)
    fig_densidade = px.violin(
        dff.dropna(subset=['Desconto']),
        x='Desconto',
        box=True,
        points=False,
        title='Distribuição e Densidade de Descontos',
        color_discrete_sequence=['#863e9c']
    )

    # 7. Gráfico de Regressão (Preço vs Desconto com linha de tendência OLS)
    dados_reg = dff[['Desconto', 'Preço']].dropna()
    fig_regressao = px.scatter(
        dados_reg,
        x='Desconto',
        y='Preço',
        trendline='ols',
        opacity=0.45,
        title='Regressão Linear: Preço vs Desconto',
        color_discrete_sequence=['#adc234']
    )
    fig_regressao.update_traces(line=dict(color='#5d278f', width=3), selector=dict(mode='lines'))
    fig_regressao.update_layout(yaxis_title='Preço (R$)')

    return fig_hist, fig_3d, fig_heatmap, fig_barras, fig_pizza, fig_densidade, fig_regressao

# Função para abrir o navegador automaticamente sem duplicar abas no modo debug
def abrir_navegador():
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new("http://127.0.0.1:8050/")

if __name__ == '__main__':
    Timer(1, abrir_navegador).start()
    app.run(debug=True, use_reloader=False, port=8050)

    # FIM DO SCRIPT