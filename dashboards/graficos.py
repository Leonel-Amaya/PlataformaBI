import plotly.express as px


def grafico_ventas_producto(df):
    """
    Genera gráfico de barras de los productos y sus ventas
    """

    datos = df.copy()

    if "Total" not in datos.columns:
        datos["Total"] = datos["Cantidad"] * datos["Precio"]

    resumen = (
        datos
        .groupby("Producto", as_index=False)["Total"]
        .sum()
    )

    figura = px.bar(
        resumen,
        x="Producto",
        y="Total",
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
    Genera un grafico de linea de las ventas por fecha
    """

    import pandas as pd
    import plotly.express as px

    datos = df.copy()

    # Convertir la fecha
    datos["Fecha"] = pd.to_datetime(datos["Fecha"])

    # Crear Total si no existe
    if "Total" not in datos.columns:
        datos["Total"] = datos["Cantidad"] * datos["Precio"]

    resumen = (
        datos
        .groupby("Fecha", as_index=False)["Total"]
        .sum()
        .sort_values("Fecha")
    )

    linea = px.line(
        resumen,
        x="Fecha",
        y="Total",
        markers=True,
        title="Ventas por fecha"
    )

    linea.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Ventas"
    )

    return linea