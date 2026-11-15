# API Options Reference

This document lists the parameters for the Charizard frontend API endpoints.

---

## Base Configuration

| Environment Variable | Default Value |
|---------------------|---------------|
| `PUBLIC_API_BASE_URL` | `http://127.0.0.1:8000` |

The API base URL is configurable via the `PUBLIC_API_BASE_URL` environment variable in your Astro project. If not set, it defaults to `http://127.0.0.1:8000`.

---

## Endpoint Reference

### Health Check

**GET `/health`**

Returns the API status and the number of investigation records loaded.

**Response:**

```json
{
  "status": "ok",
  "records": 11
}
```

---

### Investigation Listing

**GET `/investigations`**

Returns a filterable and paginated list of lightweight investigation records.

**Query Parameters:**

| Parameter | Type | Description |
|---------------------------|--------------------------------------------------------------|
| `fuel_type` | string | Substring match on fuel type (e.g., `methanol`) |
| `fuel_state` | string | Exact match: `solid`, `liquid`, or `gas` |
| `gravity_condition` | string | Exact match: `microgravity`, `normal_gravity`, or `partial_gravity` |
| `safety_category` | string | Substring match on safety categories |
| `oxygen_min` | number | Minimum oxygen percentage (inclusive) |
| `oxygen_max` | number | Maximum oxygen percentage (inclusive) |
| `pressure_min` | number | Minimum pressure in psi (inclusive) |
| `pressure_max` | number | Maximum pressure in psi (inclusive) |
| `sample_shape` | string | Substring match on sample shape |
| `sample_size` | string | Substring match on sample size |
| `diluents` | string | Substring match on diluent names |
| `hardware` | string | Substring match on experiment hardware |
| `sensors_and_measurements` | string | Substring match on sensor types |
| `objective` | string | Substring match on investigation objective |
| `limit` | integer | Page size (1-500, default 50) |
| `offset` | integer | Pagination offset (default 0) |

**Response Structure:**

```json
{
  "count": 11,
  "offset": 0,
  "limit": 50,
  "results": []
}
```

Each result contains lightweight investigation information, including identity, title, fuel, gravity condition, experimental conditions, and other filterable fields. The listing endpoint does **not** return complete `FieldValue` objects.

---

### Investigation Details

**GET `/investigations/{investigation_id}`**

Returns the complete investigation record for a specific investigation.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `investigation_id` | string | Investigation ID (e.g., `PSI-69`) |


### Search

**GET `/search`**

Required query parameter:

- `q`

Optional parameters:

- `fuel_type`
- `fuel_state`
- `gravity_condition`
- `safety_category`
- `limit`

The endpoint returns:

```json
{
  "query": "liquid oxygen microgravity",
  "matches": [],
  "count": 0
}
```

Search results include relevance and matched terms.

---

### Comparison

**POST `/compare`**

Compares two or three investigations.

**Request Body:**

```json
{
  "investigation_ids": ["PSI-69", "PSI-98"]
}
```

The backend requires between two and three valid investigation IDs.

**Response includes:**

- `investigations`
- `aligned_table`
- `what_varied`
- `what_stayed_same`
- `telemetry_summary`

Use the backend's comparison results rather than recreating comparison logic in the frontend.

Possible errors:
- HTTP 422 for an invalid number of IDs.
- HTTP 404 if an investigation does not exist.

---

### Research Agent

**POST `/chat?user={user}`**

Sends a natural-language message to the research agent.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `user` | string | Per-user identifier (required, 1-100 characters) |

**Request Body:**

```json
{
  "msg": "Search for liquid fuel experiments in microgravity."
}
```

**Response:**

```json
{
  "status": "success",
  "response": "..."
}
```

The `user` query parameter is required and must contain a valid identifier between 1 and 100 characters.

---

### Health Check

**GET `/health`**

Returns the API status and the number of investigation records loaded.

Example:

```json
{
  "status": "ok",
  "records": 11
}
```

---

## Error Handling

The backend can return the following HTTP statuses:

| Status | Meaning                    |
|--------|----------------------------|
| 200    | Request succeeded          |
| 404    | Resource not found         |
| 422    | Invalid request parameters |
| 500    | Backend error              |

Backend errors include a JSON `detail` field.

The frontend must:
- Display understandable error messages.
- Distinguish an empty result from a failed request.
- Avoid exposing unnecessary internal stack traces.
- Allow users to retry failed requests where appropriate.
- Avoid silently hiding API failures.

---

## Quick Reference: API Client Functions

These functions should be implemented in `src/lib/api.js`:

```javascript
// Health
getHealth();

// Investigations
getInvestigations(params);
getInvestigation(id);

// Telemetry
getInvestigationTelemetry(id, limit);

// Search
searchInvestigations(params);

// Comparison
compareInvestigations(ids);

// Research agent
sendAgentMessage(message, user);
```

---

## Notes for Frontend Development

- **Do not** re-implement backend filtering or comparison logic in the frontend.
- Use the backend's comparison results; do not independently recalculate them.
- Preserve `FieldValue` structure when presenting scientific metadata.
- Distinguish between verified, extracted, inferred, and unavailable data.
- Do not assume all investigations contain telemetry.
- Do not assume telemetry columns are consistent between files.
- Use the original backend field names as the source of truth.
- The API client should handle request errors centrally; the UI decides how to present them.


**Response Structure:**

```json
{
  "investigation_id": "PSI-69",
  "title": "Flame Extinguishment Experiment",
  "acronym": "FLEX",
  "doi": "10.60555/mbq8-0451",
  "source_url": "https://psi.nasa.gov/investigations/PSI-69",
  "objective": {
    "value": "...",
    "unit": null,
    "status": "extracted",
    "evidence_quote": "...",
    "evidence_location": "..."
  },
  "hardware": { ... },
  "fuel_type": { ... },
  "fuel_state": { ... },
  "sample_shape": { ... },
  "sample_size": { ... }
}
```

Most scientific fields use a `FieldValue` structure:

```json
{
  "value": "...",
  "unit": null,
  "status": "extracted",
  "evidence_quote": "...",
  "evidence_location": "..."
}
```

Possible errors:
- HTTP 404 if the investigation ID does not exist.

---

### Telemetry

**GET `/investigations/{investigation_id}/telemetry`**

Returns telemetry CSV data as JSON.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `investigation_id` | string | Investigation ID (e.g., `PSI-69`) |

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Maximum rows returned per CSV file (optional) |

**Response Structure:**

```json
{
  "investigation_id": "PSI-69",
  "files": [
    {
      "filename": "PSI-69_Experimental table_FLEX.csv",
      "columns": [],
      "row_count": 274,
      "data": []
    }
  ]
}
```

**Important Behaviors:**

- PSI-159 returns two telemetry files.
- PSI-60 returns `files: []` (metadata-only investigation, no CSV).
- Empty CSV cells are converted to `null`.
- Different telemetry files may have different columns.
- Do not assume that every investigation has telemetry.
- Do not assume all telemetry files share the same schema.
