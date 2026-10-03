"""
Lectura del archivo cargado por el usuario.
"""

import pandas as pd


class ErrorDeCarga(Exception):
    """
    El archivo no se pudo leer. El mensaje explica el motivo.
    """


def cargar_excel(archivo):
    """
    Lee un archivo Excel y devuelve un DataFrame.
    Si falla, lanza ErrorDeCarga indicando la causa.
    """

    try:
        return pd.read_excel(archivo)

    except Exception as error:
        raise ErrorDeCarga(
            f"No fue posible leer el archivo: {error}"
        ) from error
