import sys
import os
import pandas as pd
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from Dependencies.config import load_credentials, create_connection_string
from Dependencies.modules import Database, Excel, FileSystem

to_db = Database.Upload
from_excel = Excel.read_excel_with_dynamic_skip
validate_files = FileSystem.validate_file_existence
extract_table_data = FileSystem.extrair_informacoes
credentials_file_path = "./Dependencies/credentials.ini"
delete_dupes = Database.Delete


def main():

    username, password, database, server = load_credentials(credentials_file_path)
    connection_string = create_connection_string(username, password, database, server)
    files_folder = f"./Input/"
    output_directory = "./Output"
    output_errors = "./Errors"
    output_cols = "./without_cols"

    try:
        arquivos_excel = [arquivo for arquivo in os.listdir(files_folder) if arquivo.endswith('.xlsx') and arquivo.startswith('Elanco -')]
        total_arquivos = len(arquivos_excel)
    except Exception as error:
        print(f"No such file that starts with the name pattern 'Elanco -[...]', please insert a valid .xlsx file in the Files folder. \n Path: ./Input/")
        sys.exit()

    for i, arquivo in enumerate(arquivos_excel, start=1):

        file = './Input/' + arquivo
        df = from_excel(file)
        empty_columns = [col for col in df.columns if df[col].isnull().all()]
        required_columns = ['case_id', 'category2', 'last_modified_date', 'created_date', 'product']
        new_file_path = f'{os.path.splitext(arquivo)[0]}.xlsx'
        schema, tabela, datum = extract_table_data(arquivo)

        # if tabela == 'Cases_V2_Created_Daily' or tabela == 'Cases_V2_Modified_Daily':
        #     delete_dupes(tabela, connection_string, schema)

        df.drop(columns=empty_columns, inplace=True)

        df['Created On'] = pd.to_datetime(datum, format='%d/%m/%Y').date()

        try:
            df.columns = [x.lower().replace(' ','_').replace('?','').replace('-' ,'_').replace(r'/' , '_').replace('\\' , '_').replace('#' , '_') \
                                    .replace(')' , '_').replace(r'(' , '_').replace('$' , '_') for x in df.columns]
        except Exception as error:
            print(f'Arquivo ::: {arquivo} sem colunas válidas. Movendo para pasta "without_cols"')
            
            if not os.path.exists(output_cols):
                os.makedirs(output_cols)

            validate_files(file, output_cols, new_file_path)
            continue

        if all(col in df.columns for col in required_columns):
            # Removendo duplicados se as colunas estiverem presentes
            df_sem_duplicados = df.drop_duplicates(subset=required_columns)
            df_sem_duplicados

        for col in df.columns:
            if 'date' in col:
                try:
                    df[col] = pd.to_datetime(df[col], yearfirst=True)
                except ValueError:
                    print(f"A coluna {col} não pôde ser convertida para datetime com o formato especificado.")
        
        excel_file = pd.ExcelFile(file)
        excel_file.close()

        print(f"{i}/{total_arquivos} ::: To upload ::: {arquivo}")

        try:
            to_db(df, tabela, connection_string, 'append', schema)

            if not os.path.exists(output_directory):
                os.makedirs(output_directory)

            validate_files(file, output_directory, new_file_path)

        except Exception as error:
            print(f"\n-- Error when uploading to database::: \n\n{error}\n")
            
            if not os.path.exists(output_errors):
                os.makedirs(output_errors)

            validate_files(file, output_errors, new_file_path)

    print("-- Done --")

if __name__ == "__main__":

    main()
