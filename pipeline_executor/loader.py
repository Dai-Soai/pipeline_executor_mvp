import json
from pathlib import Path
from typing import Any


class ScheduleLoaderError(Exception):
    """Raised when a schedule file cannot be loaded or normalized."""


def load_schedule(file_path: str | Path) -> dict[str, Any]:
    path = Path(file_path)

    if not path.exists():
        raise ScheduleLoaderError(f"schedule file not found: {path}")

    if not path.is_file():
        raise ScheduleLoaderError(f"schedule path is not a file: {path}")

    try:
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
    except json.JSONDecodeError as error:
        raise ScheduleLoaderError(f"invalid schedule JSON: {error}") from error

    if not isinstance(payload, dict):
        raise ScheduleLoaderError("schedule root must be a JSON object")

    return normalize_schedule(payload)


def normalize_schedule(payload: dict[str, Any]) -> dict[str, Any]:
    pipeline_id = payload.get("pipeline_id")
    status = payload.get("status", "unknown")
    generated_at = payload.get("generated_at")
    tasks = payload.get("tasks", [])
    summary = payload.get("summary", {})
    metadata = payload.get("metadata", {})

    if not pipeline_id:
        raise ScheduleLoaderError("schedule requires pipeline_id")

    if not generated_at:
        raise ScheduleLoaderError("schedule requires generated_at")

    if tasks is None:
        tasks = []

    if not isinstance(tasks, list):
        raise ScheduleLoaderError("schedule tasks must be a list")

    if not isinstance(summary, dict):
        raise ScheduleLoaderError("schedule summary must be an object")

    if not isinstance(metadata, dict):
        raise ScheduleLoaderError("schedule metadata must be an object")

    return {
        "pipeline_id": str(pipeline_id),
        "status": str(status),
        "generated_at": str(generated_at),
        "tasks": tasks,
        "summary": summary,
        "metadata": metadata,
    }
