# DOCX Extraction Agents (Groq API)

This project provides three agents that work together:

1. `tables`: Extracts all tables from a DOCX file into CSV files.
2. `sql`: Extracts SQL statements from a DOCX file into individual `.sql` files.
3. `mapping`: Uses the generated CSV and SQL files to produce table mapping documents with column transformations.

## Prerequisites

- Python 3.10+
- Groq API key
- Windows PowerShell (commands below use PowerShell examples)

## Project Structure

- `run_agents.py`: Main CLI entry point
- `src/agents/table_to_csv_agent.py`: Table extraction agent
- `src/agents/sql_extractor_agent.py`: SQL extraction agent
- `src/agents/mapping_generator_agent.py`: Mapping generation agent
- `output/`: Generated artifacts (tables, sql, mappings)

## Setup

1. Open a terminal in the project root.
2. Create a virtual environment:

```powershell
python -m venv .venv
```

3. Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

4. Install dependencies:

```powershell
pip install -r requirements.txt
```

5. Create your environment file(.env file).

6. Create a Groq API key:

7. Go to [Groq Console Keys](https://console.groq.com/keys) and sign in.
8. Click `Create API Key`.
9. Enter a name for the key and create it.
10. Copy the key immediately (you may not be able to view it again).

11. Edit `.env` and set at least:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_API_BASE=https://api.groq.com/openai/v1
```

## Quick Start

Run all three agents in one command:

```powershell
python run_agents.py all --input "sample_sql_tables_documentation.docx" --tables-output "output/tables" --sql-output "output/sql" --mapping-output "output/mappings"
```

## Run Commands

Use your DOCX path for `--input`. The examples below use `sample_sql_tables_documentation.docx`.

### 1. Extract tables to CSV

```powershell
python run_agents.py tables --input "sample_sql_tables_documentation.docx" --output "output/tables"
```

### 2. Extract SQL to `.sql` files

```powershell
python run_agents.py sql --input "sample_sql_tables_documentation.docx" --output "output/sql"
```

### 3. Generate mapping documents from CSV + SQL

```powershell
python run_agents.py mapping --tables-input "output/tables" --sql-input "output/sql" --output "output/mappings"
```

### 4. Run tables + SQL in one command

```powershell
python run_agents.py both --input "sample_sql_tables_documentation.docx" --tables-output "output/tables" --sql-output "output/sql"
```

### 5. Run all three agents end-to-end

```powershell
python run_agents.py all --input "sample_sql_tables_documentation.docx" --tables-output "output/tables" --sql-output "output/sql" --mapping-output "output/mappings"
```

## Output

- `output/tables/`: `table_001.csv`, `table_002.csv`, ...
- `output/sql/`: SQL files extracted from the document
- `output/mappings/`: Mapping docs per table including column-level transformations

## Troubleshooting

- `Missing GROQ_API_KEY`: ensure `.env` exists and contains a valid key.
- `Input DOCX not found`: verify the path passed in `--input`.
- `Tables directory not found` or `SQL directory not found`: run `tables`/`sql` first or check paths for `mapping`.

## Notes

- SQL extraction and mapping generation call [Groq Chat Completions API](https://console.groq.com/docs/api-reference#chat-create).
- Table extraction is deterministic via `python-docx` and does not use LLM inference.
- File names are sanitized and made unique automatically.
