import streamlit as st
import pandas as pd
import zipfile
import io
import requests

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
    colunas_para_excluir = ['Denominação Social','Quantidade Venda Negociada', 'Quantidade Aquisição Negociada',
                            'Quantidade Posição Final', 'Quantidade Ativo Exterior', 'Emissor Ligado',
                            'Tipo Negociação', 'Valor Aquisição Negociada', 'Valor Venda Negociada',
                            'Data Confidencial Aplicação', 'Risco Emissor', 'Código Selic',
                            'Data Início Vigência', 'Código ISIN', 'Data Fim Vigência','Código BV Mercado','BV Mercado','Valor Custo Posição Final','Pessoa Física/Jurídica Emissor','Código País','País','Código Indexador Pós-Fixado','Descrição Swap','Código Swap','Descrição Indexador Pós-Fixado','Percentual Indexador Pós-Fixado', 'Percentual Cupom Pós-Fixado', 'Percentual Taxa Pré-Fixada',  'Agência de Risco',  'Data Risco',  'Grau de Risco', 'Título Cetip', 'Título Garantia',  'CNPJ Instituição Financeira Coobrigada',  'Investimento Coletivo', 'Gestor Investimento Coletivo', 'Código Ativo BV Mercado', 'Descrição Ativo Exterior', 'Quantidade Ativo Exterior', 'Valor Ativo Exterior']

    dados_fundos_total = dados_fundos_total.drop(columns=colunas_para_excluir)

    # Remover colunas onde todos os valores são nulos
    dados_fundos_total = dados_fundos_total.dropna(axis=1, how='all')


    return dados_fundos_total

# Título do Dashboard
st.title("Fundos de Investimento - CVM")

# Parâmetros para o usuário escolher o ano e o mês
st.sidebar.header("Parâmetros de Data")
ano = st.sidebar.selectbox("Selecione o Ano:", ["2024", "2023"])
mes = st.sidebar.selectbox("Selecione o Mês:", ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"])

# Carregar os dados usando a função
dados_fundos_total = carregar_dados_cvm(ano, mes)

# Limpar os dados
dados_fundos_total = limpar_dados(dados_fundos_total)

# Criar filtros no dashboard para o usuário escolher
st.sidebar.header("Filtros")
cnpj_filtro = st.sidebar.text_input("Filtrar por CNPJ do Fundo:")
tipo_aplicacao_filtro = st.sidebar.multiselect("Filtrar por Tipo de Aplicação:",
                                               options=dados_fundos_total['Tipo Aplicação'].unique())

# Aplicar os filtros
dados_filtrados = dados_fundos_total

if cnpj_filtro:
    dados_filtrados = dados_filtrados[dados_filtrados['CNPJ Fundo'] == cnpj_filtro]

# Exibir as informações básicas do fundo, se filtrado
if cnpj_filtro and not dados_filtrados.empty:
    fundo_info = dados_filtrados.iloc[0]  # Pega a primeira linha com as informações básicas
    st.write("### Informações do Fundo:")
    st.write(f"**Denominação Social**: {fundo_info['Denominação Social']}")
    st.write(f"**Tipo Fundo**: {fundo_info['Tipo Fundo']}")
    st.write(f"**Patrimônio Líquido**: R$ {fundo_info['Patrimônio Líquido']:,}")

if tipo_aplicacao_filtro:
    dados_filtrados = dados_filtrados[dados_filtrados['Tipo Aplicação'].isin(tipo_aplicacao_filtro)]

# Exibir os dados filtrados
st.write("### Dados Filtrados:")
st.dataframe(dados_filtrados)


import matplotlib.pyplot as plt

# Gráfico de Pizza
st.write("### Gráfico de Distribuição por Tipo de Aplicação:")

# Filtrar dados para remover valores nulos e negativos
grafico_dados = dados_filtrados.groupby('Tipo Aplicação')['Valor Mercado Posição Final'].sum().reset_index()
grafico_dados = grafico_dados[grafico_dados['Valor Mercado Posição Final'] > 0]  # Filtra valores positivos

# Verificar se existem dados após o filtro
if not grafico_dados.empty:
    # Criar o gráfico de pizza sem percentuais nas fatias
    fig, ax = plt.subplots()
    wedges, texts = ax.pie(
        grafico_dados['Valor Mercado Posição Final'],
        labels=None,  # Não usar labels diretamente nas fatias
        startangle=90,
        wedgeprops={'linewidth': 1, 'edgecolor': 'white'}  # Adicionar bordas brancas para melhor visualização
    )

    # Criar a legenda com o percentual calculado manualmente
    legenda = [
        f'{label}: {percent:.1f}%' for label, percent in zip(
            grafico_dados['Tipo Aplicação'],
            100 * grafico_dados['Valor Mercado Posição Final'] / grafico_dados['Valor Mercado Posição Final'].sum()
        )
    ]

    # Adicionar a legenda externa com percentuais
    ax.legend(wedges, legenda, title="Tipo de Aplicação", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    # Ajustar o gráfico para exibir bem a legenda
    plt.tight_layout()

    # Exibir o gráfico no Streamlit
    st.pyplot(fig)

