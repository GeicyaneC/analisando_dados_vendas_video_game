import pandas as pd 
import plotly.express as px
from dash import Dash, dcc, html
from dash.dash_table import DataTable
from dash import Input, Output
import dash_bootstrap_components as dbc

df = pd.read_csv("C:/Users/GeicyanePereira/Desktop/analisando_dados_vendas_video_game/analise_video_game_tratado.csv")
app = Dash(external_stylesheets=[dbc.themes.CYBORG])


################################################ TRATAMENTOS ####################################################

#limpando dados ausentes
df = df.dropna(subset=['title', 'genre', 'console', 'developer'])

# Quais são os 10 jogos mais vendidos? Gráfico 1 
jogos_mais_vendidos = df.groupby(['title'])['total_sales'].sum().sort_values(ascending=False)
top_jogos = pd.DataFrame({'titulos': jogos_mais_vendidos.index, 'vendas': jogos_mais_vendidos.values})
top_10_jogos = top_jogos[0:10]
top_10_jogos = top_10_jogos.sort_values(by='titulos')
df_top_games = df[df['title'].isin(top_10_jogos['titulos'].unique())] #dataframe original isin (verifica se o valor de uma coluna está presente em um conjunto). Fazer um comparativo com o dataframe original com o dataframe criado, vai retornar uma lista de true ou false
df_top_games = df_top_games.sort_values(by='title').head(12)

# Como foi a venda de jogos por ano para as distribuidoras que mais venderam?
df['year'] = pd.to_datetime(df['release_date']).dt.year
pub_vendas_por_ano = df.groupby(['publisher', 'year']).agg({'total_sales': 'sum'}).reset_index()
pub_vendas = pub_vendas_por_ano.groupby('publisher').sum('total_sales').reset_index()
top_pub = pub_vendas_por_ano[pub_vendas_por_ano['publisher'].isin(pub_vendas[pub_vendas['total_sales'] > 100]['publisher'].values)]

# Como variam as notas de acordo com o gênero?
popular_genres = df[df['genre'].isin(['Action', 'Adventure', 'Role-Playing', 'Shooter', 'Platform'])]

# Como varia o número de vendas dos jogos em cada região?
popular_platforms = df[df['console'].isin(['PS3', 'PS4', 'X360', 'XOne', 'Wii', 'WiiU', 'PC'])]

#################################### GRÁFICOS ############################################################

# A nota de um jogo influencia as suas vendas?
fig3 = px.scatter(df, x='critic_score', y='total_sales', color='console', hover_data=['title'], labels={
        'total_sales': 'Total de Vendas',
        'critic_score': 'Faixa de Notas dos Jogos',
        'console': 'Console'
    })

fig4 = px.histogram(
    popular_genres, x='critic_score',
    color='genre', title='Histograma Notas de Jogos por Gênero',
    nbins=10, barmode='group', histnorm='probability density',
    labels={
        'critic_score': 'Faixa de Notas dos Jogos',
        'genre': 'Gênero'
    }
)

fig5 = px.box(
    popular_platforms, y=['na_sales', 'pal_sales', 'other_sales', 'jp_sales'],
    hover_data=['title'], color='console', title='Boxplots Vendas por Região',
    labels={
        'value': 'Total de Vendas em Milhões',
        'variable': 'Região'
    }
)

# Criar gráfico de pizza para a coluna 'title'
counts_title = df['title'].value_counts().head(10).reset_index()
counts_title.columns = ["title", "count"]
fig6 = px.pie(counts_title, names="title", values="count", title="Top 10 Jogos")

# Criar gráfico de rosca para a coluna 'genre'
cores_personalizadas = ['#FF5733', '#33FF57', '#3357FF', '#F033FF', '#FF8C00']
counts_genre = df['genre'].value_counts().head(5).reset_index()
counts_genre.columns = ["genre", "count"]
fig7 = px.pie(counts_genre, names="genre", values="count", title="Top 5 Gêneros", hole=0.5, color_discrete_sequence=cores_personalizadas )

#top 5 console
counts_console = df['console'].value_counts().head(5).reset_index()
counts_console.columns = ["console","count"]
fig8 = px.pie(counts_console, names="console", values="count", title="Top 5 Plataformas", hole=0.5)

#top 10 developer
counts_developer = df['developer'].value_counts().head(10).reset_index()
counts_developer.columns = ["developer", "count"]
fig9 = px.pie(counts_developer, names="developer", values="count", title="Top 10 Fabricantes")



######################### Gráfico 1 com Filtro ##################################

@app.callback(
    Output('sales-chart', 'figure'),  # Atualiza o gráfico
    Input('multi-filter', 'value')  # Obtém o valor selecionado no filtro
)
def update_sales_chart(selected_console):
    # Filtra os dados pelo console selecionado
    if selected_console:
        filtered_data = df_top_games[df_top_games['console'].isin(selected_console)]
    else:
        filtered_data = df_top_games  # Mostra todos os dados se nenhum console for selecionado

    # Recria o gráfico com os dados filtrados
    fig1 = px.bar(
        filtered_data,
        x='title', 
        y='total_sales', 
        color='console', 
        title=f"{'Jogos Mais Vendidos por Consoles' if not selected_console else selected_console}",
        labels={
            "total_sales": "Total de Vendas em Milhões",
            "title": "Jogo",
            "console": "Plataforma"
        }
    )
    
    # Estilização do gráfico
    fig1.update_layout(
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='white'),
    )
    
    return fig1

