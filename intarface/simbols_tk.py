import tkinter as tk
from tkinter import ttk

def get_simbol():
    from yahoo_fin.stock_info import tickers_nasdaq
    def seleccionar():
        seleccion.set(combo.get())
        ventana.destroy()

    def buscar():
        texto_busqueda = entry_busqueda.get()
        # Limpiar la lista
        combo['values'] = []
        # Filtrar los valores que contienen el texto de búsqueda
        valores_filtrados = [valor for valor in my_list if texto_busqueda.lower() in valor.lower()]
        combo['values'] = valores_filtrados

    # Lista de ejemplo
    my_list = tickers_nasdaq()

    # Crear la ventana
    ventana = tk.Tk()
    ventana.title("Selección de Valor")
    ventana.geometry("200x200")

    # Variables
    seleccion = tk.StringVar()

    # Buscador
    label_busqueda = tk.Label(ventana, text="Buscar:")
    label_busqueda.pack()
    entry_busqueda = tk.Entry(ventana)
    entry_busqueda.pack()
    boton_buscar = tk.Button(ventana, text="Buscar", command=buscar)
    boton_buscar.pack()

    # Lista desplegable
    label = tk.Label(ventana, text="Selecciona un valor:")
    label.pack()
    combo = ttk.Combobox(ventana, textvariable=seleccion)
    combo['values'] = my_list
    combo.pack()

    # Botón de seleccionar
    boton_seleccionar = tk.Button(ventana, text="Seleccionar", command=seleccionar)
    boton_seleccionar.pack()

    # Ejecutar la ventana
    ventana.mainloop()

    # Imprimir el valor seleccionado
    return seleccion.get()