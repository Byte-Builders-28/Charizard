"""
FlameScope - Chat Bot Assistant
src/api/chat.py
================================
Per-user research assistant bot that translates natural language queries
into FlameScope API calls via Gemini agent with minimal context tracking.
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException
from pydantic import BaseModel, Field

from api.db import DB_PATH, get_investigation, list_investigations

log = logging.getLogger("flamescope.api.chat")

# Available Gemini models in priority order for fallback
DEFAULT_GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
FALLBACK_MODELS = [
    DEFAULT_GEMINI_MODEL,
    "gemini-3.5-flash-lite",
    "gemini-3.0-flash-lite"
]


class ChatRequest(BaseModel):
    msg: str = Field(..., description="Natural language query from user")


class ChatResponse(BaseModel):
    status: str = "success"
    response: str


@dataclass
class UserContext:
    """Minimal per-user context tracking (exactly 2 fields per spec)."""
    last_query: Optional[str] = None
    default_limit: int = 10


# In-memory context store (reset on server restart)
USER_SESSIONS: Dict[str, UserContext] = {}


def get_or_create_context(user_id: str) -> Tuple[UserContext, bool]:
    """Retrieve or initialize fresh context for a given user ID."""
    is_new = user_id not in USER_SESSIONS
    if is_new:
        USER_SESSIONS[user_id] = UserContext(last_query=None, default_limit=10)
    return USER_SESSIONS[user_id], is_new


# ---------------------------------------------------------------------------
# Tool Implementations (Connecting to FlameScope API functionalities)
# ---------------------------------------------------------------------------

def tool_search_investigations(
    q: str,
    fuel_type: Optional[str] = None,
    fuel_state: Optional[str] = None,
    gravity_condition: Optional[str] = None,
    safety_category: Optional[str] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """Execute search_investigations tool."""
    from api.main import search_investigations
    try:
        limit_val = max(1, min(50, int(limit)))
    except (ValueError, TypeError):
        limit_val = 10
    return search_investigations(
        q=q,
        fuel_type=fuel_type,
        fuel_state=fuel_state,
        gravity_condition=gravity_condition,
        safety_category=safety_category,
        limit=limit_val,
    )


def tool_get_investigation(investigation_id: str) -> Dict[str, Any]:
    """Execute get_investigation tool."""
    inv_id = investigation_id.strip()
    rec = get_investigation(DB_PATH, inv_id)
    if rec is None:
        return {"error": f"Investigation {inv_id} not found in database."}
    return rec


def tool_get_telemetry(
    investigation_id: str,
    limit: Optional[int] = None,
    user_context: Optional[UserContext] = None,
) -> Dict[str, Any]:
    """Execute get_telemetry tool using user context default_limit if needed."""
    from api.main import get_telemetry_endpoint
    effective_limit = limit
    if effective_limit is None and user_context is not None:
        effective_limit = user_context.default_limit
    if effective_limit is not None:
        try:
            effective_limit = max(1, min(50, int(effective_limit)))
        except (ValueError, TypeError):
            effective_limit = 10
    else:
        effective_limit = 10

    inv_id = investigation_id.strip()
    # Check if investigation exists first
    rec = get_investigation(DB_PATH, inv_id)
    if rec is None:
        return {"error": f"Investigation {inv_id} not found in database."}

    res = get_telemetry_endpoint(investigation_id=inv_id, limit=effective_limit)
    return res


def tool_compare_investigations(investigation_ids: List[str]) -> Dict[str, Any]:
    """Execute compare_investigations tool (2-3 IDs)."""
    from api.main import compare_investigations
    if not isinstance(investigation_ids, list):
        return {"error": "investigation_ids must be a list of 2 or 3 investigation IDs."}
    if len(investigation_ids) < 2 or len(investigation_ids) > 3:
        return {"error": "Must provide between 2 and 3 investigation IDs for comparison."}

    try:
        return compare_investigations(investigation_ids=investigation_ids)
    except HTTPException as exc:
        return {"error": exc.detail}
    except Exception as exc:
        return {"error": str(exc)}


def tool_list_investigations(
    fuel_type: Optional[str] = None,
    fuel_state: Optional[str] = None,
    gravity_condition: Optional[str] = None,
    safety_category: Optional[str] = None,
    oxygen_min: Optional[float] = None,
    oxygen_max: Optional[float] = None,
    pressure_min: Optional[float] = None,
    pressure_max: Optional[float] = None,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """Execute list_investigations tool."""
    rows, total = list_investigations(
        DB_PATH,
        fuel_type=fuel_type,
        fuel_state=fuel_state,
        gravity_condition=gravity_condition,
        safety_category=safety_category,
        oxygen_min=oxygen_min,
        oxygen_max=oxygen_max,
        pressure_min=pressure_min,
        pressure_max=pressure_max,
        limit=limit,
        offset=offset,
    )
    return {"count": total, "offset": offset, "limit": limit, "results": rows}


AVAILABLE_TOOLS = {
    "search_investigations": tool_search_investigations,
    "get_investigation": tool_get_investigation,
    "get_telemetry": tool_get_telemetry,
    "compare_investigations": tool_compare_investigations,
    "list_investigations": tool_list_investigations,
}


# ---------------------------------------------------------------------------
# Gemini Agent
# ---------------------------------------------------------------------------

def _get_api_key() -> Optional[str]:
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def build_system_prompt(user_id: str, context: UserContext) -> str:
    return f"""You are the FlameScope Research Assistant for NASA PSI combustion and spacecraft fire safety investigations.
