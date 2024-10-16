from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly
import time

app = Flask(__name__)








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

# Função para obter preços atuais e mini gráficos
def obter_precos_e_volumes():
    precos_e_volumes = {}
    mini_graficos = {}

    for cripto in logos_criptomoedas.keys():
        ticker = yf.Ticker(cripto)
        try:
            # Obter dados históricos
            hist = ticker.history(period="5d", interval="1h")
            if hist.empty:
                continue
            
            # Preço Atual
            preco_atual = hist['Close'].iloc[-1]
            preco_semanal = hist['Close'].iloc[0]
            percentual_variacao = ((preco_atual - preco_semanal) / preco_semanal) * 100
            
            # Obter volume de mercado
            info = ticker.info
            volume_mercado = info.get('volume', 0)

            # Criar mini gráfico com Plotly
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
            mini_graficos[cripto] = fig.to_html(full_html=False)

            # Armazenar preço e volume no dicionário
            precos_e_volumes[cripto] = {
                'preco': preco_atual,
                'volume': volume_mercado,
                'percentual_variacao': percentual_variacao,
                'grafico': mini_graficos[cripto]
            }
        except Exception as e:
            print(f"Erro ao obter dados para {cripto}: {e}")
    
    return precos_e_volumes



@app.route('/')
def index():
    precos_e_volumes = obter_precos_e_volumes()  # Chamando a função correta
    return render_template('index.html', precos=precos_e_volumes, logos_criptomoedas=logos_criptomoedas)

@app.route('/login')
def login():
    return render_template('login.html')


# Página de previsão de preços
@app.route('/previsao/<cripto>')
def previsao_precos(cripto):
    # Lógica para previsão aqui (como no código Streamlit)
    periodo_historico = request.args.get('periodo', '1 ano')
    periodos = int(request.args.get('dias', 90))
    
    df = yf.download(cripto, period='5y', interval='1d')
    df.reset_index(inplace=True)
    df.rename(columns={"Date": "ds", "Close": "y"}, inplace=True)

    modelo = Prophet()
    modelo.fit(df)

    futuro = modelo.make_future_dataframe(periods=periodos)
    previsao = modelo.predict(futuro)

    fig = plot_plotly(modelo, previsao)
    fig.update_layout(autosize=True, height=400, width=800, margin=dict(l=10, r=10, t=40, b=30))

    return render_template('previsao.html', cripto=cripto, grafico=fig.to_html(full_html=False), previsao=previsao.tail(periodos))

if __name__ == '__main__':
    app.run(debug=True)
