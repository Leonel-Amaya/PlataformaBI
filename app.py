import streamlit as st
from services.cargar_archivo import cargar_excel
from services.indicadores import calcular_kpis
from dashboards.graficos import grafico_ventas_producto, grafico_ventas_fecha

st.set_page_config(
    page_title="Consultoría BI",
    layout="wide"
)

st.title("Consultoría en Inteligencia de Negocios")

st.write(
    "Este MVP permite cargar información empresarial para generar indicadores."
)

archivo = st.file_uploader(
    "Seleccione un archivo Excel",
    type=["xlsx"]
)

if archivo is not None:

    datos = cargar_excel(archivo)

    if datos is not None:

        # Tabla vista previa
        st.success("Archivo cargado correctamente")
        st.subheader("Vista previa")
        st.dataframe(datos)

        # KPIs
        kpis = calcular_kpis(datos)
        st.subheader("Indicadores principales")
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

        # Gráficos
        st.subheader("Análisis de ventas")
        figura = grafico_ventas_producto(datos)
        st.plotly_chart(figura, width='stretch')

        st.subheader("Comportamiento de las ventas")
        linea = grafico_ventas_fecha(datos)
        st.plotly_chart(linea, width='stretch')

    else:

        st.error("No fue posible leer el archivo.")