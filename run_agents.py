from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from src.agents.mapping_generator_agent import MappingGeneratorAgent
from src.agents.sql_extractor_agent import SqlExtractorAgent
from src.agents.table_to_csv_agent import TableToCsvAgent
from src.common.groq_client import GroqClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DOCX extraction agents (tables + SQL)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_tables = subparsers.add_parser("tables", help="Extract DOCX tables to CSV files")
    parser_tables.add_argument("--input", required=True, help="Path to source .docx file")
    parser_tables.add_argument("--output", required=True, help="Output directory for CSV files")

    parser_sql = subparsers.add_parser("sql", help="Extract SQL statements to .sql files")
    parser_sql.add_argument("--input", required=True, help="Path to source .docx file")
    parser_sql.add_argument("--output", required=True, help="Output directory for SQL files")

    parser_both = subparsers.add_parser("both", help="Run both table and SQL extraction")
    parser_both.add_argument("--input", required=True, help="Path to source .docx file")
    parser_both.add_argument("--tables-output", required=True, help="Output directory for CSV files")
    parser_both.add_argument("--sql-output", required=True, help="Output directory for SQL files")

    parser_mapping = subparsers.add_parser("mapping", help="Generate mapping documents from CSV and SQL files")
    parser_mapping.add_argument("--tables-input", required=True, help="Directory containing CSV table files")
    parser_mapping.add_argument("--sql-input", required=True, help="Directory containing SQL files")
    parser_mapping.add_argument("--output", required=True, help="Output directory for mapping documents")

    parser_all = subparsers.add_parser("all", help="Run all three agents: tables, SQL, and mapping")
    parser_all.add_argument("--input", required=True, help="Path to source .docx file")
    parser_all.add_argument("--tables-output", required=True, help="Output directory for CSV files")
    parser_all.add_argument("--sql-output", required=True, help="Output directory for SQL files")
    parser_all.add_argument("--mapping-output", required=True, help="Output directory for mapping documents")

    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    # Only validate input path for commands that need it
    if args.command in ["tables", "sql", "both", "all"]:
        input_path = Path(args.input).expanduser().resolve()
        if not input_path.exists():
            raise FileNotFoundError(f"Input DOCX not found: {input_path}")

    if args.command == "tables":
        output_dir = Path(args.output).expanduser().resolve()
        files = TableToCsvAgent().run(input_path, output_dir)
        print(f"Extracted {len(files)} tables to {output_dir}")
        return

    if args.command == "sql":
        output_dir = Path(args.output).expanduser().resolve()
        groq = GroqClient.from_env()
        files = SqlExtractorAgent(groq).run(input_path, output_dir)
        print(f"Extracted {len(files)} SQL files to {output_dir}")
        return

    if args.command == "both":
        tables_output = Path(args.tables_output).expanduser().resolve()
        sql_output = Path(args.sql_output).expanduser().resolve()

        table_files = TableToCsvAgent().run(input_path, tables_output)
        groq = GroqClient.from_env()
        sql_files = SqlExtractorAgent(groq).run(input_path, sql_output)

        print(f"Extracted {len(table_files)} tables to {tables_output}")
        print(f"Extracted {len(sql_files)} SQL files to {sql_output}")
        return

    if args.command == "mapping":
        tables_input = Path(args.tables_input).expanduser().resolve()
        sql_input = Path(args.sql_input).expanduser().resolve()
        output_dir = Path(args.output).expanduser().resolve()

        if not tables_input.exists():
            raise FileNotFoundError(f"Tables directory not found: {tables_input}")
        if not sql_input.exists():
            raise FileNotFoundError(f"SQL directory not found: {sql_input}")

        groq = GroqClient.from_env()
        mapping_files = MappingGeneratorAgent(groq).run(tables_input, sql_input, output_dir)
        print(f"Generated {len(mapping_files)} mapping documents to {output_dir}")
        return

    if args.command == "all":
        tables_output = Path(args.tables_output).expanduser().resolve()
        sql_output = Path(args.sql_output).expanduser().resolve()
        mapping_output = Path(args.mapping_output).expanduser().resolve()

        # Step 1: Extract tables
        table_files = TableToCsvAgent().run(input_path, tables_output)
        print(f"✓ Extracted {len(table_files)} tables to {tables_output}")

        # Step 2: Extract SQL
        groq = GroqClient.from_env()
        sql_files = SqlExtractorAgent(groq).run(input_path, sql_output)
        print(f"✓ Extracted {len(sql_files)} SQL files to {sql_output}")

        # Step 3: Generate mappings
        mapping_files = MappingGeneratorAgent(groq).run(tables_output, sql_output, mapping_output)
        print(f"✓ Generated {len(mapping_files)} mapping documents to {mapping_output}")

        print(f"\nAll agents completed successfully!")
        return

    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()

