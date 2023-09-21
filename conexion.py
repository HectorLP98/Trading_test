from sqlalchemy import create_engine
import mysql.connector

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