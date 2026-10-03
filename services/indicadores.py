"""
Indicadores principales del negocio.
"""

from services import esquema


def calcular_kpis(df):
    """
    Calcula los indicadores sobre los registros utilizables.

    Un registro es utilizable si tiene un Total numérico. Las filas con
    datos vacíos o mal formateados se excluyen en lugar de romper el cálculo.
    """

    if esquema.TOTAL in df.columns:
        validos = df[df[esquema.TOTAL].notna()]
    else:
        validos = df.iloc[0:0]

    ventas_totales = float(validos[esquema.TOTAL].sum()) if len(validos) else 0.0
    numero_ventas = len(validos)

    if esquema.CLIENTE in validos.columns:
        clientes_unicos = int(validos[esquema.CLIENTE].nunique())
    else:
        clientes_unicos = 0

    if numero_ventas > 0:
        ticket_promedio = ventas_totales / numero_ventas
    else:
        ticket_promedio = 0.0

    return {
        "ventas_totales": ventas_totales,
        "numero_ventas": numero_ventas,
        "clientes_unicos": clientes_unicos,
        "ticket_promedio": ticket_promedio,
        "registros_descartados": len(df) - numero_ventas
    }
