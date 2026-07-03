from dataclasses import dataclass, field
from typing import Any


VALID_TASK_STATUSES = {
    "scheduled",
    "pending",
    "running",
    "completed",
    "failed",
    "skipped",
    "cancelled",
}

VALID_REPORT_STATUSES = {
    "pending",
    "running",
    "completed",
    "failed",
    "partial",
    "empty",
}


@dataclass(frozen=True)
class ExecutionTask:
    node_id: str
    node_name: str
    run_at: str
    delay_seconds: int
    next_attempt: int
    status: str = "scheduled"
    reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id is required")

        if not self.node_name:
            raise ValueError("node_name is required")

        if not self.run_at:
            raise ValueError("run_at is required")

        if not isinstance(self.delay_seconds, int):
            raise TypeError("delay_seconds must be int")

        if self.delay_seconds < 0:
            raise ValueError("delay_seconds cannot be negative")

        if not isinstance(self.next_attempt, int):
            raise TypeError("next_attempt must be int")

        if self.next_attempt < 1:
            raise ValueError("next_attempt must be >= 1")

        if self.status not in VALID_TASK_STATUSES:
            raise ValueError(f"invalid task status: {self.status}")


@dataclass(frozen=True)
class ExecutionResult:
    node_id: str
    success: bool
    started_at: str
    finished_at: str
    duration_ms: int
    message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id is required")

        if not isinstance(self.success, bool):
            raise TypeError("success must be bool")

        if not self.started_at:
            raise ValueError("started_at is required")

        if not self.finished_at:
            raise ValueError("finished_at is required")

        if not isinstance(self.duration_ms, int):
            raise TypeError("duration_ms must be int")

        if self.duration_ms < 0:
            raise ValueError("duration_ms cannot be negative")


@dataclass(frozen=True)
class ExecutionReport:
    pipeline_id: str
    status: str
    generated_at: str
    results: list[ExecutionResult]
    summary: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.pipeline_id:
            raise ValueError("pipeline_id is required")

        if self.status not in VALID_REPORT_STATUSES:
            raise ValueError(f"invalid report status: {self.status}")

        if not self.generated_at:
            raise ValueError("generated_at is required")

        for result in self.results:
            if not isinstance(result, ExecutionResult):
                raise TypeError("results must contain ExecutionResult items")
