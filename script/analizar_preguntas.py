import requests
import pandas as pd
import matplotlib.pyplot as plt

API_URL = "https://evaluapp.onrender.com/api/preguntas"
response = requests.get(API_URL)

if response.status_code != 200:
    print("Error al obtener preguntas")
    exit()

preguntas = response.json()
df = pd.json_normalize(preguntas, sep=".")

# Ver columnas disponibles (opcional)
print("\nColumnas reales del DataFrame:")
print(df.columns)

# Mostrar preguntas disponibles
print("\nPreguntas disponibles:")
if "examen.titulo" in df.columns:
    print(df[["id", "textoPregunta", "examen.titulo"]].head())
else:
    print(df[["id", "textoPregunta", "tipoPregunta"]].head())
    print("\nNota: La información del examen no está disponible en los datos")

# Conteo por tipo de pregunta
conteo = df["tipoPregunta"].value_counts()
print("\nNúmero de preguntas por examen:")
print(conteo)

# Gráfico
conteo.plot(kind="bar", title="Preguntas por examen", ylabel="Cantidad", xlabel="Examen", color="lightblue")
plt.tight_layout()
plt.show()
