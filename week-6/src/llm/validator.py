import json
import re

from src.llm.schema import TriageResponse


def clean_model_output(raw: str) -> str:
    cleaned = raw.strip()

    # Remove Markdown code fences.
    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    cleaned = cleaned.strip()

    # Find the first JSON object if the
    # model added unwanted text around it.
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "No JSON object found in model output."
        )

    return cleaned[start:end + 1]


def parse_and_validate(
    raw: str,
) -> TriageResponse:

    cleaned = clean_model_output(raw)

    data = json.loads(cleaned)

    return TriageResponse.model_validate(
        data
    )