import streamlit as st
from yahoo_fin.stock_info import tickers_nasdaq, tickers_other, tickers_sp500
import yfinance as yf
import pandas as pd 
import plotly.graph_objs as go
import sys
import os

# Agrega la ruta de la carpeta b1 al sistema de rutas de Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '/home/hector/Documentos/Escuelas/Autodidacta/Git_repositories/Trading_test')))

# Ahora puedes importar el módulo desde la carpeta b1
from Indicadores.Direccion import calcular_EMA
from fn_prep import get_change_percent
from Indicadores.Fuerza import calcular_rsi



# numeros de decimal a redondear
r = 5
# Agregar un campo de entrada para ingresar un número
n_rows = 3


def graficar_velas(data):
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],name="Velas")])
    # Agregar la EMA a la figura
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA7"], mode='lines', name='EMA7',fillcolor="orange"))
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA28"], mode='lines', name='EMA28',fillcolor="blue"))
    
    fig.update_layout(title='Gráfico de Velas', xaxis_title='Fecha', yaxis_title='Precio')
    tab1.plotly_chart(fig)

def graficar_linea(data,obj_st, col_use, ytitle="Precio",title='Gráfico de Línea'):
    fig = go.Figure(data=go.Scatter(x=data.index, y=data[col_use], mode='lines'))
    fig.update_layout(title=title, xaxis_title='Fecha', yaxis_title=ytitle)
    obj_st.plotly_chart(fig)



# Obtener los símbolos del NASDAQ
symbols = tickers_nasdaq() + tickers_other() + tickers_sp500()

# Título de la aplicación
st.title('Selecciona tu simbolo')
st.divider()

# Campo de entrada para buscar
simbol = st.text_input("Buscar", "BTC-USD", help="Vaya a https://es-us.finanzas.yahoo.com/ y busque su simbolo")

    
# Mostrar el valor seleccionado
st.write("Valor seleccionado:", simbol)

# Agregar botón de aceptar
   
ticker = yf.Ticker(simbol)

# Ultimo volumen
lastVolume = round(ticker.get_fast_info()["lastVolume"],r)
# Ultimo precio
lastPrice = round(ticker.get_fast_info()["lastPrice"],r)
pass_mark = False
try :
    # Market Cap = Precio de la Accion x Numero de Acciones en Circulacion
    marketCap = round(ticker.get_fast_info()["marketCap"],r)
    num_acciones = marketCap / lastPrice
    pass_mark = True
except:
    pass
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
if pass_mark:
    col3.metric("Capitalizacion", value="{:,}".format(marketCap), help="Market Cap = Precio de la Accion x Numero de Acciones en Circulacion")
st.divider()

# Cargamos las noticias 
try:
    df_news = pd.DataFrame(ticker.news)
    df_news = df_news[["title","publisher","link","type","relatedTickers"]].head(int(n_rows))
    st.table(df_news)
    st.divider()
except:
    pass
# Cargamos el historico
# period = “1d”, “5d”, “1mo”, “3mo”, “6mo”, “1y”, “2y”, “5y”, “10y”, “ytd”, “max”
# interval = “1m”, “2m”, “5m”, “15m”, “30m”, “60m”, “90m”, “1h”, “1d”, “5d”, “1wk”, “1mo”, “3mo”

# Configuracion para graficas

opcion_chart = st.selectbox('Seleccione el tipo de gráfico', ('Vela', 'Línea'))
c1, c2, c3, c4 = st.columns(4)
period = c1.selectbox("Periodo", ("1d","5d","1mo","3mo","6mo","1y","2y","5y","ytd","max"))
interval = c2.selectbox("Intervalo", ("1m","2m","5m","15m","30m","60m","90m","1h","1d","5d","1wk","1mo","3mo"))
n_valores = c3.text_input("N-valores", "7", help="Cantidad de periodos a revisar para el semaforo")
ventanaRSI = c4.text_input("Ventana RSI", "14", help="Influye en la suavidad del indicador, la capacidad para identificar niveles extremos y la sensibilidad a los cambios recientes en los precios")
# Valores default
try:
    n_valores = int(n_valores)
except:
    n_valores = 7
try:
    ventanaRSI = int(ventanaRSI)
except:
    ventanaRSI = 14

    
# Cargamos historico
df = ticker.history(period=period, interval=interval)

# Asignamos EMA
periodos_ema = [7,28]
for nn in periodos_ema:
    df[f"EMA{nn}"] = calcular_EMA(df=df,col_use="Close",n=nn)
# Calculamos la distancia entre EMAs
# calculamos la distancia entre la ema7 y la ema 28
df["distancia_EMA"] = df["EMA7"] - df["EMA28"]
# Generamos el cambio porcentual.
df = get_change_percent(df,"distancia_EMA",n_periods=1,all_periods=True, reverse=False)
# Desfasamos un lugar 
df["distancia_EMA_pc_1"] = df["distancia_EMA_pc_1"].shift(periods=-1)
# Detectamos si hubo cambio de lugar en EMAs
c1 = (df['distancia_EMA_pc_1'].shift(1) < 0) & (df['distancia_EMA_pc_1'] >= 0)
c2 = (df['distancia_EMA_pc_1'].shift(1) >= 0) & (df['distancia_EMA_pc_1'] < 0)
df["Cambio_EMA"] = c1 + c2
df['Cambio_EMA'] = df['Cambio_EMA'].astype(int)


# Sobre el RSI

# Calculo del RSI
df["RSI"] = calcular_rsi(df["Close"], ventana=ventanaRSI)
# Calculo de la variacion 
df = get_change_percent(df,"RSI",n_periods=1,all_periods=True, reverse=False)
# Desfasamos un lugar 
df["RSI_pc_1"] = df["RSI_pc_1"].shift(periods=-1)
# Calculamos los cambios de direccion
c1 = (df['RSI_pc_1'].shift(1) < 0) & (df['RSI_pc_1'] >= 0)
c2 = (df['RSI_pc_1'].shift(1) >= 0) & (df['RSI_pc_1'] < 0)
df["Cambio_RSI"] = c1 + c2
df['Cambio_RSI'] = df['Cambio_RSI'].astype(int)

indicadorRSI = "verde" if df["Cambio_RSI"].tail(n_valores).sum() < 1 else "rojo" if df["Cambio_RSI"].tail(n_valores).sum() >3 else "amarillo"




# Generamos indicadores
c1, c2, c3 = st.columns(3)
indicadorEMA = "verde" if df["Cambio_EMA"].tail(n_valores).sum() <= 1 else "rojo" if df["Cambio_EMA"].tail(n_valores).sum() >3 else "amarillo"
c1.metric("Indicador EMA", value=indicadorEMA, help="Indica la dureza de la tendencia para la EMA7")
c2.metric("Indicador RSI", value=indicadorRSI, help="Indica la dureza de la tendencia para el RSI")
print() 




# Graficamos 

tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
if opcion_chart == 'Vela':
    graficar_velas(df)
    graficar_linea(df,obj_st=tab1, col_use="RSI",ytitle="RSI",title="RSI")
elif opcion_chart == 'Línea':
    graficar_linea(df,obj_st=tab1, col_use="Close")
    
    
tab2.subheader(f"Data {simbol}")
tab2.table(df[['Open', 'High', 'Low', 'Close', 'Volume', 
       'distancia_EMA', 'distancia_EMA_pc_1','Cambio_EMA']])
print()



