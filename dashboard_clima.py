import pandas as pd
import streamlit as st
import plotly.express as px

@st.cache_data
def load_data(arquivo):
    df = pd.read_csv("benchmark_clima_dashboard.csv")
    df['date'] = pd.to_datetime(df['date'])
    df['Year'] = df['date'].dt.year
    df['Month'] = df['date'].dt.month
    df['Month_name'] = df['date'].dt.month_name()
    return df

df = load_data("benchmark_clima_dashboard.csv")

st.set_page_config(page_title = "Dashboard Clima", layout = "wide")
st.title("Dashboard Clima", text_alignment = "center")
st.caption("Dash criada para bolsa")


#criando a sidebar
st.sidebar.header("Selecione a(s) Cidade(s) e o Período:")


#box side bars
cidades = st.sidebar.multiselect("Cidade:", options = sorted(df["city"].unique()), default = (df["city"][0]))

mes = st.sidebar.multiselect("Mês:", options = sorted(df["Month"].unique()),default = sorted(df["Month"].unique()))
                        
ano = st.sidebar.multiselect("Ano:", options = sorted(df["Year"].unique()), default = sorted(df["Year"][0]))
             
# Removi o que não parece ser relevante no momento
colunas_variaveis = [col for col in df.columns if col not in ["city", "Year", "date", "state", "latitude", "longitude", "elevation_m", "Month", "Month_name"]]

variaveis_selecionadas = st.sidebar.selectbox("Variável:", colunas_variaveis)


st.sidebar.subheader("Criado por Rafael.",)

#filtro para a sidebar
df_filtrado = df[(df["city"].isin(cidades)) &
                 (df["Month"].isin(mes)) &
                 (df["Year"].isin(ano))].copy()

if df_filtrado.empty or not variaveis_selecionadas:
    st.warning("Nenhum dado encontrado com os filtros. Ajuste os filtros.")
    st.stop()

#substituindo NaN por interpolação
df_filtrado['humidity_pct'] = df_filtrado.groupby('city')['humidity_pct'].transform(lambda s: s.interpolate(method='linear'))
df_filtrado['temp_avg_c'] = df_filtrado.groupby('city')['temp_avg_c'].transform(lambda s: s.interpolate(method='linear'))


#container para series historicas
with st.container(border=True):
    st.header("Séries Históricas", text_alignment = "center")

    fig = px.line(df_filtrado, x="date", y=variaveis_selecionadas, color = 'city', title=f"{variaveis_selecionadas} por Cidade")
    fig.update_layout(legend_title_text="Cidade",
                        title=dict(
                        text=f"{variaveis_selecionadas} por cidade",
                        x=0.5,
                        xanchor="center",
                        font=dict(size=18)))

    st.plotly_chart(fig, width='stretch')

#dispor colunas
col_1, col_2, col_3 = st.columns([4,2.5,1], border = True)

#Amplitude termica mensal: media temp max mensal - media temp min mensal
amplitude_mean = df_filtrado.groupby(["Year","Month", "Month_name", "city"])[["temp_max_c", "temp_min_c"]].mean().reset_index().sort_values(by=["Year", "Month"])
amplitude_mean["amplitude_mean"] = (amplitude_mean["temp_max_c"] - amplitude_mean["temp_min_c"]).round(2)

with col_1:
    st.header("Amplitude Térmica Mensal no Período",text_alignment = "center")
    #criar box 
    cidades_3 = st.selectbox("",key= 3, options = sorted(amplitude_mean['city'].unique()))

    #filtrar cidades que foram selecionadas
    filtro_cidade = amplitude_mean[amplitude_mean['city'] == cidades_3]
    filtro_cidade['Year'] = filtro_cidade['Year'].astype(str)

    fig_1 = px.line(filtro_cidade, x="Month_name", y="amplitude_mean", color ='Year', markers=True)
    st.plotly_chart(fig_1, width='stretch')    

#precipitação do periodo: fazer um grafico de barras dos meses
precipitacao_periodo = df_filtrado.groupby(["Year","Month", "Month_name", "city"])["precipitation_mm"].sum().reset_index().sort_values(by=["Year", "Month"])

with col_2:
    st.header("Precipitação Mensal no Período")
    cidades_2 = st.selectbox("", options = sorted(precipitacao_periodo['city'].unique()))

    dados_filtrados_cidade = precipitacao_periodo[precipitacao_periodo['city'] == cidades_2]

    dados_filtrados_cidade['Year'] = dados_filtrados_cidade['Year'].astype(str)

    fig1 = px.bar(dados_filtrados_cidade, 
                  x = "Month_name", 
                  y = "precipitation_mm", 
                  color = "Year",
                  height=400) #,color_discrete_sequence=["#0f9ee0"])

    st.plotly_chart(fig1, width='stretch')

#display metrics
lat_valor = df_filtrado.loc[df_filtrado["city"] == cidades_2, "latitude"].iloc[0]
lon_valor = df_filtrado.loc[df_filtrado["city"] == cidades_2, "longitude"].iloc[0]
elev_valor = df_filtrado.loc[df_filtrado["city"] == cidades_2, "elevation_m"].iloc[0]

with col_3:
    st.metric(label = f"Latitude {cidades_2}", value=f"{lat_valor}°", border = True)
    st.metric(label=f"Longitude {cidades_2}", value=f"{lon_valor}°", border=True)
    st.metric(label=f"Altitude {cidades_2}", value=f"{elev_valor}m", border=True)


#display dataframe
st.subheader('Dados Detalhados do Período Filtrado')
st.dataframe(df_filtrado, width='stretch')
