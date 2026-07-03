import pytest

from pipeline_executor.contract import ExecutionReport, ExecutionResult
from pipeline_executor.result_builder import (
    build_execution_report,
    build_execution_summary,
    calculate_success_rate,
    count_failed_results,
    count_successful_results,
    determine_report_status,
    utc_now_iso,
)


def make_result(
    node_id: str = "execute",
    success: bool = True,
) -> ExecutionResult:
    return ExecutionResult(
        node_id=node_id,
        success=success,
        started_at="2026-07-03T20:40:20Z",
        finished_at="2026-07-03T20:40:21Z",
        duration_ms=1000,
        message="done",
    )


def test_utc_now_iso_returns_utc_timestamp():
    value = utc_now_iso()

    assert value.endswith("Z")
    assert "T" in value


def test_count_successful_results():
    results = [
        make_result("a", True),
        make_result("b", False),
        make_result("c", True),
    ]

    assert count_successful_results(results) == 2


def test_count_failed_results():
    results = [
        make_result("a", True),
        make_result("b", False),
        make_result("c", False),
    ]

    assert count_failed_results(results) == 2


def test_calculate_success_rate():
    results = [
        make_result("a", True),
        make_result("b", False),
    ]

    assert calculate_success_rate(results) == 0.5


def test_calculate_success_rate_empty_results():
    assert calculate_success_rate([]) == 0.0


def test_determine_report_status_empty():
    assert determine_report_status([]) == "empty"


def test_determine_report_status_completed():
    assert determine_report_status(
        [
            make_result("a", True),
            make_result("b", True),
        ]
    ) == "completed"


def test_determine_report_status_failed():
    assert determine_report_status(
        [
            make_result("a", False),
            make_result("b", False),
        ]
    ) == "failed"


def test_determine_report_status_partial():
    assert determine_report_status(
        [
            make_result("a", True),
            make_result("b", False),
        ]
    ) == "partial"


def test_build_execution_summary():
    summary = build_execution_summary(
        [
            make_result("a", True),
            make_result("b", False),
            make_result("c", True),
        ]
    )

    assert summary["total_results"] == 3
    assert summary["successful_results"] == 2
    assert summary["failed_results"] == 1
    assert summary["success_rate"] == 2 / 3


def test_build_execution_report():
    report = build_execution_report(
        pipeline_id="pipeline-001",
        results=[
            make_result("execute", True),
        ],
        generated_at="2026-07-03T20:40:22Z",
    )

    assert isinstance(report, ExecutionReport)
    assert report.pipeline_id == "pipeline-001"
    assert report.status == "completed"
    assert report.generated_at == "2026-07-03T20:40:22Z"
    assert report.summary["total_results"] == 1


def test_build_execution_report_empty_results():
    report = build_execution_report(
        pipeline_id="pipeline-001",
        results=[],
        generated_at="2026-07-03T20:40:22Z",
    )

    assert report.status == "empty"
    assert report.summary["total_results"] == 0


def test_build_execution_report_rejects_missing_pipeline_id():
    with pytest.raises(ValueError):
        build_execution_report(
            pipeline_id="",
            results=[],
        )
