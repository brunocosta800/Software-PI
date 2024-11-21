import dash
from dash import dcc, html, Input, Output, dash_table
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from flask_cors import CORS

app = dash.Dash(__name__)
CORS(app.server)

st.session_state.urlDadosDescritivos = f"http://192.168.15.43:5000/dadosDescritivos"
responseDescritivos = requests.get(st.session_state.urlDadosDescritivos)
dadosDescritivos = responseDescritivos.json()
dfDescritivos = pd.DataFrame(dadosDescritivos)

st.session_state.urlDestinosNormal = f"http://192.168.15.43:5000/destinosNormais?ano={'Todos'}&estado={'Todos'}&aero={'Todos'}"
responseDestinosNormal = requests.get(st.session_state.urlDestinosNormal)
dadosDestinosNormal = responseDestinosNormal.json()
Top5CidadesNormal = pd.DataFrame(dadosDestinosNormal)

urlDestinosFeriado = f"http://192.168.15.43:5000/destinosFeriado?ano={'Todos'}&estado={'Todos'}&aero={'Todos'}"
responseDestinosFeriado = requests.get(urlDestinosFeriado)
dadosDestinosFeriado = responseDestinosFeriado.json()
Top5CidadesFeriado = pd.DataFrame(dadosDestinosFeriado)

urlVoosPorFeriado = f"http://192.168.15.43:5000/voosPorFeriado?ano={'Todos'}&estado={'Todos'}&aero={'Todos'}"
responseVoosPorFeriado = requests.get(urlVoosPorFeriado)
dadosVoosPorFeriado = responseVoosPorFeriado.json()
voosPorFeriado = pd.DataFrame(dadosVoosPorFeriado)

st.session_state.urlVoosPorAno = f"http://192.168.15.43:5000/voosPorAno?estado={'Todos'}&aero={'Todos'}"
responseVoosPorAno = requests.get(st.session_state.urlVoosPorAno)
dadosVoosPorAno = responseVoosPorAno.json()
voosPorAno = pd.DataFrame(dadosVoosPorAno)

urlFeriadosPorAno = f"http://192.168.15.43:5000/feriadosProlongadosPorAno"
responseFeriadosPorAno = requests.get(urlFeriadosPorAno)
dadosFeriadosPorAno = responseFeriadosPorAno.json()
feriadosPorAno = pd.DataFrame(dadosFeriadosPorAno)

st.session_state.urlVoosPorMes = f"http://192.168.15.43:5000/voosPorMes?ano={'Todos'}&estado={'Todos'}&aero={'Todos'}"
responseVoosPorMes = requests.get(st.session_state.urlVoosPorMes)
dadosVoosPorMes = responseVoosPorMes.json()
voosPorMes = pd.DataFrame(dadosVoosPorMes)

st.session_state.urlFeriadosPorMes = f"http://192.168.15.43:5000/feriadosProlongadosPorMes?ano={'Todos'}"
responseFeriadosPorMes = requests.get(st.session_state.urlFeriadosPorMes)
dadosFeriadosPorMes = responseFeriadosPorMes.json()
feriadosPorMes = pd.DataFrame(dadosFeriadosPorMes)

ano = ["Todos", "2014","2015","2016","2017","2018", "2019","2020","2021","2022","2023"]

estados = 'http://192.168.15.43:5000/nomesEstados'
responseEstado = requests.get(estados)
estado = ['Todos'] + responseEstado.json()

aeroportos = ['Todos', 'Congonhas', 'Guarulhos']
#region graficos

#region dropdowns
app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='ano-dropdown',
                options=[{'label': ano, 'value': ano} for ano in ano],
                value='Todos',
                style={'width': '100%'}
            ),
        ], style={'flex': 1, 'padding': '10px', 'text-align': 'center', 'display': 'flex', 'align-items': 'center'}),
        
        html.Div([
            dcc.Dropdown(
                id='estado-dropdown',
                options=[{'label': estado, 'value': estado} for estado in estado],
                value='Todos',
                style={'width': '100%'}
            ),
        ], style={'flex': 1, 'padding': '10px', 'text-align': 'center', 'display': 'flex', 'align-items': 'center'}),
        
        html.Div([
            dcc.Dropdown(
                id='aero-dropdown',
                options=[{'label': aeroportos, 'value': aeroportos} for aeroportos in aeroportos],
                value='Todos',
                style={'width': '100%'}
            ),
        ], style={'flex': 1, 'padding': '10px'}),
    ], style={'flex': 1, 'padding': '10px', 'text-align': 'center', 'display': 'flex', 'align-items': 'center'}),
