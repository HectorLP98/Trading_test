import pandas as pd 


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




