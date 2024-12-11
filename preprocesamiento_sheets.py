import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

import boto3
import json
import tempfile


def get_google_credentials_from_secrets():
    # Configuración de AWS Secrets Manager
    client = boto3.client('secretsmanager', region_name='us-east-2')  # Ajusta la región
    secret_name = 'credentials-service-account'  # ARN del secreto exacto

    # Obtener las credenciales del Secret Manager
    response = client.get_secret_value(SecretId=secret_name)
    secret = response['SecretString']
    credentials_info = json.loads(secret)

    # Crear un archivo temporal con las credenciales de Google
    with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as temp_file:
        json.dump(credentials_info, temp_file)
        temp_file_path = temp_file.name  # Ruta del archivo temporal

    return temp_file_path


class GoogleDrive:
    def __init__(self):
        pass

    def access(self):
        ruta_credenciales = get_google_credentials_from_secrets()
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

        return ruta_credenciales, scopes
    
    def obtener_sheets(self):
        ruta_credenciales, scopes = self.access()

        credenciales = Credentials.from_service_account_file(ruta_credenciales, scopes=scopes)
        cliente = gspread.authorize(credenciales)
        
        base_datos = cliente.open("base_datos_tory_cafe")
        sheets = {
            "registro_ventas": base_datos.get_worksheet(0),
            "registro_personalizaciones": base_datos.get_worksheet(1),
            "precios": base_datos.get_worksheet(2),
            "clientes": base_datos.get_worksheet(3),
            "horarios": base_datos.get_worksheet(4),
            "horario_particular": base_datos.get_worksheet(5)
        }

        return sheets

    
class GoogleSheet:
    def __init__(self, sheet_name):
        self.sheet = sheet_name

    def read_data(self, range): #range = "A1:E1". Data devolvera un array de la fila 1 desde la columna A hasta la E
        data = self.sheet.get(range)
        return data

    def read_data_by_uid(self, uid):
        data = self.sheet.get_all_records()
        df = pd.DataFrame(data)
        print(df)
        filtered_data = df[df['uid'] == uid]
        return filtered_data #devuelve un data frame de una tabla, de dos filas siendo la primera las cabeceras de las columnas y la segunda los valores filtrados para acceder a un valor en concreto df["nombre"].to_string()
    
    def write_data(self, range, values): #range ej "A1:V1". values must be a list of list
        self.sheet.update(range, values)

    def write_data_by_uid(self, uid, values): 
        # Find the row index based on the UID
        cell = self.sheet.find(uid)
        row_index = cell.row
        # Update the row with the specified values
        self.sheet.update(f"A{row_index}:E{row_index}", values)

    def get_last_row_range(self):   
        last_row = len(self.sheet.get_all_values()) + 1
        deta = self.sheet.get_values()
        range_start = f"A{last_row}"
        range_end = f"{chr(ord('A') + len(deta[0]) - 1)}{last_row}"
        return f"{range_start}:{range_end}"
    
    def get_all_values(self):
        #self.sheet.get_all_values () # this return a list of list, so the get all records is easier to get values filtering
        return self.sheet.get_all_records() # thislar colum
    
    def delete_row_by_uid(self, uid):
        try:
            # Buscar el UID en la hoja
            cell = self.sheet.find(uid)
            row_index = cell.row
            # Borrar la fila
            self.sheet.delete_rows(row_index)
            print(f"Fila con UID {uid} borrada exitosamente.")
        except gspread.exceptions.CellNotFound:
            print(f"UID {uid} no encontrado.")

    def update_multiple_cells_by_id(self, token_session, dict_columnas_valores):
        try:
            # Obtener los datos de la hoja
            data = self.sheet.get_all_records()
            df = pd.DataFrame(data)
            
            # Buscar el UID en la hoja
            cell = self.sheet.find(token_session)
            row_index = cell.row
            
            # Iterar sobre el diccionario de columnas y valores
            for column_name, new_value in dict_columnas_valores.items():
                # Encontrar el índice de la columna
                col_index = df.columns.get_loc(column_name) + 1  # +1 porque las columnas empiezan desde 1 en Google Sheets
                
                # Actualizar el valor en la celda correspondiente
                self.sheet.update_cell(row_index, col_index, new_value)
                print(f"Celda en la fila {row_index}, columna '{column_name}' actualizada a '{new_value}'.")
                
        except Exception as e:
            print(f"Error: {str(e)}. UID {token_session} no encontrado.")
    

class InsertData:
    def __init__(self, sheet_name):
        self.sheet = sheet_name


    def insert_data(self, token_sesion, numero_bebida):
        clase = GoogleSheet(self.sheet)


        values = [token_sesion, numero_bebida, " ", 
                " ", " ", " ", " ", " ", " "]
        
        value = [values]
        range = clase.get_last_row_range()
        clase.write_data(range, value)


if __name__=="__main__":
    values = ["1", "2", "token", "numero_registro", 
                " ", "telefono", " ", "fecha_registro", 
                "hora_registro", " ", 1, " ", " ", " ", " ", " "]
        
    clase_insert_data = InsertData("registro_ventas")
    clase_insert_data.insert_data(values)
