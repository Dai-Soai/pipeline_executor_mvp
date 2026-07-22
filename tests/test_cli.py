import json

from pipeline_executor.cli import main


def sample_schedule():
    return {
        "pipeline_id": "pipeline-001",
        "status": "ready",
        "generated_at": "2026-07-03T20:40:00Z",
        "tasks": [
            {
                "node_id": "execute",
                "node_name": "Execute Pipeline",
                "run_at": "2026-07-03T20:40:20Z",
                "delay_seconds": 20,
                "next_attempt": 2,
                "status": "scheduled",
                "reason": "retry allowed",
                "metadata": {"command": "echo execute"},
            }
        ],
        "summary": {},
        "metadata": {},
    }


def test_cli_prints_help_when_no_command(capsys):
    exit_code = main([])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "pipeline-executor" in captured.out


def test_cli_execute_outputs_summary(tmp_path, capsys):
    schedule_file = tmp_path / "schedule.json"
    schedule_file.write_text(json.dumps(sample_schedule()), encoding="utf-8")

    exit_code = main(["execute", str(schedule_file)])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Pipeline Executor" in captured.out
    assert "Pipeline ID: pipeline-001" in captured.out
    assert "Status: completed" in captured.out
    assert "Total Results: 1" in captured.out
    assert "Successful Results: 1" in captured.out
    assert "Failed Results: 0" in captured.out


def test_cli_execute_verbose_outputs_results(tmp_path, capsys):
    schedule_file = tmp_path / "schedule.json"
    schedule_file.write_text(json.dumps(sample_schedule()), encoding="utf-8")

    exit_code = main(["execute", str(schedule_file), "--verbose"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Results" in captured.out
    assert "execute | success=True" in captured.out
    assert "message=execute" in captured.out


def test_cli_execute_returns_error_for_missing_file(capsys):
    exit_code = main(["execute", "missing.json"])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "error:" in captured.err


def test_cli_execute_returns_nonzero_for_failed_task(tmp_path, capsys):
    schedule = sample_schedule()
    schedule["tasks"][0]["metadata"]["command"] = "python -c 'import sys; sys.exit(5)'"

    schedule_file = tmp_path / "schedule.json"
    schedule_file.write_text(json.dumps(schedule), encoding="utf-8")

    exit_code = main(["execute", str(schedule_file)])

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Status: failed" in captured.out
    assert "Failed Results: 1" in captured.out


def test_cli_execute_empty_schedule(tmp_path, capsys):
    schedule = sample_schedule()
    schedule["tasks"] = []

    schedule_file = tmp_path / "schedule.json"
    schedule_file.write_text(json.dumps(schedule), encoding="utf-8")

    exit_code = main(["execute", str(schedule_file)])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Status: empty" in captured.out
    assert "Total Results: 0" in captured.out


def test_cli_execute_json_writes_report(tmp_path, capsys):
    schedule_file = tmp_path / "schedule.json"
    output_file = tmp_path / "execution_report.json"

    schedule_file.write_text(json.dumps(sample_schedule()), encoding="utf-8")

    exit_code = main(
        [
            "execute",
            str(schedule_file),
            "--json",
            "--output",
            str(output_file),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "JSON execution report written:" in captured.out
    assert output_file.exists()

    payload = json.loads(output_file.read_text(encoding="utf-8"))

    assert payload["pipeline_id"] == "pipeline-001"
    assert payload["status"] == "completed"
    assert payload["summary"]["total_results"] == 1
