import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_line(df_plot,columns,
              figsize=(15, 8),title="Grafica",
              make_hist_MACD=None, rsi=None,
              alpha=0.9,color='b'):
    #sns.set_style("darkgrid")
    sns.set_style(rc = {'axes.facecolor': 'lightsteelblue'})
    plt.figure(figsize=figsize)
    
    if isinstance(columns, str):
        columns = [columns]
        
    elif isinstance(columns,(list,tuple)):
        for col in columns:
            plt.plot(df_plot.index, df_plot[col], label=col)
    
    if isinstance(rsi,(tuple,list)):
        if len(rsi)==2:
            # Hacer minimo y maximo
            min = np.ones(len(df_plot))*rsi[0]
            max = np.ones(len(df_plot))*rsi[1]
            plt.plot(df_plot.index, min, linestyle='--',color='m')
            plt.plot(df_plot.index, max, linestyle='--',color='m')
        else:
            raise ValueError("rsi ser una lista de largo 2, (min, max)")
    
    if isinstance(make_hist_MACD,str):
        #plt.hist(df_plot[make_hist],label=make_hist)
        # Crea un gráfico de barras para el histograma
        plt.bar(df_plot.index, df_plot[make_hist_MACD], color=color, alpha=alpha, label=make_hist_MACD)
        
    plt.legend()
    plt.title(title)
    plt.xlabel('Fecha')
    plt.ylabel('Valor $')
    plt.grid(True)
    plt.show()
    
def plot_scatter(df_plot,cols_x,col_y):

    # Configura el número de filas y columnas para organizar los gráficos
    num_rows = len(cols_x) // 2 + len(cols_x) % 2  # División entera redondeada hacia arriba
    num_cols = 2

    # Configura el tamaño de la figura
    plt.figure(figsize=(15, 20))

    # Itera a través de las columnas de x y crea gráficos de dispersión
    for i, col in enumerate(cols_x):
        plt.subplot(num_rows, num_cols, i + 1)
        plt.scatter(df_plot[col], df_plot[col_y], alpha=0.5)
        plt.title(f'Scatter plot: {col_y} vs {col}')
        plt.xlabel(col)
        plt.ylabel(col_y)

    # Ajusta el espaciado entre los gráficos
    plt.tight_layout()

    # Muestra los gráficos
    plt.show()
    
def plot_correlation(df,cols_x,col_y,min_corr=0.8,figsize=(18, 15)):
   ''' 
   (Function)
      Esta funcion plotea en un Heatmap la correlacion de las variables ingresadas en x i y.
      regresa una array con las columnas que tienen una fuerte correlacion lineal tal que el 
      valor abs es mayor igual que min_corr
   (Parameters)
      - df: DataFrame con los datos
      - cols_x: Columnas que seran usadas para la comparar contra col_y
      - col_y: Columna que se quiere explicar
      - min_corr: (float) valor minimo que se acepta como correlacion, se considera para retornar las columnas que pasan este filtro
      
   '''

   if isinstance(col_y,str):
      # Agrega la columna 'Close' a la lista
      cols_x.append('Close')
   elif isinstance(col_y,(list)):
      cols_x += col_y

   # Calcula la matriz de correlación
   correlation_matrix = df[cols_x].corr()
   
   pasan_corr_lineal = correlation_matrix[correlation_matrix[col_y].abs()>=min_corr].index.values
   # Encuentra el índice del elemento col_use
   indice_drop = np.where(pasan_corr_lineal == col_y)[0]
   # Lo borra de la lista
   pasan_corr_lineal = np.delete(pasan_corr_lineal,indice_drop)
  

   # Configura el tamaño de la figura
   plt.figure(figsize=figsize)

   # Crea el mapa de calor de correlación con seaborn
   sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")

   # Añade un título
   plt.title('Matriz de Correlación')

   # Muestra el gráfico
   plt.show()
   
   return pasan_corr_lineal


def show_matriz_confusion(matriz_confusion):
    # Crear una visualización de la matriz de confusión
    plt.figure(figsize=(8, 6))
    sns.heatmap(matriz_confusion, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Clase 0", "Clase 1"],
                yticklabels=["Clase 0", "Clase 1"])
    plt.title("Matriz de Confusión")
    plt.xlabel("Predicciones")
    plt.ylabel("Valores reales")
    plt.show()