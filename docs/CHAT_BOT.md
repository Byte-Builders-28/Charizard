# 🤖 FlameScope Chat Bot — Architecture, Behavior & Usage Guide

## Overview

The FlameScope Chat Bot is an intelligent research assistant that translates natural language queries into FlameScope API calls. It operates via a Gemini agent loop that reasons over research queries, executes database and telemetry tools, and synthesizes structured scientific data into user-friendly responses.

---

## 1. Architecture & Message Flow

```
User → FlameScope API (POST /chat?user={id}) → Gemini Reasoning Loop → Tool Execution → Gemini Synthesis → User
```

### Protocol Steps:
1. **User Request**: User sends a natural language prompt with their user identifier.
2. **Context Resolution**: The API retrieves the user's isolated in-memory session (`last_query`, `default_limit`).
3. **Gemini Reasoning**: The model receives system instructions, available tool definitions, session context, and the user's message.
4. **Tool Execution**: If Gemini chooses an action (format: `{"action": "tool_name", "params": {...}}`), the API executes the tool directly against the local SQLite database and telemetry files.
5. **Synthesis**: The tool result is returned to Gemini to formulate a clean, user-friendly summary (`{"final_response": "..."}`).
6. **Delivery**: The client receives a standardized JSON response:
   ```json
   {
     "status": "success",
     "response": "User-facing summary text"
   }
   ```
   *Raw JSON tool dumps are never exposed to the user.*

---

## 2. API Endpoint Reference

### `POST /chat?user={id}`

#### Parameters:
| Location | Parameter | Type | Required | Constraints | Description |
|---|---|---|---|---|---|
| Query | `user` | string | **Yes** | 1–100 chars, non-empty | Per-user identifier for session isolation |
| Body | `msg` | string | **Yes** | 1–500 chars, non-empty | Natural language research query or command |

#### Request Body Schema:
```json
{
  "msg": "search liquid oxygen experiments"
}
```

#### Response Body Schema:
```json
{
  "status": "success",
  "response": "Found 5 experiments involving liquid oxygen. Would you like details on any?"
}
```

#### HTTP Status Codes:
- `200 OK`: Query processed successfully.
- `400 Bad Request`: `user` or `msg` is empty, whitespace-only, or exceeds character limits.
- `422 Unprocessable Entity`: Missing required query parameter or malformed JSON body.

---

## 3. Minimal Per-User Context Tracking

Per the specification, user context is strictly limited to **2 fields** and maintained **in-memory only** (resets on server restart):

| Field | Type | Default | Update Trigger | Purpose |
|---|---|---|---|---|
| `last_query` | string \| null | `null` | Updated on **every** message | Tracks most recent topic for conversational continuity |
| `default_limit` | integer | `10` | Updated **only** on explicit user request (1–50) | Preferred number of rows returned for telemetry queries |

### Context Isolation:
Context is strictly isolated per `user` parameter. Actions taken by `user=researcher_01` (e.g. changing telemetry limit to 5) do not affect `user=researcher_02`.

---

## 4. Available Tools

The bot connects to the following core FlameScope API operations:

