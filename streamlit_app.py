import streamlit as st
import pandas as pd
import zipfile
import io
import requests
import matplotlib.pyplot as plt

# Função para carregar e concatenar os dados a partir de vários arquivos ZIP
def carregar_dados_cvm(ano, mes):
    url = f'https://dados.cvm.gov.br/dados/FI/DOC/CDA/DADOS/cda_fi_{ano}{mes}.zip'
    response = requests.get(url)
    dataframes = []
    with zipfile.ZipFile(io.BytesIO(response.content), 'r') as arquivo_zip:
        for file_name in arquivo_zip.namelist():
            df = pd.read_csv(arquivo_zip.open(file_name), sep=';', encoding='ISO-8859-1')
            dataframes.append(df)
    dados_fundos_total = pd.concat(dataframes, ignore_index=True)
    return dados_fundos_total

# Renomear colunas e limpar dados
def limpar_dados(dados_fundos_total):
    dados_fundos_total = dados_fundos_total.rename(columns={
 'TP_FUNDO': 'Tipo Fundo',
    'CNPJ_FUNDO': 'CNPJ Fundo',
    'DENOM_SOCIAL': 'Denominação Social',
    'DT_COMPTC': 'Data Competência',
    'ID_DOC': 'ID Documento',
    'VL_PATRIM_LIQ': 'Patrimônio Líquido',
    'TP_APLIC': 'Tipo Aplicação',
    'TP_ATIVO': 'Tipo Ativo',
    'EMISSOR_LIGADO': 'Emissor Ligado',
    'TP_NEGOC': 'Tipo Negociação',
    'QT_VENDA_NEGOC': 'Quantidade Venda Negociada',
    'VL_VENDA_NEGOC': 'Valor Venda Negociada',
    'QT_AQUIS_NEGOC': 'Quantidade Aquisição Negociada',
    'VL_AQUIS_NEGOC': 'Valor Aquisição Negociada',
    'QT_POS_FINAL': 'Quantidade Posição Final',
    'VL_MERC_POS_FINAL': 'Valor Mercado Posição Final',
    'VL_CUSTO_POS_FINAL': 'Valor Custo Posição Final',
    'DT_CONFID_APLIC': 'Data Confidencial Aplicação',
    'CD_ATIVO': 'Código Ativo',
    'DS_ATIVO': 'Descrição Ativo',
    'DT_VENC': 'Data Vencimento',
    'PF_PJ_EMISSOR': 'Pessoa Física/Jurídica Emissor',
    'CPF_CNPJ_EMISSOR': 'CPF/CNPJ Emissor',
    'EMISSOR': 'Emissor',
    'RISCO_EMISSOR': 'Risco Emissor',
    'CD_SELIC': 'Código Selic',
    'DT_INI_VIGENCIA': 'Data Início Vigência',
    'CD_PAIS': 'Código País',
    'PAIS': 'País',
    'CD_BV_MERC': 'Código BV Mercado',
    'BV_MERC': 'BV Mercado',
    'TP_TITPUB': 'Tipo Título Público',
    'CD_ISIN': 'Código ISIN',
    'DT_EMISSAO': 'Data Emissão',
    'CNPJ_FUNDO_COTA': 'CNPJ Fundo Cota',
    'NM_FUNDO_COTA': 'Nome Fundo Cota',
    'CD_SWAP': 'Código Swap',
    'DS_SWAP': 'Descrição Swap',
    'DT_FIM_VIGENCIA': 'Data Fim Vigência',
    'CNPJ_EMISSOR': 'CNPJ Emissor',
    'TITULO_POSFX': 'Título Pós-Fixado',
    'CD_INDEXADOR_POSFX': 'Código Indexador Pós-Fixado',
    'DS_INDEXADOR_POSFX': 'Descrição Indexador Pós-Fixado',
    'PR_INDEXADOR_POSFX': 'Percentual Indexador Pós-Fixado',
    'PR_CUPOM_POSFX': 'Percentual Cupom Pós-Fixado',
    'PR_TAXA_PREFX': 'Percentual Taxa Pré-Fixada',
    'AG_RISCO': 'Agência de Risco',
    'DT_RISCO': 'Data Risco',
    'GRAU_RISCO': 'Grau de Risco',
    'TITULO_CETIP': 'Título Cetip',
    'TITULO_GARANTIA': 'Título Garantia',
    'CNPJ_INSTITUICAO_FINANC_COOBR': 'CNPJ Instituição Financeira Coobrigada',
    'INVEST_COLETIVO': 'Investimento Coletivo',
    'INVEST_COLETIVO_GESTOR': 'Gestor Investimento Coletivo',
    'CD_ATIVO_BV_MERC': 'Código Ativo BV Mercado',
    'DS_ATIVO_EXTERIOR': 'Descrição Ativo Exterior',
    'QT_ATIVO_EXTERIOR': 'Quantidade Ativo Exterior',
    'VL_ATIVO_EXTERIOR': 'Valor Ativo Exterior',
        # Continue renomeando conforme necessário...
    })

    # Excluir colunas específicas
    colunas_para_excluir = ['Quantidade Venda Negociada', 'Quantidade Aquisição Negociada',
                            'Quantidade Posição Final', 'Quantidade Ativo Exterior', 'Emissor Ligado',
                            'Tipo Negociação', 'Valor Aquisição Negociada', 'Valor Venda Negociada',
                            'Data Confidencial Aplicação', 'Risco Emissor', 'Código Selic',
                            'Data Início Vigência', 'Código ISIN', 'Data Fim Vigência','Código BV Mercado','BV Mercado','Valor Custo Posição Final','Pessoa Física/Jurídica Emissor','Código País','País','Código Indexador Pós-Fixado','Descrição Swap','Código Swap','Descrição Indexador Pós-Fixado','Percentual Indexador Pós-Fixado', 'Percentual Cupom Pós-Fixado', 'Percentual Taxa Pré-Fixada',  'Agência de Risco',  'Data Risco',  'Grau de Risco', 'Título Cetip', 'Título Garantia',  'CNPJ Instituição Financeira Coobrigada',  'Investimento Coletivo', 'Gestor Investimento Coletivo', 'Código Ativo BV Mercado', 'Descrição Ativo Exterior', 'Quantidade Ativo Exterior', 'Valor Ativo Exterior']
    dados_fundos_total = dados_fundos_total.drop(columns=colunas_para_excluir)
    return dados_fundos_total

