import streamlit as st
import requests
import zipfile
import io
import pandas as pd
import matplotlib.pyplot as plt

# Configuração do título do dashboard
st.title('Dashboard de Composição de Fundos de Investimento')
st.write('Insira o CNPJ do fundo e selecione o ano para visualizar a composição ao longo do ano.')

# Input do CNPJ do fundo e seleção de ano
cnpj_especifico = st.text_input("Digite o CNPJ do fundo", '09.136.668/0001-35')
ano = st.selectbox("Selecione o ano", ['2024'])

# Função para baixar e processar dados brutos do mês (cache dos dados brutos)
@st.cache_data(show_spinner=False)
def baixar_dados_mes_bruto(ano, mes):
    url = f'https://dados.cvm.gov.br/dados/FI/DOC/CDA/DADOS/cda_fi_{ano}{mes:02}.zip'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content), 'r') as arquivo_zip:
            dataframes = []
            for file in arquivo_zip.namelist():
                try:
                    df = pd.read_csv(arquivo_zip.open(file), sep=';', encoding='ISO-8859-1')
                    dataframes.append(df)
                except Exception as e:
                    st.warning(f"Erro ao ler o arquivo {file} no mês {mes:02}: {e}")
            dados_mes = pd.concat(dataframes, ignore_index=True)
            dados_mes = dados_mes.rename(columns={
                'CNPJ_FUNDO': 'CNPJ Fundo', 'VL_PATRIM_LIQ': 'Patrimônio Líquido',
                'VL_MERC_POS_FINAL': 'Valor Mercado Posição Final', 'DT_COMPTC': 'Data Competência',
                'DENOM_SOCIAL': 'Denominação Social', 'TP_APLIC': 'Tipo Aplicação', 
                'TP_ATIVO': 'Tipo Ativo',
            })
            return dados_mes
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao baixar os dados do mês {mes:02}: {e}")
        return None

# Função para carregar e concatenar os dados brutos de todos os meses de um ano
@st.cache_data(show_spinner=False)
def carregar_dados_ano(ano):
    todos_dados = []
    for mes in range(1, 13):
        dados_mes = baixar_dados_mes_bruto(ano, mes)
        if dados_mes is not None:
            todos_dados.append(dados_mes)
    if todos_dados:
        dados_ano = pd.concat(todos_dados, ignore_index=True)
        dados_ano['Data Competência'] = pd.to_datetime(dados_ano['Data Competência']).dt.strftime('%B')
        return dados_ano
    else:
        st.warning("Nenhum dado foi encontrado para o ano selecionado.")
        return pd.DataFrame()

# Carregar os dados brutos do ano selecionado uma vez
dados_ano_total = carregar_dados_ano(ano)

# Filtrar pelo CNPJ especificado sem recarregar dados
if not dados_ano_total.empty:
    dados_filtro_cnpj = dados_ano_total[dados_ano_total['CNPJ Fundo'] == cnpj_especifico].copy()
    
    if not dados_filtro_cnpj.empty:
        # Agrupar dados para composição de todos os meses
        df_por_mes = dados_filtro_cnpj.groupby(['Data Competência', 'Tipo Aplicação'])['Valor Mercado Posição Final'].sum().unstack().fillna(0)
        df_por_mes_percentual = df_por_mes.divide(df_por_mes.sum(axis=1).replace(0, 1), axis=0) * 100
        df_por_mes_percentual = df_por_mes_percentual.apply(lambda x: x.where(x >= 0.5, other=0))

        # Ordenar colunas globalmente
        global_totals = df_por_mes_percentual.sum(axis=0).sort_values(ascending=False).index
        df_por_mes_percentual_sorted = df_por_mes_percentual[global_totals]

        # Plot do gráfico com todos os meses
        fig, ax = plt.subplots(figsize=(12, 6))
        df_por_mes_percentual_sorted.plot(kind='bar', stacked=True, ax=ax)
        ax.set_title(f'Composição do Fundo {cnpj_especifico} - {ano}')
        ax.get_yaxis().set_visible(False)
        ax.set_xlabel('')
        
        # Adicionar os percentuais nas barras
        for c in ax.containers:
            labels = [f'{v:.1f}%' if v >= 0.5 else '' for v in c.datavalues]
            ax.bar_label(c, labels=labels, label_type='center', fontsize=10)
        
        st.pyplot(fig)
    else:
        st.write("Nenhum dado encontrado para o CNPJ informado.")
else:
    st.write("Nenhum dado disponível para o ano selecionado.")
