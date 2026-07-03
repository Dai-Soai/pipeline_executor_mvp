import pytest

from pipeline_executor.contract import ExecutionTask
from pipeline_executor.selector import (
    build_execution_task,
    count_executable_tasks,
    get_task_selection_summary,
    is_executable_task,
    select_executable_tasks,
)


def sample_schedule():
    return {
        "pipeline_id": "pipeline-001",
        "tasks": [
            {
                "node_id": "late",
                "node_name": "Late Task",
                "run_at": "2026-07-03T20:40:30Z",
                "delay_seconds": 30,
                "next_attempt": 1,
                "status": "scheduled",
            },
            {
                "node_id": "cancelled",
                "node_name": "Cancelled Task",
                "run_at": "2026-07-03T20:40:05Z",
                "delay_seconds": 5,
                "next_attempt": 1,
                "status": "cancelled",
            },
            {
                "node_id": "early",
                "node_name": "Early Task",
                "run_at": "2026-07-03T20:40:10Z",
                "delay_seconds": 10,
                "next_attempt": 1,
                "status": "scheduled",
            },
        ],
    }


def test_is_executable_task_scheduled():
    assert is_executable_task({"status": "scheduled"}) is True


def test_is_executable_task_pending():
    assert is_executable_task({"status": "pending"}) is True


def test_is_executable_task_rejects_cancelled():
    assert is_executable_task({"status": "cancelled"}) is False


def test_build_execution_task():
    task = build_execution_task(
        {
            "node_id": "execute",
            "node_name": "Execute Pipeline",
            "run_at": "2026-07-03T20:40:20Z",
            "delay_seconds": 20,
            "next_attempt": 2,
            "status": "scheduled",
            "reason": "retry allowed",
            "metadata": {
                "command": "echo execute",
            },
        }
    )

    assert isinstance(task, ExecutionTask)
    assert task.node_id == "execute"
    assert task.node_name == "Execute Pipeline"
    assert task.metadata["command"] == "echo execute"


def test_build_execution_task_uses_node_id_as_name():
    task = build_execution_task(
        {
            "node_id": "execute",
            "run_at": "2026-07-03T20:40:20Z",
            "delay_seconds": 20,
            "next_attempt": 2,
            "status": "scheduled",
        }
    )

    assert task.node_name == "execute"


def test_build_execution_task_requires_node_id():
    with pytest.raises(ValueError):
        build_execution_task(
            {
                "run_at": "2026-07-03T20:40:20Z",
                "delay_seconds": 20,
                "next_attempt": 2,
                "status": "scheduled",
            }
        )


def test_build_execution_task_requires_run_at():
    with pytest.raises(ValueError):
        build_execution_task(
            {
                "node_id": "execute",
                "delay_seconds": 20,
                "next_attempt": 2,
                "status": "scheduled",
            }
        )


def test_build_execution_task_requires_next_attempt():
    with pytest.raises(ValueError):
        build_execution_task(
            {
                "node_id": "execute",
                "run_at": "2026-07-03T20:40:20Z",
                "delay_seconds": 20,
                "status": "scheduled",
            }
        )


def test_select_executable_tasks_filters_and_sorts():
    tasks = select_executable_tasks(sample_schedule())

    assert len(tasks) == 2
    assert [task.node_id for task in tasks] == ["early", "late"]


def test_select_executable_tasks_accepts_missing_tasks():
    assert select_executable_tasks({}) == []


def test_select_executable_tasks_rejects_invalid_tasks_type():
    with pytest.raises(ValueError):
        select_executable_tasks({"tasks": {}})


def test_select_executable_tasks_rejects_non_object_task():
    with pytest.raises(ValueError):
        select_executable_tasks({"tasks": ["bad-task"]})


def test_count_executable_tasks():
    assert count_executable_tasks(sample_schedule()) == 2


def test_get_task_selection_summary():
    summary = get_task_selection_summary(sample_schedule())

    assert summary["pipeline_id"] == "pipeline-001"
    assert summary["total_tasks"] == 3
    assert summary["selected_tasks"] == 2
    assert summary["first_run_at"] == "2026-07-03T20:40:10Z"
    assert summary["last_run_at"] == "2026-07-03T20:40:30Z"
