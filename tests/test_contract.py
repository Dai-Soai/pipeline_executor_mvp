import pytest

from pipeline_executor.contract import (
    ExecutionReport,
    ExecutionResult,
    ExecutionTask,
)


def test_execution_task_creation():
    task = ExecutionTask(
        node_id="execute",
        node_name="Execute Pipeline",
        run_at="2026-07-03T20:40:20Z",
        delay_seconds=20,
        next_attempt=2,
        reason="retry allowed",
    )

    assert task.node_id == "execute"
    assert task.status == "scheduled"
    assert task.delay_seconds == 20
    assert task.next_attempt == 2
    assert task.metadata == {}


def test_execution_task_rejects_missing_node_id():
    with pytest.raises(ValueError):
        ExecutionTask(
            node_id="",
            node_name="Execute Pipeline",
            run_at="2026-07-03T20:40:20Z",
            delay_seconds=20,
            next_attempt=2,
        )


def test_execution_task_rejects_non_int_delay():
    with pytest.raises(TypeError):
        ExecutionTask(
            node_id="execute",
            node_name="Execute Pipeline",
            run_at="2026-07-03T20:40:20Z",
            delay_seconds="20",
            next_attempt=2,
        )


def test_execution_task_rejects_invalid_next_attempt():
    with pytest.raises(ValueError):
        ExecutionTask(
            node_id="execute",
            node_name="Execute Pipeline",
            run_at="2026-07-03T20:40:20Z",
            delay_seconds=20,
            next_attempt=0,
        )


def test_execution_task_rejects_invalid_status():
    with pytest.raises(ValueError):
        ExecutionTask(
            node_id="execute",
            node_name="Execute Pipeline",
            run_at="2026-07-03T20:40:20Z",
            delay_seconds=20,
            next_attempt=2,
            status="bad",
        )


def test_execution_result_creation():
    result = ExecutionResult(
        node_id="execute",
        success=True,
        started_at="2026-07-03T20:40:20Z",
        finished_at="2026-07-03T20:40:21Z",
        duration_ms=1000,
        message="completed",
    )

    assert result.node_id == "execute"
    assert result.success is True
    assert result.duration_ms == 1000
    assert result.metadata == {}


def test_execution_result_rejects_non_bool_success():
    with pytest.raises(TypeError):
        ExecutionResult(
            node_id="execute",
            success="yes",
            started_at="2026-07-03T20:40:20Z",
            finished_at="2026-07-03T20:40:21Z",
            duration_ms=1000,
        )


def test_execution_result_rejects_negative_duration():
    with pytest.raises(ValueError):
        ExecutionResult(
            node_id="execute",
            success=False,
            started_at="2026-07-03T20:40:20Z",
            finished_at="2026-07-03T20:40:21Z",
            duration_ms=-1,
        )


def test_execution_report_creation():
    result = ExecutionResult(
        node_id="execute",
        success=True,
        started_at="2026-07-03T20:40:20Z",
        finished_at="2026-07-03T20:40:21Z",
        duration_ms=1000,
    )

    report = ExecutionReport(
        pipeline_id="pipeline-001",
        status="completed",
        generated_at="2026-07-03T20:40:21Z",
        results=[result],
    )

    assert report.pipeline_id == "pipeline-001"
    assert report.status == "completed"
    assert len(report.results) == 1
    assert report.summary == {}


def test_execution_report_rejects_invalid_result_type():
    with pytest.raises(TypeError):
        ExecutionReport(
            pipeline_id="pipeline-001",
            status="completed",
            generated_at="2026-07-03T20:40:21Z",
            results=["bad-result"],
        )
