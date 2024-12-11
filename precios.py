from preprocesamiento_sheets import GoogleDrive

clase_google_drive = GoogleDrive()
sheets = clase_google_drive.obtener_sheets()
import pandas as pd

class Precios():
    def __init__(self, sheet_name):
        self.sheet_name = sheet_name

    def obtener_precios(self, producto):

        hoja1 = self.sheet_name
        data = hoja1.get_all_records()

        df = pd.DataFrame(data)
        
        #categoria_bebidas dicc
        dicc = {}
        df1 = df[df["producto"] == producto].copy()

        # Luego realiza tus modificaciones de forma segura con .loc
        df1["precio"] = df1["precio"].apply(str)  # Alternativa segura a astype("str")

        df1.loc[:, "concatenar"] = df1["subcategoria"] + ' - ' + df1["precio"] + ' ' + df1["moneda"]
        categorias = df1.categoria.unique()
        for categoria in categorias:
            aux = list(df1[df1["categoria"] == categoria ].concatenar.unique())
            dicc[categoria] = aux

        return dicc
    

if __name__ == "__main__":
    precios = sheets["precios"]
    clase = Precios(precios)
    dicc = clase.obtener_precios("bebida")
    print(dicc)