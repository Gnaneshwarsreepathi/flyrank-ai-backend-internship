import json
import os
from pathlib import Path

from dotenv import load_dotenv

from src.llm.reliable_client import call_llm


load_dotenv()

PROMPT_VERSION = "triage-v1"


def load_prompt() -> str:
    project_root = Path(__file__).resolve().parents[2]

    prompt_path = (
        project_root
        / "prompts"
        / f"{PROMPT_VERSION}.md"
    )

    return prompt_path.read_text(
        encoding="utf-8"
    )


def ask_model(text: str) -> dict:
    model = os.getenv("LLM_MODEL")

    if not model:
        raise ValueError("LLM_MODEL is missing.")

    system_prompt = load_prompt()

    user_content = json.dumps(
        {"text": text},
        ensure_ascii=False,
    )

    response = call_llm(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_content,
            },
        ],
        prompt_version=PROMPT_VERSION,
        repair_count=0,
    )

    raw_answer = response.choices[0].message.content

    if not raw_answer:
        raise ValueError(
            "The model returned an empty response."
        )

    return {
        "raw": raw_answer,
        "model": model,
        "prompt_version": PROMPT_VERSION,
    }


def repair_model_output(
    text: str,
    broken_output: str,
    validation_error: str,
) -> dict:
    model = os.getenv("LLM_MODEL")

    if not model:
        raise ValueError("LLM_MODEL is missing.")

    system_prompt = load_prompt()

    repair_message = json.dumps(
        {
            "original_input": {
                "text": text
            },
            "broken_output": broken_output,
            "validation_error": validation_error,
            "instruction": (
                "Correct the broken output. "
                "Return only one valid JSON object "
                "matching the required schema. "
                "Do not add Markdown or explanation."
            ),
        },
        ensure_ascii=False,
    )

    response = call_llm(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": repair_message,
            },
        ],
        prompt_version=PROMPT_VERSION,
        repair_count=1,
    )

    raw_answer = response.choices[0].message.content

    if not raw_answer:
        raise ValueError(
            "Repair returned an empty response."
        )

    return {
        "raw": raw_answer,
        "model": model,
        "prompt_version": PROMPT_VERSION,
    }