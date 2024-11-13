import dash
from dash import dcc, html
import requests
import pandas as pd

# URL e dados do gráfico 1 (Destinos Normais)
urlDestinosNormal = "http://192.168.15.43:5000/destinosNormais"
response = requests.get(urlDestinosNormal)
dadosDestinosNormal = response.json()
Top5CidadesNormal = pd.DataFrame(dadosDestinosNormal)

# URL e dados do gráfico 2 (Destinos Feriado)
urlDestinosFeriado = "http://192.168.15.43:5000/destinosFeriado"
response = requests.get(urlDestinosFeriado)
dadosDestinosFeriado = response.json()
Top5CidadesFeriado = pd.DataFrame(dadosDestinosFeriado)

# Criação do app Dash
app = dash.Dash(__name__)

# Layout do app
app.layout = html.Div([
    # Título principal
    html.H1("Top Cidades Mais Visitadas", style={'textAlign': 'center', 'fontFamily': 'Arial', 'fontSize': '36px', 'color': 'darkblue'}),

    # Gráfico 1: Cidades mais visitadas em dias normais
    html.Div([
        html.H2("Top 5 Cidades Mais Visitadas em Dias Normais", style={'textAlign': 'center', 'fontFamily': 'Arial', 'fontSize': '28px', 'color': 'darkgreen'}),
        dcc.Graph(id='graph-destinos-normais', figure={
            'data': [{
                'x': Top5CidadesNormal['cidade'],
                'y': Top5CidadesNormal['contagem'],
                'type': 'bar',
                'name': 'Destinos Normais'
            }],
            'layout': {
                'bargap': 0.5,
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'xaxis': {
                    'title': 'Cidades',
                    'showgrid': False,  # Remove as linhas de grade horizontais
                    'tickangle': 0,  # Rotaciona os rótulos do eixo X em 45 graus
                    'tickmode': 'array',  # Modo de exibição de ticks personalizados
                    'tickvals': Top5CidadesFeriado['cidade'],  # Coloca os rótulos nas cidades
                    'tickfont': {'size': 10, 'family': 'Arial'},  # Ajusta a fonte dos rótulos
                },
                'title': 'Destinos Mais Visitados em Dias Normais',
                'title_x': 0.5,
            }
        })
    ], style={'padding': '20px'}),  # Container para o gráfico 1

    # Gráfico 2: Cidades mais visitadas em feriados
    html.Div([
        html.H2("Top 5 Cidades Mais Visitadas em Feriados", style={'textAlign': 'center', 'fontFamily': 'Arial', 'fontSize': '28px', 'color': 'darkred'}),
        dcc.Graph(id='graph-destinos-feriado', figure={
            'data': [{
                'x': Top5CidadesFeriado['cidade'],
                'y': Top5CidadesFeriado['contagem'],
                'type': 'bar',
                'name': 'Destinos Feriado'
            }],
            'layout': {
                'bargap': 0.5,
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'xaxis': {
                    'title': 'Cidades',
                    'showgrid': False,  # Remove as linhas de grade horizontais
                    'tickangle': 0,  # Rotaciona os rótulos do eixo X em 45 graus
                    'tickmode': 'array',  # Modo de exibição de ticks personalizados
                    'tickvals': Top5CidadesFeriado['cidade'],  # Coloca os rótulos nas cidades
                    'tickfont': {'size': 10, 'family': 'Arial'},  # Ajusta a fonte dos rótulos
                },
                'title': 'Destinos Mais Visitados em Feriados',
            }
        })
    ], style={'padding': '20px'})  # Container para o gráfico 2

])

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
