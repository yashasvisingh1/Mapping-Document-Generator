from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Set

from src.common.docx_utils import extract_readable_text, load_document
from src.common.file_utils import sanitize_filename, unique_path
from src.common.groq_client import GroqClient, chunk_text


class SqlExtractorAgent:
    SYSTEM_PROMPT = (
        "You extract SQL from technical documents. "
        "Return strict JSON only with this exact structure: "
        '{"queries":[{"filename":"descriptive_name.sql","sql":"<single SQL statement>"}]}. '
        "Rules: include only valid SQL; no markdown; no explanations; preserve SQL exactly."
    )

    def __init__(self, groq: GroqClient) -> None:
        self.groq = groq

    def run(self, docx_path: Path, output_dir: Path) -> List[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)

        doc = load_document(docx_path)
        text = extract_readable_text(doc)
        chunks = chunk_text(text)

        extracted_queries: List[Dict[str, str]] = []

        for index, chunk in enumerate(chunks, start=1):
            user_prompt = (
                "Extract all SQL statements from this content chunk. "
                "If no SQL exists, return {\"queries\":[]}. "
                f"Chunk {index}/{len(chunks)}:\n\n{chunk}"
            )
            result = self.groq.chat_json(self.SYSTEM_PROMPT, user_prompt)
            chunk_queries = result.get("queries", [])
            if isinstance(chunk_queries, list):
                for item in chunk_queries:
                    if isinstance(item, dict):
                        sql_text = str(item.get("sql", "")).strip()
                        if sql_text:
                            extracted_queries.append(
                                {
                                    "filename": str(item.get("filename", "query.sql")),
                                    "sql": sql_text,
                                }
                            )

        written_files = self._write_queries(extracted_queries, output_dir)
        return written_files

    def _write_queries(self, queries: List[Dict[str, str]], output_dir: Path) -> List[Path]:
        written: List[Path] = []
        seen_sql: Set[str] = set()
        used_paths: Set[str] = set()

        for idx, query in enumerate(queries, start=1):
            sql = query["sql"].strip()
            if not sql or sql.lower() in seen_sql:
                continue
            seen_sql.add(sql.lower())

            desired_name = sanitize_filename(query.get("filename", "query.sql"), default=f"query_{idx:03d}")
            if not desired_name.lower().endswith(".sql"):
                desired_name = f"{desired_name}.sql"

            final_path = unique_path(output_dir / desired_name, used=used_paths)
            final_path.write_text(sql.rstrip() + "\n", encoding="utf-8")
            written.append(final_path)

        return written
