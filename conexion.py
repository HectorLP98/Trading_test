from sqlalchemy import create_engine
import mysql.connector
from cryptography.fernet import Fernet
import configparser

def abrir_conexion_MYSQL(username,password,database='Trading_prices',
                         host='localhost',port=3306):
    # Establecer Conexion
    # Parámetros de conexión a tu base de datos MySQL
    db_params = {
        'host':host,
        'user':username,
        'password':password,
        'database':database,  # En caso de querer una base en particular 
        'port':port
    }

    # Crea una conexión a la base de datos utilizando SQLAlchemy
    engine = create_engine(f"mysql+mysqlconnector://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}")
    
    return engine

def open_conexion_get(username,password,database='Trading_prices',
                         host='localhost',port=3306):
    
    # pip install MySQL-connector-python
    db_params = {
        'user': username,
        'password': password,
        'host': host,  # Por ejemplo, 'localhost' o la dirección IP del servidor
        'port': port,  # Por defecto, el puerto de MySQL es 3306
        'database': database,
        "auth_plugin":'mysql_native_password'
    }
    conn = mysql.connector.connect(**db_params)
    return conn



# Genera una clave de cifrado aleatoria
def generar_clave():
    return Fernet.generate_key()

# Encripta el archivo credenciales.txt
def encriptar_archivo(archivo, clave):
    '''
    (Function)
        Esta funcion encripta archivos
    (Parameters)
        - archivo: [str] ruta al archivo a encriptar
        - clave: Ha ash para el encriptamiento
    (Example)
        # Genera una clave de cifrado y la guarda en un archivo para futuras encripciones/lecturas
        clave = generar_clave()
        # Almacenamos la clave en la ruta especificada, como archivo.key
        with open('Data/clave.key', 'wb') as clave_file:
            clave_file.write(clave)

        # Encripta el archivo credenciales.txt con la clave generada
        encriptar_archivo('Data/archivo.txt', clave)
    '''
    cipher_suite = Fernet(clave)
    with open(archivo, 'rb') as file:
        plaintext = file.read()
    encrypted_text = cipher_suite.encrypt(plaintext)
    with open(archivo, 'wb') as file:
        file.write(encrypted_text)


# Lee el archivo credenciales.txt y retorna las contraseñas como un diccionario
def desencriptar_archivo(archivo, clave):
    '''
    (Function)
        Esta funcion desencripta el archivo 
    (Parameters)
        - archivo: [str] ruta al archivo encriptado
        - clave: Clave ha ash para desencriptar
    (Example)
        # Lee la clave hash para desencriptar
        with open('Data/clave.key', 'r') as clave_file:
            clave_file1 = clave_file.read()
        # Lee las contraseñas del archivo encriptado y muestra el resultado deseado
        contraseñas = desencriptar_archivo('Data/archivo.txt', clave_file1)
    '''
    cipher_suite = Fernet(clave)
    with open(archivo, 'rb') as file:
        encrypted_text = file.read()
    decrypted_text = cipher_suite.decrypt(encrypted_text).decode('utf-8')
    
    # Divide las líneas en pares key = value
    lines = decrypted_text.split('\n')
    contraseñas = {}
    for line in lines:
        parts = line.strip().split(' = ')
        if len(parts) == 2:
            key, value = parts
            contraseñas[key] = value
    
    return contraseñas


# Escribe la información desencriptada en otro archivo
def escribir_desencriptado(archivo_entrada, archivo_salida, clave):
    '''
    (Function)
        Esta funcion desencripta un archivo y lo escribe desencriptado
    (Parameters)
        - archivo_entrada: [str] ruta al archivo encriptado
        - archivo_salida_ [str] ruta donde se escribira incluye nombre archivo
        - clave: Ha ash para hacer desencriptado
    
    '''
    contraseñas = desencriptar_archivo(archivo_entrada, clave)
    with open(archivo_salida, 'w') as file:
        for key, value in contraseñas.items():
            file.write(f"{key} = {value}\n")