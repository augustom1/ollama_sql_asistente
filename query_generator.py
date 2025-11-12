import re
import sqlparse
import ollama
from typing import List, Dict, Any

# Intenta importar sqlglot para validar sintaxis y referencias (opcional)
try:
    import sqlglot
    from sqlglot import parse_one, exp
    HAS_SQLGLOT = True
except Exception:
    HAS_SQLGLOT = False


def split_sql_statements(text: str) -> List[str]:
    return [s.strip() for s in sqlparse.split(text) if s and s.strip()]


def format_sql(stmt: str) -> str:
    # Formato compatible con MySQL Workbench
    return sqlparse.format(stmt, reindent=True, keyword_case="upper").strip()


def _extract_content_from_ollama(result: Any) -> str:
    """
    Intenta obtener el texto del asistente desde distintos formatos de respuesta de Ollama.
    Maneja:
      - dict con result["message"]["content"]
      - objetos con .message.content
      - texto plano
      - cadenas tipo repr() con content="..."; (fallback)
    """
    # 1) dict (formato oficial)
    if isinstance(result, dict):
        msg = result.get("message", {})
        if isinstance(msg, dict):
            content = msg.get("content")
            if isinstance(content, str):
                return content

    # 2) objeto con .message.content (algunos wrappers)
    try:
        msg = getattr(result, "message", None)
        if msg is not None:
            content = getattr(msg, "content", None)
            if isinstance(content, str):
                return content
    except Exception:
        pass

    # 3) si es string, devolver tal cual
    if isinstance(result, str):
        return result

    # 4) fallback: parsear repr con content="..."; (frágil pero útil en tu caso)
    text = str(result)
    m = re.search(r'content="(.*)"', text, flags=re.DOTALL)
    if m:
        # Desescapar comillas si fuese necesario
        captured = m.group(1)
        # A veces el repr corta con '";, tool_calls=...' — limpiamos justo antes del cierre
        captured = re.split(r'";\s*\w+=', captured)[0]
        return captured

    return text


class QueryGenerator:
    def __init__(
        self,
        host="http://localhost:11434",
        model="qwen2.5-coder:1.5b",
        options=None,
        dialect="MySQL",
        sql_only=True,
        # catálogo opcional: {"tabla": {"col1","col2",...}, ...}
        catalog: Dict[str, set] = None,
    ):
        self.host = host
        self.model = model
        self.options = options or {}
        self.dialect = dialect
        self.sql_only = sql_only
        self.catalog = {k.lower(): {c.lower() for c in v} for k, v in (catalog or {}).items()}

        # Cliente Ollama (evita error de 'host' y permite reuso de conexión)
        self.client = ollama.Client(host=self.host)

    # --------------------------
    # PROMPTS
    # --------------------------
    def _system_prompt(self) -> str:
        base = [
            "Eres un generador de SQL.",
            f"Dialecto objetivo: {self.dialect}.",
            "Responde SOLAMENTE con sentencias SQL válidas (terminadas en ';').",
            "No incluyas explicaciones, razones, ni texto fuera de SQL.",
            "Usa sintaxis clara, JOINs explícitos y alias cortos si hacen falta.",
            "Evita funciones no vistas en clase si la consulta puede resolverse con SQL básico.",
        ]
        if self.sql_only:
            base.append("ESTRICTO: Solo SQL, sin comentarios ni bloques de markdown.")
        return " ".join(base)

    # --------------------------
    # POST-PROCESO Y FORMATEO
    # --------------------------
    def _strip_markdown_fences(self, text: str) -> str:
        return re.sub(r"^```(?:sql)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE | re.DOTALL)

    def _cut_explanations(self, text: str) -> str:
        for marker in ("Explicación:", "Razonamiento:", "\n\nExplicación", "\nExplicación"):
            idx = text.find(marker)
            if idx != -1:
                text = text[:idx].strip()
        return text

    def _postprocess_sql(self, text: str) -> str:
        """Limpia y da formato SQL con indentación estilo Workbench."""
        text = self._strip_markdown_fences(text)
        text = self._cut_explanations(text).strip()

        # Divide por sentencias y formatea cada una
        statements = split_sql_statements(text)
        if not statements:
            # Fallback: formateo general si no detecta splits
            if not text.endswith(";"):
                text += ";"
            return format_sql(text)

        formatted = [format_sql(s if s.endswith(";") else s + ";") for s in statements]
        return "\n\n".join(formatted).strip()

    # --------------------------
    # VALIDACIÓN (opcional)
    # --------------------------
    def _validate_with_catalog(self, sql_text: str) -> List[str]:
        """
        Valida que tablas/columnas existan en el catálogo.
        Devuelve lista de errores (vacía si todo OK).
        """
        errors: List[str] = []
        if not HAS_SQLGLOT or not self.catalog:
            return errors  # sin validador o sin catálogo

        stmts = split_sql_statements(sql_text)
        for s in stmts:
            try:
                node = parse_one(s, read="mysql")
            except Exception as e:
                errors.append(f"Sintaxis MySQL inválida: {e}")
                continue

            # Tablas
            for t in node.find_all(exp.Table):
                tname = (t.this.name if hasattr(t.this, "name") else str(getattr(t.this, "this", t.this))).lower()
                if tname not in self.catalog:
                    errors.append(f"Tabla no encontrada en esquema: {tname}")

            # Columnas
            for c in node.find_all(exp.Column):
                col = c.name.lower() if c.name else None
                tbl = c.table.lower() if c.table else None
                if not col:
                    continue
                if tbl:
                    if tbl not in self.catalog:
                        errors.append(f"Tabla no encontrada en esquema: {tbl}")
                    else:
                        if col not in self.catalog[tbl]:
                            errors.append(f"Columna '{tbl}.{col}' no existe en el esquema")
                else:
                    if not any(col in cols for cols in self.catalog.values()):
                        errors.append(f"Columna '{col}' no existe en el esquema (no calificada)")
        return errors

    # --------------------------
    # GENERACIÓN
    # --------------------------
    def generate_response(self, prompt: str, schema_context: str = "") -> str:
        """
        prompt: texto ya combinado por main.py (instrucciones + pregunta + ejemplos).
        schema_context: solo para depuración si lo necesitas.
        """
        messages = [
            {"role": "system", "content": self._system_prompt()},
            {"role": "user", "content": prompt},
        ]

        result = self.client.chat(
            model=self.model,
            messages=messages,
            options=self.options,
        )

        raw_text = _extract_content_from_ollama(result)
        sql = self._postprocess_sql(raw_text)

        # Si querés, podés activar validación (solo warnings, no corta la salida):
        # errors = self._validate_with_catalog(sql)
        # if errors:
        #     print("\n[AVISO VALIDACIÓN]\n - " + "\n - ".join(errors) + "\n")

        return sql