#endregion

#region graficoDadosDescritivos
    html.Div([
        html.H2("Dados Descritivos do Estudo", 
                    style={'textAlign': 'center', 'fontFamily': 'Arial', 'fontSize': '28px', 'color': 'darkgreen', 'display': 'column'}),
            dash_table.DataTable(
                id='table-descritivos',
                columns=[
                    {'name': 'Ano', 'id': 'Ano'},
                    {'name': 'Média', 'id': 'mean'},
                    {'name': 'Mediana', 'id': 'median'},
                    {'name': 'Variância', 'id': 'var'},
                    {'name': 'Desvio Padrão', 'id': 'std'}
                ],
                data = dfDescritivos.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'center',
                    'fontFamily': 'Arial',
                    'fontSize': '14px'
                },
                style_header={
                    'backgroundColor': 'darkgreen',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgba(0, 128, 0, 0.1)'
                    }
                ]
            )
        ], style={'padding': '20px', 'flex': 1, 'max-width': '90%', 'margin-left': '50px'}), 
#endregion

#region graficoTop5Normais
    html.Div([
        html.Div([
            html.H2("Top 5 Cidades Mais Visitadas em Dias Normais", 
                    style={'textAlign': 'center', 'fontFamily': 'Arial', 'fontSize': '28px', 'color': 'darkgreen'}),
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
                        'tickvals': Top5CidadesNormal['cidade'],
                        'tickfont': {'size': 10, 'family': 'Arial'},
                    },
                    'title': 'Destinos Mais Visitados em Dias Normais',
                    'title_x': 0.5,
                }
            })
        ], style={'padding': '20px', 'flex': 1, 'max-width': '50%'}),  
#endregion

#region graficoTop5Feriados
        html.Div([
            html.H2("Top 5 Cidades Mais Visitadas em Feriados", 
                    style={'textAlign': 'center', 'fontFamily': 'Arial', 'fontSize': '28px', 'color': 'darkgreen'}),
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
        ], style={'padding': '20px', 'flex': 1, 'max-width': '50%'}),
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
#endregion

#region graficoVoosPorFeriado
    html.Div([
        html.H2("Quantidade de Vôos Por Feriado", 
                style={'textAlign': 'center', 'fontFamily': 'Arial', 'fontSize': '28px', 'color': 'darkgreen'}),
        dcc.Graph(id='graph-voos-por-feriado', figure={
            'data': [{
                'x': voosPorFeriado['nome feriado'],
                'y': voosPorFeriado['contagem'],
                'type': 'bar',
                'name': 'Feriados'
            }],
            'layout': {
                'bargap': 0.5,
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'xaxis': {
                    'title': 'Feriados',
                    'showgrid': False,
                    'tickangle': 0,
                    'tickmode': 'array',
                    'tickvals': voosPorFeriado['nome feriado'],
                    'tickfont': {'size': 10, 'family': 'Arial'},
                },
                'title': 'Número de Vôos por Feriado',
                'title_x': 0.5,
            }
        })
    ], style={'padding': '20px'}),
#endregion

