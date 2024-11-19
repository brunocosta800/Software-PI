import pandas as pd
from flask import Flask
from flask import request,Response
import os
import requests
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import calendar
import json
import math
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv("variaveis.env")

with open("feriados_acumulados.json", "r") as file:
    feriados = json.load(file)

dfFeriados = pd.DataFrame(feriados)


dfFeriados['date'] = pd.to_datetime(dfFeriados['date'])

dfFeriados['diaDaSemana'] = dfFeriados['date'].dt.day_name()

diasQueNaoSaoProlongados = ['Saturday','Sunday', 'Wednesday']
dfFeriados['feriadoProlongado'] = ~dfFeriados['diaDaSemana'].isin(diasQueNaoSaoProlongados)
dias_da_semana_mapping = {
    'Monday': -2,
    'Tuesday': -3,
    'Wednesday': 0,
    'Thursday': 3,
    'Friday': 2,
    'Saturday': 0,
    'Sunday': 0
}

# Adiciona uma nova coluna com a categorização dos dias da semana
dfFeriados['intervalo'] = dfFeriados['diaDaSemana'].map(dias_da_semana_mapping)
dfFeriados['fimIntervalo'] = dfFeriados['date'] + pd.to_timedelta(dfFeriados['intervalo'], unit='D')
dfFeriados['ano'] = dfFeriados['date'].dt.year

dfFeriados['date'] = pd.to_datetime(dfFeriados['date'])

dfFeriados['diaDaSemana'] = dfFeriados['date'].dt.day_name()

diasQueNaoSaoProlongados = ['Saturday','Sunday', 'Wednesday']
dfFeriados['feriadoProlongado'] = ~dfFeriados['diaDaSemana'].isin(diasQueNaoSaoProlongados)
dias_da_semana_mapping = {
    'Monday': -2,
    'Tuesday': -3,
    'Wednesday': 0,
    'Thursday': 3,
    'Friday': 2,
    'Saturday': 0,
    'Sunday': 0
}

dfFeriados['intervalo'] = dfFeriados['diaDaSemana'].map(dias_da_semana_mapping)
dfFeriados['fimIntervalo'] = dfFeriados['date'] + pd.to_timedelta(dfFeriados['intervalo'], unit='D')

url = os.getenv("urlDataBase")
key = os.getenv("keyDataBase")
supabase: Client = create_client(url, key)

chunk_size = 1000
start = 0
end = chunk_size - 1

dfVoos = pd.DataFrame()

while True:
    response = supabase.table('Voos').select('*').range(start, end).execute()

    chunk_df = pd.DataFrame(response.data)

    dfVoos = pd.concat([dfVoos, chunk_df], ignore_index=True)
    
    if len(response.data) < chunk_size:
        break

    start += chunk_size
    end += chunk_size


print(f"Total rows retrieved: {len(dfVoos)}")

dfVoos['estado'] = dfVoos['Descricao Aeroporto Destino'].str.extract(r' - (\w{2}) - BRASIL')

dfVoos['Partida Prevista'] = dfVoos['Partida Prevista'].astype(str).str.replace('T', ' ')
dfVoos['Partida Prevista'] = dfVoos['Partida Prevista'].astype(str).str.replace(r'\+00:00', '', regex=True)
dfVoos['Partida Prevista'] = pd.to_datetime(dfVoos['Partida Prevista'])

descricaoAeroportos = dfVoos['Descricao Aeroporto Destino']
listaAeroportos = descricaoAeroportos.value_counts()

def eBrasileiro(descricaoAeroporto):
  palavras = descricaoAeroporto.split()
  if(palavras[-1] == 'BRASIL'):
    return True
  else:
    return False
  
nomeAeroportos = listaAeroportos.index.tolist()
contagemAeroportos = listaAeroportos.values.tolist()

inicioFeriados = dfFeriados['date'].tolist()
fimFeriados = dfFeriados['fimIntervalo'].tolist()
nomeFeriados = dfFeriados['name'].tolist()

dfVoos['Dentro do Feriado'] = np.nan
dfVoos['NomeFeriado'] = np.nan
for i in range(len(inicioFeriados)):
  inicio_intervalo = inicioFeriados[i]
  fim_intervalo = fimFeriados[i]
  nome_Feriado = nomeFeriados[i]

  dfVoos.loc[(dfVoos['Dentro do Feriado'] == False) | (dfVoos['Dentro do Feriado'].isna()), 'Dentro do Feriado'] = (
      (dfVoos['Partida Prevista'] >= inicio_intervalo) & (dfVoos['Partida Prevista'] <= fim_intervalo)
  )

  dfVoos.loc[(dfVoos['Dentro do Feriado'] == True) & (dfVoos['NomeFeriado'].isna()), 'NomeFeriado'] = nome_Feriado

