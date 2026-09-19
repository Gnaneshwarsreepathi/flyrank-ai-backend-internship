import json
import sys
from pathlib import Path

import requests


API_URL = "http://127.0.0.1:8000/triage"


def load_cases():
    current_directory = Path(__file__).resolve().parent
    cases_file = current_directory / "cases.json"

    with cases_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main():
    cases = load_cases()

    total = len(cases)
    correct = 0
    failures = []

    print()
    print("=" * 65)
    print("AI SUPPORT TRIAGE - EVALUATION")
    print("=" * 65)
    print()

    for case in cases:
        case_id = case["id"]
        text = case["text"]
        expected = case["expected_category"]

        try:
            response = requests.post(
                API_URL,
                json={
                    "text": text
                },
                timeout=60,
            )

        except requests.RequestException as exc:
            print(
                f"[{case_id}] ERROR: {exc}"
            )

            failures.append(
                {
                    "id": case_id,
                    "expected": expected,
                    "actual": "REQUEST_ERROR",
                }
            )

            continue

        if response.status_code != 200:
            print(
                f"[{case_id}] HTTP "
                f"{response.status_code}"
            )

            failures.append(
                {
                    "id": case_id,
                    "expected": expected,
                    "actual": (
                        f"HTTP_{response.status_code}"
                    ),
                }
            )

            continue

        try:
            result = response.json()

        except ValueError:
            print(
                f"[{case_id}] Invalid JSON response"
            )

            failures.append(
                {
                    "id": case_id,
                    "expected": expected,
                    "actual": "INVALID_JSON",
                }
            )

            continue

        actual = result.get(
            "category"
        )

        matched = (
            actual == expected
        )

        if matched:
            correct += 1
            status = "PASS"
        else:
            status = "FAIL"

            failures.append(
                {
                    "id": case_id,
                    "text": text,
                    "expected": expected,
                    "actual": actual,
                }
            )

        print(
            f"[{case_id}] {status}"
        )
        print(
            f"    Expected: {expected}"
        )
        print(
            f"    Actual:   {actual}"
        )
        print()

    score = (
        (correct / total) * 100
        if total
        else 0
    )

    print("=" * 65)
    print("RESULT")
    print("=" * 65)
    print(
        f"Correct: {correct}/{total}"
    )
    print(
        f"Match rate: {score:.2f}%"
    )

    if failures:
        print()
        print("FAILURES")
        print("-" * 65)

        for failure in failures:
            print(
                json.dumps(
                    failure,
                    indent=2,
                    ensure_ascii=False,
                )
            )

    print()

    # Return non-zero only for infrastructure/
    # request problems, not ordinary model mistakes.
    request_failures = [
        failure
        for failure in failures
        if str(
            failure.get(
                "actual",
                ""
            )
        ).startswith(
            (
                "HTTP_",
                "REQUEST_",
                "INVALID_",
            )
        )
    ]

    if request_failures:
        sys.exit(1)


if __name__ == "__main__":
    main()