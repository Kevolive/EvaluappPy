import requests
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# Configuración
API_URL = "http://localhost:8080/api/examenes"

# 1. Obtener datos
response = requests.get(API_URL)
print(f"Status code: {response.status_code}")
print(f"Respuesta JSON cruda: {response.text}")
if response.status_code != 200:
    print(f"Error al obtener datos: {response.status_code}")
    exit()

examenes = response.json()

# 2. Convertir a DataFrame
df = pd.json_normalize(
    examenes,
    sep=".",
    meta=[
        "id", "titulo", "descripcion", "fechaInicio", "fechaFin",
        "creadorId",
        "creadorNombre"
    ]
)

# 3. Parsear fechas y calcular duración
df["fechaInicio"] = pd.to_datetime(df["fechaInicio"], errors='coerce')
df["fechaFin"] = pd.to_datetime(df["fechaFin"], errors='coerce')
df["duracion_min"] = (df["fechaFin"] - df["fechaInicio"]).dt.total_seconds() / 60

# 4. Análisis básico
print("Resumen de exámenes:")
print(df[["titulo", "fechaInicio", "fechaFin", "duracion_min"]])

# 5. Exámenes por creador
if df["creadorNombre"].notna().any():
    conteo_creadores = df["creadorNombre"].value_counts()
    print("\nExámenes por creador:")
    print(conteo_creadores)
else:
    print("\nNo hay información de creadores disponible")

# 6. Gráfico de duración
plt.figure(figsize=(10, 6))
plt.barh(df["titulo"], df["duracion_min"])
plt.title("Duración de Exámenes (min)")
plt.xlabel("Duración (minutos)")
plt.ylabel("Examen")
plt.tight_layout()
plt.show()
