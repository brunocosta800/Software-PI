import dash
from dash import dcc, html
import requests
import pandas as pd

urlDestinosNormal = "http://192.168.58.95:5000/destinosNormais"
response = requests.get(urlDestinosNormal)
dadosDestinosNormal = response.json()
Top5CidadesNormal = pd.DataFrame(dadosDestinosNormal)

urlDestinosFeriado = "http://192.168.58.95:5000/destinosFeriado"
response = requests.get(urlDestinosFeriado)
dadosDestinosFeriado = response.json()
Top5CidadesFeriado = pd.DataFrame(dadosDestinosFeriado)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Top Cidades Mais Visitadas", style={'textAlign': 'center', 'fontFamily': 'Arial', 'fontSize': '36px', 'color': 'darkblue'}),

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
                    'showgrid': False,  
                    'tickangle': 0,  
                    'tickmode': 'array',  
                    'tickvals': Top5CidadesFeriado['cidade'],  
                    'tickfont': {'size': 10, 'family': 'Arial'},  
                },
                'title': 'Destinos Mais Visitados em Dias Normais',
                'title_x': 0.5,
            }
        })
    ], style={'padding': '20px'}),  

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
                    'showgrid': False,  
                    'tickangle': 0, 
                    'tickmode': 'array', 
                    'tickvals': Top5CidadesFeriado['cidade'],
                    'tickfont': {'size': 10, 'family': 'Arial'},  
                },
                'title': 'Destinos Mais Visitados em Feriados',
            }
        })
    ], style={'padding': '20px'})  
])

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
