from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List, Set

from src.common.file_utils import sanitize_filename, unique_path
from src.common.groq_client import GroqClient


class MappingGeneratorAgent:
    SYSTEM_PROMPT = (
        "You are a data mapping expert. Given a table structure (CSV) and related SQL queries, "
        "generate a detailed mapping document in JSON format with this structure: "
        '{"table_name":"name","columns":[{"name":"col","type":"inferred_type",'
        '"transformations":["list of transformations or operations found in SQL"],'
        '"description":"brief description"}]}. '
        "Analyze SQL to identify WHERE clauses, JOINs, aggregations, and transformations applied to each column."
    )

    def __init__(self, groq: GroqClient) -> None:
        self.groq = groq

    def run(
        self, tables_dir: Path, sql_dir: Path, output_dir: Path
    ) -> List[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load CSV tables
        csv_files = sorted(tables_dir.glob("*.csv"))
        if not csv_files:
            print(f"No CSV files found in {tables_dir}")
            return []

        # Load SQL files
        sql_files = sorted(sql_dir.glob("*.sql"))
        sql_content = self._load_sql_files(sql_files)

        # Generate mapping for each table
        written_files: List[Path] = []
        used_paths: Set[str] = set()

        for idx, csv_file in enumerate(csv_files, start=1):
            table_data = self._load_csv(csv_file)
            if not table_data:
                continue

            mapping = self._generate_mapping(
                csv_file.stem, table_data, sql_content, idx, len(csv_files)
            )

            # Write mapping document
            mapping_filename = f"{csv_file.stem}_mapping.md"
            mapping_path = unique_path(
                output_dir / mapping_filename, used=used_paths
            )
            self._write_mapping_document(mapping, mapping_path)
            written_files.append(mapping_path)

        return written_files

    def _load_csv(self, csv_path: Path) -> List[List[str]]:
        """Load CSV file as list of rows."""
        try:
            with csv_path.open("r", encoding="utf-8") as f:
                reader = csv.reader(f)
                return list(reader)
        except Exception as e:
            print(f"Error loading {csv_path}: {e}")
            return []

    def _load_sql_files(self, sql_files: List[Path]) -> str:
        """Load and concatenate all SQL files."""
        sql_parts: List[str] = []
        for sql_file in sql_files:
            try:
                content = sql_file.read_text(encoding="utf-8").strip()
                if content:
                    sql_parts.append(f"-- {sql_file.name}\n{content}")
            except Exception as e:
                print(f"Error loading {sql_file}: {e}")
        return "\n\n".join(sql_parts)

    def _generate_mapping(
        self,
        table_name: str,
        table_data: List[List[str]],
        sql_content: str,
        current: int,
        total: int,
    ) -> Dict:
        """Generate mapping document using Groq."""
        # Format table structure
        table_preview = "\n".join(
            [",".join(row) for row in table_data[:10]]
        )  # First 10 rows

        user_prompt = (
            f"Analyze this table and related SQL to generate a mapping document.\n\n"
            f"Table: {table_name}\n"
            f"CSV Preview (first 10 rows):\n{table_preview}\n\n"
            f"Related SQL queries:\n{sql_content[:8000]}\n\n"
            f"Generate a comprehensive mapping with column types, transformations, and descriptions. "
            f"Processing table {current}/{total}."
        )

        try:
            result = self.groq.chat_json(self.SYSTEM_PROMPT, user_prompt)
            return result
        except Exception as e:
            print(f"Error generating mapping for {table_name}: {e}")
            # Fallback to basic structure
            headers = table_data[0] if table_data else []
            return {
                "table_name": table_name,
                "columns": [
                    {
                        "name": col,
                        "type": "unknown",
                        "transformations": [],
                        "description": "Column from source table",
                    }
                    for col in headers
                ],
            }

    def _write_mapping_document(
        self, mapping: Dict, output_path: Path
    ) -> None:
        """Write mapping as a formatted markdown document."""
        table_name = mapping.get("table_name", "Unknown")
        columns = mapping.get("columns", [])

        lines: List[str] = [
            f"# Data Mapping: {table_name}",
            "",
            f"**Table Name:** `{table_name}`",
            f"**Total Columns:** {len(columns)}",
            "",
            "---",
            "",
            "## Column Mappings",
            "",
        ]

        for idx, col in enumerate(columns, start=1):
            col_name = col.get("name", "unknown")
            col_type = col.get("type", "unknown")
            transformations = col.get("transformations", [])
            description = col.get("description", "No description available")

            lines.append(f"### {idx}. `{col_name}`")
            lines.append("")
            lines.append(f"**Type:** `{col_type}`")
            lines.append("")
            lines.append(f"**Description:** {description}")
            lines.append("")

            if transformations:
                lines.append("**Transformations:**")
                for transform in transformations:
                    lines.append(f"- {transform}")
                lines.append("")
            else:
                lines.append("**Transformations:** None identified")
                lines.append("")

            lines.append("---")
            lines.append("")

        # Add raw JSON at the end for reference
        lines.append("## Raw Mapping Data")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(mapping, indent=2))
        lines.append("```")

        output_path.write_text("\n".join(lines), encoding="utf-8")
