import requests
import pandas as pd
import matplotlib.pyplot as plt 

#Primer paso: obtener todas las reguntas para dar las opciones

PREGUNTAS_URL = "https://evaluapp.onrender.com/api/preguntas"
OPCIONES_BASE_URL = "https://evaluapp.onrender.com/api/opciones/pregunta"

resp_preg = requests.get(PREGUNTAS_URL)
if resp_preg.status_code != 200:
    print("Error al obtener lapregunta")
    exit()

preguntas = resp_preg.json()

# Recorrer cada pregunta y pedir sus opciones
todas_opciones= []

for pregunta in preguntas:
    pregunta_id = pregunta["id"]
    texto = pregunta.get("testoPregunta", "sin texto")

    resp_opt = requests.get(f"{OPCIONES_BASE_URL}/{pregunta_id}")
    if resp_opt.status_code != 200:
        print(f"Error con la pregunta {pregunta_id}")
        continue
    opciones = resp_opt.json()
    for opcion in opciones:
        opcion["pregunta_id"]= pregunta_id
        opcion["texto_pregunta"] = texto
        todas_opciones.append(opcion)

# Tercero: Convertir la data en la DataFrame

df= pd.json_normalize(todas_opciones, sep=".")

print("\nOpciones recibidas:")
print(df[["id", "textoOpcion", "esCorrecta", "pregunta_id", "texto_pregunta"]].head())

#CuartoAnálisis por pregunta

conteo_opciones = df["pregunta_id"].value_counts()
correctas_por_pregunta = df[df["esCorrecta"] == True]["pregunta_id"].value_counts()

#Quinto: Validar preguntas mal configuradas
preguntas_con_problemas = correctas_por_pregunta[(correctas_por_pregunta > 1) | (correctas_por_pregunta == 0)]
print("\n Preguntas con 0 o más de una opción correcta:")
print(preguntas_con_problemas)

#Sexto: gráfico de la cantidad de opciones por pregunta

conteo_opciones.plot(kind= "bar", title = "Cantidad de opciones por pregunta", ylabel= "Opciones", xlabel= "ID pregunta", color="red")
plt.tight_layout()
plt.show()

