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
    print("=== Chat SQL (modo SQL-ONLY / Teoría) ===\n")

    # Cargar esquemas
    loader = DatabaseLoader(config.DB_SCHEMA_DIR)
    loader.load_schemas()

    if not loader.schemas:
        print("No se encontraron archivos SQL en /schemas. El programa terminará.")
        return

    # Cargar contexto del profesor (tus ejemplos y estilo para SQL)
    teacher_context = load_teacher_context(config.TEACHER_CONTEXT_PATH)
    if teacher_context:
        print("Contexto del profesor cargado desde teacher_context.txt.")
    else:
        print("No se encontró teacher_context.txt o está vacío (se usará solo el prompt base).")

    print(f"\nEsquemas cargados: {list(loader.schemas.keys())}")

    # Instancias de generadores: uno para SQL y otro para Teoría
    gen_sql = QueryGenerator(
        host=config.OLLAMA_HOST,
        model=config.OLLAMA_MODEL,
        options=config.OLLAMA_OPTIONS,
        dialect=config.SQL_DIALECT,
        sql_only=True
    )

    gen_theory = QueryGenerator(
        host=config.OLLAMA_HOST,
        model=config.OLLAMA_MODEL,
        options=config.THEORY_OLLAMA_OPTIONS,
        dialect=config.SQL_DIALECT,
        sql_only=False
    )

    # Selección de modo
    theory_mode = False
    if config.ALLOW_THEORY_MODE:
        ans = input("¿Activar modo teoría? (s/n): ").strip().lower()
        theory_mode = (ans == 's')

    modo_texto = "TEORÍA" if theory_mode else "SQL"
    print(f"\nListo. Modo actual: {modo_texto}")
    print("Comandos rápidos: ':sql' (modo SQL), ':teoria' (modo teoría), ':modo' (ver modo), 'salir' (terminar).")
    print("Escribe tu pedido.\n")

    while True:
        question = input("Tú: ").strip()
        if not question:
            continue

        # Comandos de modo
        if question.lower() in ("salir", "exit", "quit"):
            print("¡Hasta luego!")
            break
        if question.lower() == ":sql":
            theory_mode = False
            print("→ Modo cambiado a SQL.")
            continue
        if question.lower() == ":teoria":
            theory_mode = True
            print("→ Modo cambiado a TEORÍA.")
            continue
        if question.lower() == ":modo":
            print(f"→ Modo actual: {'TEORÍA' if theory_mode else 'SQL'}")
            continue

        start_time = time.time()

        if theory_mode:
            # En modo teoría NO usamos el teacher_context estricto (impulsa a SQL).
            prompt = (
                "Pregunta teórica de Bases de Datos:\n"
                f"{question}\n\n"
                "Responde como profesor: breve, claro y orientado a examen. "
                "Usa viñetas cuando ayude y ejemplos simples. "
                f"No generes SQL salvo que lo pida explícitamente. Si lo piden, usa {config.SQL_DIALECT}."
            ).strip()

            response = gen_theory.generate_response(prompt)
        else:
            # Modo SQL: usamos esquemas y contexto del profesor
            schema_context = loader.get_schema_context(question, max_chars=config.MAX_SCHEMA_CHARS)
            prompt = (
                f"{teacher_context}\n\n"
                f"Pregunta: {question}\n\n"
                f"Esquemas (referencia):\n{schema_context}\n\n"
                f"Responde SOLO con SQL válido de {config.SQL_DIALECT}, sin explicación."
            ).strip()

            response = gen_sql.generate_response(prompt, schema_context)

        elapsed = time.time() - start_time

        print("\n--- Respuesta ---\n")
        print(response)
        print(f"\n--- Tiempo de respuesta: {elapsed:.2f} segundos ---\n")

if __name__ == "__main__":
    main()