import streamlit as st
import pandas as pd
from pymongo import MongoClient
import plotly.express as px
from datetime import datetime
from sklearn.linear_model import LinearRegression, LogisticRegression
import numpy as np

client = MongoClient('mongodb://root:mongo@localhost:27017/')
db = client['clima_dashboard']
collection = db['dados_climaticos']

def get_data_from_mongo():
    data = collection.find()
    df = pd.DataFrame(list(data))
    df['data'] = pd.to_datetime(df['data'])
    
    return df

aba_selecionada = st.sidebar.selectbox('Escolha uma aba', ['Visão Geral', 'Visão Específica', 'Previsões'])

if aba_selecionada == 'Visão Específica':
    df = get_data_from_mongo()

    anos = sorted(df['data'].dt.year.unique())

    st.title('Dashboard Específico de Condições Climáticas')

    ano = st.selectbox('Selecione o Ano:', anos, index=len(anos)-1)

    df_ano = df[df['data'].dt.year == ano]

    meses_disponiveis = sorted(
        df_ano['data'].dt.month.unique()
    )
    meses_formatados = [datetime(1900, mes, 1).strftime('%B') for mes in meses_disponiveis]

    mes = st.selectbox('Selecione o Mês:', meses_formatados)

    mes_numero = datetime.strptime(mes, "%B").month

    df_filtered = df_ano[df_ano['data'].dt.month == mes_numero]
    df_filtered['data_dia'] = df_filtered['data'].dt.date

    df_daily = df_filtered.groupby('data_dia').agg({
        'temperatura': 'mean',
        'umidade_relativa': 'mean',
        'pressao': 'mean',
        'precipitacao': 'sum',
        'vento_velocidade': 'mean'
    }).reset_index()

    st.header(f'Condições Climáticas em {mes} de {ano}')
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric('Temperatura Média (°C)', f"{round(df_daily['temperatura'].mean(), 2):.2f}" if not df_daily['temperatura'].isna().all() else "Dados não disponíveis")
    with col2:
        st.metric('Umidade Relativa (%)', f"{round(df_daily['umidade_relativa'].mean(), 2):.2f}" if not df_daily['umidade_relativa'].isna().all() else "Dados não disponíveis")
    with col3:
        st.metric('Precipitação Total (mm)', f"{round(df_daily['precipitacao'].sum(), 2):.2f}" if not df_daily['precipitacao'].isna().all() else "Dados não disponíveis")


    graficos = {
        f'Temperatura diária em {mes} de {ano}': ('temperatura', 'Temperatura (°C)'),
        f'Umidade Relativa diária em {mes} de {ano}': ('umidade_relativa', 'Umidade Relativa (%)'),
        f'Pressão diária em {mes} de {ano}': ('pressao', 'Pressão (hPa)'),
        f'Velocidade do Vento diária em {mes} de {ano}': ('vento_velocidade', 'Velocidade (m/s)')
    }

    for titulo, (variavel, eixo_y) in graficos.items():
        st.subheader(titulo)     
        fig = px.line(df_daily, x='data_dia', y=variavel, labels={'data_dia': 'Data', variavel: eixo_y})
        st.plotly_chart(fig)

    df_dia_precipitacao = df_filtered.groupby('data_dia').agg({'precipitacao': 'sum'}).reset_index()
    st.subheader(f'Total de Precipitação Diária em {mes} de {ano}')
    fig_prec_dia = px.line(
        df_dia_precipitacao,
        x='data_dia',
        y='precipitacao',
        labels={'data_dia': 'Data', 'precipitacao': 'Precipitação Total (mm)'}
    )
    fig_prec_dia.update_layout(xaxis_title='Data', yaxis_title='Precipitação Total (mm)')
    st.plotly_chart(fig_prec_dia)

    df_combined_all = df_filtered.groupby('data_dia').agg({
        'temperatura': 'mean',
        'umidade_relativa': 'mean',
        'pressao': 'mean',
        'vento_velocidade': 'mean',
        'precipitacao': 'sum'
    }).reset_index()

    st.subheader(f'Relação entre Variáveis Climáticas em {mes} de {ano}')
    fig_combined_all = px.line(
        df_combined_all,
        x='data_dia',
        y=['temperatura', 'umidade_relativa', 'pressao', 'vento_velocidade', 'precipitacao'],
        labels={
            'data_dia': 'Data',
            'value': 'Valor',
            'variable': 'Métrica'
        },
        color_discrete_map={
            'temperatura': 'red',
            'umidade_relativa': 'green',
            'pressao': 'yellow',
            'vento_velocidade': 'orange',
            'precipitacao': 'blue'
        }
    )

    fig_combined_all.update_layout(
        xaxis_title='Data',
        yaxis_title='Valores',
        legend_title='Métricas'
    )
    st.plotly_chart(fig_combined_all)

    df_ano = df[df['data'].dt.year == ano]
    df_mes = df_ano.groupby(df_ano['data'].dt.month).agg({
        'temperatura': 'mean',
        'umidade_relativa': 'mean',
        'pressao': 'mean',
        'precipitacao': 'sum',
        'vento_velocidade': 'mean'
    }).reset_index()
    df_mes['mes_nome'] = df_mes['data'].apply(lambda x: datetime(1900, x, 1).strftime('%B'))

    st.subheader(f'Temperatura Média Mensal em {ano}')
    fig_temp_mes = px.bar(df_mes, x='mes_nome', y='temperatura', text='temperatura')
    fig_temp_mes.update_traces(
        texttemplate='%{text:.1f}', 
        hovertemplate='Temperatura: %{y:.2f} °C<extra></extra>'  
    )
    st.plotly_chart(fig_temp_mes)

    st.subheader(f'Total de Precipitação Mensal em {ano}')
    fig_prec_mes = px.bar(df_mes, x='mes_nome', y='precipitacao', text='precipitacao')
    fig_prec_mes.update_traces(
        texttemplate='%{text:.1f}', 
        hovertemplate='Precipitação: %{y:.1f} mm<extra></extra>' 
    )
    st.plotly_chart(fig_prec_mes)

