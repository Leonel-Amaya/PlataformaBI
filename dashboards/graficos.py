"""
Gráficos del tablero. Reciben datos ya preparados.

Cuando no hay información suficiente para dibujar, devuelven None
en lugar de fallar, y la vista muestra el mensaje correspondiente.
"""

import pandas as pd
import plotly.express as px

from services import esquema


def _datos_utilizables(df, columna):
    """
    Deja solo las filas con la columna pedida y el Total disponibles.
    """

    faltan = [c for c in (columna, esquema.TOTAL) if c not in df.columns]

    if faltan:
        return None

    datos = df[[columna, esquema.TOTAL]].dropna()

    if datos.empty:
        return None

    return datos


def grafico_ventas_producto(df):
    """
    Genera gráfico de barras de los productos y sus ventas.
    """

    datos = _datos_utilizables(df, esquema.PRODUCTO)

    if datos is None:
        return None

    resumen = (
        datos
        .groupby(esquema.PRODUCTO, as_index=False)[esquema.TOTAL]
        .sum()
        .sort_values(esquema.TOTAL, ascending=False)
    )

    figura = px.bar(
        resumen,
        x=esquema.PRODUCTO,
        y=esquema.TOTAL,
        title="Ventas por producto",
        text_auto=True
    )

    figura.update_layout(
        xaxis_title="Producto",
        yaxis_title="Ventas"
    )

    return figura


def grafico_ventas_fecha(df):
    """
    Genera un gráfico de línea de las ventas por fecha.
    """

    datos = _datos_utilizables(df, esquema.FECHA)

    if datos is None:
        return None

    datos[esquema.FECHA] = pd.to_datetime(
        datos[esquema.FECHA],
        errors="coerce"
    )

    datos = datos.dropna(subset=[esquema.FECHA])

    if datos.empty:
        return None

    resumen = (
        datos
        .groupby(esquema.FECHA, as_index=False)[esquema.TOTAL]
        .sum()
        .sort_values(esquema.FECHA)
    )

    linea = px.line(
        resumen,
        x=esquema.FECHA,
        y=esquema.TOTAL,
        markers=True,
        title="Ventas por fecha"
    )

    linea.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Ventas"
    )

    return linea
