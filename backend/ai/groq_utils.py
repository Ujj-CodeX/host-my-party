"""
ai app — Groq call wrapper with GroqCallLog audit logging (Section 3.4).

Every AI Layer endpoint goes through call_groq() so that every
request/response, its latency, and its eventual parse outcome is
recorded in GroqCallLog — without each view having to duplicate that
bookkeeping by hand. call_groq_validated() builds on top of that with
versioned prompts (ai/prompt_templates.py) and strict JSON-schema
validation (ai/schema_validation.py) — the two Section 3.4 items that
used to be missing: every call site hardcoded prompt_template_version
"v1" regardless of the prompt's actual wording, and "did it parse as
JSON" was the only check on Groq's output, with no shape/type validation
beyond that.
"""

import time

from core.models import GroqCallLog

from .prompt_templates import PROMPT_VERSIONS
from .schema_validation import parse_and_validate

GROQ_MODEL = "llama-3.3-70b-versatile"
PROMPT_TEMPLATE_VERSION = "v1"  # fallback for call sites not yet in PROMPT_VERSIONS


def call_groq(client, *, call_type, prompt, request_payload, party=None,
               max_tokens=1000, prompt_template_version=PROMPT_TEMPLATE_VERSION):
    """
    Makes the actual Groq chat-completion call and immediately persists a
    GroqCallLog row — request_payload is the structured business inputs
    (not the full rendered prompt; the prompt is reproducible from
    template_version + request_payload, which keeps the log readable).

    Returns (raw_response_text, log_entry). log_entry.success is False and
    response_parsed is None until the caller finishes parsing and calls
    finalize_log() — if the API call itself fails, the exception is
    re-raised after the failure is recorded (error_message + latency),
    so callers see the same exception behavior as before this wrapper
    existed, just with an audit trail left behind.
    """
    started = time.monotonic()
    log_entry = GroqCallLog.objects.create(
        party=party,
        call_type=call_type,
        prompt_template_version=prompt_template_version,
        request_payload=request_payload,
        response_raw="",
        success=False,
    )
    try:
        groq_resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        raw = groq_resp.choices[0].message.content.strip()
        log_entry.response_raw = raw
        log_entry.latency_ms = int((time.monotonic() - started) * 1000)
        log_entry.save(update_fields=["response_raw", "latency_ms"])
        return raw, log_entry
    except Exception as exc:
        log_entry.latency_ms = int((time.monotonic() - started) * 1000)
        log_entry.error_message = str(exc)[:255]
        log_entry.save(update_fields=["latency_ms", "error_message"])
        raise


def finalize_log(log_entry, *, success, parsed=None, error_message=""):
    """Call once the caller knows whether the response parsed cleanly
    against the expected schema (Section 3.4's response validator)."""
    log_entry.response_parsed = parsed
    log_entry.success = success
    log_entry.error_message = (error_message or "")[:255]
    log_entry.save(update_fields=["response_parsed", "success", "error_message"])


def call_groq_validated(client, *, call_type, prompt, request_payload, template_key,
                         party=None, max_tokens=1000):
    """
    call_groq() + strict JSON-schema validation (Section 3.4), in one
    step. template_key looks up PROMPT_VERSIONS so the
    prompt_template_version recorded on the GroqCallLog row always
    matches the builder function that actually produced `prompt`, instead
    of every call site hardcoding "v1" regardless of prompt changes.

    Returns (parsed, used_fallback, log_entry):
    - parsed is None and used_fallback is True when the response failed
      to parse as JSON OR failed schema validation — the caller is
      expected to run its own existing pure-Python fallback in that case,
      exactly as it already did for a raw json.JSONDecodeError.
    - parsed is the validated object/array and used_fallback is False
      on success.
    """
    version = PROMPT_VERSIONS.get(template_key, PROMPT_TEMPLATE_VERSION)
    raw, log_entry = call_groq(
        client, call_type=call_type, prompt=prompt, request_payload=request_payload,
        party=party, max_tokens=max_tokens, prompt_template_version=version,
    )
    parsed, error_message = parse_and_validate(raw, call_type)
    finalize_log(log_entry, success=not error_message, parsed=parsed, error_message=error_message)
    return parsed, bool(error_message), log_entry