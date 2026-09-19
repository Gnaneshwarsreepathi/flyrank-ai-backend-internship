import json
from datetime import datetime, timezone
from pathlib import Path


def quarantine_failure(
    input_text: str,
    raw_output: str,
    error: str,
    prompt_version: str,
) -> None:

    project_root = (
        Path(__file__)
        .resolve()
        .parents[2]
    )

    logs_directory = (
        project_root
        / "logs"
    )

    logs_directory.mkdir(
        exist_ok=True
    )

    log_file = (
        logs_directory
        / "quarantine.jsonl"
    )

    record = {
        "timestamp": (
            datetime.now(timezone.utc)
            .isoformat()
        ),
        "input": input_text,
        "raw_output": raw_output,
        "error": error,
        "prompt_version": prompt_version,
    }

    with log_file.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                record,
                ensure_ascii=False,
            )
            + "\n"
        )