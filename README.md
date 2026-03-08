# DOCX Extraction Agents (Groq API)

This workspace includes two Python agents:

1. `table_to_csv_agent`: Extracts all tables from a `.docx` file and writes each table to a CSV file.
2. `sql_extractor_agent`: Extracts SQL statements from a `.docx` file and writes each SQL statement to its own `.sql` file.

## Setup

1. Create and activate a Python environment.
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Create `.env` from `.env.example` and set your Groq API key:

```powershell
Copy-Item .env.example .env
```

## Usage

### Run table extraction agent

```powershell
python run_agents.py tables --input "sample_sql_tables_documentation.docx" --output "output/tables"
```

### Run SQL extraction agent

```powershell
python run_agents.py sql --input "sample_sql_tables_documentation.docx" --output "output/sql"
```

### Run both agents

```powershell
python run_agents.py both --input "sample_sql_tables_documentation.docx" --tables-output "output/tables" --sql-output "output/sql"
```

## Notes

- SQL extraction uses Groq (`https://api.groq.com/openai/v1/chat/completions`).
- Table extraction is deterministic via `python-docx` and does not require model inference.
- Output file names are sanitized and made unique automatically.