| Tool | API Endpoint | Parameters | Purpose |
|---|---|---|---|
| `search_investigations` | `GET /search` | `q` (required), optional filters (`fuel_type`, `fuel_state`, `gravity_condition`, `safety_category`, `limit`) | Full-text and structured search across investigations |
| `get_investigation` | `GET /investigations/{id}` | `investigation_id` (e.g. `PSI-69`) | Retrieves complete investigation record (all 20 fields) |
| `get_telemetry` | `GET /investigations/{id}/telemetry` | `investigation_id`, `limit` (1–50, defaults to user's `default_limit`) | Reads and summarizes raw CSV telemetry data |
| `compare_investigations` | `POST /compare` | `investigation_ids` (2 to 3 IDs) | Side-by-side comparison of aligned attributes, differences, and constants |
| `list_investigations` | `GET /investigations` | `fuel_type`, `fuel_state`, `gravity_condition`, `safety_category`, `limit`, `offset` | Lightweight filtered listing of investigations |

### Explicit Constraints:
- **No reload**: Database reload (`POST /reload`) is an administrative operation and is strictly forbidden via `/chat`.
- **Comparison limits**: Side-by-side comparisons support between 2 and 3 investigations.
- **Investigation validation**: All referenced IDs must exist in the database. Non-existent IDs produce a polite explanation phrased by the assistant.

---

## 5. Environment & Model Configuration

The assistant uses Google Gemini with automatic fallback for high availability:

| Setting | Environment Variable | Default Value | Notes |
|---|---|---|---|
| **API Key** | `GEMINI_API_KEY` or `GOOGLE_API_KEY` | None | Read directly from environment |
| **Model** | `GEMINI_MODEL` | `gemini-2.5-flash-lite` | Falls back to `gemini-2.0-flash-lite`, `gemini-2.5-flash`, etc. |

### Offline / Fallback Engine:
If no Gemini API key is configured or during transient network/quota outages, the chat bot automatically transitions to an internal deterministic engine to fulfill search, detail, telemetry, comparison, and limit update queries without interruption.

---

## 6. Behavior & Example Interactions

### 1. New User Greeting
**Request:**
```http
POST /chat?user=newbie_01
{"msg": "hello"}
```
**Response:**
```json
{
  "status": "success",
  "response": "Welcome to FlameScope Assistant! I can help you search combustion investigations, look up details, view telemetry data, and compare experiments. Try 'search [topic]', 'show PSI-XXX', or 'compare PSI-A and PSI-B'."
}
```

### 2. Searching Experiments
**Request:**
```http
POST /chat?user=researcher_01
{"msg": "search liquid oxygen experiments"}
```
**Response:**
```json
{
  "status": "success",
  "response": "Found 5 experiments matching 'liquid oxygen':\n- PSI-69: Flame Extinguishment Experiment (FLEX)\n- PSI-68: Flame Extinguishment Experiment - 2 (FLEX-2)\n- PSI-25: Burning and Suppression of Solids - II (BASS-II)\n- PSI-26: Burning and Suppression of Solids (BASS)\n- PSI-159: Advanced Combustion via Microgravity Experiments (ACME CFI-G)\nWould you like details on any of these?"
}
```

### 3. Setting Default Telemetry Limit
**Request:**
```http
POST /chat?user=researcher_01
{"msg": "set telemetry limit to 5"}
```
**Response:**
```json
{
  "status": "success",
  "response": "Updated your default telemetry limit to 5 rows."
}
```

### 4. Telemetry Retrieval with Per-User Preferences
**User A (`researcher_01` with limit=5):**
```http
POST /chat?user=researcher_01
{"msg": "telemetry PSI-69"}
```
**Response:**
```json
{
  "status": "success",
  "response": "PSI-69 telemetry (5 rows from PSI-69_Experimental table_FLEX.csv): FLEX Test #=1, Fuel=Methanol, Ambient pressure=757.7; FLEX Test #=2, Fuel=Methanol, Ambient pressure=758.1; ..."
}
```

**User B (`researcher_02` with default limit=10):**
```http
POST /chat?user=researcher_02
{"msg": "telemetry PSI-69"}
```
**Response:**
```json
{
  "status": "success",
  "response": "PSI-69 telemetry (10 rows from PSI-69_Experimental table_FLEX.csv): ..."
}
```

### 5. Investigation Details
**Request:**
```http
POST /chat?user=researcher_01
{"msg": "show PSI-69"}
```
**Response:**
```json
{
  "status": "success",
  "response": "Investigation PSI-69 (FLEX): Flame Extinguishment Experiment\n- Fuel: methanol, heptane\n- Gravity Condition: microgravity\n- Objective: Map the flammability limits of liquid fuels in microgravity..."
}
```

### 6. Comparing Investigations
**Request:**
```http
POST /chat?user=researcher_01
{"msg": "compare PSI-69 and PSI-98"}
```
**Response:**
```json
{
  "status": "success",
  "response": "Comparison of PSI-69, PSI-98:\n- Key differences: title, acronym, fuel_type, fuel_state, sample_shape, hardware\n- Identical parameters: gravity_condition (microgravity)"
}
```

### 7. Administrative Reload Protection
**Request:**
```http
POST /chat?user=researcher_01
{"msg": "reload database"}
```
**Response:**
```json
{
  "status": "success",
  "response": "Reloading the database is an administrative action and is not permitted through the chat interface."
}
```

### 8. Invalid or Out-of-Scope Queries
**Request:**
```http
POST /chat?user=researcher_01
{"msg": "what is the recipe for chocolate cake?"}
```
**Response:**
```json
{
  "status": "success",
  "response": "I'm not sure how to help with that. Try 'search [topic]', 'show PSI-XXX', or 'compare PSI-A and PSI-B'."
}
```

---

## 7. How to Use the Chat Bot

### Prerequisites
1. Start the FastAPI server:
   ```powershell
   $env:PYTHONPATH = "src"
   $env:GEMINI_API_KEY = "your_gemini_api_key"  # Optional: fallback engine runs if omitted
   & .venv/Scripts/python.exe -m uvicorn api.main:app --port 8000 --reload
   ```

### Option A: Using `curl` (PowerShell / Command Prompt)

```powershell
curl.exe -X POST "http://127.0.0.1:8000/chat?user=researcher_01" `
  -H "Content-Type: application/json" `
  -d "{\"msg\": \"search liquid oxygen experiments\"}"
```

### Option B: Using PowerShell `Invoke-RestMethod`

```powershell
$body = @{ msg = "telemetry PSI-69" } | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/chat?user=researcher_01" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body

$response.response
```

### Option C: Using Python `requests`

```python
import requests

BASE_URL = "http://127.0.0.1:8000/chat"
user_id = "researcher_01"

def ask_bot(query: str):
    res = requests.post(f"{BASE_URL}?user={user_id}", json={"msg": query})
    res.raise_for_status()
    print("Bot:", res.json()["response"])

ask_bot("hello")
ask_bot("search liquid oxygen")
ask_bot("set telemetry limit to 5")
ask_bot("telemetry PSI-69")
ask_bot("compare PSI-69 and PSI-98")
```

### Option D: Interactive Swagger UI
Open your browser to:
`http://127.0.0.1:8000/docs`
Navigate to the `POST /chat` endpoint under the **chat** tag to test queries interactively.
