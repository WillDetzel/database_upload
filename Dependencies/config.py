import configparser

def load_credentials(credentials_file_path):
    # Criar um objeto ConfigParser
    config = configparser.ConfigParser()
    
    # Ler o arquivo .ini
    config.read(credentials_file_path)
    
    # Obter as credenciais da seção [credentials]
    username = config.get('credentials', 'db_username')
    password = config.get('credentials', 'db_password')
    database = config.get('credentials', 'database')
    server = config.get('credentials', 'server')    
    
    return username, password, database, server

def create_connection_string(username, password, database, server):
    CONNECTION_STRING = (
        'DRIVER=ODBC Driver 17 for SQL Server;'
        'SERVER={};'
        'DATABASE={};'
        'UID={};'
        'PWD={};'
    ).format(server, database, username, password)
    
    return CONNECTION_STRING
