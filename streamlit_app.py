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

# Função para processar e baixar dados mês a mês
@st.cache_data
def baixar_dados_mes(ano, mes, cnpj_especifico):
    url = f'https://dados.cvm.gov.br/dados/FI/DOC/CDA/DADOS/cda_fi_{ano}{mes:02}.zip'
    try:
        response = requests.get(url, timeout=10)  # Timeout de 10 segundos
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content), 'r') as arquivo_zip:
            dataframes = [pd.read_csv(arquivo_zip.open(file), sep=';', encoding='ISO-8859-1', 
                                      usecols=['CNPJ_FUNDO', 'VL_PATRIM_LIQ', 'VL_MERC_POS_FINAL', 
                                               'DT_COMPTC', 'DENOM_SOCIAL', 'TP_APLIC', 'TP_ATIVO']) 
                          for file in arquivo_zip.namelist()]
            dados_mes = pd.concat(dataframes, ignore_index=True)
            dados_mes = dados_mes.rename(columns={
                'CNPJ_FUNDO': 'CNPJ Fundo', 'VL_PATRIM_LIQ': 'Patrimônio Líquido',
                'VL_MERC_POS_FINAL': 'Valor Mercado Posição Final', 'DT_COMPTC': 'Data Competência',
                'DENOM_SOCIAL': 'Denominação Social', 'TP_APLIC': 'Tipo Aplicação', 
                'TP_ATIVO': 'Tipo Ativo',
            })
            # Filtrar pelo CNPJ especificado
            dados_filtrados = dados_mes[dados_mes['CNPJ Fundo'] == cnpj_especifico]
            return dados_filtrados if not dados_filtrados.empty else None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao baixar os dados do mês {mes:02}: {e}")
        return None

# Baixar e filtrar dados para o ano selecionado, com opção de parar se não houver dados
todos_dados = []
for mes in range(1, 13):
    with st.spinner(f"Baixando dados para {ano}-{mes:02}..."):
        dados_filtrados = baixar_dados_mes(ano, mes, cnpj_especifico)
        if dados_filtrados is not None:
            todos_dados.append(dados_filtrados)
        else:
            st.write(f"Nenhum dado encontrado para o CNPJ {cnpj_especifico} no mês {mes:02}.")
    # Checar o uso de memória após cada mês
    if len(todos_dados) > 10:  # Condicional para parar caso já tenha 10 meses baixados, adaptável
        break

# Concatenar todos os dados filtrados
if todos_dados:
    dados_fundos_total = pd.concat(todos_dados, ignore_index=True)
else:
    st.warning("Nenhum dado foi encontrado para o CNPJ informado ou houve erro no download.")
    dados_fundos_total = None

# Verificar e processar os dados se disponíveis
if dados_fundos_total is not None and not dados_fundos_total.empty:
    # Ajustar a coluna 'Data Competência' para o formato correto
    dados_fundos_total['Data Competência'] = pd.to_datetime(dados_fundos_total['Data Competência']).dt.strftime('%B')

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
