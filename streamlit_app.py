import altair as alt
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Calculadora de actividades", page_icon="🎬")
st.title("Calculadora de actividades diarias")
st.write("""
En esta página podrás calcular los gastos necesarios para poder registrar tus actividades diarias.
""")

# Ruta del archivo CSV
csv_path = "data/Datos_de_matricula.csv"

# Cargar el archivo CSV
df = pd.read_csv(csv_path)

# Convertir columnas numéricas (por si vienen como texto)
cols_numericas = ["coste", "presupuesto", "n_de_personas"]
for c in cols_numericas:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# Mostrar DataFrame
st.subheader("Datos registrados")
st.dataframe(df, hide_index=True)

# -------------------------------------------------------------------------
# Formulario para agregar datos
# -------------------------------------------------------------------------
st.subheader("Agregar nueva actividad")
with st.form("agregar_datos"):
    fecha = st.date_input("Introduzca la fecha")
    nombre = st.text_input("Introduzca el nombre de la actividad")
    coste = st.number_input("Introduzca el costo", min_value=1)
    presupuesto = st.number_input("Introduzca el presupuesto", min_value=1)
    tiempo = st.number_input("Introduzca el tiempo invertido", min_value=1)
    tipo = st.selectbox(
        "Seleccione el tipo de actividad",
        ["Alimento", "Ahorro", "Transporte", "Académico", "Entretenimiento",
         "Ejercicio", "Salud", "Inversión", "Deporte", "Ocio", "Otros"]
    )
    momento = st.selectbox("Seleccione el momento", ["Mañana", "Tarde", "Noche"])
    personas = st.number_input("Introduzca el número de personas", min_value=1)
    
    boton_agregar = st.form_submit_button("Agregar")

    if boton_agregar:
        # Crear nuevo registro
        nuevo = {
            "fecha": fecha.strftime("%d/%m/%Y"),
            "nombre_actividad": nombre,
            "coste": coste,
            "presupuesto": presupuesto,
            "tiempo_invertido": tiempo,
            "tipo": tipo,
            "momento": momento,
            "n_de_personas": personas
        }

        # Añadir al DataFrame
        df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)

        # Guardar en el CSV
        df.to_csv(csv_path, index=False)

        st.success("Datos agregados y guardados correctamente en el archivo CSV.")

# -------------------------------------------------------------------------
# GRÁFICA DE REGRESIÓN LINEAL CON CHECKBOXES
# -------------------------------------------------------------------------

# ----------------- Sección de gráfica (reemplaza la tuya) -----------------
st.subheader("Gráfica de regresión lineal")

# Asegurarnos de que 'numero' exista y sea numérico
if "numero" not in df.columns:
    df.insert(0, "numero", range(1, len(df) + 1))
df["numero"] = pd.to_numeric(df["numero"], errors="coerce")

# Convertir columnas a numéricas (si hay texto)
for c in ["coste", "presupuesto", "n_de_personas", "tiempo_invertido"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

st.write("Selecciona las variables para graficar:")
op_coste = st.checkbox("Coste")
op_presupuesto = st.checkbox("Presupuesto")
op_tiempo = st.checkbox("Tiempo invertido")
op_personas = st.checkbox("Número de personas")

variables = []
if op_coste and "coste" in df.columns:
    variables.append(("coste", "Coste"))
if op_presupuesto and "presupuesto" in df.columns:
    variables.append(("presupuesto", "Presupuesto"))
if op_tiempo and "tiempo_invertido" in df.columns:
    variables.append(("tiempo_invertido", "Tiempo invertido"))
if op_personas and "n_de_personas" in df.columns:
    variables.append(("n_de_personas", "Número de personas"))

if not variables:
    st.info("Activa una variable para mostrar su regresión lineal.")
else:
    # Paleta simple para diferenciar líneas (se repite si hay > len(colors))
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

    layered = None
    charts = []
    for i, (col, label) in enumerate(variables):
        color = colors[i % len(colors)]

        # Puntos
        points = alt.Chart(df).mark_point().encode(
            x=alt.X("numero:Q", title="Número"),
            y=alt.Y(f"{col}:Q", title=label),
            tooltip=["numero", col]
        )

        # Línea de regresión (se usa transform_regression sobre el mismo dataframe)
        reg_line = alt.Chart(df).transform_regression(
            "numero", col, method="linear"
        ).mark_line().encode(
            x="numero:Q",
            y=alt.Y(f"{col}:Q"),
            color=alt.value(color)
        )

        charts.append(points + reg_line)

    # Superponer todas las capas
    layered = alt.layer(*charts).properties(width=800, height=450)
    st.altair_chart(layered, use_container_width=True)
# -------------------------------------------------------------------------
