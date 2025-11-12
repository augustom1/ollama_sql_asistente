import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de Ollama
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
# Modelo pequeño y rápido
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b")

# Configuración de la base de datos (esquemas locales)
DB_SCHEMA_DIR = "schemas"

# Archivo de contexto del profesor (ejemplos y estilo SQL)
TEACHER_CONTEXT_PATH = "teacher_context.txt"

# Modos
STRICT_SQL_ONLY = True               # Modo por defecto: Solo SQL, sin explicación
ALLOW_THEORY_MODE = True             # Permite activar modo teoría desde la terminal

# Dialecto SQL (para el modo SQL)
SQL_DIALECT = "MySQL"

# Rendimiento y longitud
MAX_SCHEMA_CHARS = 4000              # recorta contexto para acelerar
MAX_OUTPUT_TOKENS = 256              # límite de tokens de salida (suficiente para 2-3 sentencias SQL)

# Para modo teoría (respuestas breves pero no limitadas a SQL)
THEORY_MAX_OUTPUT_TOKENS = 800

# Opciones del modelo (más determinista y rápido) - SQL
OLLAMA_OPTIONS = {
    "temperature": 0.05,
    "top_k": 40,
    "top_p": 0.8,
    "num_predict": MAX_OUTPUT_TOKENS,
    # Stops sencillos por si el modelo intenta explicar
    "stop": ["Explicación:", "Razonamiento:", "\n\nExplicación"]
}

# Opciones del modelo para modo teoría (un poco más de espacio)
THEORY_OLLAMA_OPTIONS = {
    "temperature": 0.2,
    "top_k": 50,
    "top_p": 0.9,
    "num_predict": THEORY_MAX_OUTPUT_TOKENS,
}