# Função para comparar a composição de dois meses
def comparar_meses(df_mes1, df_mes2):
    df_agrupado_mes1 = df_mes1.groupby('Tipo Aplicação')['Valor Mercado Posição Final'].sum().reset_index()
    df_agrupado_mes2 = df_mes2.groupby('Tipo Aplicação')['Valor Mercado Posição Final'].sum().reset_index()

    # Combinar os dados para comparar
    comparacao = pd.merge(df_agrupado_mes1, df_agrupado_mes2, on='Tipo Aplicação', how='outer', suffixes=('_mes1', '_mes2'))
    
    # Preencher valores NaN com 0
    comparacao = comparacao.fillna(0)

    # Calcular a variação percentual
    comparacao['Variação (%)'] = ((comparacao['Valor Mercado Posição Final_mes2'] - comparacao['Valor Mercado Posição Final_mes1']) / comparacao['Valor Mercado Posição Final_mes1']) * 100

    return comparacao

# Título do Dashboard
st.title("Fundos de Investimento - Comparação entre Meses")

# Parâmetros para o usuário escolher os dois meses
st.sidebar.header("Selecione os Meses para Comparação")
ano = st.sidebar.selectbox("Selecione o Ano:", ["2024", "2023"])
mes1 = st.sidebar.selectbox("Selecione o Primeiro Mês:", ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"])
mes2 = st.sidebar.selectbox("Selecione o Segundo Mês:", ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"])

# Carregar os dados dos dois meses
dados_mes1 = carregar_dados_cvm(ano, mes1)
dados_mes2 = carregar_dados_cvm(ano, mes2)

# Limpar os dados
dados_mes1 = limpar_dados(dados_mes1)
dados_mes2 = limpar_dados(dados_mes2)

# Exibir as informações básicas do fundo
cnpj_filtro = st.sidebar.text_input("Filtrar por CNPJ do Fundo:")
if cnpj_filtro:
    dados_mes1 = dados_mes1[dados_mes1['CNPJ Fundo'] == cnpj_filtro]
    dados_mes2 = dados_mes2[dados_mes2['CNPJ Fundo'] == cnpj_filtro]

# Exibir os dados filtrados
st.write(f"### Dados de {mes1}/{ano}:")
st.dataframe(dados_mes1[['Denominação Social', 'Tipo Fundo', 'Patrimônio Líquido']].drop_duplicates())

st.write(f"### Dados de {mes2}/{ano}:")
st.dataframe(dados_mes2[['Denominação Social', 'Tipo Fundo', 'Patrimônio Líquido']].drop_duplicates())

# Comparar a composição dos dois meses
comparacao = comparar_meses(dados_mes1, dados_mes2)

# Exibir a comparação
st.write("### Comparação da Composição por Tipo de Aplicação:")
st.dataframe(comparacao)

# Gráfico de barras para mostrar a variação percentual
st.write("### Gráfico de Variação Percentual entre os Meses")
fig, ax = plt.subplots()
ax.barh(comparacao['Tipo Aplicação'], comparacao['Variação (%)'], color='skyblue')
ax.set_xlabel('Variação (%)')
ax.set_ylabel('Tipo de Aplicação')
st.pyplot(fig)
