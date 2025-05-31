import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json

# Configuración de la página
st.set_page_config(page_title="Evaluapp", layout="wide")

# URLs de la API
API_BASE_URL = "https://evaluapp.onrender.com/api"

# Funciones auxiliares
def get_data(endpoint, params=None):
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            # Si es None, devolver lista vacía
            if data is None:
                return []
            
            # Si es una lista, convertir IDs a enteros
            if isinstance(data, list):
                for item in data:
                    if "id" in item:
                        try:
                            item["id"] = int(item["id"])
                        except (ValueError, TypeError):
                            item["id"] = 0  # Valor por defecto si no se puede convertir
                    if "preguntasIds" in item:
                        try:
                            item["preguntasIds"] = [int(id) for id in item["preguntasIds"]]
                        except (ValueError, TypeError):
                            item["preguntasIds"] = []
            return data
        else:
            st.error(f"Error {response.status_code} al obtener datos de {endpoint}")
            return []
    except Exception as e:
        st.error(f"Error al obtener datos de {endpoint}: {str(e)}")
        return []

def post_data(endpoint, data):
    try:
        response = requests.post(f"{API_BASE_URL}/{endpoint}", json=data)
        if response.status_code == 200:
            return response.json()
        else:
            try:
                # Intentar obtener más detalles del error
                error_data = response.json()
                error_message = error_data.get('message', 'Error desconocido')
                error_detail = error_data.get('detail', 'Sin detalles')
                raise Exception(f"Error {response.status_code}: {error_message}\nDetalles: {error_detail}")
            except json.JSONDecodeError:
                # Si no es JSON, mostrar el texto de la respuesta
                error_text = response.text[:200]  # Mostrar los primeros 200 caracteres
                raise Exception(f"Error {response.status_code}: Respuesta no válida\nRespuesta del servidor: {error_text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error de conexión: {str(e)}")

def get_examenes():
    try:
        examenes = get_data("examenes")
        # Asegurarnos de que es una lista
        if not isinstance(examenes, list):
            examenes = []
        
        # Limpiar datos nulos
        for examen in examenes:
            if examen.get("preguntasIds") is None:
                examen["preguntasIds"] = []
            # Asegurarnos que los IDs son enteros
            examen["preguntasIds"] = [int(id) for id in examen["preguntasIds"] if isinstance(id, (int, str))]
        
        return examenes
    except Exception as e:
        st.error(f"Error al procesar los examenes: {str(e)}")
        return []

def get_preguntas():
    preguntas = get_data("preguntas")
    return preguntas

def get_resultados():
    return get_data("resultados")

def get_profesores():
    try:
        profesores = get_data("teacher/profile")
        return profesores
    except Exception as e:
        st.error(f"Error al obtener profesores: {str(e)}")
        return []

