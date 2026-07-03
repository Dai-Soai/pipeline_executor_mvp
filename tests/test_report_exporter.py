import json

import pytest

from pipeline_executor.contract import ExecutionReport, ExecutionResult
from pipeline_executor.report_exporter import (
    execution_report_to_dict,
    write_execution_report_json,
)


def make_result() -> ExecutionResult:
    return ExecutionResult(
        node_id="execute",
        success=True,
        started_at="2026-07-03T20:40:20Z",
        finished_at="2026-07-03T20:40:21Z",
        duration_ms=1000,
        message="completed",
        metadata={
            "command": "echo execute",
        },
    )


def make_report() -> ExecutionReport:
    return ExecutionReport(
        pipeline_id="pipeline-001",
        status="completed",
        generated_at="2026-07-03T20:40:21Z",
        results=[make_result()],
        summary={
            "total_results": 1,
            "successful_results": 1,
            "failed_results": 0,
            "success_rate": 1.0,
        },
        metadata={
            "source": "executor",
        },
    )


def test_execution_report_to_dict():
    payload = execution_report_to_dict(make_report())

    assert payload["pipeline_id"] == "pipeline-001"
    assert payload["status"] == "completed"
    assert payload["results"][0]["node_id"] == "execute"
    assert payload["summary"]["total_results"] == 1
    assert payload["metadata"]["source"] == "executor"


def test_execution_report_to_dict_rejects_invalid_report():
    with pytest.raises(TypeError):
        execution_report_to_dict({"bad": "report"})


def test_write_execution_report_json(tmp_path):
    output_file = tmp_path / "execution_report.json"

    written_path = write_execution_report_json(make_report(), output_file)

    assert written_path == output_file
    assert output_file.exists()

    payload = json.loads(output_file.read_text(encoding="utf-8"))

    assert payload["pipeline_id"] == "pipeline-001"
    assert payload["results"][0]["message"] == "completed"


def test_write_execution_report_json_creates_parent_directory(tmp_path):
    output_file = tmp_path / "nested" / "reports" / "execution_report.json"

    write_execution_report_json(make_report(), output_file)

    assert output_file.exists()


def test_write_execution_report_json_overwrites_existing_file(tmp_path):
    output_file = tmp_path / "execution_report.json"
    output_file.write_text("old-content", encoding="utf-8")

    write_execution_report_json(make_report(), output_file)

    payload = json.loads(output_file.read_text(encoding="utf-8"))

    assert payload["pipeline_id"] == "pipeline-001"


def test_write_execution_report_json_preserves_utf8(tmp_path):
    report = ExecutionReport(
        pipeline_id="pipeline-001",
        status="completed",
        generated_at="2026-07-03T20:40:21Z",
        results=[
            ExecutionResult(
                node_id="notify",
                success=True,
                started_at="2026-07-03T20:40:20Z",
                finished_at="2026-07-03T20:40:21Z",
                duration_ms=1000,
                message="hoàn thành",
            )
        ],
        summary={},
        metadata={},
    )
    output_file = tmp_path / "execution_report.json"

    write_execution_report_json(report, output_file)

    assert "hoàn thành" in output_file.read_text(encoding="utf-8")
