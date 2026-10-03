"""
Define el esquema de datos esperado y reconoce nombres de columna alternativos.
"""

import unicodedata

import pandas as pd

FECHA = "Fecha"
CLIENTE = "Cliente"
PRODUCTO = "Producto"
CANTIDAD = "Cantidad"
PRECIO = "Precio"
TOTAL = "Total"

COLUMNAS_REQUERIDAS = [FECHA, CLIENTE, PRODUCTO, CANTIDAD, PRECIO]
COLUMNAS_NUMERICAS = [CANTIDAD, PRECIO]
COLUMNAS_TEXTO = [CLIENTE, PRODUCTO]
COLUMNAS_CONOCIDAS = COLUMNAS_REQUERIDAS + [TOTAL]

# Nombres alternativos que se aceptan para cada columna del esquema.
# Las llaves se comparan sin mayúsculas, sin tildes y sin espacios sobrantes.
ALIAS = {
    "fecha": FECHA,
    "fechas": FECHA,
    "fecha de venta": FECHA,
    "fecha venta": FECHA,
    "dia": FECHA,

    "cliente": CLIENTE,
    "clientes": CLIENTE,
    "nombre del cliente": CLIENTE,
    "nombre cliente": CLIENTE,
    "comprador": CLIENTE,

    "producto": PRODUCTO,
    "productos": PRODUCTO,
    "articulo": PRODUCTO,
    "item": PRODUCTO,
    "descripcion": PRODUCTO,

    "cantidad": CANTIDAD,
    "cantidades": CANTIDAD,
    "unidades": CANTIDAD,
    "cant": CANTIDAD,

    "precio": PRECIO,
    "precios": PRECIO,
    "precio unitario": PRECIO,
    "valor unitario": PRECIO,
    "valor": PRECIO,

    "total": TOTAL,
    "venta total": TOTAL,
    "importe": TOTAL,
    "subtotal": TOTAL,
}


def _clave(nombre):
    """
    Reduce un nombre de columna a una forma comparable:
    sin mayúsculas, sin tildes y con los espacios normalizados.
    """

    texto = str(nombre).strip().lower()

    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))

    texto = texto.replace("_", " ").replace("-", " ")

    return " ".join(texto.split())


def mapa_renombres(df):
    """
    Devuelve qué columnas del archivo corresponden a columnas del esquema.
    Una columna que ya tiene el nombre correcto nunca se reemplaza.
    """

    ocupadas = {c for c in df.columns if c in COLUMNAS_CONOCIDAS}
    renombres = {}

    for columna in df.columns:

        if columna in COLUMNAS_CONOCIDAS:
            continue

        canonico = ALIAS.get(_clave(columna))

        if canonico is not None and canonico not in ocupadas:
            renombres[columna] = canonico
            ocupadas.add(canonico)

    return renombres


def normalizar_columnas(df):
    """
    Devuelve una copia con los nombres de columna llevados al esquema.
    """

    return df.rename(columns=mapa_renombres(df))


def columnas_faltantes(df):
    """
    Lista las columnas requeridas que no están en el archivo.
    """

    return [c for c in COLUMNAS_REQUERIDAS if c not in df.columns]


def celdas_vacias(serie):
    """
    Marca las celdas vacías, incluyendo las que solo contienen espacios.
    """

    texto = serie.astype("string").str.strip()

    return serie.isna() | texto.eq("").fillna(False)


def a_numero(serie):
    """
    Convierte a número tolerando los formatos que llegan desde Excel:
    símbolo de moneda, espacios, punto como separador de miles y coma
    como separador decimal. Lo que no se puede convertir queda nulo.
    """

    if pd.api.types.is_numeric_dtype(serie):
        return pd.to_numeric(serie, errors="coerce")

    texto = serie.astype("string").str.strip()

    # Quitar moneda y espacios: "$ 45.000" -> "45.000"
    texto = texto.str.replace(r"[$\s]", "", regex=True)

    # Punto como separador de miles: "1.234.567,89" -> "1234567.89"
    miles_punto = texto.str.fullmatch(
        r"-?\d{1,3}(\.\d{3})+(,\d+)?"
    ).fillna(False)

    texto = texto.mask(
        miles_punto,
        texto.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    )

    # Coma como separador de miles: "1,234,567.89" -> "1234567.89"
    miles_coma = texto.str.fullmatch(
        r"-?\d{1,3}(,\d{3})+(\.\d+)?"
    ).fillna(False)

    texto = texto.mask(
        miles_coma,
        texto.str.replace(",", "", regex=False)
    )

    # Lo que queda con coma usa coma decimal: "80,5" -> "80.5"
    texto = texto.mask(
        ~(miles_punto | miles_coma),
        texto.str.replace(",", ".", regex=False)
    )

    return pd.to_numeric(texto, errors="coerce")
