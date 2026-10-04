"""
Gráficos del tablero. Reciben datos ya preparados.

Cuando no hay información suficiente para dibujar, devuelven None
en lugar de fallar, y la vista muestra el mensaje correspondiente.
"""

import pandas as pd
import plotly.express as px

from services import esquema

# Medidas disponibles para el ranking de productos
MEDIDA_VENTAS = "ventas"
MEDIDA_UNIDADES = "unidades"

# Cantidad de productos que se muestran por separado en la torta
TOP_PRODUCTOS = 5
OTROS = "Otros"

# Con una o dos porciones la torta no comunica nada: una sola porción
# siempre es el 100%. Por debajo de este mínimo no se dibuja.
MINIMO_PORCIONES = 3

# Paleta categórica validada para daltonismo en ambos temas.
# Los cinco primeros colores identifican productos; el gris es el resto
# agrupado, que es contexto y no una identidad propia.
PALETA = {
    "light": {
        "series": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"],
        "otros": "#c3c2b7",
        "superficie": "#fcfcfb",
        "texto": "#0b0b0b"
    },
    "dark": {
        "series": ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181"],
        "otros": "#c3c2b7",
        "superficie": "#1a1a19",
        "texto": "#ffffff"
    }
}


def _datos_utilizables(df, columna, valor=None):
    """
    Deja solo las filas que tienen disponibles la columna pedida y la
    columna de valor (por defecto, Total).
    """

    valor = valor or esquema.TOTAL

    if columna not in df.columns or valor not in df.columns:
        return None

    datos = df[[columna, valor]].dropna()

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


def _resumen_top(df, medida):
    """
    Suma la medida por producto, deja los TOP_PRODUCTOS mayores y agrupa
    el resto bajo 'Otros'. Devuelve None si no hay nada que mostrar.
    """

    if medida == MEDIDA_UNIDADES:
        valor = esquema.CANTIDAD
    else:
        valor = esquema.TOTAL

    datos = _datos_utilizables(df, esquema.PRODUCTO, valor)

    if datos is None:
        return None

    resumen = (
        datos
        .groupby(esquema.PRODUCTO, as_index=False)[valor]
        .sum()
    )

    # Una torta representa partes de un total: los valores negativos o en
    # cero no tienen una porción que mostrar.
    resumen = resumen[resumen[valor] > 0]

    if resumen.empty:
        return None

    resumen = resumen.sort_values(valor, ascending=False)

    principales = resumen.head(TOP_PRODUCTOS)
    resto = resumen.iloc[TOP_PRODUCTOS:]

    if not resto.empty:

        agrupado = pd.DataFrame({
            esquema.PRODUCTO: [OTROS],
            valor: [resto[valor].sum()]
        })

        principales = pd.concat([principales, agrupado], ignore_index=True)

    return principales.rename(columns={valor: "Valor"})


def _tema_actual():
    """
    Devuelve el tema activo de Streamlit para elegir la paleta.
    """

    try:
        import streamlit as st
        tipo = st.context.theme.type
    except Exception:
        tipo = None

    return "dark" if tipo == "dark" else "light"


def grafico_torta_productos(df, medida=MEDIDA_VENTAS):
    """
    Genera una torta con la participación de los productos más vendidos.

    Muestra por separado los TOP_PRODUCTOS primeros y agrupa el resto en
    'Otros', para que las porciones sigan siendo comparables a simple vista.
    """

    resumen = _resumen_top(df, medida)

    if resumen is None or len(resumen) < MINIMO_PORCIONES:
        return None

    paleta = PALETA[_tema_actual()]

    colores = [
        paleta["otros"] if nombre == OTROS else paleta["series"][i]
        for i, nombre in enumerate(resumen[esquema.PRODUCTO])
    ]

    if medida == MEDIDA_UNIDADES:
        titulo = f"Top {TOP_PRODUCTOS} productos por unidades vendidas"
        formato = "%{value:,.0f} unidades"
    else:
        titulo = f"Top {TOP_PRODUCTOS} productos por ventas"
        formato = "$%{value:,.0f}"

    torta = px.pie(
        resumen,
        names=esquema.PRODUCTO,
        values="Valor",
        title=titulo,
        hole=0.45
    )

    torta.update_traces(
        sort=False,
        direction="clockwise",
        marker=dict(
            colors=colores,
            # Separador del color de fondo entre porciones contiguas
            line=dict(color=paleta["superficie"], width=2)
        ),
        # Etiqueta directa en cada porción: la identidad nunca depende
        # solo del color
        textinfo="label+percent",
        textposition="auto",
        insidetextorientation="horizontal",
        hovertemplate=(
            "<b>%{label}</b><br>"
            + formato
            + "<br>%{percent} del total<extra></extra>"
        )
    )

    torta.update_layout(
        showlegend=True,
        legend=dict(title="Producto"),
        uniformtext=dict(minsize=11, mode="hide")
    )

    return torta