############################ Gráfico 2 com Filtro #######################################

# Callback para atualizar o gráfico de vendas por publisher
@app.callback(
    Output('sales-chart-publisher', 'figure'),  # Atualiza o gráfico de vendas por publisher
    [Input('multi-filter-publisher', 'value')]  # Obtém a seleção dos publishers
)
def update_sales_chart_publisher(selected_publishers):
    # Filtra os dados de acordo com os publishers selecionados
    filtered_data = top_pub

    if selected_publishers:
        filtered_data = filtered_data[filtered_data['publisher'].isin(selected_publishers)]

    # Cria o gráfico para os dados filtrados
    fig2 = px.line(
        filtered_data,
        x='year',
        y='total_sales',
        color='publisher',
        title=f"{'Jogos Mais Vendidos por Distribuidoras' if not selected_publishers else ', '.join(selected_publishers)}",
        labels={"total_sales": "Total de Vendas em Milhões", "year": "Ano"}
    )

    # Personaliza o layout
    fig2.update_layout(
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='white'),
    )

    return fig2
####################################################################

app.layout = html.Div([
    html.H2("Análise Estratégica das Vendas de Games", style={'color': 'white', 'text-align': 'center', 'font-family': 'Trebuchet MS'}),
    
    dcc.Tabs([
        dcc.Tab(label='Vendas de Jogos', children=[
            dbc.Row([ 
                dbc.Col(dcc.Dropdown(
                    id='multi-filter',
                    options=[{'label': console, 'value': console} for console in df_top_games['console'].unique()],
                    value=[],
                    multi=True,  # Permite seleção múltipla
                    placeholder="Selecione uma ou mais Plataformas",
                    searchable=True,  # Permite pesquisa dentro da lista
                    style={
                        "width": "100%",
                        "backgroundColor": "#333",
                        "color": "black",
                        "border": "1px solid #555",
                        "border-radius": "5px",
                        "box-shadow": "none",
                    },
                ),width=6),
                dbc.Col(dcc.Dropdown(
                    id='multi-filter-publisher',
                    options=[{'label': publisher, 'value': publisher} for publisher in top_pub['publisher'].unique()],
                    value=[],  # Valor inicial, nenhum publisher selecionado
                    multi=True,
                    placeholder="Selecione uma ou mais Distribuidoras",
                    searchable=True,  # Permite pesquisa dentro da lista
                    style={
                        "width": "100%",
                        "backgroundColor": "#333",
                        "color": "black",
                        "border": "1px solid #555",
                        "border-radius": "5px",
                        "box-shadow": "none",
                    },
                ),width=6),
            ], style={"margin-bottom": "40px"}),
            dcc.Graph(id='sales-chart', style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
            dcc.Graph(id='sales-chart-publisher', style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
            dcc.Graph(figure=fig5)
        ]),
        
        dcc.Tab(label='Notas e Gêneros', children=[
            dcc.Graph(figure=fig3),
            dcc.Graph(figure=fig4)
        ]),
        
        dcc.Tab(label='Distribuições', children=[
            dcc.Graph(figure=fig6, style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
            dcc.Graph(figure=fig7, style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
            dcc.Graph(figure=fig8, style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
            dcc.Graph(figure=fig9, style={'width': '50%', 'display': 'inline-block', 'padding': '10px'})
        ])
    ], style={
        'color': 'white',
        'border': 'none',
        'font-family': 'Trebuchet MS'
    },
colors={
    "border": "#555",  # Cor da borda ao redor das abas
    "primary": "#222",  # Cor da aba ativa
    "background": "#444"  # Cor das abas inativas
})
])

# Alterar a cor do fundo do gráfico

fig3.update_layout(
    paper_bgcolor='black',
    plot_bgcolor='black',
    font=dict(color='white'),
)

fig4.update_layout(
    paper_bgcolor='black',
    plot_bgcolor='black',
    font=dict(color='white'),
)

fig5.update_layout(
    paper_bgcolor='black',
    plot_bgcolor='black',
    font=dict(color='white'),
)

fig6.update_layout(
    paper_bgcolor='black',
    plot_bgcolor='black',
    font=dict(color='white'),
)

fig7.update_layout(
    paper_bgcolor='black',
    plot_bgcolor='black',
    font=dict(color='white'),
)

fig8.update_layout(
    paper_bgcolor = 'black',
    plot_bgcolor = 'black',
    font=dict(color='white'),
)

fig9.update_layout(
    paper_bgcolor = 'black',
    plot_bgcolor = 'black',
    font=dict(color='white'),
)

app.run_server(debug=True, use_reloader=False, port=8051)  # Turn off reloader if inside Jupyter