Your job is to translate user natural language queries into FlameScope API calls, reason over the returned data, and deliver concise, user-friendly responses.

User Session Context:
- User ID: {user_id}
- User Default Telemetry Limit: {context.default_limit} rows
- User Last Query: {context.last_query or 'None'}

Available Tools:
1. `search_investigations`
   - Params: `q` (required, string), `fuel_type` (str), `fuel_state` (str: solid|liquid|gas), `gravity_condition` (str), `safety_category` (str), `limit` (int: 1-50, default 10)
2. `get_investigation`
   - Params: `investigation_id` (required, string, e.g. "PSI-69")
3. `get_telemetry`
   - Params: `investigation_id` (required, string), `limit` (int: 1-50, default is user's default_limit: {context.default_limit})
4. `compare_investigations`
   - Params: `investigation_ids` (required, list of 2 or 3 strings, e.g. ["PSI-69", "PSI-98"])
5. `list_investigations`
   - Params: `fuel_type`, `fuel_state`, `gravity_condition`, `safety_category`, `limit` (default 50), `offset` (default 0)

CONSTRAINTS & RULES:
- There is NO "reload" functionality in chat. Never attempt to reload the database.
- Maximum 3 investigations for comparison (minimum 2).
- Only return your final user-friendly text in "final_response" - NEVER output raw unformatted JSON tool dumps to the user.
- If an investigation is not found or tool reports an error, explain it politely and helpfully.
- If the query is invalid or you cannot determine what combustion data the user needs, respond with:
  "I'm not sure how to help with that. Try 'search [topic]', 'show PSI-XXX', or 'compare PSI-A and PSI-B'."
- If the user sends a greeting (like 'hi', 'hello', 'hey') or asks what you can do, provide a warm welcome explaining FlameScope research capabilities.

RESPONSE PROTOCOL:
You MUST output a valid JSON object matching one of these two formats:
Format 1 (To call a tool):
{{"action": "tool_name", "params": {{...}}}}
Format 2 (To provide final response to user):
{{"final_response": "user-friendly text here"}}
"""


def _clean_json_text(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def call_gemini_model(prompt: str, system_instruction: str) -> Optional[str]:
    """Invoke Gemini using google.generativeai with model fallback."""
    api_key = _get_api_key()
    if not api_key:
        return None

    import google.generativeai as genai
    genai.configure(api_key=api_key)

    models_to_try = []
    env_model = os.environ.get("GEMINI_MODEL")
    if env_model:
        models_to_try.append(env_model)
    for m in FALLBACK_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)

    last_exc = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                ),
            )
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception as exc:
            log.warning("Gemini model %s failed: %s", model_name, exc)
            last_exc = exc
            continue

    if last_exc:
        log.error("All Gemini model attempts failed: %s", last_exc)
    return None


def execute_gemini_agent(user_id: str, msg: str, context: UserContext) -> Optional[str]:
    """Run the Gemini reasoning loop: User -> Gemini (action) -> Tool -> Gemini (final_response)."""
    system_instruction = build_system_prompt(user_id, context)
    prompt = f"User: {msg}\nPer-user default_limit: {context.default_limit}\n"

    raw_output = call_gemini_model(prompt, system_instruction)
    if not raw_output:
        return None

    cleaned = _clean_json_text(raw_output)
    try:
        data = json.loads(cleaned)
    except Exception as exc:
        log.warning("Could not parse initial Gemini JSON response: %s | Raw: %s", exc, raw_output)
        return raw_output

    # Check if Gemini directly gave final_response
    if "final_response" in data:
        return data["final_response"]

    # Check if Gemini specified an action
    action = data.get("action")
    if not action:
        # Check if response has plain text or explanation
        return data.get("response") or data.get("message") or raw_output

    params = data.get("params") or {}
    # Handle flat params in root object
    if not params:
        params = {k: v for k, v in data.items() if k not in ("action", "user")}

    # Validate action against available tools
    if action not in AVAILABLE_TOOLS:
        if "reload" in action.lower():
            return "Reloading the database is an administrative function and is not available via chat."
        return "I'm not sure how to help with that. Try 'search [topic]', 'show PSI-XXX', or 'compare PSI-A and PSI-B'."

    tool_func = AVAILABLE_TOOLS[action]
    try:
        if action == "get_telemetry":
            # Pass user_context so default_limit is applied if needed
            tool_result = tool_func(**params, user_context=context) if "user_context" not in params else tool_func(**params)
        else:
            tool_result = tool_func(**params)
    except TypeError as te:
        log.warning("Tool %s argument error: %s with params %s", action, te, params)
        tool_result = {"error": f"Invalid parameters for {action}: {te}"}
    except Exception as exc:
        log.warning("Tool %s execution error: %s", action, exc)
        tool_result = {"error": str(exc)}

    # Send tool output back to Gemini to synthesize final user-friendly response
    follow_up_prompt = (
        f"User query was: {msg}\n"
        f"You executed tool '{action}' with params {json.dumps(params)}.\n"
        f"Tool Result:\n{json.dumps(tool_result, default=str)}\n\n"
        "Synthesize this into a user-friendly final response for the user. "
        "Do NOT output raw tool JSON. Respond in JSON format: {\"final_response\": \"...\"}"
    )

    second_output = call_gemini_model(follow_up_prompt, system_instruction)
    if not second_output:
        # Fallback to formatting tool result if second Gemini call fails
        return format_tool_result_fallback(action, tool_result)

    cleaned_second = _clean_json_text(second_output)
    try:
        second_data = json.loads(cleaned_second)
        if "final_response" in second_data:
            return second_data["final_response"]
    except Exception:
        pass

    return cleaned_second


# ---------------------------------------------------------------------------
# Fallback / Deterministic Engine (Offline or missing Gemini API key)
# ---------------------------------------------------------------------------

def format_tool_result_fallback(action: str, result: Dict[str, Any]) -> str:
    """Format tool results into user-friendly text without exposing raw JSON."""
    if "error" in result:
        return f"Could not complete request: {result['error']}"

    if action == "search_investigations":
        matches = result.get("matches", [])
        count = result.get("count", 0)
        query = result.get("query", "")
        if count == 0:
            return f"Found 0 experiments matching '{query}'. Try different keywords."
        lines = [f"Found {count} experiment{'s' if count != 1 else ''} matching '{query}':"]
        for m in matches[:5]:
            lines.append(f"- {m['investigation_id']}: {m.get('title', 'Untitled')}")
        lines.append("Would you like details on any of these?")
        return "\n".join(lines)

    if action == "get_investigation":
        inv_id = result.get("investigation_id", "")
        title = result.get("title", "")
        acronym = result.get("acronym") or "N/A"
        obj = result.get("objective", {})
        obj_text = obj.get("value") if isinstance(obj, dict) else obj
        fuel = result.get("fuel_type", {})
        fuel_text = fuel.get("value") if isinstance(fuel, dict) else fuel
        grav = result.get("gravity_condition", {})
        grav_text = grav.get("value") if isinstance(grav, dict) else grav

        return (
            f"Investigation {inv_id} ({acronym}): {title}\n"
            f"- Fuel: {fuel_text}\n"
            f"- Gravity Condition: {grav_text}\n"
            f"- Objective: {obj_text or 'Not specified'}"
        )

    if action == "get_telemetry":
        inv_id = result.get("investigation_id", "")
        files = result.get("files", [])
        if not files:
            return f"No telemetry CSV files found for {inv_id}."
        f0 = files[0]
        data = f0.get("data", [])
        row_count = len(data)
        cols = f0.get("columns", [])
        summary_rows = []
        for r in data[:3]:
            row_items = [f"{k}={v}" for k, v in list(r.items())[:3] if v is not None]
            summary_rows.append(", ".join(row_items))
        preview = "; ".join(summary_rows) if summary_rows else "No data rows"
        return f"{inv_id} telemetry ({row_count} rows from {f0.get('filename')}): {preview}"

    if action == "compare_investigations":
        varied = result.get("what_varied", [])
        same = result.get("what_stayed_same", [])
        invs = [i.get("investigation_id") for i in result.get("investigations", [])]
        return (
            f"Comparison of {', '.join(invs)}:\n"
            f"- Key differences: {', '.join(varied[:6]) or 'None'}\n"
            f"- Identical parameters: {', '.join(same[:6]) or 'None'}"
        )

    if action == "list_investigations":
        count = result.get("count", 0)
        items = result.get("results", [])
        names = [f"{i['investigation_id']} ({i.get('title')})" for i in items[:5]]
        return f"Found {count} investigations. Sample: " + "; ".join(names)

    return "Data retrieved successfully."


def execute_fallback_intent(msg: str, user_id: str, context: UserContext) -> str:
    """Deterministic natural language processor when Gemini is offline or unavailable."""
    msg_clean = msg.strip()
    msg_lower = msg_clean.lower()

    # 1. Greetings / Help
    if re.search(r"^(hi|hello|hey|help|start|who are you|greetings)[\s!.]*$", msg_lower):
        return (
            "Welcome to FlameScope Assistant! I can help you search combustion investigations, "
            "look up details, view telemetry data, and compare experiments. "
            "Try 'search [topic]', 'show PSI-XXX', or 'compare PSI-A and PSI-B'."
        )

    # 2. Check for reload attempt
    if "reload" in msg_lower:
        return "Reloading the database is an administrative action and is not permitted through the chat interface."

    # 3. Telemetry queries
    telem_match = re.search(r"(?:telemetry|data|telemetry\s+for)\s+(PSI-\d+)", msg_clean, re.I)
    if telem_match:
        inv_id = telem_match.group(1).upper()
        # Check if user specified a custom limit in query e.g. "limit 5"
        limit_match = re.search(r"limit\s+(\d+)", msg_lower)
        limit = int(limit_match.group(1)) if limit_match else context.default_limit
        res = tool_get_telemetry(inv_id, limit=limit, user_context=context)
        return format_tool_result_fallback("get_telemetry", res)

    # 4. Compare queries
    compare_ids = re.findall(r"PSI-\d+", msg_clean, re.I)
    if "compare" in msg_lower and len(compare_ids) >= 2:
        norm_ids = [cid.upper() for cid in compare_ids[:3]]
        res = tool_compare_investigations(norm_ids)
        return format_tool_result_fallback("compare_investigations", res)

    # 5. Detail queries
    detail_match = re.search(r"(?:show|get|detail|details|info|about)\s+(PSI-\d+)", msg_clean, re.I)
    if detail_match or re.match(r"^PSI-\d+$", msg_clean, re.I):
        inv_id = (detail_match.group(1) if detail_match else msg_clean).upper()
        res = tool_get_investigation(inv_id)
        return format_tool_result_fallback("get_investigation", res)

    # 6. Search queries
    search_match = re.search(r"^(?:search|find|lookup)\s+(.+)", msg_clean, re.I)
    if search_match:
        q = search_match.group(1).strip()
        res = tool_search_investigations(q=q)
        return format_tool_result_fallback("search_investigations", res)

    # 7. Default search attempt if query contains relevant terms
    res = tool_search_investigations(q=msg_clean)
    if res.get("count", 0) > 0:
        return format_tool_result_fallback("search_investigations", res)

    # 8. Invalid / unknown query fallback
    return "I'm not sure how to help with that. Try 'search [topic]', 'show PSI-XXX', or 'compare PSI-A and PSI-B'."


# ---------------------------------------------------------------------------
# Main Chat Controller
# ---------------------------------------------------------------------------

def process_chat_message(user_id: str, msg: str) -> str:
    """Process a chat message for a given user according to CHAT_BOT_SPEC."""
    # 1. Validation
    user_id = user_id.strip()
    if not user_id:
        raise HTTPException(status_code=400, detail="User parameter cannot be empty")
    if len(user_id) > 100:
        raise HTTPException(status_code=400, detail="User parameter cannot exceed 100 characters")

    msg = msg.strip()
    if not msg:
        raise HTTPException(status_code=400, detail="Message body cannot be empty")
    if len(msg) > 500:
        raise HTTPException(status_code=400, detail="Message body cannot exceed 500 characters")

    # 2. Retrieve or initialize context
    context, is_new_user = get_or_create_context(user_id)

    # If unknown user sent a greeting or empty inquiry, return welcome message
    msg_lower = msg.lower()
    if is_new_user and re.search(r"^(hi|hello|hey|start|help|who are you)[\s!.]*$", msg_lower):
        context.last_query = msg
        return (
            "Welcome to FlameScope Assistant! I can help you search combustion investigations, "
            "retrieve telemetry data, and compare experiments. Try 'search [topic]', 'show PSI-XXX', "
            "or 'compare PSI-A and PSI-B'."
        )

    # 3. Check for explicit change to default_limit
    # Context updates only when user explicitly changes default_limit.
    limit_change_match = re.search(
        r"(?:set|change|update|make)\s+(?:my\s+)?(?:default\s+)?(?:telemetry\s+)?limit\s+(?:to\s+)?(\d+)",
        msg,
        re.I,
    ) or re.search(r"^(?:telemetry\s+)?limit\s*[:=]\s*(\d+)$", msg, re.I)

    if limit_change_match:
        val = int(limit_change_match.group(1))
        context.last_query = msg
        if 1 <= val <= 50:
            context.default_limit = val
            return f"Updated your default telemetry limit to {val} rows."
        else:
            return f"Telemetry limit must be between 1 and 50 rows. Your default limit remains {context.default_limit}."

    # Update last_query on every message (as specified)
    context.last_query = msg

    # 4. Check for reload prohibition
    if re.search(r"\breload\b", msg_lower):
        return "Reloading the database is an administrative action and is not permitted through the chat interface."

    # 5. Execute with Gemini Agent if API key is present
    api_key = _get_api_key()
    if api_key:
        try:
            gemini_response = execute_gemini_agent(user_id, msg, context)
            if gemini_response:
                return gemini_response
        except Exception as exc:
            log.warning("Gemini execution failed: %s; falling back to deterministic engine", exc)

    # 6. Fallback engine
    return execute_fallback_intent(msg, user_id, context)
