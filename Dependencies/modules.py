from sqlalchemy import create_engine, inspect, event
import os
import sys
import shutil
import re
from datetime import datetime
from urllib import parse
import pandas as pd

class Database:

    def Upload(dataset, table_name, connection_string, if_it_exists, schema):
        """Grava registros armazenados em um DataFrame em um banco de dados SQL"""
        # Criar parâmetros
        params = parse.quote_plus(connection_string)
        # Criar Engine
        engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))
        
        @event.listens_for(engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
            if executemany:
                cursor.fast_executemany = True 
        chunksize = (len(dataset) // 4) + 2
        print(f"-- Table to insert data into........ '{table_name}'")
        dataset.to_sql(table_name, engine, chunksize=chunksize, index=False, if_exists=if_it_exists, schema= schema)

    def Delete(table_name, connection_string, schema):
        """Deleta registros duplicados com base em colunas específicas"""
        
        params = parse.quote_plus(connection_string)
        engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))

        engine.execute(f"""
            WITH CTE AS (
            SELECT 
                case_id, 
                category2,
                last_modified_date,
                product,
                ROW_NUMBER() OVER (PARTITION BY case_id, category2, last_modified_date, product ORDER BY (SELECT NULL)) AS rn
            FROM {schema}.{table_name}
            )
            DELETE
            FROM CTE 
            WHERE rn > 1;
        """)

class Excel:

    def read_excel_with_dynamic_skip(file_path, min_non_nulls=3):
        # Ler o arquivo XLSX em um DataFrame do pandas sem pular linhas
        excel_file = pd.ExcelFile(file_path)
        df = pd.read_excel(excel_file, header=None)
        
        # Inspecionar as primeiras linhas para determinar a linha do cabeçalho
        header_row = None
        for i in range(len(df)):
            row = df.iloc[i]
            non_null_count = row.count()
            if non_null_count >= min_non_nulls:
                # Considera que esta linha é o cabeçalho
                header_row = i
                break
        
        if header_row is not None:
            df = pd.read_excel(file_path, header=header_row)
            excel_file.close()
            return df
        else:
            excel_file.close()
            raise ValueError("Cabeçalho não encontrado")
            
class FileSystem:

    def validate_file_existence(file_path, output_directory, new_file_path):
        """Valida se o arquivo já existe no caminho de output e pede substituição caso sim
        
        :param file_path: 'From' path of file.
        :param output_directory: 'To' path of file.
        :param new_file_path: New name of file, if edited. 
        """
        if os.path.isfile(os.path.join(output_directory, new_file_path)):
            replace_file = input(f"The file for '{new_file_path}' already exists. Replace it? (y/n): ")
            if replace_file.lower() == 'y':
                os.remove(os.path.join(output_directory, new_file_path))
                print(f"Replaced '{new_file_path}'.")
                shutil.move(file_path, os.path.join(output_directory, new_file_path))
            else:
                print(f"File not replaced. Please move it from the Scripts folder!")
                sys.exit()
        else:
            shutil.move(file_path, os.path.join(output_directory, new_file_path))
            print(f"-- File does not exist. Creating one for '{new_file_path}'.")
        
    def extrair_informacoes(nome_arquivo):
        """Extrai o nome da tabela, schema e data em que será upado no banco, diretamente do nome do arquivo

        :param nome_arquivo: Name of '.xlsx' file.
        :return: strings for 'schema', 'table', 'data'
        """
        padrao = r"(\w+)\s-\s([\w\s]+)_(\d{2}-\d{2}-\d{4})\.xlsx"
        match = re.search(padrao, nome_arquivo)
        if match:
            schema = match.group(1) + "_Ops"
            tabela = match.group(2).replace(" ", "_")
            data_str = match.group(3)
            datum = datetime.strptime(data_str, '%d-%m-%Y').strftime('%d/%m/%Y')
            return schema, tabela, datum
        else:
            return None, None, None
        