import requests
import json
from datetime import datetime

# Configuración
API_URL = "http://localhost:8080/api"

# 1. Obtener exámenes disponibles
print("\nObteniendo exámenes disponibles...")
examenes_response = requests.get(f"{API_URL}/examenes")

if examenes_response.status_code != 200:
    print(f"Error al obtener exámenes: {examenes_response.status_code}")
    print(f"Mensaje de error: {examenes_response.text}")
    exit()

try:
    examenes = examenes_response.json()
    print(f"\nExámenes encontrados:")
    for i, examen in enumerate(examenes, 1):
        print(f"{i}. {examen['titulo']} (ID: {examen['id']})")
    
    # Si hay exámenes, seleccionamos el primero
    if examenes:
        examen_seleccionado = examenes[0]
        print(f"\nSeleccionando examen: {examen_seleccionado['titulo']}")
        
        # 2. Obtener preguntas del examen seleccionado
        print(f"\nObteniendo preguntas para el examen...")
        preguntas_response = requests.get(f"{API_URL}/examenes/{examen_seleccionado['id']}/preguntas")
        
        if preguntas_response.status_code != 200:
            print(f"Error al obtener preguntas: {preguntas_response.status_code}")
            print(f"Mensaje de error: {preguntas_response.text}")
            exit()
        
        try:
            preguntas = preguntas_response.json()
            print(f"\nPreguntas encontradas:")
            for i, pregunta in enumerate(preguntas, 1):
                print(f"{i}. {pregunta['pregunta']}")
            
            # 3. Simular respuestas
            print("\nSimulando respuestas...")
            resultados = []
            for pregunta in preguntas:
                # Tomamos la primera opción como respuesta (simulación)
                opcion_id = pregunta['opciones'][0]['id']
                resultados.append({
                    "pregunta_id": pregunta['id'],
                    "opcion_id": opcion_id
                })
            
            # 4. Enviar resultados
            print("\nEnviando resultados...")
            resultado_data = {
                "examen_id": examen_seleccionado['id'],
                "usuario_id": 1,  # Por ahora usamos un usuario con ID 1
                "resultados": resultados
            }
            
            response = requests.post(f"{API_URL}/resultados", json=resultado_data)
            
            if response.status_code == 201:
                print("\nExamen realizado exitosamente!")
                print("Los resultados se han guardado en la base de datos.")
            else:
                print(f"Error al guardar resultados: {response.status_code}")
                print(f"Mensaje de error: {response.text}")
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {str(e)}")
            print(f"Respuesta completa: {preguntas_response.text}")
            exit()
    else:
        print("No hay exámenes disponibles")
except json.JSONDecodeError as e:
    print(f"Error al decodificar JSON de exámenes: {str(e)}")
    print(f"Respuesta completa: {examenes_response.text}")
    exit()
    print(f"- {pregunta['pregunta']}")
    # Tomamos la primera opción como respuesta (simulación)
    opcion_id = pregunta['opciones'][0]['id']
    resultados.append({
        "pregunta_id": pregunta['id'],
        "opcion_id": opcion_id
    })

# 3. Enviar resultados
print("\nEnviando resultados...")
resultado_data = {
    "examen_id": examen_id,
    "usuario_id": 1,  # Por ahora usamos un usuario con ID 1
    "resultados": resultados
}

response = requests.post(f"{API_URL}/resultados", json=resultado_data)

if response.status_code == 201:
    print("\nExamen realizado exitosamente!")
    print("Los resultados se han guardado en la base de datos.")
else:
    print(f"Error al guardar resultados: {response.status_code}")
    print(f"Mensaje de error: {response.text}")
