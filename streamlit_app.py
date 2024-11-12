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

# Função para processar e baixar dados de um mês específico e já aplicar o filtro pelo CNPJ
@st.cache_data(show_spinner=False)
def baixar_dados_mes_filtrado(ano, mes, cnpj_especifico):
    url = f'https://dados.cvm.gov.br/dados/FI/DOC/CDA/DADOS/cda_fi_{ano}{mes:02}.zip'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content), 'r') as arquivo_zip:
            dataframes = []
            for file in arquivo_zip.namelist():
                try:
                    df = pd.read_csv(arquivo_zip.open(file), sep=';', encoding='ISO-8859-1')
                    
                    # Renomear colunas e selecionar apenas as relevantes
                    df = df.rename(columns={
                        'CNPJ_FUNDO': 'CNPJ Fundo', 'VL_PATRIM_LIQ': 'Patrimônio Líquido',
                        'VL_MERC_POS_FINAL': 'Valor Mercado Posição Final', 'DT_COMPTC': 'Data Competência',
                        'DENOM_SOCIAL': 'Denominação Social', 'TP_APLIC': 'Tipo Aplicação', 
                        'TP_ATIVO': 'Tipo Ativo',
                    })
                    
                    # Filtrar pelo CNPJ especificado
                    df_filtrado = df[df['CNPJ Fundo'] == cnpj_especifico]
                    
                    # Adicionar à lista somente se houver dados relevantes
                    if not df_filtrado.empty:
                        # Transformar a data de competência para o nome do mês
                        df_filtrado['Data Competência'] = pd.to_datetime(df_filtrado['Data Competência']).dt.strftime('%B')
                        dataframes.append(df_filtrado)
                except Exception as e:
                    st.warning(f"Erro ao ler o arquivo {file} no mês {mes:02}: {e}")
            
            # Concatenar apenas os dados filtrados
            return pd.concat(dataframes, ignore_index=True) if dataframes else None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao baixar os dados do mês {mes:02}: {e}")
        return None

# Baixar e filtrar dados para o ano selecionado de forma incremental, mês a mês
dados_fundos_total = []
for mes in range(1, 13):
    with st.spinner(f"Baixando dados para {ano}-{mes:02}..."):
        dados_mes = baixar_dados_mes_filtrado(ano, mes, cnpj_especifico)
        if dados_mes is not None:
            dados_fundos_total.append(dados_mes)

# Concatenar os dados de todos os meses filtrados
if dados_fundos_total:
    dados_fundos_total = pd.concat(dados_fundos_total, ignore_index=True)
else:
    st.warning("Nenhum dado foi encontrado para o CNPJ informado ou houve erro no download.")
    dados_fundos_total = None

# Verificar e processar os dados se disponíveis
if dados_fundos_total is not None and not dados_fundos_total.empty:
    # Agrupar dados para composição de todos os meses
    df_por_mes = dados_fundos_total.groupby(['Data Competência', 'Tipo Aplicação'])['Valor Mercado Posição Final'].sum().unstack().fillna(0)
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
    st.write("Nenhum dado encontrado para o CNPJ informado ou houve um erro no processamento.")
