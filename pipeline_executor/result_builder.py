from datetime import datetime, timezone
from typing import Any

from pipeline_executor.contract import ExecutionReport, ExecutionResult


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def count_successful_results(results: list[ExecutionResult]) -> int:
    return sum(1 for result in results if result.success)


def count_failed_results(results: list[ExecutionResult]) -> int:
    return sum(1 for result in results if not result.success)


def calculate_success_rate(results: list[ExecutionResult]) -> float:
    if not results:
        return 0.0

    return count_successful_results(results) / len(results)


def determine_report_status(results: list[ExecutionResult]) -> str:
    if not results:
        return "empty"

    successful = count_successful_results(results)
    failed = count_failed_results(results)

    if successful > 0 and failed == 0:
        return "completed"

    if failed > 0 and successful == 0:
        return "failed"

    return "partial"


def build_execution_summary(results: list[ExecutionResult]) -> dict[str, Any]:
    total_results = len(results)
    successful_results = count_successful_results(results)
    failed_results = count_failed_results(results)

    return {
        "total_results": total_results,
        "successful_results": successful_results,
        "failed_results": failed_results,
        "success_rate": calculate_success_rate(results),
    }


def build_execution_report(
    pipeline_id: str,
    results: list[ExecutionResult],
    generated_at: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> ExecutionReport:
    if not pipeline_id:
        raise ValueError("pipeline_id is required")

    if generated_at is None:
        generated_at = utc_now_iso()

    return ExecutionReport(
        pipeline_id=pipeline_id,
        status=determine_report_status(results),
        generated_at=generated_at,
        results=results,
        summary=build_execution_summary(results),
        metadata=metadata or {},
    )
