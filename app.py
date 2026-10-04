import streamlit as st

from services import esquema
from services.cargar_archivo import ErrorDeCarga, cargar_excel
from services.preparacion import preparar_datos
from services.validacion import AUSENTE, AVISO, ERROR, OK, validar_datos
from services.filtros import filtrar_por_producto, opciones_de_producto
from services.indicadores import calcular_kpis
from dashboards.graficos import (
    MEDIDA_UNIDADES,
    MINIMO_PORCIONES,
    MEDIDA_VENTAS,
    grafico_torta_productos,
    grafico_ventas_fecha,
    grafico_ventas_producto
)

st.set_page_config(
    page_title="Consultoría BI",
    layout="wide"
)

# Cómo se muestra cada estado de la validación
# Cómo se mide el ranking de productos
MEDIDAS = {
    "Ventas ($)": MEDIDA_VENTAS,
    "Unidades": MEDIDA_UNIDADES
}

MOSTRAR = {
    OK: st.success,
    AVISO: st.warning,
    ERROR: st.error,
    AUSENTE: st.error
}

st.title("Consultoría en Inteligencia de Negocios")

st.write(
    "Este MVP permite cargar información empresarial para generar indicadores."
)

archivo = st.file_uploader(
    "Seleccione un archivo Excel",
    type=["xlsx"]
)

if archivo is None:
    st.info(
        "El archivo debe incluir las columnas: "
        f"{', '.join(esquema.COLUMNAS_REQUERIDAS)}."
    )
    st.stop()

# Carga
try:
    datos_originales = cargar_excel(archivo)

except ErrorDeCarga as error:
    st.error(str(error))
    st.stop()

st.success("Archivo cargado correctamente")

# Vista previa
st.subheader("Vista previa")
st.dataframe(datos_originales)

# Validación sobre el archivo completo, antes de filtrar
st.subheader("Calidad de los datos")

for resultado in validar_datos(datos_originales):
    MOSTRAR[resultado.estado](f"**{resultado.titulo}:** {resultado.mensaje}")

# Sin las columnas requeridas no hay nada que calcular
datos = preparar_datos(datos_originales)
faltantes = esquema.columnas_faltantes(datos)

if faltantes:
    st.warning(
        "No se pueden generar indicadores hasta corregir la estructura "
        "del archivo."
    )
    st.stop()

# Filtro
producto_seleccionado = st.selectbox(
    "Seleccione un producto",
    opciones_de_producto(datos)
)

datos = filtrar_por_producto(datos, producto_seleccionado)

if datos.empty:
    st.info("No hay registros para la selección actual.")
    st.stop()

# KPIs
kpis = calcular_kpis(datos)

st.subheader("Indicadores principales")

if kpis["numero_ventas"] == 0:
    st.warning(
        "Ningún registro de la selección tiene Cantidad y Precio válidos, "
        "por lo que no se pueden calcular los indicadores."
    )

else:
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Ventas Totales",
        f"${kpis['ventas_totales']:,.0f}"
    )

    col2.metric(
        "Número de Ventas",
        kpis["numero_ventas"]
    )

    col3.metric(
        "Clientes",
        kpis["clientes_unicos"]
    )

    col4.metric(
        "Ticket Promedio",
        f"${kpis['ticket_promedio']:,.0f}"
    )

    if kpis["registros_descartados"] > 0:
        st.caption(
            f"Se excluyeron {kpis['registros_descartados']} registros "
            f"por tener datos vacíos o inválidos."
        )

# Gráficos
st.subheader("Análisis de ventas")

figura = grafico_ventas_producto(datos)

if figura is None:
    st.info("No hay datos suficientes para graficar las ventas por producto.")
else:
    st.plotly_chart(figura, width='stretch')

st.subheader("Participación por producto")

medida = st.radio(
    "Medir los más vendidos por",
    list(MEDIDAS),
    horizontal=True
)

torta = grafico_torta_productos(datos, medida=MEDIDAS[medida])

if torta is None:
    st.info(
        "La participación se muestra cuando hay al menos "
        f"{MINIMO_PORCIONES} productos con valores positivos."
    )
else:
    st.plotly_chart(torta, width='stretch')

st.subheader("Comportamiento de las ventas")

linea = grafico_ventas_fecha(datos)

if linea is None:
    st.info("No hay datos suficientes para graficar las ventas por fecha.")
else:
    st.plotly_chart(linea, width='stretch')
