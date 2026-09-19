import os

import openai
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.llm.client import (
    PROMPT_VERSION,
    ask_model,
    repair_model_output,
)
from src.llm.quarantine import quarantine_failure
from src.llm.schema import (
    TriageRequest,
    TriageResponse,
)
from src.llm.validator import parse_and_validate


# =========================================================
# ENVIRONMENT
# =========================================================
load_dotenv(override=True)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="AI Support Triage API",
    version="1.0.0",
    description=(
        "Classifies customer support messages "
        "using an AI model."
    ),
)


# =========================================================
# REQUEST VALIDATION ERROR HANDLER
# =========================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = exc.errors()

    first_error = (
        errors[0]
        if errors
        else {}
    )

    location = first_error.get(
        "loc",
        [],
    )

    field = (
        str(location[-1])
        if location
        else "unknown"
    )

    message = first_error.get(
        "msg",
        "Invalid input",
    )

    return JSONResponse(
        status_code=400,
        content={
            "error": "Invalid request",
            "field": field,
            "message": message,
        },
    )


# =========================================================
# ROOT / HEALTH CHECK
# =========================================================

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "AI Support Triage API",
    }


# =========================================================
# TRIAGE ENDPOINT
# =========================================================

@app.post(
    "/triage",
    response_model=TriageResponse,
)
def triage(
    request: TriageRequest,
):

    # =====================================================
    # STAGE 4 - KILL SWITCH
    # =====================================================

    llm_enabled = os.getenv(
        "LLM_ENABLED",
        "true",
    ).lower() == "true"

    if not llm_enabled:
        return JSONResponse(
            status_code=503,
            content={
                "error": (
                    "AI service is currently disabled."
                )
            },
        )

    # =====================================================
    # STAGE 1 - STUB MODE
    # =====================================================

    stub_mode = (
        os.getenv(
            "LLM_STUB",
            "0",
        )
        == "1"
    )

    if stub_mode:
        return TriageResponse(
            category="other",
            urgency="normal",
            confidence=0.40,
            reason=(
                "Stub response used "
                "without calling the model."
            ),
        )

    # =====================================================
    # FIRST MODEL CALL
    # =====================================================

    try:
        first_result = ask_model(
            request.text
        )

    # -----------------------------------------------------
    # Timeout -> HTTP 504
    # -----------------------------------------------------

    except openai.APITimeoutError:
        return JSONResponse(
            status_code=504,
            content={
                "error": (
                    "AI model request timed out."
                )
            },
        )

    # -----------------------------------------------------
    # Other provider/model error -> HTTP 502
    # -----------------------------------------------------

    except Exception as exc:
        return JSONResponse(
            status_code=502,
            content={
                "error": (
                    "AI model request failed."
                ),
                "detail": str(exc),
            },
        )

    # =====================================================
    # GET RAW MODEL OUTPUT
    # =====================================================

    raw_output = first_result["raw"]

    # =====================================================
    # FIRST PARSE + VALIDATION
    # =====================================================

    try:
        validated_response = (
            parse_and_validate(
                raw_output
            )
        )

        return validated_response

    except Exception as first_error:

        # =================================================
        # EXACTLY ONE REPAIR ATTEMPT
        # =================================================

        try:
            repaired_result = (
                repair_model_output(
                    text=request.text,
                    broken_output=raw_output,
                    validation_error=str(
                        first_error
                    ),
                )
            )

            repaired_raw = (
                repaired_result["raw"]
            )

            # ---------------------------------------------
            # Validate repaired response
            # ---------------------------------------------

            validated_response = (
                parse_and_validate(
                    repaired_raw
                )
            )

            return validated_response

        # -------------------------------------------------
        # Repair call timeout
        # -------------------------------------------------

        except openai.APITimeoutError:

            quarantine_failure(
                input_text=request.text,
                raw_output=raw_output,
                error=(
                    "Repair request timed out."
                ),
                prompt_version=(
                    PROMPT_VERSION
                ),
            )

            return JSONResponse(
                status_code=504,
                content={
                    "error": (
                        "AI model repair "
                        "request timed out."
                    )
                },
            )

        # -------------------------------------------------
        # Repair/validation failed
        # -------------------------------------------------

        except Exception as repair_error:

            # Use repaired output when available.
            # Otherwise quarantine original output.
            failed_raw = locals().get(
                "repaired_raw",
                raw_output,
            )

            quarantine_failure(
                input_text=request.text,
                raw_output=failed_raw,
                error=str(
                    repair_error
                ),
                prompt_version=(
                    PROMPT_VERSION
                ),
            )

            # IMPORTANT:
            # Never return raw model output
            # to the API caller.
            return JSONResponse(
                status_code=422,
                content={
                    "error": (
                        "The AI response "
                        "could not be validated."
                    ),
                    "prompt_version": (
                        PROMPT_VERSION
                    ),
                },
            )