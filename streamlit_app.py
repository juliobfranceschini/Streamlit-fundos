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

# Função para baixar e processar dados de um mês específico aplicando filtro de CNPJ e agregando resultados
@st.cache_data(show_spinner=False)
def processar_dados_mes_filtrado(ano, mes, cnpj_especifico):
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
                    
                    # Transformar a data de competência para o nome do mês e agregar
                    if not df_filtrado.empty:
                        df_filtrado['Data Competência'] = pd.to_datetime(df_filtrado['Data Competência']).dt.strftime('%B')
                        df_agg = df_filtrado.groupby(['Data Competência', 'Tipo Aplicação'])['Valor Mercado Posição Final'].sum()
                        dataframes.append(df_agg)
                except Exception as e:
                    st.warning(f"Erro ao ler o arquivo {file} no mês {mes:02}: {e}")
            
            # Concatenar e retornar os dados agregados do mês
            return pd.concat(dataframes) if dataframes else None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao baixar os dados do mês {mes:02}: {e}")
        return None

# Inicializar DataFrame para acumular dados agregados por mês
dados_acumulados = pd.DataFrame()

# Processamento incremental: carregar e agregar dados mês a mês
for mes in range(1, 13):
    with st.spinner(f"Baixando e processando dados para {ano}-{mes:02}..."):
        dados_mes = processar_dados_mes_filtrado(ano, mes, cnpj_especifico)
        if dados_mes is not None:
            dados_acumulados = pd.concat([dados_acumulados, dados_mes], axis=0)

# Verificar e processar os dados se disponíveis
if not dados_acumulados.empty:
    # Reset index to have 'Data Competência' and 'Tipo Aplicação' as columns
    dados_acumulados = dados_acumulados.reset_index()
    df_por_mes = dados_acumulados.pivot(index='Data Competência', columns='Tipo Aplicação', values='Valor Mercado Posição Final').fillna(0)

    # Calcular o percentual de cada aplicação em relação ao total do mês
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
