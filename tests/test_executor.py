import pytest

from pipeline_executor.contract import ExecutionResult, ExecutionTask
from pipeline_executor.executor import (
    execute_command,
    execute_task,
    execute_tasks,
    get_task_command,
    utc_now_iso,
)


def make_task(command: str = "echo hello") -> ExecutionTask:
    return ExecutionTask(
        node_id="execute",
        node_name="Execute Pipeline",
        run_at="2026-07-03T20:40:20Z",
        delay_seconds=20,
        next_attempt=2,
        status="scheduled",
        metadata={
            "command": command,
        },
    )


def test_utc_now_iso_returns_utc_timestamp():
    value = utc_now_iso()

    assert value.endswith("Z")
    assert "T" in value


def test_get_task_command():
    task = make_task("echo hello")

    assert get_task_command(task) == "echo hello"


def test_get_task_command_rejects_missing_command():
    task = ExecutionTask(
        node_id="execute",
        node_name="Execute Pipeline",
        run_at="2026-07-03T20:40:20Z",
        delay_seconds=20,
        next_attempt=2,
        status="scheduled",
        metadata={},
    )

    with pytest.raises(ValueError):
        get_task_command(task)


def test_get_task_command_rejects_non_string_command():
    task = ExecutionTask(
        node_id="execute",
        node_name="Execute Pipeline",
        run_at="2026-07-03T20:40:20Z",
        delay_seconds=20,
        next_attempt=2,
        status="scheduled",
        metadata={
            "command": ["echo", "hello"],
        },
    )

    with pytest.raises(TypeError):
        get_task_command(task)


def test_execute_command_success():
    success, message, exit_code = execute_command("echo hello")

    assert success is True
    assert message == "hello"
    assert exit_code == 0


def test_execute_command_failure():
    success, message, exit_code = execute_command("python -c 'import sys; sys.exit(3)'")

    assert success is False
    assert exit_code == 3


def test_execute_task_success():
    task = make_task("echo hello")

    result = execute_task(task)

    assert isinstance(result, ExecutionResult)
    assert result.node_id == "execute"
    assert result.success is True
    assert result.message == "hello"
    assert result.metadata["exit_code"] == 0


def test_execute_task_failure():
    task = make_task("python -c 'import sys; sys.exit(4)'")

    result = execute_task(task)

    assert result.success is False
    assert result.metadata["exit_code"] == 4


def test_execute_tasks_multiple():
    tasks = [
        make_task("echo one"),
        ExecutionTask(
            node_id="notify",
            node_name="Notify Result",
            run_at="2026-07-03T20:40:10Z",
            delay_seconds=10,
            next_attempt=1,
            status="scheduled",
            metadata={
                "command": "echo two",
            },
        ),
    ]

    results = execute_tasks(tasks)

    assert len(results) == 2
    assert results[0].message == "one"
    assert results[1].message == "two"
