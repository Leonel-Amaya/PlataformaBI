"""
Valida la calidad de los datos sin interrumpir la ejecución.

Ninguna comprobación lanza excepciones: si una columna no existe o trae
un formato equivocado, se reporta como hallazgo y el análisis continúa.
"""

from dataclasses import dataclass

import pandas as pd

from services import esquema

OK = "ok"
AVISO = "aviso"
ERROR = "error"
AUSENTE = "ausente"


@dataclass
class Resultado:
    """
    Hallazgo individual de la validación.
    """

    titulo: str
    estado: str
    mensaje: str


def validar_datos(df):
    """
    Revisa el archivo y devuelve la lista de hallazgos.
    """

    datos = esquema.normalizar_columnas(df)

    resultados = [
        _validar_estructura(df, datos),
        _validar_filas_vacias(datos),
        _validar_celdas_vacias(datos),
        _validar_duplicados(datos),
    ]

    for columna in esquema.COLUMNAS_NUMERICAS:
        resultados.append(_validar_numerica(datos, columna))

    resultados.append(_validar_fechas(datos))

    return resultados


def _validar_estructura(original, datos):
    """
    Comprueba que estén las columnas requeridas e informa las que se
    reconocieron bajo otro nombre.
    """

    faltantes = esquema.columnas_faltantes(datos)
    renombradas = esquema.mapa_renombres(original)

    if faltantes:

        detalle = ", ".join(faltantes)

        return Resultado(
            "Estructura del archivo",
            ERROR,
            f"Faltan las columnas requeridas: {detalle}. "
            f"El archivo debe incluir: "
            f"{', '.join(esquema.COLUMNAS_REQUERIDAS)}."
        )

    if renombradas:

        detalle = ", ".join(
            f"'{origen}' como '{destino}'"
            for origen, destino in renombradas.items()
        )

        return Resultado(
            "Estructura del archivo",
            AVISO,
            f"Están todas las columnas requeridas. Se interpretó {detalle}."
        )

    return Resultado(
        "Estructura del archivo",
        OK,
        "El archivo tiene todas las columnas requeridas."
    )


def _validar_filas_vacias(datos):
    """
    Cuenta las filas sin ningún dato.
    """

    if datos.empty:
        return Resultado(
            "Filas vacías",
            ERROR,
            "El archivo no contiene registros."
        )

    vacias = int(datos.isna().all(axis=1).sum())

    if vacias == 0:
        return Resultado(
            "Filas vacías",
            OK,
            "No hay filas vacías."
        )

    return Resultado(
        "Filas vacías",
        AVISO,
        f"Se encontraron {vacias} filas completamente vacías. "
        f"Se descartan del análisis."
    )


def _validar_celdas_vacias(datos):
    """
    Cuenta las celdas vacías de cada columna requerida presente.
    """

    presentes = [c for c in esquema.COLUMNAS_REQUERIDAS if c in datos.columns]

    if not presentes:
        return Resultado(
            "Celdas vacías",
            AUSENTE,
            "No se puede revisar: no hay columnas del esquema en el archivo."
        )

    conteos = {}

    for columna in presentes:
        vacias = int(esquema.celdas_vacias(datos[columna]).sum())
        if vacias > 0:
            conteos[columna] = vacias

    if not conteos:
        return Resultado(
            "Celdas vacías",
            OK,
            "No se encontraron celdas vacías."
        )

    detalle = ", ".join(
        f"{columna}: {cantidad}"
        for columna, cantidad in conteos.items()
    )

    return Resultado(
        "Celdas vacías",
        AVISO,
        f"Hay celdas vacías ({detalle}). "
        f"Esos registros se excluyen de los cálculos afectados."
    )


def _validar_duplicados(datos):
    """
    Cuenta los registros repetidos.
    """

    if datos.empty:
        return Resultado(
            "Registros duplicados",
            AUSENTE,
            "No hay registros para revisar."
        )

    duplicados = int(datos.duplicated().sum())

    if duplicados == 0:
        return Resultado(
            "Registros duplicados",
            OK,
            "No se encontraron registros duplicados."
        )

    return Resultado(
        "Registros duplicados",
        AVISO,
        f"Se encontraron {duplicados} registros duplicados."
    )


def _validar_numerica(datos, columna):
    """
    Revisa que una columna numérica tenga números y que sean mayores a cero.
    """

    if columna not in datos.columns:
        return Resultado(
            columna,
            AUSENTE,
            f"La columna '{columna}' no está en el archivo, "
            f"no se pudo validar."
        )

    serie = datos[columna]
    numeros = esquema.a_numero(serie)

    sin_formato = int((~esquema.celdas_vacias(serie) & numeros.isna()).sum())
    no_positivos = int((numeros <= 0).sum())

    problemas = []

    if sin_formato > 0:
        problemas.append(
            f"{sin_formato} valores que no son numéricos"
        )

    if no_positivos > 0:
        problemas.append(
            f"{no_positivos} valores menores o iguales a cero"
        )

    if not problemas:
        return Resultado(
            columna,
            OK,
            f"Todos los valores de '{columna}' son válidos."
        )

    return Resultado(
        columna,
        ERROR,
        f"En '{columna}' hay {' y '.join(problemas)}."
    )


def _validar_fechas(datos):
    """
    Revisa que la columna de fecha se pueda interpretar.
    """

    if esquema.FECHA not in datos.columns:
        return Resultado(
            esquema.FECHA,
            AUSENTE,
            f"La columna '{esquema.FECHA}' no está en el archivo, "
            f"no se pudo validar."
        )

    serie = datos[esquema.FECHA]
    fechas = pd.to_datetime(serie, errors="coerce")

    invalidas = int((~esquema.celdas_vacias(serie) & fechas.isna()).sum())

    if invalidas == 0:
        return Resultado(
            esquema.FECHA,
            OK,
            "Todas las fechas son válidas."
        )

    return Resultado(
        esquema.FECHA,
        ERROR,
        f"Hay {invalidas} fechas que no se pudieron interpretar."
    )
