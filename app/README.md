# Evaluapp Dashboard

Interfaz web interactiva para crear, realizar y analizar exámenes utilizando Streamlit.

## Funcionalidades

- **Crear Exámenes**:
  - Definir título y descripción del examen
  - Seleccionar fechas de inicio y fin
  - Elegir preguntas existentes del banco de preguntas

- **Realizar Exámenes**:
  - Seleccionar y realizar exámenes disponibles
  - Responder preguntas con opciones múltiples
  - Enviar resultados para evaluación

- **Analizar Resultados**:
  - Ver resultados de exámenes realizados
  - Visualizar estadísticas y gráficos
  - Analizar rendimiento por examen

## Requisitos

- Python 3.8+
- Streamlit (ya incluido en requirements.txt)

## Instalación

1. Crear un entorno virtual:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Ejecución

Para ejecutar la aplicación:
```bash
streamlit run app/app.py
```

La aplicación se abrirá automáticamente en tu navegador web.
