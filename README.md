# Chat SQL - Generador de Consultas Automatizado

Este proyecto permite generar sentencias SQL a partir de preguntas en lenguaje natural utilizando modelos locales de Ollama. Está diseñado como herramienta de apoyo para estudiantes que preparan exámenes de bases de datos en MySQL.

## Descripción General

El asistente toma como entrada una consigna en lenguaje natural (por ejemplo, “Mostrar los atletas de Argentina”) y produce una consulta SQL estructurada y formateada lista para ejecutarse en MySQL Workbench. Utiliza esquemas locales para comprender la estructura de las tablas y ejemplos de estilo del profesor para imitar su formato de respuesta.

## Características Principales

- Genera solo SQL (sin explicaciones ni comentarios adicionales).
- Compatible con MySQL Workbench.
- Permite cargar múltiples esquemas locales en formato `.sql`.
- Integra un archivo de contexto para imitar el estilo de respuesta del profesor.
- Cronómetro de tiempo de respuesta integrado.
- Configuración flexible mediante variables de entorno.

## Estructura del Proyecto

```
ChatSQL/
├── main.py                  # Punto de entrada principal
├── config.py                # Configuración general y variables
├── database_loader.py       # Carga y análisis de esquemas SQL
├── query_generator.py       # Generador de consultas usando Ollama
├── teacher_context.txt      # Contexto y estilo de respuestas del profesor
├── requirements.txt         # Dependencias del proyecto
└── schemas/                 # Carpeta para archivos SQL de esquemas
```

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tuusuario/ChatSQL.git
cd ChatSQL
```

### 2. Crear y activar un entorno virtual

```bash
python -m venv venv
venv\Scripts\activate       # Windows
# o
source venv/bin/activate      # Linux / Mac
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Ollama y variables de entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:1.5b
```

Asegúrate de tener Ollama instalado y en ejecución local.  
Descarga disponible en [https://ollama.com](https://ollama.com).

## Uso

1. Coloca tus archivos `.sql` con los esquemas de base de datos dentro de la carpeta `schemas/`.
2. (Opcional) Modifica `teacher_context.txt` para adaptar el estilo de las respuestas.
3. Ejecuta el programa con:

```bash
python main.py
```

4. Ingresa una consigna en lenguaje natural, por ejemplo:

```
Tú: Mostrar los nombres de los atletas de un país específico (por ejemplo, Chile)
```

El asistente responderá con la sentencia SQL correspondiente, ya formateada.

## Exportación de Respuestas

1. Copia todas las respuestas generadas y guárdalas en un archivo `respuestas.sql`.
2. Puedes abrir ese archivo en MySQL Workbench para verificar o ejecutar las consultas.
3. Para entregar el examen, basta con incluir todas las respuestas en dicho archivo.

## Requisitos del Sistema

- Python 3.9 o superior.
- Ollama instalado y corriendo localmente.
- Modelo descargado: `qwen2.5-coder:1.5b`

Instalación del modelo:
```bash
ollama pull qwen2.5-coder:1.5b
```

## Créditos

Autor: Augusto Meyer  
Año: 2025  
Propósito: Herramienta educativa para práctica de SQL mediante IA local.  

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulte el archivo `LICENSE` para más detalles.
