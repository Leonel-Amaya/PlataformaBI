import pandas as pd

def cargar_excel(archivo):
    """
    Lee un archivo Excel y devuelve un DataFrame.
    """

    try:
        df = pd.read_excel(archivo)
        return df

    except Exception as e:
        return None