elif aba_selecionada == 'Visão Geral':

    df = get_data_from_mongo()

    st.title('Dashboard Geral de Condições Climáticas')
    
    variavel = st.selectbox(
        "Selecione a variável para análise:",
        options=["temperatura", "precipitacao", "umidade_relativa"],
        format_func=lambda x: {
            "temperatura": "Temperatura Média (°C)",
            "precipitacao": "Precipitação Total (mm)",
            "umidade_relativa": "Umidade Relativa Média (%)"
        }[x]
    )

    df['ano'] = df['data'].dt.year
    df['mes'] = df['data'].dt.month
    
    df['nome_mes'] = df['mes'].apply(lambda x: datetime.strptime(str(x), "%m").strftime("%B"))

    df_agg = df.groupby(['ano', 'nome_mes']).agg({
        variavel: 'mean' if variavel != 'precipitacao' else 'sum'
    }).reset_index()

    df_agg['mes_ordenado'] = df_agg['nome_mes'].apply(lambda x: datetime.strptime(x, "%B").month)
    df_agg = df_agg.sort_values(by=['mes_ordenado'])

    fig_comparativo = px.line(
        df_agg,
        x='nome_mes',
        y=variavel,
        color='ano',
        markers=True,
        title=f"Evolução de {variavel.capitalize()} ao Longo dos Meses por Ano",
        labels={'nome_mes': 'Mês', variavel: variavel.capitalize()}
    )

    st.plotly_chart(fig_comparativo)

    df_agg_anos = df.groupby('ano').agg({
        variavel: 'mean' if variavel != 'precipitacao' else 'sum'
    }).reset_index()

    fig_anos = px.line(
        df_agg_anos,
        x='ano',
        y=variavel,
        markers=True,
        title=f"Evolução de {variavel.capitalize()} ao Longo dos Anos",
        labels={
            'ano': 'Ano',
            variavel: variavel.capitalize()
        }
    )
    fig_anos.update_layout(xaxis=dict(tickmode='linear', dtick=1))
    st.plotly_chart(fig_anos)


