import requests
import pandas as pd
import matplotlib.pyplot as plt

API_URL = "https://evaluapp.onrender.com/api/admin/users"
response = requests.get(API_URL)

if response.status_code != 200:
    print("Error al obtener usuarios")
    exit()

usuarios = response.json()
df = pd.DataFrame(usuarios)

# Conteo por rol
conteo_roles = df["role"].value_counts()
porcentaje_roles = df["role"].value_counts(normalize=True) * 100

# Mostrar resultados en consola
print("\nUsuarios por rol:")
print(conteo_roles)
print("\nPorcentaje por rol:")
print(porcentaje_roles.round(2))

# Gráfico de barras
conteo_roles.plot(kind="bar", title="Cantidad de usuarios por rol", ylabel="Usuarios", xlabel="Rol", color='skyblue')
plt.tight_layout()
plt.show()

# Gráfico de torta
porcentaje_roles.plot(kind="pie", autopct='%1.1f%%', startangle=90, title="Distribución de roles")
plt.ylabel("")  # Quitar etiqueta del eje Y
plt.tight_layout()
plt.show()
