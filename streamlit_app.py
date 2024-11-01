import streamlit as st
import requests
import zipfile
import io
import pandas as pd

# Function to download and process data for a specified year and month
def processar_dados(ano, mes):
    # URL for the CVM ZIP file for the specified year and month
    url = f'https://dados.cvm.gov.br/dados/FI/DOC/CDA/DADOS/cda_fi_{ano}{mes:02}.zip'
    st.write(f"Baixando dados de {ano}-{mes:02}...")

    # Download the ZIP file
    response = requests.get(url)

    # Check if the download was successful
    if response.status_code == 200:
        # Open the ZIP file
        with zipfile.ZipFile(io.BytesIO(response.content), 'r') as arquivo_zip:
            dataframes = []
            
            # Iterate over all CSV files in the ZIP
            for file_name in arquivo_zip.namelist():
                df = pd.read_csv(arquivo_zip.open(file_name), sep=';', encoding='ISO-8859-1')
                dataframes.append(df)

            # Combine all DataFrames into one
            dados_fundos_total = pd.concat(dataframes, ignore_index=True)

            # Rename columns
            dados_fundos_total = dados_fundos_total.rename(columns={
                'TP_FUNDO': 'Tipo Fundo',
                'CNPJ_FUNDO': 'CNPJ Fundo',
                'DENOM_SOCIAL': 'Denominação Social',
                'DT_COMPTC': 'Data Competência',
                'VL_PATRIM_LIQ': 'Patrimônio Líquido',
                'TP_APLIC': 'Tipo Aplicação',
                'VL_MERC_POS_FINAL': 'Valor Mercado Posição Final',
                # Add more renaming as needed
            })

            # Drop unnecessary columns
            colunas_para_excluir = ['Quantidade Venda Negociada', 'Quantidade Aquisição Negociada', 'Quantidade Posição Final']
            dados_fundos_total = dados_fundos_total.drop(columns=colunas_para_excluir, errors='ignore')

            # Calculate application percentage relative to net assets
            if 'Valor Mercado Posição Final' in dados_fundos_total.columns and 'Patrimônio Líquido' in dados_fundos_total.columns:
                dados_fundos_total['Percentual Aplicação'] = (
                    dados_fundos_total['Valor Mercado Posição Final'] / dados_fundos_total['Patrimônio Líquido']
                ) * 100

            return dados_fundos_total
    else:
        st.error(f"Erro ao baixar dados de {ano}-{mes:02}. URL: {url}")
        return None

# Streamlit App Layout
st.title("Dashboard de Fundos CVM")

# User inputs for year and month
ano = st.selectbox("Selecione o Ano", options=['2024', '2023'])
mes = st.selectbox("Selecione o Mês", options=range(1, 13), format_func=lambda x: f"{x:02}")

# Button to load data
if st.button("Carregar Dados"):
    df = processar_dados(ano, mes)
    if df is not None:
        st.write("Dados Carregados com Sucesso!")
        
        # Display data sample
        st.subheader("Amostra dos Dados")
        st.dataframe(df.head())

        # Plotting options
        st.subheader("Visualizações")
        
        # Select options for visualizations
        chart_type = st.selectbox("Escolha o Tipo de Gráfico", ["Barras", "Pizza"])
        
        # Group data by "Tipo Aplicação" and calculate percentage sum
        resumo_aplicacao = df.groupby("Tipo Aplicação")['Percentual Aplicação'].sum().sort_values(ascending=False)
        
        if chart_type == "Barras":
            st.bar_chart(resumo_aplicacao)
        elif chart_type == "Pizza":
            st.pyplot(resumo_aplicacao.plot(kind='pie', autopct='%1.1f%%').get_figure())