elif aba_selecionada == 'Previsões':
    df = get_data_from_mongo()

    df['ano'] = df['data'].dt.year
    df_ano = df.groupby('ano').agg({
        'temperatura': 'mean',
        'precipitacao': 'mean',
        'umidade_relativa': 'mean'
    }).reset_index()

    X = df_ano['ano'].values.reshape(-1, 1)
    y_temperatura = df_ano['temperatura'].values
    y_precipitacao = df_ano['precipitacao'].values
    y_umidade = df_ano['umidade_relativa'].values

    modelo_temperatura = LinearRegression()
    modelo_temperatura.fit(X, y_temperatura)

    modelo_precipitacao = LinearRegression()
    modelo_precipitacao.fit(X, y_precipitacao)

    modelo_umidade = LinearRegression()
    modelo_umidade.fit(X, y_umidade)

    anos_futuros = np.arange(2022, 2032).reshape(-1, 1)
    previsao_temperatura = modelo_temperatura.predict(anos_futuros)
    previsao_precipitacao = modelo_precipitacao.predict(anos_futuros)
    previsao_umidade = modelo_umidade.predict(anos_futuros)

    df_previsao = pd.DataFrame({
        'ano': anos_futuros.flatten(),
        'temperatura_media': previsao_temperatura,
        'precipitacao_media': previsao_precipitacao,
        'umidade_relativa_media': previsao_umidade
    })

    st.title('Previsões Climáticas')

    variavel = st.selectbox('Escolha a variável para previsão anual', ['Temperatura', 'Precipitação', 'Umidade Relativa'])

    if variavel == 'Temperatura':
        fig = px.line(df_previsao, x='ano', y='temperatura_media', title='Previsão de Temperatura Média Anual (2022-2031)', labels={'x': 'Ano', 'y': 'Temperatura (°C)'})
    elif variavel == 'Precipitação':
        fig = px.line(df_previsao, x='ano', y='precipitacao_media', title='Previsão de Precipitação Média Anual (2022-2031)', labels={'x': 'Ano', 'y': 'Precipitação (mm)'})
    else:
        fig = px.line(df_previsao, x='ano', y='umidade_relativa_media', title='Previsão de Umidade Relativa Média Anual (2022-2031)', labels={'x': 'Ano', 'y': 'Umidade Relativa (%)'})
    
    st.plotly_chart(fig)

    ano_escolhido = st.selectbox('Escolha o ano para previsão mensal', anos_futuros.flatten())

    meses = np.arange(1, 13) 
    X_mensal = np.array([[ano_escolhido] for _ in meses]) 

    previsao_mensal_temperatura = modelo_temperatura.predict(X_mensal) + (np.random.rand(12) * 2 - 1)  
    previsao_mensal_precipitacao = np.maximum(0, modelo_precipitacao.predict(X_mensal) + (np.random.rand(12) * 10 - 5)) 
    previsao_mensal_umidade = modelo_umidade.predict(X_mensal) + (np.random.rand(12) * 5 - 2)  

    df_previsao_mensal = pd.DataFrame({
        'mes': meses,
        'temperatura_media': previsao_mensal_temperatura,
        'precipitacao_media': previsao_mensal_precipitacao,
        'umidade_relativa_media': previsao_mensal_umidade
    })

    df_previsao_mensal['nome_mes'] = df_previsao_mensal['mes'].apply(lambda x: datetime(2020, x, 1).strftime('%B'))

    fig_temperatura = px.line(df_previsao_mensal, x='nome_mes', y='temperatura_media', 
                            title=f'Previsão Mensal de Temperatura para o Ano {ano_escolhido}', 
                            labels={'nome_mes': 'Mês', 'temperatura_media': 'Temperatura (°C)'})
    fig_precipitacao = px.line(df_previsao_mensal, x='nome_mes', y='precipitacao_media', 
                            title=f'Previsão Mensal de Precipitação para o Ano {ano_escolhido}', 
                            labels={'nome_mes': 'Mês', 'precipitacao_media': 'Precipitação (mm)'})
    fig_umidade = px.line(df_previsao_mensal, x='nome_mes', y='umidade_relativa_media', 
                        title=f'Previsão Mensal de Umidade Relativa para o Ano {ano_escolhido}', 
                        labels={'nome_mes': 'Mês', 'umidade_relativa_media': 'Umidade Relativa (%)'})

    st.plotly_chart(fig_temperatura)
    st.plotly_chart(fig_precipitacao)
    st.plotly_chart(fig_umidade)

    df = df.dropna(subset=['temperatura', 'umidade_relativa', 'pressao', 'radiacao', 'vento_direcao', 'vento_velocidade', 'latitude', 'longitude'])

    df['ano'] = df['data'].dt.year
    df['mes'] = df['data'].dt.month

    df_ano_mes = df.groupby(['ano', 'mes']).agg({
        'temperatura': 'mean',
        'precipitacao': 'mean',
        'umidade_relativa': 'mean'
    }).reset_index()

    X_ano_mes = df_ano_mes[['ano', 'mes']].values 
    y_temperatura = df_ano_mes['temperatura'].values
    y_precipitacao = df_ano_mes['precipitacao'].values
    y_umidade = df_ano_mes['umidade_relativa'].values

    modelo_temperatura = LinearRegression()
    modelo_temperatura.fit(X_ano_mes, y_temperatura)

    modelo_precipitacao = LinearRegression()
    modelo_precipitacao.fit(X_ano_mes, y_precipitacao)

    modelo_umidade = LinearRegression()
    modelo_umidade.fit(X_ano_mes, y_umidade)

    df['choveu'] = np.where(df['precipitacao'] > 0, 1, 0)

    X_chuva = df[['temperatura', 'umidade_relativa', 'pressao', 'radiacao', 'vento_direcao', 'vento_velocidade', 'latitude', 'longitude']].values
    y_chuva = df['choveu'].values

    modelo_chuva = LogisticRegression()
    modelo_chuva.fit(X_chuva, y_chuva)

    data_escolhida = st.date_input("Escolha a data para previsão climática", min_value=datetime(2022, 1, 1), max_value=datetime(2031, 12, 31))

    ano_escolhido_data = data_escolhida.year
    mes_escolhido_data = data_escolhida.month

    X_data = np.array([[ano_escolhido_data, mes_escolhido_data]])  
    temperatura_prevista = modelo_temperatura.predict(X_data)  
    precipitacao_prevista = modelo_precipitacao.predict(X_data) 
    umidade_prevista = modelo_umidade.predict(X_data) 


    dados_previsao_chuva = np.array([[temperatura_prevista[0], umidade_prevista[0], 1013, 15, 180, 10, -23.55, -46.63]]) 

    probabilidade_chuva = modelo_chuva.predict_proba(dados_previsao_chuva)[:, 1] 

    st.write(f"Previsão para {data_escolhida.strftime('%d/%m/%Y')}:")
    st.write(f"Temperatura: {temperatura_prevista[0]:.2f} °C")
    st.write(f"Precipitação: {precipitacao_prevista[0]:.2f} mm")
    st.write(f"Umidade Relativa: {umidade_prevista[0]:.2f} %")

    st.write(f"Probabilidade de Chuva: {probabilidade_chuva[0] * 100:.2f}%")