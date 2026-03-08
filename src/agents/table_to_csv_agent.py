from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from src.common.docx_utils import extract_tables, load_document


class TableToCsvAgent:
    def run(self, docx_path: Path, output_dir: Path) -> List[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)

        doc = load_document(docx_path)
        tables = extract_tables(doc)

        written_files: List[Path] = []
        for idx, table in enumerate(tables, start=1):
            csv_path = output_dir / f"table_{idx:03d}.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerows(table)
            written_files.append(csv_path)

        return written_files
