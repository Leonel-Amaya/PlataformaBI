import streamlit as st
from services.cargar_archivo import cargar_excel

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

        st.success("Archivo cargado correctamente")

        st.subheader("Vista previa")

        st.dataframe(datos)

    else:

        st.error("No fue posible leer el archivo.")