"""
ai app — Groq call wrapper with GroqCallLog audit logging (Section 3.4).


"""

import time

from core.models import GroqCallLog

from .prompt_templates import PROMPT_VERSIONS
from .schema_validation import parse_and_validate

GROQ_MODEL = "llama-3.3-70b-versatile"
PROMPT_TEMPLATE_VERSION = "v1" 


def call_groq(client, *, call_type, prompt, request_payload, party=None,
               max_tokens=1000, prompt_template_version=PROMPT_TEMPLATE_VERSION):
   
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
    
    version = PROMPT_VERSIONS.get(template_key, PROMPT_TEMPLATE_VERSION)
    raw, log_entry = call_groq(
        client, call_type=call_type, prompt=prompt, request_payload=request_payload,
        party=party, max_tokens=max_tokens, prompt_template_version=version,
    )
    parsed, error_message = parse_and_validate(raw, call_type)
    finalize_log(log_entry, success=not error_message, parsed=parsed, error_message=error_message)
    return parsed, bool(error_message), log_entry