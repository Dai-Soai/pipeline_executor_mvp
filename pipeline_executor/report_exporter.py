import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from pipeline_executor.contract import ExecutionReport


def execution_report_to_dict(report: ExecutionReport) -> dict[str, Any]:
    if not isinstance(report, ExecutionReport):
        raise TypeError("report must be ExecutionReport")

    return {
        "pipeline_id": report.pipeline_id,
        "status": report.status,
        "generated_at": report.generated_at,
        "results": [asdict(result) for result in report.results],
        "summary": report.summary,
        "metadata": report.metadata,
    }


def write_execution_report_json(
    report: ExecutionReport,
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = execution_report_to_dict(report)

    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return path
