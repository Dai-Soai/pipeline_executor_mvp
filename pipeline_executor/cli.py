import argparse
import sys

from pipeline_executor.executor import execute_tasks
from pipeline_executor.loader import ScheduleLoaderError, load_schedule
from pipeline_executor.result_builder import build_execution_report
from pipeline_executor.selector import select_executable_tasks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pipeline-executor",
        description="Execute scheduled pipeline tasks.",
    )

    subparsers = parser.add_subparsers(dest="command")

    execute_parser = subparsers.add_parser(
        "execute",
        help="Execute tasks from a schedule file.",
    )
    execute_parser.add_argument(
        "schedule",
        help="Path to schedule.json.",
    )
    execute_parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Command timeout in seconds.",
    )
    execute_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show task execution details.",
    )

    return parser


def run_execute(args: argparse.Namespace) -> int:
    try:
        schedule = load_schedule(args.schedule)
        tasks = select_executable_tasks(schedule)
        results = execute_tasks(tasks, timeout_seconds=args.timeout)
        report = build_execution_report(
            pipeline_id=schedule["pipeline_id"],
            results=results,
            metadata={
                "source": "schedule",
                "schedule_file": args.schedule,
                "selected_tasks": len(tasks),
            },
        )
    except (ScheduleLoaderError, ValueError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print("Pipeline Executor")
    print("=================")
    print(f"Pipeline ID: {report.pipeline_id}")
    print(f"Status: {report.status}")
    print(f"Generated At: {report.generated_at}")
    print()
    print("Summary")
    print("-------")
    print(f"Total Results: {report.summary['total_results']}")
    print(f"Successful Results: {report.summary['successful_results']}")
    print(f"Failed Results: {report.summary['failed_results']}")
    print(f"Success Rate: {report.summary['success_rate']:.2f}")

    if args.verbose:
        print()
        print("Results")
        print("-------")
        for result in report.results:
            print(
                f"- {result.node_id} | "
                f"success={result.success} | "
                f"duration_ms={result.duration_ms} | "
                f"message={result.message}"
            )

    return 0 if report.status in {"completed", "empty"} else 2


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "execute":
        return run_execute(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
