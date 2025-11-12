import re
from pathlib import Path
import sqlparse

class DatabaseLoader:
    def __init__(self, schema_dir="schemas"):
        self.schema_dir = Path(schema_dir)
        self.schemas = {}          # nombre -> texto esquema (minificado)
        self.table_index = {}      # nombre -> set(tablas) para selección

    def _minify_sql(self, content: str) -> str:
        # Quita comentarios y exceso de espacios; sube keywords a UPPER
        return sqlparse.format(
            content,
            strip_comments=True,
            keyword_case='upper',
            reindent=False
        ).strip()

    def _extract_tables(self, sql_text: str):
        # Captura nombres de tablas de CREATE/ALTER/INSERT/UPDATE/DELETE
        # Muy simple, suficiente para selección aproximada
        tables = set()
        # CREATE TABLE `foo` (...) / CREATE TABLE foo (...)
        for m in re.finditer(r"\bCREATE\s+TABLE\s+`?([A-Za-z0-9_]+)`?", sql_text, flags=re.IGNORECASE):
            tables.add(m.group(1).lower())
        # ALTER TABLE
        for m in re.finditer(r"\bALTER\s+TABLE\s+`?([A-Za-z0-9_]+)`?", sql_text, flags=re.IGNORECASE):
            tables.add(m.group(1).lower())
        # INSERT INTO / UPDATE / DELETE FROM
        for m in re.finditer(r"\b(?:INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+`?([A-Za-z0-9_]+)`?", sql_text, flags=re.IGNORECASE):
            tables.add(m.group(1).lower())
        return tables

    def load_schemas(self):
        """Carga y minifica todos los esquemas .sql del directorio"""
        if not self.schema_dir.exists():
            self.schema_dir.mkdir(parents=True, exist_ok=True)
            print(f"Directorio '{self.schema_dir}' creado. Coloca tus archivos SQL allí.")
            return

        for sql_file in self.schema_dir.glob("*.sql"):
            text = sql_file.read_text(encoding="utf-8")
            minified = self._minify_sql(text)
            self.schemas[sql_file.stem] = minified
            self.table_index[sql_file.stem] = self._extract_tables(minified)
            print(f"Esquema cargado: {sql_file.stem} (tablas: {', '.join(sorted(self.table_index[sql_file.stem])) or '—'})")

    def _score_schema(self, name: str, question: str) -> int:
        """Puntúa un esquema por coincidencia de nombre o tablas mencionadas en la pregunta"""
        q = question.lower()
        score = 0
        # nombre de archivo mencionado
        if name.lower() in q:
            score += 3
        # tablas mencionadas
        for t in self.table_index.get(name, []):
            if t in q:
                score += 2
        return score

    def get_schema_context(self, question: str, max_chars: int = 6000) -> str:
        """Devuelve contexto concatenado de los esquemas más relevantes, limitado en longitud"""
        if not self.schemas:
            return ""

        # Ordena por relevancia, luego por tamaño creciente (para encajar más)
        ordered = sorted(
            self.schemas.items(),
            key=lambda kv: (-self._score_schema(kv[0], question), len(kv[1]))
        )

        selected = []
        total = 0
        for name, text in ordered:
            if total + len(text) + 100 > max_chars and selected:
                continue
            selected.append((name, text))
            total += len(text)

        # Arma contexto compacto
        parts = []
        for name, text in selected:
            parts.append(f"-- SCHEMA: {name}\n{text}\n")
        return "\n".join(parts)
