import json

import pytest

from pipeline_executor.loader import (
    ScheduleLoaderError,
    load_schedule,
    normalize_schedule,
)


def test_load_schedule_from_file(tmp_path):
    schedule_file = tmp_path / "schedule.json"
    schedule_file.write_text(
        json.dumps(
            {
                "pipeline_id": "pipeline-001",
                "status": "ready",
                "generated_at": "2026-07-03T20:40:00Z",
                "tasks": [],
                "summary": {},
                "metadata": {},
            }
        ),
        encoding="utf-8",
    )

    payload = load_schedule(schedule_file)

    assert payload["pipeline_id"] == "pipeline-001"
    assert payload["status"] == "ready"
    assert payload["generated_at"] == "2026-07-03T20:40:00Z"
    assert payload["tasks"] == []


def test_load_schedule_rejects_missing_file(tmp_path):
    with pytest.raises(ScheduleLoaderError):
        load_schedule(tmp_path / "missing.json")


def test_load_schedule_rejects_invalid_json(tmp_path):
    schedule_file = tmp_path / "bad.json"
    schedule_file.write_text("{bad-json", encoding="utf-8")

    with pytest.raises(ScheduleLoaderError):
        load_schedule(schedule_file)


def test_load_schedule_rejects_non_object_json(tmp_path):
    schedule_file = tmp_path / "list.json"
    schedule_file.write_text(json.dumps([]), encoding="utf-8")

    with pytest.raises(ScheduleLoaderError):
        load_schedule(schedule_file)


def test_normalize_schedule_defaults_optional_fields():
    payload = normalize_schedule(
        {
            "pipeline_id": "pipeline-001",
            "generated_at": "2026-07-03T20:40:00Z",
            "tasks": None,
            "summary": {},
            "metadata": {},
        }
    )

    assert payload["pipeline_id"] == "pipeline-001"
    assert payload["status"] == "unknown"
    assert payload["tasks"] == []


def test_normalize_schedule_rejects_missing_pipeline_id():
    with pytest.raises(ScheduleLoaderError):
        normalize_schedule(
            {
                "generated_at": "2026-07-03T20:40:00Z",
                "tasks": [],
            }
        )


def test_normalize_schedule_rejects_missing_generated_at():
    with pytest.raises(ScheduleLoaderError):
        normalize_schedule(
            {
                "pipeline_id": "pipeline-001",
                "tasks": [],
            }
        )


def test_normalize_schedule_rejects_invalid_tasks_type():
    with pytest.raises(ScheduleLoaderError):
        normalize_schedule(
            {
                "pipeline_id": "pipeline-001",
                "generated_at": "2026-07-03T20:40:00Z",
                "tasks": {},
            }
        )


def test_normalize_schedule_rejects_invalid_summary_type():
    with pytest.raises(ScheduleLoaderError):
        normalize_schedule(
            {
                "pipeline_id": "pipeline-001",
                "generated_at": "2026-07-03T20:40:00Z",
                "tasks": [],
                "summary": [],
            }
        )


def test_normalize_schedule_rejects_invalid_metadata_type():
    with pytest.raises(ScheduleLoaderError):
        normalize_schedule(
            {
                "pipeline_id": "pipeline-001",
                "generated_at": "2026-07-03T20:40:00Z",
                "tasks": [],
                "summary": {},
                "metadata": [],
            }
        )
