"""
Filtros aplicados sobre los datos ya preparados.
"""

from services import esquema

TODOS = "Todos"


def opciones_de_producto(df):
    """
    Lista los productos disponibles para el selector.
    """

    if esquema.PRODUCTO not in df.columns:
        return [TODOS]

    productos = (
        df[esquema.PRODUCTO]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    return [TODOS] + sorted(productos)


def filtrar_por_producto(df, producto):
    """
    Filtra por producto. Devuelve todo si no hay selección o si la
    columna no está disponible.
    """

    if producto == TODOS or esquema.PRODUCTO not in df.columns:
        return df

    return df[df[esquema.PRODUCTO] == producto]
