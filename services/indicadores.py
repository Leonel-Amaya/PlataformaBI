import pandas as pd


def calcular_kpis(df):
    """
    Calcula indicadores básicos del negocio.
    """

    df = df.copy()

    if "Total" not in df.columns:
        df["Total"] = df["Cantidad"] * df["Precio"]

    ventas_totales = df["Total"].sum()
    numero_ventas = len(df)
    clientes_unicos = df["Cliente"].nunique()
    ticket_promedio = ventas_totales / numero_ventas

    return {
        "ventas_totales": ventas_totales,
        "numero_ventas": numero_ventas,
        "clientes_unicos": clientes_unicos,
        "ticket_promedio": ticket_promedio
    }