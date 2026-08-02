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