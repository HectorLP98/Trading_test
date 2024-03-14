import streamlit as st
from yahoo_fin.stock_info import tickers_nasdaq
import yfinance as yf
import pandas as pd 
import plotly.graph_objs as go


# numeros de decimal a redondear
r = 5
# Agregar un campo de entrada para ingresar un número
n_rows = 3


def graficar_velas(data):
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'])])

    fig.update_layout(title='Gráfico de Velas', xaxis_title='Fecha', yaxis_title='Precio')
    tab1.plotly_chart(fig)

def graficar_linea(data):
    fig = go.Figure(data=go.Scatter(x=data.index, y=data['Close'], mode='lines'))
    fig.update_layout(title='Gráfico de Línea', xaxis_title='Fecha', yaxis_title='Precio')
    tab1.plotly_chart(fig)



# Obtener los símbolos del NASDAQ
nasdaq_symbols = tickers_nasdaq()

# Título de la aplicación
st.title('Mercado NASDAQ')
st.divider()

# Mostrar la lista en la aplicación
st.write("Lista de simbolos:")
simbol = st.selectbox("", nasdaq_symbols)


# Mostrar el valor seleccionado
st.write("Valor seleccionado:", simbol)

# Agregar botón de aceptar
   
ticker = yf.Ticker(simbol)

# Ultimo volumen
lastVolume = round(ticker.get_fast_info()["lastVolume"],r)
# Ultimo precio
lastPrice = round(ticker.get_fast_info()["lastPrice"],r)
# Market Cap = Precio de la Accion x Numero de Acciones en Circulacion
marketCap = round(ticker.get_fast_info()["marketCap"],r)
num_acciones = marketCap / lastPrice
#precio mas bajo del año
yearHigh = round(ticker.get_fast_info()["yearHigh"],r)
# precio mas alto del año
yearLow = round(ticker.get_fast_info()["yearLow"],r)
# zona horaria
timezone = ticker.get_fast_info()["timezone"]
# divisa
currency = ticker.get_fast_info()["currency"]

# Ponemos en columnas los utlimos precios
col1, col2 = st.columns(2)

col1.metric("Precio", value="{:,}".format(lastPrice), help="Ultimo precion captado")
col2.metric("Volumen", value="{:,}".format(lastVolume), help="Ultimo volumen captado")
col3, col4 = st.columns(2)
col3.metric("Zona horaria", value=timezone)
col4.metric("Divisa", value=currency, help="Divisa en la que opera")
# Ponemos en columnas los precios
col1, col2, col3 = st.columns(3)

col1.metric("Higher price in year", value="{:,}".format(yearHigh), help="Precio mas alto en el año")
col2.metric("Lower price in year", value="{:,}".format(yearLow), help="Precio mas bajo en el año")
col3.metric("Capitalizacion", value="{:,}".format(marketCap), help="Market Cap = Precio de la Accion x Numero de Acciones en Circulacion")
st.divider()

# Cargamos las noticias 
df_news = pd.DataFrame(ticker.news)
df_news = df_news[["title","publisher","link","type","relatedTickers"]].head(int(n_rows))
st.table(df_news)
st.divider()

# Cargamos el historico
# period = “1d”, “5d”, “1mo”, “3mo”, “6mo”, “1y”, “2y”, “5y”, “10y”, “ytd”, “max”
# interval = “1m”, “2m”, “5m”, “15m”, “30m”, “60m”, “90m”, “1h”, “1d”, “5d”, “1wk”, “1mo”, “3mo”

# Graficamos 
opcion_chart = st.selectbox('Seleccione el tipo de gráfico', ('Vela', 'Línea'))
c1, c2 = st.columns(2)
period = c1.selectbox("Periodo", ("1d","5d","1mo","3mo","6mo","1y","2y","5y","ytd","max"))
interval = c2.selectbox("Intervalo", ("1m","2m","5m","15m","30m","60m","90m","1h","1d","5d","1wk","1mo","3mo"))
df = ticker.history(period=period, interval=interval)


tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
if opcion_chart == 'Vela':
    graficar_velas(df)
elif opcion_chart == 'Línea':
    graficar_linea(df)
    c1.line_chart(df)
    
tab2.subheader(f"Data {simbol}")
tab2.table(df)