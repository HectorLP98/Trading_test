import pandas as pd 
import ta
from scipy import stats
from tabulate import tabulate
import numpy as np


def get_change_percent(df1,col, n_periods=1 ,all_periods=True,reverse=True):
    '''
    (Function)
        Esta funcion calcula y anexa el cambio percentual en un periodo determinado
        es importante que esten ordenados del mas viejo al mas actual.
    (Parameters) 
        - df: [dataframe]
        - col: [str] Columna a usar para obtener el cambio porcentual
        - periods: [int] numero de periodos para calcular el cambio porcentual, por default es 1 fila
        - reverse: [bool] Default True para ir de abajo hacia arriba
    (Returns)
        df con las columnas anexadas
    '''
    # variables not move
    
    df = df1.copy()
    aux = 1
    if reverse:
        if n_periods >0: 
            aux = -1
    if all_periods:
        for i in range(1,n_periods+1):
            name_col = col+'_pc_'+str(i)
            df[name_col] = df[col].pct_change(periods=-i)*100*aux
            
            
    else:
        i = n_periods
        name_col = col+'_pc_'+str(i)
        df[name_col] = df[col].pct_change(periods=-i)*100*aux
    
    
    return df

def get_ditection_pc(df1,pattern_col:str='_pc'):
    '''
    (Function)
        Esta funcion calcula y anexa la direction que tomara la serie temporal 
        en el periodo n+1
    (Parameters) 
        - df: [dataframe]
        - pattern_col: [str]
    (Returns)
        df  con sufijo _direction
    '''
    df = df1.copy()
    
    cols_use = [valor for valor in df.columns if pattern_col in valor ]
    for col in cols_use:
        name_coldir = col.replace(pattern_col,"_dir")
        df[name_coldir] = df[col].map(lambda x: "UP" if x>0 else "DOWN")
    return df

def change_percentual(df1,cols_use,n_periods=1,reverse=True
                      ,get_direction=True,pattern_col_use= '_pc',
                      all_periods=True):
    '''
    (Function)
        Esta funcion calcula y anexa el cambio percentual en un periodo determinado
        es importante que esten ordenados del mas viejo al mas actual.
    (Parameters) 
        - df1: [dataframe]
        - cols_use: [str|list] Columna a usar para obtener el cambio porcentual
        - n_periods: [int] numero de periodos para calcular el cambio porcentual, por default es 1 fila
        - reverse: [bool] Default True para ir de abajo hacia arriba
        - get_direction: [bool] default True, para obtener las columnas de las direcciones
        - pattern_col_use: [str] patron para identificar las columnas con el cambio porcentual
        - all_periods: [bool] default True, para calcular y generar las columnas del periodo 1 al n_periods
    (Returns)
        df con las columnas anexadas
    '''
    
    df = df1.copy()
    
    if isinstance(cols_use,str):
        col = cols_use
        #print(col)
        df = get_change_percent(df,col,n_periods,all_periods,reverse)
        if get_direction:
            df = get_ditection_pc(df, pattern_col_use)
            
    elif isinstance(cols_use,(list,tuple)):
        for col in cols_use:
            df = get_change_percent(df,col,n_periods,all_periods)
            if get_direction:
                df = get_ditection_pc(df, pattern_col_use)
    return df

def get_volatilidad(df1,cols_cv):
    '''
    (Function)
        Esta funcion calcula la volatilidad del precio, es necesario tener columnas con el 
        cambio porcentual, corra la funcion change_percentual para obtenerlas
    (Parameters)
        - df1: [DataFrame] 
        - Columnas a usar para el calculo de la volatilidad
    (Returns)
        diccionario con las colunas y la volatilidad obtenida.
    '''
    df = df1.copy()

    dict_statistics = {}
    #cols_cv = [valor for valor in df.columns if pattern_col_use in valor]
    if isinstance(cols_cv,str):
        cols_cv = [cols_cv]
        
    for name_col in cols_cv:
        # Coeficiente de variacion
        cv = (df[name_col].std() / df[name_col].mean()) * 100
        dict_statistics[name_col] =  abs(cv)

    return dict_statistics


def put_EMA(df1,col_use,periodos=[8,13,55,144]):
    '''
    (Function)
        Esta funcion calcula la EMA para los periodos señalados usando la columna especifica
    (Parameters)
        df1: DataFrame con el historico
        col_use: [str] Columna a usar para calcular las emas
        periodos: [list,int] periodos para las EMAS
        
    '''
    if isinstance(periodos,(int,float)):
        periodos = [periodos]
    
    df = df1.copy()
    for period in periodos:
        df['EMA'+str(period)] = ta.trend.EMAIndicator(close= df[col_use], window= int(period), fillna= False).ema_indicator()
        
    return df
    
def num_fib(k):
    if k<=2 and k>0: return 1
    else: return num_fib(k-1)+num_fib(k-2)
    
