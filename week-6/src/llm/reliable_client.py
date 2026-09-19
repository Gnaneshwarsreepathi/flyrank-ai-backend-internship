import json
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path

import openai
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv(override=True)

MAX_ATTEMPTS = 3
TIMEOUT_SECONDS = 30.0


def get_client() -> OpenAI:
    base_url = os.getenv("LLM_BASE_URL")
    api_key = os.getenv("LLM_API_KEY")

    if not base_url:
        raise ValueError("LLM_BASE_URL is missing.")

    if not api_key:
        raise ValueError("LLM_API_KEY is missing.")

    return OpenAI(
        base_url=base_url,
        api_key=api_key,
        timeout=TIMEOUT_SECONDS,
        # We own the retry policy.
        max_retries=0,
    )


def write_call_log(record: dict) -> None:
    project_root = Path(__file__).resolve().parents[2]

    logs_directory = project_root / "logs"
    logs_directory.mkdir(exist_ok=True)

    log_file = logs_directory / "llm_calls.jsonl"

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


def should_retry(exc: Exception) -> bool:
    # Timeout -> retry
    if isinstance(exc, openai.APITimeoutError):
        return True

    # Connection/transient network failure -> retry
    if isinstance(exc, openai.APIConnectionError):
        return True

    if isinstance(exc, openai.APIStatusError):
        status = exc.status_code

        # Rate limited
        if status == 429:
            return True

        # Server-side failure
        if 500 <= status <= 599:
            return True

        # 400 / 401 / 403 and other client
        # errors must fail immediately.
        return False

    return False


def get_retry_delay(
    exc: Exception,
    attempt: int,
) -> float:
    # Respect Retry-After on HTTP 429 when available.
    if isinstance(exc, openai.APIStatusError):
        if exc.status_code == 429:
            retry_after = exc.response.headers.get(
                "retry-after"
            )

            if retry_after:
                try:
                    return float(retry_after)
                except ValueError:
                    pass

    # attempt 0 -> ~1 second
    # attempt 1 -> ~2 seconds
    # attempt 2 -> ~4 seconds
    base_delay = 2 ** attempt
    jitter = random.uniform(0.0, 0.5)

    return base_delay + jitter


def call_llm(
    messages: list,
    prompt_version: str,
    repair_count: int,
):
    model = os.getenv("LLM_MODEL")

    if not model:
        raise ValueError("LLM_MODEL is missing.")

    client = get_client()

    last_error = None

    for attempt in range(MAX_ATTEMPTS):
        started = time.perf_counter()

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )

            duration_ms = round(
                (time.perf_counter() - started) * 1000,
                2,
            )

            usage = response.usage

            input_tokens = (
                usage.prompt_tokens
                if usage
                else None
            )

            output_tokens = (
                usage.completion_tokens
                if usage
                else None
            )

            write_call_log(
                {
                    "timestamp": datetime.now(
                        timezone.utc
                    ).isoformat(),
                    "prompt_version": prompt_version,
                    "model": model,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "duration_ms": duration_ms,
                    "repair_count": repair_count,
                    "attempt": attempt + 1,
                    "status": "success",
                }
            )

            return response

        except Exception as exc:
            duration_ms = round(
                (time.perf_counter() - started) * 1000,
                2,
            )

            last_error = exc

            write_call_log(
                {
                    "timestamp": datetime.now(
                        timezone.utc
                    ).isoformat(),
                    "prompt_version": prompt_version,
                    "model": model,
                    "input_tokens": None,
                    "output_tokens": None,
                    "duration_ms": duration_ms,
                    "repair_count": repair_count,
                    "attempt": attempt + 1,
                    "status": "error",
                    "error_type": type(exc).__name__,
                }
            )

            if not should_retry(exc):
                raise

            if attempt == MAX_ATTEMPTS - 1:
                raise

            delay = get_retry_delay(
                exc,
                attempt,
            )

            time.sleep(delay)

    raise last_error