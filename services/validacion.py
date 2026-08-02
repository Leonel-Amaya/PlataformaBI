import pandas as pd


def validar_datos(df):
    """
    Valida la calidad de los datos
    """

    resultados = {}

    # Valores nulos por columna
    resultados["nulos"] = df.isnull().sum()

    # Registros duplicados
    resultados["duplicados"] = df.duplicated().sum()

    # Validar precios negativos o cero
    if "Precio" in df.columns:
        resultados["precios_invalidos"] = (df["Precio"] <= 0).sum()
    else:
        resultados["precios_invalidos"] = 0

    # Validar cantidades negativas o cero
    if "Cantidad" in df.columns:
        resultados["cantidades_invalidas"] = (df["Cantidad"] <= 0).sum()
    else:
        resultados["cantidades_invalidas"] = 0

    # Validar fechas
    if "Fecha" in df.columns:

        fechas = pd.to_datetime(
            df["Fecha"],
            errors="coerce"
        )

        resultados["fechas_invalidas"] = fechas.isna().sum()

    else:
        resultados["fechas_invalidas"] = 0

    return resultados