filtroAviao = dfVoos[dfVoos['Dentro do Feriado']]

filtroAviao['Partida Prevista'] = pd.to_datetime(dfVoos['Partida Prevista'])
filtroAviao = filtroAviao.sort_values(by='Partida Prevista')

dataInicioAno = '01/01/2023'
dataInicioAno = pd.to_datetime(dataInicioAno, format='%d/%m/%Y')
listaDatas = []

for i in range(len(inicioFeriados)):
  inicio_intervalo = inicioFeriados[i]
  fim_intervalo = fimFeriados[i]
  nome_Feriado = nomeFeriados[i]

  dias = pd.date_range(start=inicio_intervalo, end=fim_intervalo).tolist()

  for dia in dias:
    listaDatas.append(dia)
print(listaDatas)

listaDatas = pd.Series(listaDatas).drop_duplicates().tolist()

destinosFeriado = dfVoos[dfVoos['Dentro do Feriado'] == "VERDADEIRO"]['Descricao Aeroporto Destino'].value_counts().head(5)
destinosFeriado
nomeCidades = []

nomeDeCidade = destinosFeriado.index
for texto in nomeDeCidade:
  nomes = texto.split('-')
  nomeCidades.append(nomes[-3])
  
app = Flask(__name__)

@app.route("/nomesEstados", methods=['GET'])
def get_nomesEstados():
    dfVoos['estado'] = dfVoos['Descricao Aeroporto Destino'].str.extract(r' - (\w{2}) - BRASIL')
    estados_unicos = dfVoos['estado'].dropna().unique().tolist()

    return Response(json.dumps(estados_unicos), mimetype='application/json')

@app.route("/destinosNormais", methods=['GET'])
def get_Top5Normal():
    ano = request.args.get('ano')
    estado = request.args.get('estado')
    aero = request.args.get('aero')
    aero = aero.upper()

    if ano == 'Todos':
        if estado == 'Todos':
            if aero == 'TODOS':
                destinosNormal = dfVoos[dfVoos['Dentro do Feriado'] == False]['Descricao Aeroporto Destino'].value_counts().head(5)
            else:
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == False]
                destinosNormal = filtered_df[filtered_df['AEROPORTO ORIGEM'] == aero]['Descricao Aeroporto Destino'].value_counts().head(5)
        else:
            if aero == 'TODOS':
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == False]
                destinosNormal = filtered_df[filtered_df['estado'] == estado]['Descricao Aeroporto Destino'].value_counts().head(5)
            else:
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == False]
                filtered_df2 = filtered_df[filtered_df['estado'] == estado]
                destinosNormal = filtered_df2[filtered_df2['AEROPORTO ORIGEM'] == aero]['Descricao Aeroporto Destino'].value_counts().head(5)
    else:
        if estado == 'Todos':
            if aero == 'TODOS':
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == False]
                destinosNormal = filtered_df[filtered_df['Ano'] == int(ano)]['Descricao Aeroporto Destino'].value_counts().head(5)
            else:
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == False]
                filtered_df2 = filtered_df[filtered_df['Ano'] == int(ano)]
                destinosNormal = filtered_df2[filtered_df2['AEROPORTO ORIGEM'] == aero]['Descricao Aeroporto Destino'].value_counts().head(5)
        else:
            if aero == 'TODOS':
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == False]
                filtered_df2 = filtered_df[filtered_df['estado'] == estado]
                filtered_df3 = filtered_df2[filtered_df2['Ano'] == int(ano)]
                destinosNormal = filtered_df3['Descricao Aeroporto Destino'].value_counts().head(5)
            else:
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == False]
                filtered_df2 = filtered_df[filtered_df['estado'] == estado]
                filtered_df3 = filtered_df2[filtered_df2['Ano'] == int(ano)]
                destinosNormal = filtered_df3[filtered_df3['AEROPORTO ORIGEM'] == aero]['Descricao Aeroporto Destino'].value_counts().head(5)
            

    nomeCidades = []

    nomeDeCidade = destinosNormal.index
    for texto in nomeDeCidade:
        nomes = texto.split('-')
        nomeCidades.append(nomes[1].strip())
    
    destinos_df = pd.DataFrame(destinosNormal).reset_index()
    destinos_df.columns = ['aeroporto', 'contagem']
    destinos_df['cidade'] = nomeCidades
    
    return Response(destinos_df.to_json(orient="records"), mimetype='application/json')