#region graficoVoosPorAno
    html.Div([
    html.Div([
        html.H2("Quantidade de Vôos Por Ano", 
                style={'textAlign': 'center', 'fontFamily': 'Arial', 'fontSize': '28px', 'color': 'darkgreen'}),
        dcc.Graph(id='graph-voos-por-ano', figure={
            'data': [{
                'x': voosPorAno['ano'],
                'y': voosPorAno['contagem'],
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': 'Vôos por Ano',
            }],
            'layout': {
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'xaxis': {
                    'title': 'Ano',
                    'showgrid': False,
                    'tickangle': 0,
                    'tickmode': 'array',
                    'tickvals': voosPorAno['ano'],
                    'tickfont': {'size': 10, 'family': 'Arial'},
                },
                'yaxis': {
                    'title': 'Número de Vôos',
                    'showgrid': True,
                },
                'title': 'Número de Vôos por Ano',
                'title_x': 0.5,
            }
        })
    ], style={'padding': '20px', 'flex': 1, 'max-width': '50%'}),
#endregion

#region graficoFeriadosPorAno
    html.Div([
        html.H2("Quantidade de Feriados Prolongados Por Ano", 
                style={'textAlign': 'center', 'fontFamily': 'Arial', 'fontSize': '28px', 'color': 'darkgreen'}),
        dcc.Graph(id='graph-feriados-por-ano', figure={
            'data': [{
                'x': feriadosPorAno['ano'],
                'y': feriadosPorAno['contagem'],
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': 'Feriados por Ano',
            }],
            'layout': {
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'xaxis': {
                    'title': 'Ano',
                    'showgrid': False,
                    'tickangle': 0,
                    'tickmode': 'array',
                    'tickvals': feriadosPorAno['ano'],
                    'tickfont': {'size': 10, 'family': 'Arial'},
                },
                'yaxis': {
                    'title': 'Número de Feriados',
                    'showgrid': True,
                },
                'title': 'Número de Feriados Prolongados por Ano',
                'title_x': 0.5,
            }
        })
        ], style={'padding': '20px', 'flex': 1, 'max-width': '50%'})  # Flexível para dividir espaço
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
#endregion

#region graficoVoosPorMes
    html.Div([
        html.H2("Quantidade de Vôos Por Mês", 
                style={'textAlign': 'center', 'fontFamily': 'Arial', 'fontSize': '28px', 'color': 'darkgreen'}),
        dcc.Graph(id='graph-voos-por-mes', figure={
            'data': [{
                'x': voosPorMes['mes'],
                'y': voosPorMes['contagem'],
                'type': 'bar',
                'name': 'Mês'
            }],
            'layout': {
                'bargap': 0.5,
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'xaxis': {
                    'title': 'Mês',
                    'showgrid': False,
                    'tickangle': 0,
                    'tickmode': 'array',
                    'tickvals': voosPorMes['mes'],
                    'tickfont': {'size': 10, 'family': 'Arial'},
                },
                'title': 'Número de Vôos por Mês',
                'title_x': 0.5,
            }
        })
    ], style={'padding': '20px'}),
    
#endregion

#region graficoDpPorAno
    html.Div([
        html.H2("Feriados Prolongados Por Mês", 
                style={'textAlign': 'center', 'fontFamily': 'Arial', 'fontSize': '28px', 'color': 'darkgreen'}),
        dcc.Graph(id='graph-feriados-por-mes', figure={
            'data': [{
                'x': feriadosPorMes['mes'],
                'y': feriadosPorMes['contagem'],
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': 'Mês'
            }],
            'layout': {
                'bargap': 0.5,
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'xaxis': {
                    'title': 'Mês',
                    'showgrid': False,
                    'tickangle': 0,
                    'tickmode': 'array',
                    'tickvals': feriadosPorMes['mes'],
                    'tickfont': {'size': 10, 'family': 'Arial'},
                },
            }
        })
    ], style={'padding': '20px'})
])
#endregion

#endregion

#region cbGraficos

#region cbTop5Feriado
@app.callback(
    Output('graph-destinos-feriado', 'figure'),
    Input('ano-dropdown', 'value'),
    Input('estado-dropdown', 'value'),
    Input('aero-dropdown', 'value')
)
def update_graph_destinos_normais(selected_year, selected_state, selected_aero):
    urlDestinosFeriado = f"http://192.168.15.43:5000/destinosFeriado?ano={selected_year}&estado={selected_state}&aero={selected_aero}"
    responseDestinosFeriado = requests.get(urlDestinosFeriado)
    dadosDestinosFeriado = responseDestinosFeriado.json()
    Top5CidadesFeriado = pd.DataFrame(dadosDestinosFeriado)
    
    fig = px.bar(Top5CidadesFeriado, x='cidade', y='contagem', color_discrete_sequence=['#2484BF'])
    return fig
#endregion

