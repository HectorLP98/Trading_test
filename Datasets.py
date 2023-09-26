# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 09:29:13 2022

@author: 52551
"""

import pandas as pd
from datetime import datetime, timedelta
import time
from fechas import fecha_a_milisegundos, interval_to_milliseconds
import tqdm



def get_historical_from(cliente, symbol:str, interval:str, 
                        date_start:str,fecha_format: str = '%Y-%m-%d %H:%M:%S'):
    '''
    (Function)
    Esta funcion integra la recursividad para extraer el historico de un symbolo 
    en binance
    (Parameters)
        - cliente: [binance.client] cliente para poder consumir la api
        - symbol: [str] Indica el activo (par relacional de criptoactivos) a extraer, ejemplo  (BTCUSDT)
        - interval: [str]  Indica el intervalo del historico
        - date_start [str] Fecha de inicio de la extracción, ejemplo "2022-01-01 00:00:00" poner formato en caso
          de modificar el formato de fecha
        - fecha_format: [str] ejemplo del formato '%Y-%m-%d %H:%M:%S'
    (Returns)
        lista de precios, cuyo elemento es un diccionario con los datos en corte horizontal
        
    '''
    # convert interval to useful value in seconds
    timeframe = interval_to_milliseconds(interval)
    limite = 1000
    idx = 0
    # init our list
    output_data = []
    # it can be difficult to know when a symbol was listed on Binance so allow start time to be before list date
    symbol_existed = False
    start_ts = fecha_a_milisegundos(date_start,fecha_format) #datetime.strptime(date_start, format_date_start)
    while True:
        # fetch the klines from start_ts up to max 500 entries or the end_ts if set
        temp_data = cliente.klines(symbol=symbol, interval=interval, # Aternativa get_klines
                                limit=limite, startTime=start_ts ) 
        # handle the case where our start date is before the symbol pair listed on Binance
        if not symbol_existed and len(temp_data):
            symbol_existed = True

        if symbol_existed:
            # append this loops data to our output data
            output_data += temp_data

            # update our start timestamp using the last value in the array and add the interval timeframe
            start_ts = temp_data[len(temp_data) - 1][0] + timeframe
        else:
            # it wasn't listed yet, increment our start date
            start_ts += timeframe

        idx += 1
        # check if we received less than the required limit and exit the loop
        if len(temp_data) < limite:
            # exit the while loop
            break
        
        if idx % 50 == 0:
            print("Llevamos ",idx, " iteraciones")
        # sleep after every 3rd call to be kind to the API
        if idx % 3 == 0:
            time.sleep(1)
    return output_data


def generate_dataset(cliente, symbol, interval,
                     date_start,fecha_format='%Y-%m-%d %H:%M:%S',
                    type_upload='manual',
                    hrs_diff=6,con=None,table_name=None):
    '''
    (Function)
        Esta funcion genera un DataFrame con los datos historico de un simbolo que 
        opera en binance.
    (Parameters)
        - cliente: [binance.client] cliente para poder consumir la api
        - symbol: [str] Indica el activo (par relacional de criptoactivos) a extraer, ejemplo  (BTCUSDT)
        - interval: [str]  Indica el intervalo del historico
        - date_start [str] Fecha de inicio de la extracción, ejemplo "2022-01-01 00:00:00" poner formato en caso
          de modificar el formato de fecha
        - fecha_format: [str] ejemplo del formato '%Y-%m-%d %H:%M:%S'
        - type_upload: [str] debe ser ["auto", "manual"] por default es "manual",
            determina la manera de extraer los datos. Si desea que identifique la fecha por 
            si solo use "append" y necesitara incluir el conector (con) y el nombre de la 
            tabla (table_name) para extraer los datos de dicha base.
            En caso de usar manual necesitara solo la fecha apartir de la cual quiere los datos.
        - hrs_diff: [int] Debido al UTC es necesario quitar horas para emparejar a nuestra hora
                segun el pais, puede hacer pruebas para ajustar a su pais, default 6
        - con: Conector con la base de datos que contiene sus historicos, solo si type_upload="auto" 
        - table_name: [str] NOmbre de la tabla del historico a analisar, solo si type_upload="auto" 
    (Return)
        pd.DataFrame
    '''
    if type_upload.lower() == 'manual':
        
        if isinstance(date_start,str):
            ## Seteamos a datetime y ajustamos el tiempo por zona horaria
            last_date = datetime.strptime(date_start, fecha_format)
            
        else:
            raise ValueError('date_start debe ser un str, example 2020-01-01 00:00:00')
        
        
    elif type_upload.lower() == "auto":
        
        # Leemos la ultima fecha para cargar los datos apartir de ahi.
        # Close_Time, Hour_Close
        last_df = pd.read_sql_query(f'''
                    SELECT Close_Time
                    FROM {table_name}
                    LIMIT 1
                    ''', con)
        date_str = last_df.Close_Time.values[0]
        date_str = date_str.split(".")[0]
        last_date = datetime.strptime(date_str, fecha_format)
        #last_date = last_df.Close_Time.dt.strftime(fecha_format).values[0]
        
        
        
    else:
        raise ValueError("type_upload musth be in [auto,manual]")
    
    # Hacemos el request a la api de binance
    output_data = get_historical_from(cliente,symbol,interval,last_date,fecha_format)
    
    #Damos formato DataFrame
    doc_columns = ['Open_Time','Open','High','Low','Close','Volumne',
                'Close_Time','Quote_asset_vol','Number_trades','Taker_buy_base',
                'Taker_buy_quote','Ignore']
    df_aux = pd.DataFrame(output_data,columns=doc_columns)
    
    for col in ["Open","High",	"Low","Close","Volumne","Taker_buy_base","Taker_buy_quote",
            "Quote_asset_vol"]:
        df_aux[col] = df_aux[col].astype(float)
                
    for col in ["Number_trades"]:
        df_aux[col] = df_aux[col].astype(int)
        
    df_aux['Open_Time'] = pd.to_datetime(df_aux['Open_Time'],unit = 'ms' ) -  timedelta(hours=hrs_diff)
    df_aux['Close_Time'] = pd.to_datetime(df_aux['Close_Time'],unit = 'ms' ) -  timedelta(hours=hrs_diff)
    
    return df_aux


def up_to_db(cliente, simbolos:list, intervalos:list, 
             date_start:str,fecha_format:str='%Y-%m-%d %H:%M:%S',
             type_upload='manual',
             hrs_diff=6,con_get=None,con_set=None,if_exist='replace'):
    '''
    (Function)
        Esta funcion genera un DataFrame con los datos historico de un simbolo que 
        opera en binance.
    (Parameters)
        - cliente: [binance.client] cliente para poder consumir la api
        - simbolos: [list|tuple|iterable] Indica los activos (par relacional de criptoactivos) a extraer, ejemplo  (BTCUSDT)
        - intervalos: [list|tuple|iterable]  Indica los intervalos del historico
        - date_start [str] Fecha de inicio de la extracción, ejemplo "2022-01-01 00:00:00" poner formato en caso
          de modificar el formato de fecha
        - fecha_format: [str] ejemplo del formato '%Y-%m-%d %H:%M:%S'
        - type_upload: [str] debe ser ["auto", "manual"] por default es "manual", determina la manera de extraer los datos. Si desea que identifique la fecha por 
            si solo use "append" y necesitara incluir el conector (con) y el nombre de la 
            tabla (table_name) para extraer los datos de dicha base.
            En caso de usar manual necesitara solo la fecha apartir de la cual quiere los datos.
        - hrs_diff: [int] Debido al UTC es necesario quitar horas para emparejar a nuestra hora
                segun el pais, puede hacer pruebas para ajustar a su pais, default 6
        - con: Conector con la base de datos que contiene sus historicos, solo si type_upload="auto" 
        - if_exist: [str] por default "replace" puede ser ['fail', 'replace', 'append'], indica 
                    que hacer en caso de que la tabla que intenta cargar exista.
    (Return)
        pd.DataFrame
    '''
    for symbol in tqdm.tqdm(simbolos):
        for interval in intervalos:
            
            # NOmbre de la tabla
            table_name = symbol+'_'+interval
            
            df = generate_dataset(cliente, symbol, interval,
                        date_start,fecha_format=fecha_format,
                        type_upload=type_upload,
                        hrs_diff=hrs_diff,con=con_get,table_name=table_name)
                

            df = df[['Open_Time', 'Open', 'High', 'Low', 'Close', 'Volumne', 'Close_Time',
                'Quote_asset_vol', 'Number_trades', 'Taker_buy_base', 'Taker_buy_quote']]

            
            
            cargados = df.to_sql(table_name,con_set,if_exists=if_exist,index=False)

            print(f"Se cargo la tabla: {table_name}")
            time.sleep(1)


# PRofundidad de mercado
def depth(cliente,simbolo,limite):
# from perfil_binance import cuenta_binance as cb
# client = Client('', '')
# cliente = cb('demo')
# simbolo = 'TRXUSDT'
# limite = 100 hasta 5,000
# return un df con la cantidad de dolares y el precio del activo.

    
    depth = cliente.get_order_book(symbol=simbolo, limit=limite)
    lp_c = []
    lp_v = []
    l_c = []
    l_v = []
    for key, val in depth.items():
        if key == 'bids': # Compras
            for j in val:
                lp_c.append(float(j[0]))
                l_c.append(round(float(j[1]),2))
           # print(key,len(val))
        elif key == 'asks': # Ventas
           # print(key,len(val))
            for j in val:
               # print(j)
                lp_v.append(float(j[0]))
                l_v.append(round(float(j[1]),2))
    df = pd.DataFrame({'Q_venta': l_v,
                       'P_venta': lp_v,
                       'Q_compra':l_c,
                       'P_compra':lp_c})
    df.tail()
    return df



# isBuyerMaker: true => la operación fue iniciada por el lado de la venta; el lado de la compra ya era el libro de pedidos. es compra
# isBuyerMaker: false => la operación fue iniciada por el lado comprador; el lado de la venta ya era el libro de pedidos     es venta                                                                          False = orden de mercado. no pasa por el libro.
# qty: cantidad de cripto 
# quoteQty: Total de compra en USDT
def historical_trades(cliente,simbolo, ago, limite=1000,fromid=None):
# Esta funcion retorna un df que contiene el historial de trades
# from perfil_binance import cuenta_binance as cb
# client = Client('', '')
# cliente = cb('demo')
# simolo = 'TRXUSDT'
# ago = 5 ; los ultimos trades de hace 5 minutos, este parametro es entero y representa minutos unicamente
# limite = 1 hasta 1000
# fromid = probar cualquier id.
# # isBuyerMaker: true => es compra
# isBuyerMaker: false => es venta
    '''
    trades = cliente.get_historical_trades(symbol=simbolo, limit=limite, fromid=fromid)
    df = pd.DataFrame(trades)
    df['price'] = df['price'].astype('float16')
    df['qty'] = df['qty'].astype('float64')
    df['time'] = pd.to_datetime(df['time'],unit = 'ms' )
    df['quoteQty'] = df['quoteQty'].astype('float64')
    df.drop(columns='isBestMatch', axis = 1, inplace=True)
    df = df.round({ 'qty':1, 'quoteQty':3})
'''  
    
    trades = cliente.get_historical_trades(symbol='BTCUSDT', limit=1000 )# , fromId =dfp.id.min()-1000)
    dfp = pd.DataFrame(trades)
    dfp['time'] = pd.to_datetime(dfp['time'],unit = 'ms' )

    
    ahora = datetime.now()
    tb = ahora - timedelta(minutes = ago) + timedelta(hours=5)
    date_min = dfp.time.min()


   # print(dfp.shape, '*********')
    #print('Time buscado ', tb)
    while date_min>tb:
        trades = cliente.get_historical_trades(symbol='BTCUSDT', limit=1000 , fromId =dfp.id.min()-1000)
        dfpp = pd.DataFrame(trades)
        dfpp['time'] = pd.to_datetime(dfpp['time'],unit = 'ms' )
        #dfp.time = df.time - timedelta(hours=5)
        date_min = dfpp.time.min()
        #print(dfpp.time.min())
        dfp = dfp.append(dfpp, ignore_index = True)
    dfp['price'] = dfp['price'].astype('float16')
    dfp['qty'] = dfp['qty'].astype('float64')
    dfp['quoteQty'] = dfp['quoteQty'].astype('float64')
    dfp.drop(columns='isBestMatch', axis = 1, inplace=True)
    dfp = dfp.round({ 'qty':1, 'quoteQty':3})
    
    return dfp