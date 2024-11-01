from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_pymongo import PyMongo
from datetime import timedelta
from datetime import datetime
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import time
import logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)


app = Flask(__name__)

#------------------- Conexão com Database------------------------

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/APMC'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_PERMANENT'] = True 
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.secret_key = '123456789'

db = SQLAlchemy(app)



with app.app_context():
    db.create_all()
    print("Tabelas criadas com sucesso!")



#------------------- Fução principal------------------------
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
    graficos_normais = {}

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

            # Gráfico Mini
            fig = go.Figure()
            cor_linha = '#0eda0a' if percentual_variacao >= 0 else 'red'
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', line=dict(color=cor_linha), name='Preço'))
            fig.update_layout(
                showlegend=False,
                xaxis_title='',
                yaxis_title='',
                height=80,
                width=150,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=False, showticklabels=False),
                paper_bgcolor='rgba(0,0,0,0)',  
                plot_bgcolor='rgba(0,0,0,0)'    
            )
            mini_graficos[cripto] = fig.to_html(full_html=False)

            # Gráfico Normal
            normal_fig = go.Figure()

            # Defina a cor da linha com base na variação percentual
            cor_linha_normal = '#0eda0a' if percentual_variacao >= 0 else '#ff4d4d'

            # Adiciona a linha e os marcadores para o histórico de preços
            normal_fig.add_trace(go.Scatter(
                x=hist.index,
                y=hist['Close'],
                mode='lines+markers',
                line=dict(color=cor_linha_normal, width=2),
                name='Preço',
                marker=dict(size=6, color=cor_linha_normal, line=dict(width=1, color='white'))
            ))

            # Atualização de layout para um estilo mais sofisticado
            normal_fig.update_layout(
                title=f'Histórico de Preços de {cripto}',  # Título do gráfico
                xaxis_title='Data',
                yaxis_title='Preço $',
                height=450,  # Altura do gráfico
                width=850,   # Largura do gráfico
                margin=dict(l=50, r=50, t=50, b=50),
                xaxis=dict(
                    showgrid=True, gridcolor='rgba(200, 200, 200, 0.5)',
                    title_font=dict(size=16, color='#333333'),
                    tickfont=dict(size=12, color='#333333')
                ),
                yaxis=dict(
                    showgrid=True, gridcolor='rgba(200, 200, 200, 0.5)',
                    title_font=dict(size=16, color='#333333'),
                    tickfont=dict(size=12, color='#333333')
                ),
                title_font=dict(size=18, color='#333333', family="Arial, sans-serif"),
                paper_bgcolor='rgba(245,245,245,0.8)',  # Fundo ligeiramente cinza para um contraste suave
                plot_bgcolor='rgba(250,250,250,1)',     # Fundo do gráfico com tom claro para destacar os dados
                font=dict(family="Arial, sans-serif", size=13, color="#333333")  # Fonte geral do gráfico
            )

            # Converter para HTML para exibição
            graficos_normais[cripto] = normal_fig.to_html(full_html=False)


            # Armazenar preço e volume no dicionário
            precos_e_volumes[cripto] = {
                'preco': preco_atual,
                'volume': volume_mercado,
                'percentual_variacao': percentual_variacao,
                'grafico': mini_graficos[cripto],
                'grafico_normal': graficos_normais[cripto]
            }
        except Exception as e:
            print(f"Erro ao obter dados para {cripto}: {e}")
    
    return precos_e_volumes

@app.route('/atualizar_dados/<cripto>')
def atualizar_dados(cripto):
    precos_e_volumes = obter_precos_e_volumes()
    dados_atualizados = precos_e_volumes.get(cripto, {})
    return jsonify(dados_atualizados)



@app.route('/')
def index():
    precos_e_volumes = obter_precos_e_volumes() 
    return render_template('index.html', precos=precos_e_volumes, logos_criptomoedas=logos_criptomoedas)


