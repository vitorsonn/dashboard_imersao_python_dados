import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title=("Dashboard de Salarios na Área de Dados"), # titulo do site
    layout="wide" # pagina ampla
)

df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")
# Sidebar do dashboard com os filtros

st.sidebar.header("Filtros") #titulo da sidebar

#filtro de anos
anos_disponiveis = sorted(df["ano"].unique())
anos_selecionados = st.sidebar.multiselect("Ano",anos_disponiveis,default=anos_disponiveis)

#filtros de senioridade
senioridades_disponiveis = sorted(df["senioridade"].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade",senioridades_disponiveis,default=senioridades_disponiveis)

#filtros por tipo de contrato
contratos_disponiveis = sorted(df["contrato"].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato",contratos_disponiveis,default=contratos_disponiveis)

#filtros por tamanho da empresa
tamanhos_disponiveis = sorted(df["tamanho_empresa"].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da empresa",tamanhos_disponiveis,default=tamanhos_disponiveis)

# filtragem do DataFrame 
# o df principal vai ser atualizado com os dados selecionados do usuario na sidebar

df_filtrado = df[
    (df["ano"].isin(anos_selecionados)) &
    (df["contrato"].isin(contratos_selecionados)) &
    (df["senioridade"].isin(senioridades_selecionadas)) &
    (df["tamanho_empresa"].isin(tamanhos_selecionados))
    
]

# conteudo principal

st.title("Dashboard de Análise de salários na area de dados")
st.markdown("Explore os dados salariais na area de dados nos ultimos anos. Utilze filtros a esquerda para refinar sua analise")

# Métricas Principais (KPIs)
# Métricas são valores médios ainda sem filtros que vão introduzir a estatistica dos dados ao usuario 

st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty: # se não tiver vazio...
    salario_medio = df_filtrado["usd"].mean()
    salario_maximo = df_filtrado["usd"].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
    
else:
    salario_medio, salario_maximo, total_registros , cargo_mais_frequente = 0, 0 ,0

col1, col2, col3, col4, = st.columns(4) # definindo as colunas

col1.metric("Salário Médio",f"${salario_medio:,.0f}")
col2.metric("Salario Máximo",f"${salario_maximo:,.0f}")    
col3.metric("Total de registros",f"{total_registros:,}")
col4.metric("Cargo mais frequente",cargo_mais_frequente)

st.markdown("---")

# Análises visuais com Plotyly

st.subheader("Graficos")

col_graf1, col_graf2 = st.columns(2) # vão ser dois gráficos na mesma linha

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index() #nlargest mostra os maiores valores, nesse caso os 10 maiores
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h', # horizontal
            title="Top 10 Cargos por salário médio",
            labels={'usd': "Média salarial anual(USD)", 'cargo':''} 
        )
        
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True) # exibir o gráfico com o streamlit
        
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição") # erro se não aparecer o gráfico (df vazio)   

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
        df_filtrado,
        x='usd',
        nbins=30,
        title='Distribuição de salarios anuais',
        labels={'usd': "Faixa salarial (USD)", 'count': ''}
        )
            
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição") # erro se não aparecer o gráfico (df vazio)   


col_graf3, col_graf4 = st.columns(2) # mais dois gráficos que vão estar na mesma seção


with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values="quantidade",
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )
        
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
        
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição") # erro se não aparecer o gráfico (df vazio)   


with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist'] # filtrando pelo cargo de Data Scientist
        media_ds_pais =  df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(
            media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title="Salario médio de cientista de dados por país",
            labels={'usd': 'Salário médio (USD)', "residencia_iso3": "País"}
        )
        
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição") # erro se não aparecer o gráfico (df vazio)   

  # --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)