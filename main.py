from database_loader import DatabaseLoader
from query_generator import QueryGenerator
import config
import time
from pathlib import Path

def load_teacher_context(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    try:
        return p.read_text(encoding="utf-8").strip()
    except Exception:
        return ""

def main():
    print("=== Chat SQL (modo SQL-ONLY) ===\n")

    # Cargar esquemas
    loader = DatabaseLoader(config.DB_SCHEMA_DIR)
    loader.load_schemas()

    if not loader.schemas:
        print("No se encontraron archivos SQL en /schemas. El programa terminará.")
        return

    # Cargar contexto del profesor (tus ejemplos y estilo)
    teacher_context = load_teacher_context(config.TEACHER_CONTEXT_PATH)
    if teacher_context:
        print("Contexto del profesor cargado desde teacher_context.txt.")
    else:
        print("No se encontró teacher_context.txt o está vacío (se usará solo el prompt base).")

    print(f"\nEsquemas cargados: {list(loader.schemas.keys())}")

    generator = QueryGenerator(
        host=config.OLLAMA_HOST,
        model=config.OLLAMA_MODEL,
        options=config.OLLAMA_OPTIONS,
        dialect=config.SQL_DIALECT,
        sql_only=config.STRICT_SQL_ONLY
    )

    print("\nListo. Escribe tu pedido (ej: 'crear tabla X', 'insert de ejemplo', 'update ...').")
    print("Escribe 'salir' para terminar.\n")

    while True:
        question = input("Tú: ").strip()
        if question.lower() in ("salir", "exit", "quit"):
            print("¡Hasta luego!")
            break
        if not question:
            continue

        start_time = time.time()
        schema_context = loader.get_schema_context(question, max_chars=config.MAX_SCHEMA_CHARS)

        # Prompt final: tus ejemplos + consigna + esquemas
        prompt = (
            f"{teacher_context}\n\n"
            f"Pregunta: {question}\n\n"
            f"Esquemas (referencia):\n{schema_context}\n\n"
            f"Responde SOLO con SQL válido de {config.SQL_DIALECT}, sin explicación."
        ).strip()

        response = generator.generate_response(prompt, schema_context)
        elapsed = time.time() - start_time

        print("\n--- SQL generado ---\n")
        print(response)
        print(f"\n--- Tiempo de respuesta: {elapsed:.2f} segundos ---\n")

if __name__ == "__main__":
    main()