@app.route('/previsao/<cripto>', methods=['GET', 'POST'])
def previsao_precos(cripto):
    # Obter preços e volumes
    precos = obter_precos_e_volumes()

    if cripto not in precos:
        flash("Cripto não encontrada", "error")
        return redirect(url_for('index'))

    # Inicializar variáveis
    periodo_historico = '1y'
    periodos = 90
    grafico = None
    previsao = None
    precos_historicos_dict = {}

    # Processar o formulário
    if request.method == 'POST':
        periodo_historico = request.form.get('periodo', '1y')
        try:
            periodos = int(request.form.get('dias', 90))
            if periodos < 30 or periodos > 365:
                periodos = 90  # Valor padrão caso esteja fora do intervalo
        except ValueError:
            periodos = 90  # Valor padrão caso ocorra erro na conversão

        # Obter dados históricos para a previsão
        try:
            df = yf.download(cripto, period='5y', interval='1d')
            df.reset_index(inplace=True)

            # Verifica se o DataFrame não está vazio
            if df.empty:
                flash("Nenhum dado encontrado para a criptomoeda.", "error")
                return redirect(url_for('index'))

            df.rename(columns={"Date": "ds", "Close": "y"}, inplace=True)

            modelo = Prophet()
            modelo.fit(df)

            # Gerar previsão
            futuro = modelo.make_future_dataframe(periods=periodos)
            previsao = modelo.predict(futuro)

            # Filtrar a previsão para as datas desejadas
            previsao_filtrada = previsao[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periodos)

            # Criar gráfico de previsão com plotly
            fig = go.Figure()

            # Filtrar a previsão para incluir apenas os dias futuros
            data_historica_ultima = df['ds'].max()  # Última data do histórico
            previsao_futura = previsao[previsao['ds'] > data_historica_ultima]  # Filtra para dias futuros

            # Linha de Previsão
            fig.add_trace(go.Scatter(
                x=previsao_futura['ds'],
                y=previsao_futura['yhat'],
                mode='lines+markers',
                name='Previsão',
                line=dict(color='royalblue', width=2, dash='solid'),  # Cor e estilo da linha
                marker=dict(size=6, color='royalblue', symbol='circle')  # Marcadores nos pontos
            ))

            # Linha Histórica
            fig.add_trace(go.Scatter(
                x=df['ds'],
                y=df['y'],
                mode='lines',
                name='Histórico',
                line=dict(color='lightgreen', width=2, dash='dash'),  # Linha pontilhada
            ))

            # Atualizar layout do gráfico
            fig.update_layout(
                title=f'Previsão de Preços para {cripto}',
                xaxis_title='Data',
                yaxis_title='Preço',
                height=500,
                width=900,
                margin=dict(l=20, r=20, t=40, b=30),  # Ajustes de margens
                paper_bgcolor='rgba(0,0,0,0)',  # Fundo transparente
                plot_bgcolor='rgba(255, 255, 255, 0.8)',  # Fundo do gráfico
                hovermode='x unified',  # Habilitar hover unificado
                font=dict(size=14),  # Tamanho da fonte
                legend=dict(
                    x=0,
                    y=1.0,
                    bgcolor='rgba(255, 255, 255, 0.8)',  # Fundo da legenda
                    bordercolor='Black',
                    borderwidth=1
                ),
                xaxis=dict(showgrid=True, gridcolor='LightGray'),  # Grade do eixo x
                yaxis=dict(showgrid=True, gridcolor='LightGray'),  # Grade do eixo y
            )

            grafico = fig.to_html(full_html=False)


            # Filtro de histórico
            precos_historicos = df[df['ds'] >= (datetime.now() - pd.DateOffset(years=int(periodo_historico[:-1])))]

            # Verifica se o DataFrame não está vazio e contém a coluna 'ds'
            if not precos_historicos.empty and 'ds' in precos_historicos.columns:
                precos_historicos_dict = precos_historicos.set_index('ds')['y'].to_dict()
            else:
                precos_historicos_dict = {}  # Caso não haja dados disponíveis

        except Exception as e:
            logging.error(f"Erro ao gerar previsão para {cripto}: {e}")
            flash("Ocorreu um erro ao processar sua solicitação.", "error")
            return redirect(url_for('index'))

    # Retornar template com dados
    return render_template(
        'Cripto.html',
        cripto=cripto,
        grafico=grafico,
        previsao=previsao_filtrada.set_index('ds') if previsao is not None else None,  # Use a previsão filtrada
        precos=precos,
        precos_historicos=precos_historicos_dict,
        logos_criptomoedas=logos_criptomoedas,
        periodo_historico=periodo_historico,
        periodos=periodos
    )







if __name__ == '__main__':
    app.run(debug=True)
