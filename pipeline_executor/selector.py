from typing import Any

from pipeline_executor.contract import ExecutionTask


EXECUTABLE_STATUSES = {
    "scheduled",
    "pending",
}


def is_executable_task(task: dict[str, Any]) -> bool:
    return task.get("status") in EXECUTABLE_STATUSES


def build_execution_task(task: dict[str, Any]) -> ExecutionTask:
    node_id = task.get("node_id")
    node_name = task.get("node_name") or node_id
    run_at = task.get("run_at")
    delay_seconds = task.get("delay_seconds", 0)
    next_attempt = task.get("next_attempt")

    if not node_id:
        raise ValueError("task requires node_id")

    if not run_at:
        raise ValueError("task requires run_at")

    if next_attempt is None:
        raise ValueError("task requires next_attempt")

    return ExecutionTask(
        node_id=str(node_id),
        node_name=str(node_name),
        run_at=str(run_at),
        delay_seconds=int(delay_seconds),
        next_attempt=int(next_attempt),
        status=task.get("status", "scheduled"),
        reason=task.get("reason"),
        metadata=task.get("metadata", {}),
    )


def select_executable_tasks(schedule: dict[str, Any]) -> list[ExecutionTask]:
    raw_tasks = schedule.get("tasks", [])

    if raw_tasks is None:
        raw_tasks = []

    if not isinstance(raw_tasks, list):
        raise ValueError("schedule tasks must be a list")

    selected: list[ExecutionTask] = []

    for task in raw_tasks:
        if not isinstance(task, dict):
            raise ValueError("task item must be an object")

        if not is_executable_task(task):
            continue

        selected.append(build_execution_task(task))

    return sorted(selected, key=lambda task: task.run_at)


def count_executable_tasks(schedule: dict[str, Any]) -> int:
    return len(select_executable_tasks(schedule))


def get_task_selection_summary(schedule: dict[str, Any]) -> dict[str, Any]:
    selected = select_executable_tasks(schedule)
    raw_tasks = schedule.get("tasks", []) or []

    return {
        "pipeline_id": schedule.get("pipeline_id"),
        "total_tasks": len(raw_tasks),
        "selected_tasks": len(selected),
        "first_run_at": selected[0].run_at if selected else None,
        "last_run_at": selected[-1].run_at if selected else None,
    }
