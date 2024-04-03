import pandas as pd

def calcular_EMA(df, col_use, n):
    """
    Calcula la media móvil exponencial (EMA) de una columna en un DataFrame.

    Parámetros:
        - df: DataFrame de pandas.
        - col_use: Nombre de la columna a utilizar para el cálculo.
        - n: Número de días para calcular la EMA.

    Retorna:
        - ema: Serie de pandas que contiene la EMA calculada.
    """
    alpha = 2 / (n + 1)  # Factor de suavizado para la EMA
    ema = pd.Series(index=df.index)  # Crear una Serie vacía para almacenar los valores de la EMA

    # Calcular la EMA para cada fila del DataFrame
    for i in range(len(df)):
        if i == 0:
            ema.iloc[i] = df[col_use].iloc[i]  # El primer valor de la EMA es igual al primer valor de la columna
        else:
            ema.iloc[i] = (df[col_use].iloc[i] - ema.iloc[i-1]) * alpha + ema.iloc[i-1]  # Fórmula de la EMA

    return ema

# Ejemplo de uso:
# Suponiendo que tienes un DataFrame llamado 'data' y quieres calcular la EMA de la columna 'precio' con un período de 10 días.
# ema_result = calcular_EMA(data, 'precio', 10)