@app.route("/destinosFeriado", methods=['GET'])
def get_Top5Feriado():
    ano = request.args.get('ano')
    estado = request.args.get('estado')
    aero = request.args.get('aero')
    aero = aero.upper()

    if ano == 'Todos':
        if estado == 'Todos':
            if aero == 'TODOS':
                destinosFeriado = dfVoos[dfVoos['Dentro do Feriado'] == True]['Descricao Aeroporto Destino'].value_counts().head(5)
            else:
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == True]
                destinosFeriado = filtered_df[filtered_df['AEROPORTO ORIGEM'] == aero]['Descricao Aeroporto Destino'].value_counts().head(5)
        else:
            if aero == 'TODOS':
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == True]
                destinosFeriado = filtered_df[filtered_df['estado'] == estado]['Descricao Aeroporto Destino'].value_counts().head(5)
            else:
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == True]
                filtered_df2 = filtered_df[filtered_df['estado'] == estado]
                destinosFeriado = filtered_df2[filtered_df2['AEROPORTO ORIGEM'] == aero]['Descricao Aeroporto Destino'].value_counts().head(5)
    else:
        if estado == 'Todos':
            if aero == 'TODOS':
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == True]
                destinosFeriado = filtered_df[filtered_df['Ano'] == int(ano)]['Descricao Aeroporto Destino'].value_counts().head(5)
            else:
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == True]
                filtered_df2 = filtered_df[filtered_df['Ano'] == int(ano)]
                destinosFeriado = filtered_df2[filtered_df2['AEROPORTO ORIGEM'] == aero]['Descricao Aeroporto Destino'].value_counts().head(5)
        else:
            if aero == 'TODOS':
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == True]
                filtered_df2 = filtered_df[filtered_df['estado'] == estado]
                filtered_df3 = filtered_df2[filtered_df2['Ano'] == int(ano)]
                destinosFeriado = filtered_df3['Descricao Aeroporto Destino'].value_counts().head(5)
            else:
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == True]
                filtered_df2 = filtered_df[filtered_df['estado'] == estado]
                filtered_df3 = filtered_df2[filtered_df2['Ano'] == int(ano)]
                destinosFeriado = filtered_df3[filtered_df3['AEROPORTO ORIGEM'] == aero]['Descricao Aeroporto Destino'].value_counts().head(5)

    nomeCidades = []

    nomeDeCidade = destinosFeriado.index
    for texto in nomeDeCidade:
        nomes = texto.split('-')
        nomeCidades.append(nomes[1].strip())
    
    destinos_df = pd.DataFrame(destinosFeriado).reset_index()
    destinos_df.columns = ['aeroporto', 'contagem']
    destinos_df['cidade'] = nomeCidades
    
    return Response(destinos_df.to_json(orient="records"), mimetype='application/json')

@app.route("/voosPorFeriado", methods=['GET'])
def get_voosPorFeriado():
    ano = request.args.get('ano')
    estado = request.args.get('estado')
    aero = request.args.get('aero')
    aero = aero.upper()

    if ano == 'Todos':
        if estado == 'Todos':
            if aero == 'TODOS':
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == True]
                qtdeVoosPorFeriado = filtered_df['NomeFeriado'].value_counts()
            else:
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == True]
                qtdeVoosPorFeriado = filtered_df[filtered_df['AEROPORTO ORIGEM'] == aero]['NomeFeriado'].value_counts()
        else:
            if aero == 'TODOS':
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == True]
                qtdeVoosPorFeriado = filtered_df[filtered_df['estado'] == estado]['NomeFeriado'].value_counts()
            else:
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == True]
                filtered_df2 = filtered_df[filtered_df['estado'] == estado]
                qtdeVoosPorFeriado = filtered_df2[filtered_df2['AEROPORTO ORIGEM'] == aero]['NomeFeriado'].value_counts()
    else:
        if estado == 'Todos':
            if aero == 'TODOS':
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == True]
                qtdeVoosPorFeriado = filtered_df[filtered_df['Ano'] == int(ano)]['NomeFeriado'].value_counts()
            else:
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == True]
                filtered_df2 = filtered_df[filtered_df['Ano'] == int(ano)]
                qtdeVoosPorFeriado = filtered_df2[filtered_df2['AEROPORTO ORIGEM'] == aero]['NomeFeriado'].value_counts()
        else:
            if aero == 'TODOS':
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == True]
                filtered_df2 = filtered_df[filtered_df['estado'] == estado]
                filtered_df3 = filtered_df2[filtered_df2['Ano'] == int(ano)]
                qtdeVoosPorFeriado = filtered_df3['NomeFeriado'].value_counts()
            else:
                filtered_df = dfVoos[dfVoos['Dentro do Feriado'] == True]
                filtered_df2 = filtered_df[filtered_df['estado'] == estado]
                filtered_df3 = filtered_df2[filtered_df2['Ano'] == int(ano)]
                qtdeVoosPorFeriado = filtered_df3[filtered_df3['AEROPORTO ORIGEM'] == aero]['NomeFeriado'].value_counts()


    voosPorFeriado = pd.DataFrame(qtdeVoosPorFeriado).reset_index()
    voosPorFeriado.columns = ['nome feriado', 'contagem']
    
    return Response(voosPorFeriado.to_json(orient="records"), mimetype='application/json')

