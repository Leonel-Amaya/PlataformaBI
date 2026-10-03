# Backlog de mejoras técnicas

Estado del análisis: 2026-09-28. Última actualización: 2026-10-03.
Resueltos los puntos 1-10, 12 y 14 (robustez de carga y validación). Los fallos marcados como **verificado** fueron
reproducidos ejecutando el código, no son suposiciones.

---

## Prioridad 1 — Fallos que rompen la app

- [x] **1. Sin validación de esquema al cargar el archivo**
  Si el Excel no trae `Producto`, `app.py:30` lanza `KeyError` antes de cualquier
  validación. Lo mismo con `Cliente` en `services/indicadores.py:16`.
  *Solución:* validar columnas requeridas justo después de cargar y mostrar qué falta.

- [x] **2. `ZeroDivisionError` con archivo vacío** — *verificado*
  `services/indicadores.py:17` — `ventas_totales / numero_ventas` revienta si el
  archivo (o el filtro aplicado) deja 0 filas.
  *Solución:* guardia de división y estado vacío en la UI.

- [x] **3. `TypeError` si `Precio` o `Cantidad` vienen como texto** — *verificado*
  `services/validacion.py:19` — comparar `"80000" <= 0` falla. Muy común en Excel
  con celdas formateadas como texto.
  *Solución:* `pd.to_numeric(errors="coerce")` y reportar los no convertibles como
  dato inválido.

- [x] **4. El gráfico de línea revienta con fechas inválidas** — *verificado*
  `dashboards/graficos.py:46` usa `pd.to_datetime()` sin `errors="coerce"`.
  Contradicción interna: la validación detecta y reporta las fechas malas, pero el
  flujo sigue y el gráfico se cae con esas mismas fechas.
  *Solución:* `errors="coerce"` y descartar nulos antes de agrupar.

- [x] **5. Validación silenciosa en falso positivo** — *verificado*
  `services/validacion.py:20-21` — si falta la columna `Precio`, devuelve `0` y la UI
  muestra "Todos los precios son válidos". Reportar "todo bien" sobre algo que ni
  existe es peor que fallar.
  *Solución:* distinguir tres estados: válido / inválido / columna ausente.

---

## Prioridad 2 — Diseño y correctitud

- [x] **6. Se valida después de filtrar**
  `app.py:38-49` — la calidad de datos reportada es la del producto seleccionado, no
  la del archivo. Al cambiar de producto cambian los indicadores de calidad.
  *Solución:* validar el archivo completo una vez; filtrar solo para KPIs y gráficos.

- [x] **7. `Total` se calcula en tres lugares distintos**
  `services/indicadores.py:12`, `dashboards/graficos.py:12` y `dashboards/graficos.py:50`
  repiten `Cantidad * Precio`. Si cambia la regla (descuento, IVA), hay que acordarse
  de tres sitios.
  *Solución:* centralizar en `preparar_datos()` que normalice tipos y calcule `Total`
  una sola vez. **Destraba varios de los demás puntos.**

- [x] **8. `validar_datos()` devuelve tipos mezclados**
  `nulos` es una `Series` y el resto son enteros, por eso `app.py:52` hace `.sum()`.
  *Solución:* estructura de retorno uniforme (dataclass o dict de forma fija).

- [x] **9. El error de carga se descarta**
  `services/cargar_archivo.py:12` captura la excepción, no usa `e` y devuelve `None`.
  Nunca se sabe por qué falló: ¿archivo corrupto, protegido, formato raro?
  *Solución:* propagar el motivo hasta la UI.

- [x] **10. Nombres de columna repetidos como literales**
  `"Producto"`, `"Precio"`, `"Cantidad"`, `"Fecha"`, `"Cliente"` están escritos a mano
  en cinco archivos. Un typo no se detecta hasta tiempo de ejecución.
  *Solución:* módulo de constantes / esquema.

---

## Prioridad 3 — Rendimiento y estructura

- [ ] **11. Sin caché: el Excel se relee en cada interacción**
  Streamlit re-ejecuta todo el script con cada cambio del `selectbox`, así que
  `cargar_excel()` vuelve a parsear el archivo cada vez. Con 6 filas no se nota; con
  50.000 sí.
  *Solución:* `@st.cache_data` en carga y agregaciones.

- [x] **12. `import` dentro de la función**
  `dashboards/graficos.py:40-41` — `pandas` y `plotly` importados dentro de
  `grafico_ventas_fecha`, y `plotly` ya estaba arriba. Mover al encabezado.

- [ ] **13. Sin tipado ni docstring uniforme**
  Sin type hints en ningún módulo; `services/filtros.py` es el único sin docstring.

- [x] **14. `app.py` crece lineal**
  123 líneas y seguirá creciendo con cada sección nueva. Los cinco bloques `if/else`
  de validación (`app.py:54-85`) son el mismo patrón repetido cinco veces.
  *Solución:* extraer el render de validación a una función que itere sobre los
  resultados.

---

## Prioridad 4 — Proyecto y entrega

- [ ] **15. Sin pruebas**
  No hay un solo test. Los servicios son funciones puras con entrada/salida clara —
  el código más fácil de testear.

- [ ] **16. `requirements.txt` es un `pip freeze` completo**
  44 líneas con dependencias transitivas pinneadas. Las directas reales son cuatro:
  `streamlit`, `pandas`, `plotly`, `openpyxl`.

- [ ] **17. Sin README**
  No hay instrucciones de instalación ni ejecución, ni documentación del formato de
  Excel esperado.

- [ ] **18. Sin manejo de errores global en la UI**
  Cualquier excepción no capturada le muestra al usuario un traceback de Python.

---

## Resumen

El proyecto está bien estructurado: la separación en capas
(`app.py` → `services/` → `dashboards/`) es correcta. El problema no es la
arquitectura, es la **robustez ante datos reales**: todo el código asume que el Excel
viene perfecto. Los puntos 1 a 5 son los que convierten una demo exitosa en una demo
fallida.

**Orden recomendado:** Prioridad 1 completa en una sola pasada (cambios pequeños y
relacionados entre sí), luego el punto 7.

---

## Esquema de datos esperado

Contrato implícito definido por `examples/ventas.xlsx`:

| Columna    | Tipo     | Notas                          |
|------------|----------|--------------------------------|
| `Fecha`    | datetime |                                |
| `Cliente`  | texto    |                                |
| `Producto` | texto    |                                |
| `Cantidad` | entero   | debe ser > 0                   |
| `Precio`   | entero   | debe ser > 0                   |
| `Total`    | numérico | opcional, se calcula si falta  |