#region cbTop5Normais
@app.callback(
    Output('graph-destinos-normais', 'figure'),
    Input('ano-dropdown', 'value'),
    Input('estado-dropdown', 'value'),
    Input('aero-dropdown', 'value')
)
def update_graph_destinos_feriado(selected_year, selected_state, selected_aero):
    urlDestinosNormal = f"http://192.168.15.43:5000/destinosNormais?ano={selected_year}&estado={selected_state}&aero={selected_aero}"
    responseDestinosNormal = requests.get(urlDestinosNormal)
    dadosDestinosNormal = responseDestinosNormal.json()
    Top5CidadesNormal = pd.DataFrame(dadosDestinosNormal)
    
    fig = px.bar(Top5CidadesNormal, x='cidade', y='contagem', color_discrete_sequence=['#2484BF'])
    return fig
#endregion

#region cbVoosPorFeriado
@app.callback(
    Output('graph-voos-por-feriado', 'figure'),
    Input('ano-dropdown', 'value'),
    Input('estado-dropdown', 'value'),
    Input('aero-dropdown', 'value')
)
def update_graph_voos_por_feriado(selected_year, selected_state, selected_aero):
    urlVoosPorFeriado = f"http://192.168.15.43:5000/voosPorFeriado?ano={selected_year}&estado={selected_state}&aero={selected_aero}"
    responseVoosPorFeriado = requests.get(urlVoosPorFeriado)
    dadosVoosPorFeriado = responseVoosPorFeriado.json()
    voosPorFeriado = pd.DataFrame(dadosVoosPorFeriado)
    
    fig = px.bar(voosPorFeriado, x='nome feriado', y='contagem', color_discrete_sequence=['#2484BF'])
    return fig
#endregion

#region cbVoosPorAno
@app.callback(
    Output('graph-voos-por-ano', 'figure'),
    Input('estado-dropdown', 'value'),
    Input('aero-dropdown', 'value')
)
def update_graph_voos_por_ano(selected_state, selected_aero):
    urlVoosPorAno = f"http://192.168.15.43:5000/voosPorAno?estado={selected_state}&aero={selected_aero}"
    responseVoosPorAno = requests.get(urlVoosPorAno)
    dadosVoosPorAno = responseVoosPorAno.json()
    voosPorAno = pd.DataFrame(dadosVoosPorAno)
    
    fig = px.line(voosPorAno, x='ano', y='contagem', markers=True)
    fig.update_traces(line=dict(color='#2484BF'), marker=dict(color='#2484BF'))
    return fig
#endregion

#region cbVoosPorMes
@app.callback(
    Output('graph-voos-por-mes', 'figure'),
    Input('ano-dropdown', 'value'),
    Input('estado-dropdown', 'value'),
    Input('aero-dropdown', 'value')
)
def update_graph_voos_por_mes(selected_year, selected_state, selected_aero):
    urlVoosPorMes = f"http://192.168.15.43:5000/voosPorMes?ano={selected_year}&estado={selected_state}&aero={selected_aero}"
    responseVoosPorMes = requests.get(urlVoosPorMes)
    dadosVoosPorMes = responseVoosPorMes.json()
    voosPorMes = pd.DataFrame(dadosVoosPorMes)
    
    fig = px.bar(voosPorMes, x='mes', y='contagem', color_discrete_sequence=['#2484BF'])
    return fig
#endregion

#region cbFeriadosPorMes
@app.callback(
    Output('graph-feriados-por-mes', 'figure'),
    Input('ano-dropdown', 'value')
)
def update_graph_voos_por_mes(selected_year):
    st.session_state.urlFeriadosPorMes = f"http://192.168.15.43:5000/feriadosProlongadosPorMes?ano={selected_year}"
    responseFeriadosPorMes = requests.get(st.session_state.urlFeriadosPorMes)
    dadosFeriadosPorMes = responseFeriadosPorMes.json()
    feriadosPorMes = pd.DataFrame(dadosFeriadosPorMes)
    
    fig = px.bar(feriadosPorMes, x='mes', y='contagem', color_discrete_sequence=['#2484BF'])
    return fig
#endregion

#endregion

if __name__ == '__main__':
    app.run_server(host = '127.0.0.1', debug=True, port=8051)
