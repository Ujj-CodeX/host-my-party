"""
ai app — strict JSON-schema validation for every Groq response (Section 3.4).

Each GroqCallLog.CallType has an exact expected shape. Groq is asked to
reply with ONLY JSON, but LLMs still drift (extra prose, wrong field
names, wrong types) — this is the "response parser/validator" Section
3.4 calls for. If the parsed JSON doesn't match its schema, it's treated
exactly like a parse failure: the caller's existing pure-Python fallback
runs instead of the app silently trusting malformed AI output.
"""

import json

from jsonschema import ValidationError
from jsonschema import validate as _jsonschema_validate

from core.models import GroqCallLog

_RESTAURANT_ITEM_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "price", "isVeg", "isJainCompatible", "isDiabeticFriendly"],
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "price": {"type": "number"},
        "isVeg": {"type": "boolean"},
        "isJainCompatible": {"type": "boolean"},
        "isDiabeticFriendly": {"type": "boolean"},
    },
}

SCHEMAS = {
    GroqCallLog.CallType.RESTAURANT_FILTER: {
        "type": "array",
        "items": {
            "type": "object",
            "required": ["id", "name", "distanceKm", "eligibleMenu"],
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "distanceKm": {"type": "number"},
                "eligibleMenu": {"type": "array", "items": _RESTAURANT_ITEM_SCHEMA},
            },
        },
    },
    GroqCallLog.CallType.SCHEDULING: {
        "type": "object",
        "required": ["fire_at", "reasoning"],
        "properties": {
            "fire_at": {"type": "string", "pattern": r"^\d{2}:\d{2}$"},
            "reasoning": {"type": "string"},
        },
    },
    GroqCallLog.CallType.BUDGET_GUARDIAN: {
        "type": "object",
        "required": ["status"],
        "properties": {
            "status": {"enum": ["ok", "exceeded"]},
        },
    },
    GroqCallLog.CallType.MERGE_CHECK: {
        "type": "object",
        "required": ["has_merges", "merges"],
        "properties": {
            "has_merges": {"type": "boolean"},
            "merges": {"type": "array"},
        },
    },

    GroqCallLog.CallType.DINEOUT_RANKING: {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["id", "aiReason"],
        "properties": {"id": {"type": "string"}, "aiReason": {"type": "string"}},
    },
    GroqCallLog.CallType.WHOLE_SUM_OPTIMIZER: {
    "type": "object",
    "required": ["restaurant_id", "restaurant_name", "items"],
    "properties": {
        "restaurant_id": {"type": "string"},
        "restaurant_name": {"type": "string"},
        "items": {"type": "array"},
    },
},
},
}


def parse_and_validate(raw_text, call_type):
    """
    Strips markdown fences, parses JSON, then validates against this
    call_type's registered schema.

    Returns (parsed, error_message). error_message is "" on success —
    callers treat any non-empty error_message as "fall back to the
    pure-Python path", the same trigger a raw json.JSONDecodeError used
    to be, just with schema drift now caught too, not only malformed JSON.
    """
    clean = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(clean)
    except json.JSONDecodeError as exc:
        return None, f"json_decode_error: {exc}"

    schema = SCHEMAS.get(call_type)
    if schema is None:
        return parsed, ""  # no schema registered for this call_type — accept as-is

    try:
        _jsonschema_validate(instance=parsed, schema=schema)
    except ValidationError as exc:
        return None, f"schema_validation_error: {exc.message}"

    return parsed, ""