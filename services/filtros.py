def filtrar_por_producto(df, producto):

    if producto == "Todos":
        return df

    return df[df["Producto"] == producto]