@app.route("/voosPorAno", methods=['GET'])
def get_voosPorAno():
    estado = request.args.get('estado')
    aero = request.args.get('aero')
    aero = aero.upper()

    if estado == 'Todos':
        if aero == 'TODOS':
            qtdeVoosPorAno = dfVoos['Ano'].value_counts().sort_index()
        else:
            filtered_df = dfVoos[dfVoos['AEROPORTO ORIGEM']==aero]
            qtdeVoosPorAno = filtered_df['Ano'].value_counts().sort_index()
    else:
        if aero == 'TODOS':
            filtered_df = dfVoos[dfVoos['estado']==estado]
            qtdeVoosPorAno = filtered_df['Ano'].value_counts().sort_index()
        else:
            filtered_df = dfVoos[dfVoos['AEROPORTO ORIGEM']==aero]
            filtered_df2 = filtered_df[filtered_df['estado'] == estado]
            qtdeVoosPorAno = filtered_df2['Ano'].value_counts().sort_index()
    
    qtdeVoosPorAno = qtdeVoosPorAno.iloc[:-1]

    voosPorAno = pd.DataFrame(qtdeVoosPorAno).reset_index()
    voosPorAno.columns = ['ano', 'contagem']
    
    return Response(voosPorAno.to_json(orient="records"), mimetype='application/json')

@app.route("/feriadosProlongadosPorAno", methods=['GET'])
def get_feriadosProlongadosPorAno():
    quantidadeFeriadosProlongadosPorAno = (dfFeriados['feriadoProlongado'] == True).groupby(dfFeriados['ano']).sum()

    feriadosProlongadosPorAno = pd.DataFrame(quantidadeFeriadosProlongadosPorAno).reset_index()
    feriadosProlongadosPorAno.columns = ['ano', 'contagem']
    
    return Response(feriadosProlongadosPorAno.to_json(orient="records"), mimetype='application/json')

@app.route("/voosPorMes", methods=['GET'])
def get_voosPorMes():
    ano = request.args.get('ano')
    estado = request.args.get('estado')
    aero = request.args.get('aero')
    aero = aero.upper()

    if ano == 'Todos':
        if estado == 'Todos':
            if aero == 'TODOS':
                qtdeVoosPorMes = dfVoos['Mes'].value_counts().sort_index()
            else:
                filtered_df = dfVoos[dfVoos['AEROPORTO ORIGEM'] == aero]
                qtdeVoosPorMes = filtered_df['Mes'].value_counts().sort_index()
        else:
            if aero == 'TODOS':
                filtered_df = dfVoos[dfVoos['estado'] == estado]
                qtdeVoosPorMes = filtered_df['Mes'].value_counts().sort_index()
            else:
                filtered_df = dfVoos[dfVoos['estado'] == estado]
                filtered_df2 = filtered_df[filtered_df['AEROPORTO ORIGEM'] == aero]
                qtdeVoosPorMes = filtered_df2['Mes'].value_counts().sort_index()
    else:
        if estado == 'Todos':
            if aero == 'TODOS':
                filtered_df = dfVoos[dfVoos['Ano'] == int(ano)]
                qtdeVoosPorMes = filtered_df['Mes'].value_counts().sort_index()
            else:
                filtered_df = dfVoos[dfVoos['Ano'] == int(ano)]
                filtered_df2 = filtered_df[filtered_df['AEROPORTO ORIGEM'] == aero]
                qtdeVoosPorMes = filtered_df2['Mes'].value_counts().sort_index()
        else:
            if aero == 'TODOS':
                filtered_df = dfVoos[dfVoos['estado'] == estado]
                filtered_df2 = filtered_df[filtered_df['Ano'] == int(ano)]
                qtdeVoosPorMes = filtered_df2['Mes'].value_counts().sort_index()
            else:
                filtered_df = dfVoos[dfVoos['estado'] == estado]
                filtered_df2 = filtered_df[filtered_df['Ano'] == int(ano)]
                filtered_df3 = filtered_df2[filtered_df2['AEROPORTO ORIGEM'] == aero]
                qtdeVoosPorMes = filtered_df3['Mes'].value_counts().sort_index()
    
    qtdeVoosPorMes = qtdeVoosPorMes.reindex(range(1, 13))
    qtdeVoosPorMes = qtdeVoosPorMes.sort_index()
    
    voosPorMes = pd.DataFrame(qtdeVoosPorMes).reset_index()
    voosPorMes.columns = ['mes', 'contagem']
    voosPorMes['mes'] = voosPorMes['mes'].apply(lambda x: calendar.month_name[x])
    
    return Response(voosPorMes.to_json(orient="records"), mimetype='application/json')

if __name__ == "__main__":
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 5000)))