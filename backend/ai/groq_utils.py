"""
ai app — Groq call wrapper with GroqCallLog audit logging.

Every AI Layer endpoint (Section 3.4) goes through call_groq() so that
every request/response, its latency, and its eventual parse outcome is
recorded in GroqCallLog — without each view having to duplicate that
bookkeeping by hand.

"""

import time

from core.models import GroqCallLog

GROQ_MODEL = "llama-3.3-70b-versatile"
PROMPT_TEMPLATE_VERSION = "v1"


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