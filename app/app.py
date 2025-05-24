import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Evaluapp", layout="wide")

# URLs de la API
API_BASE_URL = "http://localhost:8080/api"

# Funciones auxiliares
def get_data(endpoint):
    response = requests.get(f"{API_BASE_URL}/{endpoint}")
    if response.status_code == 200:
        return response.json()
    return []

def post_data(endpoint, data):
    response = requests.post(f"{API_BASE_URL}/{endpoint}", json=data)
    return response.json()

def get_examenes():
    examenes = get_data("examenes")
    # Limpiar datos nulos
    for examen in examenes:
        if examen.get("preguntasIds") is None:
            examen["preguntasIds"] = []
    return examenes

def get_preguntas():
    return get_data("preguntas")

def get_resultados():
    return get_data("resultados")

# Sidebar - Navegación
st.sidebar.title("Evaluapp")
page = st.sidebar.radio("Navegar a", ["Inicio", "Crear Examen", "Realizar Examen", "Analizar Resultados"])

# Contenido principal
if page == "Inicio":
    st.title("Bienvenido a Evaluapp")
    st.write("Esta aplicación te permite crear exámenes, realizarlos y analizar los resultados.")
    
    # Mostrar estadísticas rápidas
    col1, col2, col3 = st.columns(3)
    with col1:
        examenes = get_examenes()
        st.metric("Exámenes", len(examenes))
    with col2:
        preguntas = get_preguntas()
        st.metric("Preguntas", len(preguntas))
    with col3:
        resultados = get_resultados()
        st.metric("Resultados", len(resultados))

elif page == "Crear Examen":
    st.title("Crear Nuevo Examen")
    
    # Formulario para crear examen
    with st.form("crear_examen"):
        titulo = st.text_input("Título del examen", "")
        descripcion = st.text_area("Descripción", "")
        fecha_inicio = st.date_input("Fecha de inicio", datetime.now())
        fecha_fin = st.date_input("Fecha de fin", datetime.now())
        
        # Obtener preguntas y verificar su estructura
        preguntas = get_preguntas()
        
        # Crear un diccionario para mapear id -> texto
        preguntas_dict = {p["id"]: p.get("textoPregunta", f"Pregunta {p['id']}") for p in preguntas}
        
        # Selección de preguntas
        preguntas_seleccionadas = st.multiselect(
            "Selecciona preguntas",
            options=[p["id"] for p in preguntas],
            format_func=lambda x: preguntas_dict.get(x, "Pregunta desconocida")
        )
        
        # Mostrar mensaje si no hay preguntas disponibles
        if not preguntas:
            st.warning("No hay preguntas disponibles en el sistema")
        
        submitted = st.form_submit_button("Crear Examen")
        if submitted:
            # Validar que se han seleccionado preguntas
            if not preguntas_seleccionadas:
                st.error("Debes seleccionar al menos una pregunta")
                st.stop()
                
                
            examen_data = {
                "titulo": titulo,
                "descripcion": descripcion,
                "fechaInicio": fecha_inicio.isoformat(),
                "fechaFin": fecha_fin.isoformat(),
                "preguntasIds": preguntas_seleccionadas
            }
            result = post_data("examenes", examen_data)
            st.success(f"Examen creado exitosamente: {result}")

elif page == "Realizar Examen":
    st.title("Realizar Examen")
    
    # Selección de examen
    examenes = get_examenes()
    examen_id = st.selectbox(
        "Selecciona un examen",
        options=[e["id"] for e in examenes],
        format_func=lambda x: next((e["titulo"] for e in examenes if e["id"] == x), "")
    )
    
    if examen_id:
        try:
            examen = next(e for e in examenes if e["id"] == examen_id)
            st.subheader(examen["titulo"])
            st.write(examen["descripcion"])
            
            # Mostrar preguntas y opciones
            preguntas = get_preguntas()
            respuestas = {}
            
            # Verificar si hay preguntas asignadas
            if not examen["preguntasIds"]:
                st.warning("Este examen no tiene preguntas asignadas")
                st.stop()  # Detener la ejecución de Streamlit
            
            for pregunta_id in examen["preguntasIds"]:
                try:
                    pregunta = next(p for p in preguntas if p["id"] == pregunta_id)
                    st.subheader(pregunta["textoPregunta"])
                    
                    # Obtener opciones de la pregunta
                    opciones = get_data(f"opciones?pregunta_id={pregunta_id}")
                    if not opciones:
                        st.error(f"No se encontraron opciones para la pregunta: {pregunta['textoPregunta']}")
                        continue
                    
                    respuesta = st.radio(
                        "",
                        options=[o["id"] for o in opciones],
                        format_func=lambda x: next((o["textoOpcion"] for o in opciones if o["id"] == x), "")
                    )
                    respuestas[pregunta_id] = respuesta
                except StopIteration:
                    st.error(f"Pregunta no encontrada: {pregunta_id}")
                    continue
            
            if st.button("Enviar Examen"):
                if respuestas:
                    resultado_data = {
                        "examenId": examen_id,
                        "respuestas": respuestas
                    }
                    result = post_data("resultados", resultado_data)
                    st.success("Examen enviado exitosamente!")
                else:
                    st.error("No se han respondido preguntas")
        except StopIteration:
            st.error("Examen no encontrado")
        if st.button("Enviar Examen"):
            resultado_data = {
                "examenId": examen_id,
                "respuestas": respuestas
            }


elif page == "Analizar Resultados":
    st.title("Analizar Resultados")
    
    # Obtener y mostrar resultados
    resultados = get_resultados()
    if resultados:
        df = pd.DataFrame(resultados)
        
        # Mostrar tabla de resultados
        st.subheader("Resultados Recientes")
        st.dataframe(df)
        
        # Gráficos
        st.subheader("Análisis de Resultados")
        
        # Promedio por examen
        if "examen.titulo" in df.columns and "puntaje" in df.columns:
            promedio_examen = df.groupby("examen.titulo")["puntaje"].mean()
            st.bar_chart(promedio_examen)
        
        # Distribución de puntajes
        if "puntaje" in df.columns:
            st.subheader("Distribución de Puntajes")
            st.hist_chart(df["puntaje"])
