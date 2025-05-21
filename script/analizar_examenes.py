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
        ["creador", "email"],
        ["creador", "role"],
        ["creador", "profile", "name"]
    ]
)

# 3. Parsear fechas y calcular duración
df["fechaInicio"] = pd.to_datetime(df["fechaInicio"])
df["fechaFin"] = pd.to_datetime(df["fechaFin"])
df["duracion_min"] = (df["fechaFin"] - df["fechaInicio"]).dt.total_seconds() / 60

# 4. Análisis básico
print("Resumen de exámenes:")
print(df[["titulo", "fechaInicio", "fechaFin", "duracion_min"]])

# 5. Exámenes por creador
conteo_creadores = df["creador.profile.name"].value_counts()
print("\nExámenes por creador:")
print(conteo_creadores)

# 6. Gráfico de duración
df.plot(x="titulo", y="duracion_min", kind="barh", figsize=(10, 6), title="Duración de Exámenes (min)")
plt.tight_layout()
plt.show()
