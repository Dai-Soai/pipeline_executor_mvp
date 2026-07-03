# Pipeline Executor MVP

Pipeline Executor MVP for executing scheduled pipeline tasks and producing execution reports in the RADAR Services utility chain.

---

## Features

- Load pipeline schedules
- Select executable tasks
- Execute scheduled commands
- Collect execution results
- Build execution reports
- Export JSON execution reports
- CLI interface
- Python package

---

## Architecture

Schedule
    ↓
Loader
    ↓
Selector
    ↓
Executor
    ↓
Execution Report
    ├── CLI
    └── JSON

---

## Project Structure

pipeline_executor/

- contract.py
- loader.py
- selector.py
- executor.py
- result_builder.py
- report_exporter.py
- cli.py

tests/

data/

outputs/

---

## CLI

Run:

```bash
pipeline-executor execute data/sample_schedule.json
```

Verbose:

```bash
pipeline-executor execute data/sample_schedule.json --verbose
```

JSON report:

```bash
pipeline-executor execute \
    data/sample_schedule.json \
    --json \
    --output outputs/execution_report.json
```

---

## Output

Human-readable execution summary

or

JSON execution report

---

## Status

MVP v0.1.0
