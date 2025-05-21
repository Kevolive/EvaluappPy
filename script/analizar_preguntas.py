import requests
import pandas as pd
import matplotlib.pyplot as plt

API_URL = "http://localhost:8080/api/preguntas"
response = requests.get(API_URL)

if response.status_code != 200:
    print("Error al obtener preguntas")
    exit()

preguntas = response.json()
df = pd.json_normalize(preguntas, sep=".")

# Ver columnas disponibles (opcional)
print("\nColumnas reales del DataFrame:")
print(df.columns)

# Mostrar preguntas con su examen
print("\nPreguntas por examen:")
print(df[["id", "textoPregunta", "examen.titulo"]].head())

# Conteo por examen
conteo = df["examen.titulo"].value_counts()
print("\nNúmero de preguntas por examen:")
print(conteo)

# Gráfico
conteo.plot(kind="bar", title="Preguntas por examen", ylabel="Cantidad", xlabel="Examen", color="lightblue")
plt.tight_layout()
plt.show()
