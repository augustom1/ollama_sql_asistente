# Asistente SQL para Parciales

Asistente local que usa Ollama y un modelo ligero para generar consultas SQL en estilo de examen, usando:
- Esquemas SQL del profesor (carpeta `schemas/`)
- Un archivo de estilo y teoría (`teacher_context.txt`)
- Preguntas en lenguaje natural

El proyecto funciona completamente en tu máquina, sin Internet.

## Requisitos

- Python 3.10+
- Ollama instalado
- Modelo descargado:

```
ollama pull qwen2.5-coder:1.5b
```

## Instalación

### Opción A: Clonar con Git

```
git clone <URL_DE_TU_REPO>
cd <carpeta>
pip install -r requirements.txt
```

### Opción B: Descargar ZIP

1. Descargar desde GitHub → Download ZIP  
2. Descomprimir  
3. Instalar dependencias:

```
pip install -r requirements.txt
```

No es necesario usar venv.

## Preparar los esquemas

Coloca los archivos `.sql` del profesor en:

```
schemas/
```

El programa cargará automáticamente todos los esquemas.

## Uso

En terminal o VS Code:

```
python main.py
```

Ejemplo:

```
Tú: Mostrar los atletas de Argentina.
```

Salida:

```sql
use 2parcial;

SELECT A.NombreAtleta
FROM Atleta A
JOIN Pais P ON A.PaisID = P.PaisID
WHERE P.NombrePais = 'Argentina';
```

Para salir:

```
salir
```

## Modo teoría

Cambiar en `config.py`:

```
STRICT_SQL_ONLY = False
```

Y agregar teoría en `teacher_context.txt`.

## Actualizar el proyecto

```
git pull
```

## Estructura

```
.
├── main.py
├── query_generator.py
├── config.py
├── database_loader.py
├── teacher_context.txt
├── requirements.txt
└── schemas/
```

## Nota para el examen

Probá todas las consultas en MySQL Workbench antes de entregar tu archivo `.sql`.
