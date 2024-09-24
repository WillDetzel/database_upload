# database_upload

Uploads data from specific input based on xlsx file.

## Requisites

- Python 3.x (preferably 3 - upper)

- Required libraries: 
pandas==2.2.2
SQLAlchemy==2.0.30
openpyxl==3.1.5

- credentials.ini, containing as follows:
1. db_username - username of database
2. db_password - password of database
3. database - database name
4. server - server name
-> Get a file like this:
[credentials]
db_username = db_username
db_password = db_password
database = database
server = server

## Instalation

Follow the steps below in order to use it:

1. Clone:
    ```bash
    git clone https://github.com/seu-usuario/database_upload.git
    ```
2. Navigation:
    ```bash
    cd project folder
    ```
3. (Opcional) Create an environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Project Structure

├── src/                 # Main Code
├── Dependencies/        # Folder for dependencies
    ├── config.py        # Python file with credentials and database configuration
    ├── modules.py       # Python file with required modules
    ├── credentials.ini  # File containing credentials, as explained above
├── Input/               # Where required files must be
├── Output/              # Where uploaded files will be put - if the folder doesn't exist, it will be created
├── requirements.txt     # Project dependencies
└── readme.md            # This file


## Usage

```bash
python main.py
