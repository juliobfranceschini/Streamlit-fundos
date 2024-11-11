import streamlit as st
import requests
import zipfile
import io
import pandas as pd

# Function to download and process data for a specified year and month, with caching
@st.cache_data(show_spinner=False)
def processar_dados(ano, mes):
    # URL para o arquivo ZIP da CVM para o ano e mês especificados
    url = f'https://dados.cvm.gov.br/dados/FI/DOC/CDA/DADOS/cda_fi_{ano}{mes:02}.zip'
    st.write(f"Baixando dados de {ano}-{mes:02}...")

    # Baixar o arquivo ZIP
    response = requests.get(url)

    # Verificar se o download foi bem-sucedido
    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content), 'r') as arquivo_zip:
            dataframes = []
            # Iterar sobre todos os arquivos CSV no ZIP, carregando apenas colunas necessárias
            for file_name in arquivo_zip.namelist():
                df = pd.read_csv(arquivo_zip.open(file_name), sep=';', encoding='ISO-8859-1',
                                 usecols=['TP_FUNDO', 'CNPJ_FUNDO', 'DENOM_SOCIAL', 'DT_COMPTC', 'VL_PATRIM_LIQ', 
                                          'TP_APLIC', 'VL_MERC_POS_FINAL'])
                dataframes.append(df)

            # Concatenar todos os DataFrames em um único
            dados_fundos_total = pd.concat(dataframes, ignore_index=True)

            # Renomear colunas para melhorar a legibilidade
            dados_fundos_total = dados_fundos_total.rename(columns={
                'TP_FUNDO': 'Tipo Fundo',
                'CNPJ_FUNDO': 'CNPJ Fundo',
                'DENOM_SOCIAL': 'Denominação Social',
                'DT_COMPTC': 'Data Competência',
                'VL_PATRIM_LIQ': 'Patrimônio Líquido',
                'TP_APLIC': 'Tipo Aplicação',
                'VL_MERC_POS_FINAL': 'Valor Mercado Posição Final',
            })

            # Calcular o percentual de aplicação em relação ao patrimônio líquido
            if 'Valor Mercado Posição Final' in dados_fundos_total.columns and 'Patrimônio Líquido' in dados_fundos_total.columns:
                dados_fundos_total['Percentual Aplicação'] = (
                    dados_fundos_total['Valor Mercado Posição Final'] / dados_fundos_total['Patrimônio Líquido']
                ) * 100

            return dados_fundos_total
    else:
        st.error(f"Erro ao baixar dados de {ano}-{mes:02}. URL: {url}")
        return None

# Layout da App Streamlit
st.title("Dashboard de Fundos CVM")

# Inputs para o ano e mês
ano = st.selectbox("Selecione o Ano", options=['2024', '2023'])
mes = st.selectbox("Selecione o Mês", options=range(1, 13), format_func=lambda x: f"{x:02}")

# Botão para carregar dados
if st.button("Carregar Dados"):
    df = processar_dados(ano, mes)
    if df is not None:
        st.write("Dados Carregados com Sucesso!")
        
        # Exibir uma amostra dos dados
        st.subheader("Amostra dos Dados")
        st.dataframe(df.head())

        # Se o DataFrame estiver muito grande, solicite ao usuário para carregar tudo
        if len(df) > 10000:
            st.warning("Os dados são muito grandes. Apenas uma amostra foi carregada.")
            if st.checkbox("Carregar todos os dados? Isso pode demorar."):
                st.write("Carregando todos os dados...")
                st.dataframe(df)

        # Opções de Visualização
        st.subheader("Visualizações")
        
        # Escolha do tipo de gráfico
        chart_type = st.selectbox("Escolha o Tipo de Gráfico", ["Barras", "Pizza"])
        
        # Agrupamento por "Tipo Aplicação" e cálculo da soma percentual
        resumo_aplicacao = df.groupby("Tipo Aplicação")['Percentual Aplicação'].sum().sort_values(ascending=False)
        
        # Exibir o gráfico escolhido
        if chart_type == "Barras":
            st.bar_chart(resumo_aplicacao)
        elif chart_type == "Pizza":
            st.pyplot(resumo_aplicacao.plot(kind='pie', autopct='%1.1f%%').get_figure())
