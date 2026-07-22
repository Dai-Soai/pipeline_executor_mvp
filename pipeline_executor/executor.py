import subprocess
import time
from datetime import datetime, timezone

from pipeline_executor.contract import ExecutionResult, ExecutionTask


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def get_task_command(task: ExecutionTask) -> str:
    command = task.metadata.get("command")

    if not command:
        raise ValueError(f"task {task.node_id} requires metadata.command")

    if not isinstance(command, str):
        raise TypeError("metadata.command must be string")

    return command


def execute_command(
    command: str,
    timeout_seconds: int = 30,
) -> tuple[bool, str, int]:
    try:
        completed = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return (
            False,
            f"command timed out after {timeout_seconds}s",
            124,
        )

    output = (completed.stdout or "").strip()
    error_output = (completed.stderr or "").strip()

    message_parts = []
    if output:
        message_parts.append(output)
    if error_output:
        message_parts.append(error_output)

    message = (
        "\n".join(message_parts)
        if message_parts
        else f"exit_code={completed.returncode}"
    )

    return completed.returncode == 0, message, completed.returncode


def execute_task(
    task: ExecutionTask,
    timeout_seconds: int = 30,
) -> ExecutionResult:
    command = get_task_command(task)

    started_at = utc_now_iso()
    start_time = time.perf_counter()

    success, message, exit_code = execute_command(
        command,
        timeout_seconds=timeout_seconds,
    )

    duration_ms = int((time.perf_counter() - start_time) * 1000)
    finished_at = utc_now_iso()

    return ExecutionResult(
        node_id=task.node_id,
        success=success,
        started_at=started_at,
        finished_at=finished_at,
        duration_ms=duration_ms,
        message=message,
        metadata={
            "command": command,
            "exit_code": exit_code,
            "task": {
                "node_id": task.node_id,
                "node_name": task.node_name,
                "run_at": task.run_at,
                "next_attempt": task.next_attempt,
                "status": task.status,
            },
        },
    )


def execute_tasks(
    tasks: list[ExecutionTask],
    timeout_seconds: int = 30,
) -> list[ExecutionResult]:
    return [execute_task(task, timeout_seconds=timeout_seconds) for task in tasks]
