


# Se importan las librerias
import pandas as pd   # El famosos pandas
import yfinance as yf   # Para el ticker

nombre_archivos = ["AMZN_1d.csv", "name2","name3","otro_nombre"]


for name_file in nombre_archivos:
    
    # Ruta del archivo a modificar
    path='/home/rolando/Documents/Limon/Trading_test/Data/'
    try:
        print('Se ha actualizado la info de:')
        # Leyendo el archivo
        df_hist=pd.read_csv(path+name_file)
        # Se toma un dia anterior a la fecha final del archivo
        fecha_inicial=pd.to_datetime(df_hist.Date).max()-pd.Timedelta(days=1)
        # Se cambia formato
        fecha_inicial=fecha_inicial.strftime('%Y-%m-%d')
        # Se toma el simbolo correspondiente
        simbol=name_file.split('_')[0]
        # Se le asigna la clase a tickr
        ticker = yf.Ticker(simbol)
        # Se obtiene el nuevo df a partir de la fecha inicial
        df_new = ticker.history(start=fecha_inicial, interval="1d")
        # El indice se hace formato date
        df_new.reset_index(drop=False,inplace=True)
        # Se concatena el historico con el nuevo df
        df_final=pd.concat([df_hist.iloc[:-2],df_new])
        df_final.drop_duplicates(subset="Date",keep="last",inplace=True)
        # Se reinician los indices
        df_final.reset_index(drop=True,inplace=True)
        # Se guarda el df final 
        df_final.to_csv(f"Data/{simbol}_1d.csv", index=False, encoding="utf8")   
        print(name_file)
    except:
        print("Error no existe archivo: ",name_file)
    