def sucesion_fib(n):
    for i in range(1,n+1):
        print(num_fib(i))

def put_BandasBollinguer(df1,col_use,ventana, desviacion=2, put_indicator=True):
    df = df1.copy()
    if put_indicator:
        # Indicador bb: It returns 1, if col_use is higher than bollinger_hband. Else, it returns 0.
        df['BBH_indicator']=ta.volatility.BollingerBands(df[col_use], 
                                                        window = ventana,
                                                        window_dev = desviacion,
                                                        fillna = False).bollinger_hband_indicator()
        # Indicador bb: It returns 1, if col_use is lower than bollinger_lband. Else, it returns 0.
        df['BBL_indicator']=ta.volatility.BollingerBands(df[col_use],
                                                        window = ventana,
                                                        window_dev = desviacion,
                                                        fillna = False).bollinger_lband_indicator()
    # Valor bb higher
    df['BBH']=ta.volatility.BollingerBands(df[col_use], 
                                                    window = ventana,
                                                    window_dev = desviacion,
                                                    fillna = False).bollinger_hband()
    # Valor bb lower
    df['BBL']=ta.volatility.BollingerBands(df[col_use],
                                                    window = ventana,
                                                    window_dev = desviacion,
                                                    fillna = False).bollinger_lband()
    # Valor bb average
    df['BBA']=ta.volatility.BollingerBands(df[col_use],
                                                    window = ventana,
                                                    window_dev = desviacion,
                                                    fillna = False).bollinger_mavg()
    return df


def prueba_hipotesis(df,col_use, alpha, dist='norm', get_data=False):
    '''
    (Function)
        Esta funcion hace 3 pruebas de hipotesis para normalidad
    (Parameters)
        - df: [list, tuple, array, DataFrame, Series] datos sobre los que se desea la prueba de hipotesis
        - col_use: [str] en caso de ser DataFrame usa esa columna para la prueba
        - alpha: [float] Nivel de significancia sobre el que se desea hacer la prueba 0.05 -> 95%
        - dist: [str] tipo de distribucion para hacer la prueba, puede probar: 
                {'norm', 'expon', 'logistic', 'gumbel', 'gumbel_l', 'gumbel_r', 'extreme1'}
        - get_data: [bool] True para retornar el diccionario de datos 
    (Ejemplo de uso)
        > data = np.random.normal(0, 1, 1000)
        > prueba_hipotesis(data,col_use, alpha, dist = 'norm', get_data=False)
    '''
    datos = {}
    
    if isinstance(df,pd.DataFrame):
        data = df[col_use].dropna()
    elif isinstance(df, (np.ndarray, list, tuple, pd.Series)):
        data = df

    # Realiza la prueba de Anderson-Darling
    result = stats.anderson(data,dist=dist) 
    # Comprueba si la muestra sigue una distribución normal basada en el estadístico de prueba
    if result.statistic < result.critical_values[2]:
        res = "Sigue distribucion"
    else:
        res = "No sigue distribucion"

    # apendamos los valores necesarios
    datos.update({"Anderson-Darling":{'Est_prueba':result.statistic,
                                    "P-value":result.critical_values[2],
                                    "Veredicto":res}})


    # Realiza la prueba de Shapiro-Wilk
    statistic, p_value = stats.shapiro(data)

    # Comprueba si la muestra sigue una distribución normal basada en el valor p
    if p_value > alpha:
        res = "Sigue distribucion"
    else:
        res = "No sigue distribucion"
        
    # apendamos los valores necesarios
    datos.update({"Shapiro-Wilk":{'Est_prueba':statistic,
                                    "P-value":p_value,
                                    "Veredicto":res}})


    # Realiza la prueba de Kolmogorov-Smirnov
    kstest_result = stats.kstest(data, dist)

    if kstest_result.pvalue > alpha:
        res = "Sigue distribucion"
    else:
        res = "No sigue distribucion"
        
    # apendamos los valores necesarios
    datos.update({"Kolmogorov-Smirnov":{'Est_prueba':kstest_result.statistic,
                                    "P-value":kstest_result.pvalue,
                                    "Veredicto":res}})


    table = []
    for test, values in datos.items():
        row = [test, values['Est_prueba'], values['P-value'], values['Veredicto']]
        table.append(row)

    headers = ['Prueba', 'Estadístico de Prueba', 'Valor P', 'Veredicto']
    table_str = tabulate(table, headers, tablefmt='grid')

    print(table_str)
    if get_data:
        return datos

def get_cols_pc_and_dir(n_period,col_use,separeted=True):
    cols_pc = []
    cols_dir = []
    for i in range(1,n_period+1):
        cols_pc.append(col_use+'_pc_'+str(i))
        cols_dir.append(col_use+'_dir_'+str(i))
    if separeted:
        return cols_dir, cols_pc
    else:
        return cols_dir + cols_pc