def obtener_profesor_existente():
    try:
        # Obtener el perfil de teacher existente
        response = requests.get(f"{API_BASE_URL}/teacher/profile")
        if response.status_code == 200:
            profesores = response.json()
            if profesores:
                return profesores[0]["id"]  # Usamos el primer profesor disponible
        st.error(f"Error al obtener profesor existente: {response.text}")
        return None
    except Exception as e:
        st.error(f"Error al obtener profesor existente: {str(e)}")
        return None

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
    
    # Obtener profesor existente o usar uno por defecto
    profesor_id = obtener_profesor_existente()
    
    if not profesor_id:
        st.info("No se pudo obtener un profesor existente")
        st.info("Usando un ID de profesor por defecto...")
        # Usar un ID numérico por defecto
        profesor_id = 1  # ID por defecto que debería existir
    
    # Mostrar el profesor seleccionado
    st.info(f"Usando profesor con ID: {profesor_id}")
    
    # No necesitamos mostrar el selectbox si ya tenemos un profesor
    # profesor_id = st.selectbox(
    #     "Selecciona el profesor que crea el examen",
    #     options=[p["id"] for p in profesores],
    #     format_func=lambda x: next((f"{p['name']} {p['lastName']}" for p in profesores if p["id"] == x), "Profesor")
    # )
    
    if not profesor_id:
        st.error("Debes seleccionar un profesor")
        st.stop()
    
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
        
        if not preguntas:
            st.warning("No hay preguntas disponibles en el sistema")
        
        submitted = st.form_submit_button("Crear Examen")
        if submitted:
            try:
                # Validar campos requeridos
                if not titulo.strip():
                    st.error("El título del examen es requerido")
                    st.stop()
                
                if fecha_fin <= fecha_inicio:
                    st.error("La fecha de fin debe ser posterior a la fecha de inicio")
                    st.stop()
                
                if not preguntas_seleccionadas:
                    st.error("Debes seleccionar al menos una pregunta")
                    st.stop()
                
                # Verificar que las preguntas seleccionadas existen
                preguntas_validas = []
                for pregunta_id in preguntas_seleccionadas:
                    try:
                        pregunta = next(p for p in preguntas if p["id"] == pregunta_id)
                        preguntas_validas.append(pregunta)
                    except StopIteration:
                        st.error(f"Pregunta no válida: {pregunta_id}")
                
                if not preguntas_validas:
                    st.error("No se encontraron preguntas válidas")
                    st.stop()
                
                # Mostrar las preguntas seleccionadas
                st.subheader("Preguntas seleccionadas:")
                for pregunta in preguntas_validas:
                    st.write(f"- {pregunta['textoPregunta']}")
                
                # Validar datos antes de enviar
                if not profesor_id:
                    st.error("Debes seleccionar un profesor")
                    st.stop()
                
                examen_data = {
                    "titulo": titulo,
                    "descripcion": descripcion,
                    "fechaInicio": fecha_inicio.isoformat(),
                    "fechaFin": fecha_fin.isoformat(),
                    "preguntasIds": [int(p) for p in preguntas_seleccionadas],  # Convertir a enteros
                    "creadorId": profesor_id
                }
                
                # Usar el profesor existente
                try:
                    examen_data["creadorId"] = int(profesor_id)  # Convertir a entero
                except ValueError:
                    st.error("El ID del profesor debe ser un número")
                    st.stop()
                
                try:
                    result = post_data("examenes", examen_data)
                    st.success(f"Examen creado exitosamente!")
                    st.info("Redirigiendo a la página de inicio...")
                    page = "Inicio"
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al crear el examen: {str(e)}")
                    st.info("Por favor, verifique:")
                    st.info("1. Que el servidor esté corriendo")
                    st.info("2. Que las fechas sean válidas")
                    st.info("3. Que las preguntas seleccionadas existan")
                    st.info("4. Que el título no esté vacío")
                    st.info("5. Que el profesor seleccionado sea válido")
            except Exception as e:
                st.error(f"Error inesperado: {str(e)}")

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
            # Convertir examen_id a entero
            examen_id = int(examen_id)
            
            # Buscar el examen
            examen = next((e for e in examenes if e["id"] == examen_id), None)
            if not examen:
                st.error(f"Examen con ID {examen_id} no encontrado")
                st.stop()
            
            st.subheader(examen["titulo"])
            st.write(examen["descripcion"])
            
            # Inicializar respuestas en session_state si no existen
            if 'respuestas' not in st.session_state:
                st.session_state.respuestas = {}
            respuestas = st.session_state.respuestas
            
            # Mostrar preguntas y opciones
            preguntas = get_preguntas()
            
            # Verificar si hay preguntas asignadas
            if not examen["preguntasIds"]:
                
                # Mostrar cada pregunta y sus opciones
                for pregunta_id in examen["preguntasIds"]:
                    try:
                        # Convertir a entero y asegurarnos que es un número válido
                        pregunta_id = int(pregunta_id)
                        
                        # Buscar la pregunta por ID
                        pregunta = next((p for p in preguntas if p["id"] == pregunta_id), None)
                        
                        if pregunta:
                            # Mostrar la pregunta
                            st.markdown("---")
                            st.subheader(pregunta["textoPregunta"])
                            
                            # Obtener opciones de la pregunta
                            opciones = get_data(f"opciones?pregunta_id={pregunta_id}")
                            if not opciones:
                                st.error(f"No se encontraron opciones para la pregunta: {pregunta['textoPregunta']}")
                                continue
                            
                            # Mostrar las opciones
                            st.write("Opciones:")
                            for i, opcion in enumerate(opciones, 1):
                                st.write(f"{i}. {opcion['textoOpcion']}")
                            
                            # Crear radio button para seleccionar respuesta
                            respuesta = st.radio(
                                "",
                                options=[o["id"] for o in opciones],
                                format_func=lambda x: next((f"{i}. {o['textoOpcion']}" for i, o in enumerate(opciones, 1) if o["id"] == x), "")
                            )
                            
                            # Guardar la respuesta en session_state
                            st.session_state.respuestas[pregunta_id] = respuesta
                        else:
                            st.error(f"Pregunta con ID {pregunta_id} no encontrada en la base de datos")
                            continue
                    except ValueError:
                        st.error(f"ID de pregunta inválido: {pregunta_id}")
                        continue
                    except Exception as e:
                        st.error(f"Error al procesar la pregunta {pregunta_id}: {str(e)}")
                        continue
            else:
                st.warning("Este examen no tiene preguntas asignadas. ¿Te gustaría crear una nueva?")
                if st.button("Crear nuevo examen", key="crear_examen_btn"):
                    page = "Crear Examen"
                    st.rerun()
                st.stop()
            
            # Mostrar resumen de respuestas seleccionadas
            st.write("Respuestas seleccionadas:")
            for pregunta_id, respuesta_id in st.session_state.respuestas.items():
                pregunta = next((p for p in preguntas if p["id"] == pregunta_id), None)
                if pregunta:
                    opciones = get_data(f"opciones?pregunta_id={pregunta_id}")
                    if opciones:
                        respuesta = next((o for o in opciones if o["id"] == respuesta_id), None)
                        if respuesta:
                            st.write(f"- {pregunta['textoPregunta']}: {respuesta['textoOpcion']}")
            
            # Botón para enviar el examen
            if st.button("Enviar Examen", key="enviar_examen_btn"):
                if not respuestas:
                    st.error("No se han respondido preguntas")
                    st.stop()
                
                # Mostrar resumen antes de enviar
                st.write("Resumen de respuestas a enviar:")
                for pregunta_id, respuesta_id in respuestas.items():
                    pregunta = next((p for p in preguntas if p["id"] == pregunta_id), None)
                    if pregunta:
                        respuesta = next((o for o in opciones if o["id"] == respuesta_id), None)
                        if respuesta:
                            st.write(f"- {pregunta['textoPregunta']}: {respuesta['textoOpcion']}")
                
                resultado_data = {
                    "examenId": examen_id,  # Ya convertido antes
                    "respuestas": respuestas
                }
                
                try:
                    result = post_data("resultados", resultado_data)
                    st.success("Examen enviado exitosamente!")
                except Exception as e:
                    st.error(f"Error al enviar el examen: {str(e)}")
        except StopIteration:
            st.error("Examen no encontrado")
            st.stop()