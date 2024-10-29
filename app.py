import streamlit as st
import yfinance as yf
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly
import plotly.graph_objects as go
import time

# Configuração da página
st.set_page_config(page_title="APMC", page_icon="logo.png", layout="wide")

# Dicionário com URLs dos logos das criptomoedas
logos_criptomoedas = {
    "BTC-USD": "https://cryptologos.cc/logos/bitcoin-btc-logo.png",
    "ETH-USD": "https://cryptologos.cc/logos/ethereum-eth-logo.png",
    "LTC-USD": "https://cryptologos.cc/logos/litecoin-ltc-logo.png",
    "BCH-USD": "https://cryptologos.cc/logos/bitcoin-cash-bch-logo.png",
    "BNB-USD": "https://s2.coinmarketcap.com/static/img/coins/64x64/1839.png",
    "LINK-USD": "https://cryptologos.cc/logos/chainlink-link-logo.png",
    "MATIC-USD": "https://cryptologos.cc/logos/polygon-matic-logo.png",
    "NUC-USD": "https://global.discourse-cdn.com/nubank/original/4X/a/0/f/a0f05863f4539896223167b6726a9a5d616f2253.png",
    "SOL-USD": "https://cryptologos.cc/logos/solana-sol-logo.png",
    "XRP-USD": "https://s2.coinmarketcap.com/static/img/coins/64x64/52.png"
}

# Função para obter preços atuais e mini gráfico da semana
def obter_precos_atuais():
    precos = {}
    mini_graficos = {}
    for cripto in logos_criptomoedas.keys():
        ticker = yf.Ticker(cripto)
        try:
            hist = ticker.history(period="5d", interval="1h")
            if hist.empty:
                continue
            preco_atual = hist['Close'].iloc[-1]
            preco_semanal = hist['Close'].iloc[0]
            percentual_variacao = ((preco_atual - preco_semanal) / preco_semanal) * 100

            # Criar mini gráfico
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='Preço'))
            fig.update_layout(
                showlegend=False,
                xaxis_title='',
                yaxis_title='',
                height=80,
                width=150,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=False, showticklabels=False)
            )
            mini_graficos[cripto] = fig

            precos[cripto] = {
                'preco': preco_atual,
                'percentual_variacao': percentual_variacao,
                'grafico': mini_graficos[cripto]
            }
        except Exception as e:
            st.error(f"Erro ao obter dados para {cripto}: {e}")

    return precos

# Adicionar logo no cabeçalho

# Página inicial
def mostrar_precos_atuais():
    st.title("Preços Atuais das Criptomoedas")
    st.write("Clique na criptomoeda para fazer a previsão de preços.")

    precos = obter_precos_atuais()

    for i, (cripto, dados) in enumerate(precos.items()):
        col1, col2, col3 = st.columns([1, 3, 2])
        with col1:
            if st.button("", key=f"{cripto}button{i}", help="Clique para previsão"):
                st.session_state['criptomoeda_selecionada'] = cripto
                st.session_state['pagina'] = 'previsao'
                st.experimental_rerun()
        with col2:
            st.image(logos_criptomoedas[cripto], width=40)
            st.write(f"{cripto}:", f"${dados['preco']:.2f}")
            st.markdown(
                f"*Variação:* <span style='color:{'green' if dados['percentual_variacao'] > 0 else 'red'};'>{dados['percentual_variacao']:.2f}%</span>",
                unsafe_allow_html=True)
        with col3:
            st.plotly_chart(dados['grafico'], use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

    # Atualiza a página a cada 10 segundos
    time.sleep(10)
    st.experimental_rerun()

# Página de previsão
def previsao_precos():
    criptomoeda = st.session_state['criptomoeda_selecionada']
    st.title(f"Previsão de Preços: {criptomoeda}")

    periodo_historico = st.selectbox("Selecione o período histórico de dados",
                                     ["1 ano", "2 anos", "5 anos", "Máximo"])

    periodo_mapeamento = {
        "1 ano": "2023-08-15",
        "2 anos": "2022-08-15",
        "5 anos": "2019-08-15",
        "Máximo": "2010-01-01"
    }

    intervalo_dados = st.selectbox("Selecione o intervalo dos dados", ["1d", "5d", "1mo"])

    periodos = st.slider("Selecione o período de previsão (dias)", 30, 365, 90)

    if st.button("Iniciar Previsão"):
        with st.spinner("Baixando dados e treinando o modelo..."):
            df = yf.download(criptomoeda, start=periodo_mapeamento[periodo_historico],
                             end=pd.Timestamp.today().strftime('%Y-%m-%d'), interval=intervalo_dados)
            df.reset_index(inplace=True)

            df.rename(columns={"Date": "ds", "Close": "y"}, inplace=True)

            modelo = Prophet()
            modelo.fit(df)

            futuro = modelo.make_future_dataframe(periods=periodos)
            previsao = modelo.predict(futuro)

            fig = plot_plotly(modelo, previsao)

            # Ajusta o tamanho do gráfico para dispositivos móveis
            fig.update_layout(
                autosize=True,
                height=400,  # Ajuste conforme necessário
                width=300,  # Ajuste conforme necessário
                margin=dict(l=10, r=10, t=40, b=30)  # Ajuste das margens
            )

            st.plotly_chart(fig, use_container_width=True)

            # Renomear as colunas da tabela
            previsao.rename(columns={
                'ds': 'data',
                'yhat': 'média',
                'yhat_lower': 'mínimo',
                'yhat_upper': 'máximo'
            }, inplace=True)

            st.write("Previsões:")
            st.dataframe(previsao[['data', 'média', 'mínimo', 'máximo']].tail(periodos))

    if st.button("Voltar para a Tela Inicial"):
        st.session_state['pagina'] = 'inicio'
        st.experimental_rerun()

# Controle de navegação entre páginas
if 'pagina' not in st.session_state:
    st.session_state['pagina'] = 'inicio'
    st.session_state['criptomoeda_selecionada'] = None

if st.session_state['pagina'] == 'inicio':
    mostrar_precos_atuais()
elif st.session_state['pagina'] == 'previsao':
    previsao_precos()