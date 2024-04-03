import pandas as pd

def calcular_rsi(datos, ventana=14):
    # Calcular cambios en precios
    delta = datos.diff()

    # Eliminar primer elemento NaN
    delta = delta.dropna()

    # Separar cambios positivos y negativos
    ganancias = delta.where(delta > 0, 0)
    pérdidas = delta.where(delta < 0, 0)

    # Calcular promedios móviles
    promedio_ganancias = ganancias.rolling(window=ventana, min_periods=ventana).mean()
    promedio_pérdidas = pérdidas.rolling(window=ventana, min_periods=ventana).mean()

    # Calcular el RSI
    rs = promedio_ganancias / promedio_pérdidas.abs()
    rsi = 100 - (100 / (1 + rs))

    return rsi