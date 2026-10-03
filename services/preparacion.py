"""
Deja los datos listos para analizar: nombres de columna, tipos y Total.
"""

import pandas as pd

from services import esquema


def preparar_datos(df):
    """
    Normaliza el archivo cargado sin descartar información útil.

    - Lleva los nombres de columna al esquema.
    - Elimina las filas completamente vacías.
    - Convierte Cantidad y Precio a número, y Fecha a fecha.
      Lo que no se puede convertir queda como nulo, no rompe.
    - Calcula Total cuando no viene en el archivo.
    """

    datos = esquema.normalizar_columnas(df)

    datos = datos.dropna(how="all").reset_index(drop=True)

    for columna in esquema.COLUMNAS_NUMERICAS:
        if columna in datos.columns:
            datos[columna] = esquema.a_numero(datos[columna])

    if esquema.FECHA in datos.columns:
        datos[esquema.FECHA] = pd.to_datetime(
            datos[esquema.FECHA],
            errors="coerce"
        )

    for columna in esquema.COLUMNAS_TEXTO:
        if columna in datos.columns:
            texto = datos[columna].astype("string").str.strip()
            datos[columna] = texto.replace("", pd.NA)

    datos[esquema.TOTAL] = _calcular_total(datos)

    return datos


def _calcular_total(datos):
    """
    Usa el Total del archivo si existe y es numérico;
    si no, lo calcula como Cantidad * Precio.
    """

    if esquema.TOTAL in datos.columns:

        total = esquema.a_numero(datos[esquema.TOTAL])

        if total.notna().any():
            return total

    hay_insumos = all(
        columna in datos.columns
        for columna in esquema.COLUMNAS_NUMERICAS
    )

    if hay_insumos:
        return datos[esquema.CANTIDAD] * datos[esquema.PRECIO]

    return pd.Series(pd.NA, index=datos.index, dtype="Float64")
