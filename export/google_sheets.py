import pathlib
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime
import locale

# Configurar locale para português
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
    except:
        pass  # Se não conseguir configurar o locale, usa o padrão

SPREADSHEET_ID = None  # Será preenchido na primeira execução

def format_date(date_str: str) -> str:
    """
    Formata a data do post para um formato amigável
    
    Args:
        date_str: String com a data no formato original
        
    Returns:
        str: Data formatada em português
    """
    try:
        # Tenta diferentes formatos de data
        for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%a, %d %b %Y %H:%M:%S %z"]:
            try:
                date = datetime.strptime(date_str, fmt)
                return date.strftime("%d/%m/%Y %H:%M")
            except ValueError:
                continue
        return date_str  # Retorna original se nenhum formato funcionar
    except:
        return date_str

def get_or_create_spreadsheet(sheets_service, drive_service):
    """
    Obtém a planilha fixa ou cria uma nova se não existir
    """
    global SPREADSHEET_ID
    
    # Se já temos o ID da planilha, apenas retorna
    if SPREADSHEET_ID:
        return SPREADSHEET_ID
        
    # Tenta encontrar a planilha pelo nome
    results = drive_service.files().list(
        q="name='Alta Vista - Posts' and mimeType='application/vnd.google-apps.spreadsheet'",
        spaces='drive',
        fields='files(id, name)'
    ).execute()
    
    files = results.get('files', [])
    
    # Se encontrou a planilha, usa ela
    if files:
        SPREADSHEET_ID = files[0]['id']
        return SPREADSHEET_ID
    
    # Se não encontrou, cria uma nova
    spreadsheet = {
        'properties': {
            'title': 'Alta Vista - Posts'
        }
    }
    spreadsheet = sheets_service.spreadsheets().create(body=spreadsheet).execute()
    SPREADSHEET_ID = spreadsheet['spreadsheetId']
    return SPREADSHEET_ID

def share_spreadsheet(drive_service, spreadsheet_id, email):
    """
    Compartilha a planilha com o e-mail fornecido
    """
    try:
        # Verifica se o usuário já tem acesso
        permissions = drive_service.permissions().list(
            fileId=spreadsheet_id,
            fields='permissions(id,emailAddress)'
        ).execute()
        
        # Se o usuário já tem acesso, não precisa compartilhar novamente
        for permission in permissions.get('permissions', []):
            if permission.get('emailAddress') == email:
                print(f"Spreadsheet already shared with {email}")
                return

        # Se não tem acesso, compartilha
        permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': email
        }
        drive_service.permissions().create(
            fileId=spreadsheet_id,
            body=permission,
            fields='id'
        ).execute()
        print(f"Spreadsheet shared with {email}")
    except Exception as e:
        print(f"Warning: Could not share spreadsheet: {e}")

def upload_csv(csv_path: pathlib.Path, share_with_email: str = None) -> str:
    """
    Upload a CSV file to Google Sheets, using a fixed spreadsheet with monthly tabs
    
    Args:
        csv_path (pathlib.Path): Path to the CSV file
        share_with_email (str, optional): Email to share the spreadsheet with
        
    Returns:
        str: URL of the spreadsheet
    """
    # Load credentials
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    current_dir = pathlib.Path(__file__).parent
    credentials_path = current_dir / 'temp_credentials.json'
    
    print(f"Trying to load credentials from: {credentials_path}")
    print(f"File exists: {credentials_path.exists()}")
    
    credentials = service_account.Credentials.from_service_account_file(
        str(credentials_path), scopes=SCOPES)

    # Create services
    sheets_service = build('sheets', 'v4', credentials=credentials)
    drive_service = build('drive', 'v3', credentials=credentials)

    # Get or create the fixed spreadsheet
    spreadsheet_id = get_or_create_spreadsheet(sheets_service, drive_service)

    # Share the spreadsheet if an email is provided
    if share_with_email:
        share_spreadsheet(drive_service, spreadsheet_id, share_with_email)

    # Read CSV
    df = pd.read_csv(csv_path)
    
    # Adiciona coluna de data formatada se não existir
    if 'published' in df.columns:
        df['data_formatada'] = df['published'].apply(format_date)
    
    # Get current month and year
    current_date = datetime.now()
    sheet_name = current_date.strftime("%B %Y").capitalize()
    
    try:
        # Tenta obter a aba
        sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            ranges=sheet_name
        ).execute()
    except:
        # Se a aba não existe, cria
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "requests": [{
                    "addSheet": {
                        "properties": {
                            "title": sheet_name
                        }
                    }
                }]
            }
        ).execute()

    # Prepare data
    values = [df.columns.tolist()] + df.values.tolist()
    
    # Clear existing content in the sheet
    sheets_service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A1:Z"
    ).execute()
    
    # Update spreadsheet
    body = {
        'values': values
    }
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A1",
        valueInputOption='RAW',
        body=body
    ).execute()

    # Return the URL
    return f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}' 