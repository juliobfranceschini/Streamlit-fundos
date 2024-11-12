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

# Função para processar e baixar dados de todos os meses do ano selecionado
@st.cache_data
def processar_dados(ano):
    todos_dados = []
    for mes in range(1, 13):
        url = f'https://dados.cvm.gov.br/dados/FI/DOC/CDA/DADOS/cda_fi_{ano}{mes:02}.zip'
        response = requests.get(url)
        
        if response.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(response.content), 'r') as arquivo_zip:
                dataframes = [pd.read_csv(arquivo_zip.open(file), sep=';', encoding='ISO-8859-1') 
                              for file in arquivo_zip.namelist()]
                dados_mes = pd.concat(dataframes, ignore_index=True)
                
                # Renomear colunas conforme necessário
                dados_mes = dados_mes.rename(columns={
                    'TP_FUNDO': 'Tipo Fundo', 'CNPJ_FUNDO': 'CNPJ Fundo',
                    'VL_PATRIM_LIQ': 'Patrimônio Líquido', 'VL_MERC_POS_FINAL': 'Valor Mercado Posição Final',
                    'DT_COMPTC': 'Data Competência', 'DENOM_SOCIAL': 'Denominação Social',
                    'TP_APLIC': 'Tipo Aplicação', 'TP_ATIVO': 'Tipo Ativo',
                    # Adicione outras renomeações conforme necessário
                })
                todos_dados.append(dados_mes)
    
    # Concatenar todos os DataFrames em um único
    if todos_dados:
        return pd.concat(todos_dados, ignore_index=True)
    else:
        st.error("Erro ao baixar os dados.")
        return None

# Processamento dos dados para o ano selecionado
dados_fundos_total = processar_dados(ano)

if dados_fundos_total is not None:
    # Filtrar pelo CNPJ especificado
    filtro_cnpj = dados_fundos_total[dados_fundos_total['CNPJ Fundo'] == cnpj_especifico].copy()
    
    # Verificar a existência do DataFrame filtrado
    if not filtro_cnpj.empty:
        filtro_cnpj['Data Competência'] = filtro_cnpj['Data Competência'].str[:10]

        # Ajustar 'Tipo Aplicação' usando 'Tipo Título Público' quando relevante
        if 'Tipo Título Público' in filtro_cnpj.columns:
            filtro_cnpj.loc[
                (filtro_cnpj['Tipo Aplicação'] == 'Títulos Públicos') & 
                (filtro_cnpj['Tipo Título Público'].notna()),
                'Tipo Aplicação'
            ] = filtro_cnpj['Tipo Título Público']

        # Agrupar dados para composição de todos os meses
        df_por_mes = filtro_cnpj.groupby(['Data Competência', 'Tipo Aplicação'])['Valor Mercado Posição Final'].sum().unstack().fillna(0)
        df_por_mes.index = pd.to_datetime(df_por_mes.index).strftime('%B')
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
        
        # Adicionar os percentuais nas barras, com textos centralizados
        for c in ax.containers:
            labels = [f'{v:.1f}%' if v >= 0.5 else '' for v in c.datavalues]
            ax.bar_label(c, labels=labels, label_type='center', fontsize=10)
        
        st.pyplot(fig)
    else:
        st.write("Nenhum dado encontrado para o CNPJ informado.")
