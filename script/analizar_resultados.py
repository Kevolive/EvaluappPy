import requests
import pandas as pd
import matplotlib.pyplot as plt

API_URL = "https://evaluapp.onrender.com/api/resultados"
response = requests.get(API_URL)

if response.status_code != 200:
    print(f"Error al obtener resultados: {response.status_code}")
    print(f"Mensaje de error: {response.text}")
    exit()

resultados = response.json()
print("\nDatos recibidos de la API:")
print(resultados)

# Convertir JSON a DataFrame
df = pd.json_normalize(
    resultados,
    sep="."
)
print("\nColumnas disponibles:")
print(df.columns)


# Parsear fecha
# df["fecha"] = pd.to_datetime(df["fecha"])

# Mostrar resultados crudos
print("\nResultados cargados:")
print(df[["usuario.email", "examen.titulo", "puntaje", "fecha"]].head())

# Promedio por examen
promedio_examen = df.groupby("examen.titulo")["puntaje"].mean()
print("\nPromedio por examen:")
print(promedio_examen.round(2))

# Promedio por usuario
promedio_usuario = df.groupby("usuario.email")["puntaje"].mean()
print("\nPromedio por usuario:")
print(promedio_usuario.round(2))

# Usuario con mejor y peor promedio
mejor = promedio_usuario.idxmax()
peor = promedio_usuario.idxmin()
print(f"\n📈 Mejor promedio: {mejor} con {promedio_usuario[mejor]:.2f}")
print(f"📉 Peor promedio: {peor} con {promedio_usuario[peor]:.2f}")

# Gráfico: promedio por examen
promedio_examen.plot(kind="bar", title="Promedio de puntaje por examen", color="skyblue")
plt.ylabel("Puntaje")
plt.xlabel("Examen")
plt.tight_layout()
plt.show()
