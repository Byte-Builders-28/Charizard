# AGENTS.md

# CHARIZARD Frontend Development Guide

## 1. Project Overview

Build the frontend for CHARIZARD, a microgravity combustion research data explorer.

The application allows users to:

- Browse spacecraft combustion investigations.
- Inspect investigation metadata and experimental conditions.
- Explore available telemetry data.
- Compare multiple investigations.
- Interact with a research agent through natural language.
- Understand the scope and limitations of the available dataset.

The frontend communicates with an existing FastAPI backend.

Do not recreate backend functionality or processing logic.

## 2. Technology Stack

- **Framework:** Astro
- **Styling:** Tailwind CSS v4
- **Interactions:** Vanilla JavaScript (ES modules)
- **API communication:** Native Fetch API
- **Backend:** Existing FastAPI application

Avoid:

- React, Vue, Svelte, or other frontend frameworks.
- Axios or additional HTTP libraries.
- Unnecessary state-management libraries.
- Unnecessary animation libraries.
- Large UI component libraries.

Use Astro's component system and native JavaScript wherever possible.

## 3. Design Direction

The visual identity should feel like a scientific research publication or a specialized research instrument.

Avoid generic SaaS and AI-dashboard aesthetics.

### Design constraints

- No sidebar.
- Use a simple horizontal navigation bar.
- No gradients.
- No neon colors or glowing effects.
- No glassmorphism.
- Avoid excessive rounded corners.
- Avoid unnecessary decorative elements.
- Do not use generic astronaut or rocket imagery.
- Prefer solid colors, typography, spacing, borders, and structured layouts.

### Suggested palette

| Role             | Color     |
| ---------------- | --------- |
| Main background  | `#F3F0E8` |
| Primary surface  | `#FFFFFF` |
| Primary text     | `#202421` |
| Secondary text   | `#666B64` |
| Primary accent   | `#D85A32` |
| Secondary accent | `#526B55` |
| Borders          | `#D8D5CC` |

These values are starting points. Keep the palette centralized in the global stylesheet.

Do not introduce additional colors without a clear design purpose.

## 4. Application Architecture

Use a modular, page-oriented Astro architecture.

Separate responsibilities into three main layers:

1. **Pages:** Define routes and compose page layouts.
2. **Components:** Provide reusable UI and presentation.
3. **Client-side JavaScript:** Handle interactions, API communication, data retrieval, and UI population.

The client-side JavaScript layer is responsible for implementing all functions that provide data to the frontend.

Cline is responsible for deciding how to organize this JavaScript implementation.

Do not prescribe separate JavaScript files for individual pages or features.

### Architecture overview

```text
                 Astro Pages
                      |
                      v
               UI Components
                      |
                      v
            Client-side JavaScript
                      |
                      v
                API Client
                      |
                      v
               FastAPI Backend
```

### Responsibilities

**Astro pages**

- Define page structure.
- Compose reusable components.
- Provide the required page containers and elements.
- Load the necessary client-side functionality.

**Astro components**

- Render reusable markup.
- Present data passed through props.
- Provide consistent UI elements.
- Avoid implementing backend communication.

**Client-side JavaScript**

- Implement data-providing functions.
- Call the centralized API client.
- Handle page interactions.
- Populate page content.
- Handle loading, empty, and error states.
- Coordinate UI updates.

**API client**

- Centralize backend communication.
- Construct HTTP requests.
- Parse responses.
- Handle request errors.
- Return data to the calling code.

### Data flow

1. Astro renders the initial page structure.
2. Client-side JavaScript initializes when the page loads.
3. The relevant data functions are called.
4. The API client communicates with FastAPI.
5. Returned data is used to populate the page.
6. The UI reflects success, loading, empty, or error states.

Do not introduce a global state-management system unless a concrete requirement justifies it.

## 5. Project Structure

Use the following structure as an architectural baseline.

```text
src/
├── components/
│   ├── navigation/
│   │   └── Navbar.astro
│   │
│   ├── home/
│   │
│   ├── investigations/
│   │
│   ├── details/
│   │
│   └── shared/
│
├── layouts/
│   └── MainLayout.astro
│
├── pages/
│   ├── index.astro
│   ├── investigations/
│   │   ├── index.astro
│   │   └── [id].astro
│   ├── compare.astro
│   ├── dataset.astro
│   ├── agent.astro
│   └── about.astro
│
├── lib/
│   └── api.js
│
└── styles/
    └── global.css
```

This is a suggested organization, not a strict file-generation checklist.

Cline may:

- Add files when necessary.
- Combine related functionality where appropriate.
- Organize client-side JavaScript according to implementation needs.
- Adjust component organization as the application grows.

Do not create unnecessary files or abstractions.

In particular, do not create mandatory page-specific scripts such as `home.js`, `agent.js`, or `investigations.js`.

## 6. Centralized API Client

Create:

`src/lib/api.js`

This is the single client-side module responsible for backend communication.

All frontend API requests must go through this module.

### Responsibilities

- Configure the backend URL.
- Make HTTP requests using native `fetch()`.
- Serialize query parameters.
- Handle JSON request bodies.
- Parse JSON responses.
- Handle HTTP errors.
- Handle network failures.
- Expose reusable asynchronous functions.
- Return parsed response data.

The API client must not:

- Manipulate the DOM.
- Render HTML.
- Contain page-specific logic.
- Store page-specific application state.
- Implement frontend filtering independently of the backend.
- Duplicate backend processing logic.

### Configuration

Use:

`PUBLIC_API_BASE_URL`

Development fallback:

`http://127.0.0.1:8000`

Only expose the public API base URL through the `PUBLIC_` environment variable.

### Required API functions

Implement reusable functions for the documented endpoints:

```js
// Health
getHealth();

// Investigations
getInvestigations((params = {}));
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

Cline is responsible for implementing these functions and any additional data-providing functions required by the frontend.

### API client behavior

Every function must:

- Accept only relevant arguments.
- Construct the correct endpoint and HTTP method.
- Return parsed response data.
- Throw meaningful errors when requests fail.
- Avoid silently returning fabricated or empty data after a failed request.

Use a shared internal request helper to prevent duplicated fetch and error-handling logic.

Example architectural direction:

```js
const API_BASE = import.meta.env.PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
	// Centralized fetch implementation.
}

export async function getHealth() {
	return request("/health");
}
```

This is an architectural example, not a requirement to use this exact implementation.

## 7. Backend API Reference

Base URL:

`http://127.0.0.1:8000`

Interactive documentation:

`http://127.0.0.1:8000/docs`

Alternative documentation:

`http://127.0.0.1:8000/redoc`

### 7.1 Health

**GET `/health`**

Returns the API status and the number of investigation records loaded.

Example:

```json
{
	"status": "ok",
	"records": 11
}
```

### 7.2 Investigation listing

**GET `/investigations`**

Returns a filterable and paginated list of lightweight investigation records.

Supported query parameters:

| Parameter                  | Description                                                |
| -------------------------- | ---------------------------------------------------------- |
| `fuel_type`                | Substring match on fuel type                               |
| `fuel_state`               | Exact match: solid, liquid, gas                            |
| `gravity_condition`        | Exact match: microgravity, normal_gravity, partial_gravity |
| `safety_category`          | Substring match on safety categories                       |
| `oxygen_min`               | Minimum oxygen percentage                                  |
| `oxygen_max`               | Maximum oxygen percentage                                  |
| `pressure_min`             | Minimum pressure in psi                                    |
| `pressure_max`             | Maximum pressure in psi                                    |
| `sample_shape`             | Substring match on sample shape                            |
| `sample_size`              | Substring match on sample size                             |
| `diluents`                 | Substring match on diluent names                           |
| `hardware`                 | Substring match on experiment hardware                     |
| `sensors_and_measurements` | Substring match on sensor types                            |
| `objective`                | Substring match on investigation objective                 |
| `limit`                    | Page size, 1-500, default 50                               |
| `offset`                   | Pagination offset, default 0                               |

Response structure:

```json
{
	"count": 11,
	"offset": 0,
	"limit": 50,
	"results": []
}
```

Each result contains lightweight investigation information, including identity, title, fuel, gravity condition, experimental conditions, and other filterable fields.

The listing endpoint does not return the complete `FieldValue` objects.

### 7.3 Investigation details

**GET `/investigations/{investigation_id}`**

Returns the complete investigation record.

The full record includes the investigation identity and scientific fields.

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

Preserve this structure when presenting scientific metadata.

A nonexistent investigation returns HTTP 404.

### 7.4 Telemetry

**GET `/investigations/{investigation_id}/telemetry`**

Returns telemetry CSV data as JSON.

Optional query parameter:

- `limit`: Maximum rows returned per CSV file.

Response structure:

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

Important behavior:

- PSI-159 returns two telemetry files.
- PSI-60 returns `files: []`.
- Empty CSV cells are converted to `null`.
- Different telemetry files may have different columns.

Do not assume that every investigation has telemetry or that all telemetry files share the same schema.

### 7.5 Comparison

**POST `/compare`**

Compares two or three investigations.

Request body:

```json
{
	"investigation_ids": ["PSI-69", "PSI-98"]
}
```

The backend requires between two and three valid investigation IDs.

Response includes:

- `investigations`
- `aligned_table`
- `what_varied`
- `what_stayed_same`
- `telemetry_summary`

Use the backend's comparison results rather than recreating comparison logic in the frontend.

Possible errors:

- HTTP 422 for an invalid number of IDs.
- HTTP 404 if an investigation does not exist.

### 7.6 Search

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

Use the backend search endpoint. Do not implement a separate search engine in the frontend.

### 7.7 Research agent

**POST `/chat?user={user}`**

Sends a natural-language message to the research agent.

Request body:

```json
{
	"msg": "Search for liquid fuel experiments in microgravity."
}
```

Response:

```json
{
	"status": "success",
	"response": "..."
}
```

The `user` query parameter is required and must contain a valid identifier between 1 and 100 characters.

Use a consistent client-side identifier appropriate to the application's session design.

Do not invent authentication or account functionality.

### 7.8 Reload

**POST `/reload`**

Reloads investigation records from the processed JSON into SQLite.

This is a backend development operation. Do not expose it as a normal user-facing frontend action unless explicitly required.

## 8. Modular Component Guidelines

Components should have one clear responsibility.

### Astro components

Use `.astro` components for:

- Reusable markup.
- Layout sections.
- Cards and data presentation.
- Shared visual states.
- Navigation structure.

Components should receive data through props wherever practical.

Example:

```astro
---
const { investigation } = Astro.props;
---

<article>
  <h2>{investigation.title}</h2>
  <p>{investigation.investigation_id}</p>
</article>
```

Do not place API requests inside reusable presentation components.

### Interactive components

Use vanilla JavaScript for interactive behavior.

Use `data-*` attributes or other stable selectors to connect markup with interaction logic.

Example:

```html
<button data-action="open-menu">Menu</button>
```

Avoid tightly coupling JavaScript to styling classes.

### Component rules

- Keep components focused.
- Avoid deeply nested component hierarchies.
- Prefer composition over inheritance.
- Pass data explicitly.
- Avoid duplicating markup across pages.
- Do not create a component for every trivial HTML element.
- Use shared components when there is a genuine reuse case.
- Keep presentation separate from backend communication.

## 9. Client-side JavaScript Guidelines

Cline is responsible for implementing all client-side JavaScript required by the application.

This includes:

- Calling API functions.
- Retrieving page data.
- Populating page content.
- Handling user interactions.
- Managing temporary UI state.
- Handling loading states.
- Handling empty states.
- Handling errors.
- Updating the interface after user actions.

The implementation should be organized in a way that is appropriate for the actual complexity of the application.

Do not enforce a one-script-per-page architecture.

Do not create unnecessary controller abstractions.

Do not put API request logic directly into individual components.

### JavaScript conventions

- Use ES modules.
- Prefer `const` and `let`.
- Use async/await for asynchronous operations.
- Use meaningful function and variable names.
- Keep functions focused.
- Avoid global variables where practical.
- Avoid duplicating event-handling logic.
- Use stable selectors.
- Clean up event listeners where necessary.

### Astro and browser execution

Astro components are not automatically interactive.

Use browser-side JavaScript for client-side interactions and dynamic data population.

Ensure browser-only code runs in the browser and does not depend on browser globals during server-side rendering.

## 10. Page Requirements

### 10.1 Homepage `/`

The homepage should be the main entry point to the application.

Use:

- A simple horizontal navigation bar.
- A prominent hero section.
- A compact dataset summary.
- A small selection of featured investigations.

#### Navigation

Left:

- CHARIZARD wordmark.

Right:

- Home
- Investigations
- Dataset
- About

Keep navigation compact and visually secondary to the main content.

Use a responsive mobile menu when necessary.

#### Hero

Eyebrow:

`MICROGRAVITY COMBUSTION RESEARCH`

Headline:

`Understanding fire beyond Earth.`

Description:

Explore spacecraft combustion investigations, examine experimental conditions, and compare findings from microgravity research.

#### Main calls to action

**Browse**

Navigate to `/investigations`.

**Use Agent**

Navigate to `/agent`.

These are the two primary actions.

Do not add unnecessary secondary calls to action.

#### Dataset summary

Display:

- 11 investigations.
- 2,241 telemetry rows.
- 10 investigations with telemetry.

These are documented dataset totals, not live measurements.

#### Featured investigations

Display a small selection of actual investigation records retrieved from the backend.

Possible fields:

- Investigation ID.
- Title.
- Acronym.
- Hardware.
- Fuel type.
- Gravity condition.

use dummy data

### 10.2 Investigation explorer `/investigations`

Provide an interface for browsing the available investigation records.

Requirements:

- Fetch investigation records.
- Display investigation information.
- Support pagination.
- Provide relevant filters.
- Provide text search.
- Display loading, empty, and error states.

Use the existing listing and search endpoints.

Multiple filters are combined using AND logic by the backend.

Do not recreate backend filtering logic.

### 10.3 Investigation details `/investigations/[id]`

Display the complete investigation record.

Requirements:

- Retrieve the selected investigation.
- Present scientific metadata.
- Preserve field units.
- Display extraction status.
- Display evidence quotes and locations where available.
- Retrieve telemetry data when available.
- Support multiple telemetry files.
- Handle missing and unavailable fields.

Do not present inferred or unavailable information as verified facts.

### 10.4 Comparison `/compare`

Allow users to select two or three investigations.

Requirements:

- Select investigations.
- Prevent invalid submissions.
- Submit selected IDs to the comparison endpoint.
- Display aligned attributes.
- Display what varied.
- Display what stayed the same.
- Display telemetry summaries.

Use the backend's comparison results.

Do not independently recreate the comparison algorithm.

### 10.5 Dataset `/dataset`

Provide an overview of the available research dataset.

The documented dataset contains:

- 11 investigations.
- 2,241 telemetry rows.
- 11 CSV files.
- 10 investigations with telemetry.
- PSI-60 is metadata-only.

These figures describe the documented dataset.

There is no dedicated aggregate telemetry-statistics endpoint.

If calculating totals dynamically, retrieve telemetry metadata for each investigation and sum the returned `row_count` values.

Do not download every telemetry row just to calculate the total.

### 10.6 Agent `/agent`

Provide a natural-language interface to the existing research agent.

Requirements:

- Accept user messages.
- Submit messages through the centralized API client.
- Display agent responses.
- Display loading states.
- Handle request failures.
- Prevent duplicate submissions while a request is pending.
- Preserve the conversation context supported by the backend.

Do not simulate responses or fabricate research results.

Do not claim capabilities that the backend does not provide.

### 10.7 About `/about`

Provide concise information about:

- The project.
- Its research scope.
- The available dataset.
- Data provenance.
- Data limitations.

Do not invent affiliations, scientific findings, or institutional endorsements.

## 11. Data Integrity

Scientific data must be presented accurately.

Follow these rules:

- Do not fabricate missing values.
- Preserve units.
- Preserve extraction status.
- Preserve evidence references.
- Distinguish verified, extracted, inferred, and unavailable information where those statuses are present.
- Do not interpret unavailable values as zero.
- Do not assume all investigations contain telemetry.
- Do not assume telemetry columns are consistent between files.
- Do not treat CSV values as numeric without validating them.
- Do not claim that data is live or streaming.
- Do not generate scientific conclusions unsupported by the returned data.

Use the original backend field names as the source of truth.

## 12. Error Handling

The backend can return the following HTTP statuses:

| Status | Meaning                    |
| ------ | -------------------------- |
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

The API client should handle common request errors centrally. The UI should decide how to present those errors.

## 13. Styling Guidelines

Use Tailwind CSS v4.

Keep reusable design tokens in the global stylesheet.

Prefer:

- Consistent spacing.
- Clear typographic hierarchy.
- Solid color surfaces.
- Restrained borders.
- Responsive layouts.
- Accessible contrast.
- Simple hover and focus states.

Avoid:

- Arbitrary one-off colors throughout components.
- Excessive shadows.
- Excessive rounded containers.
- Unnecessary animation.
- Gradient backgrounds.
- Neon accents.
- Decorative charts without supporting data.

Do not use styling as a substitute for content hierarchy.

## 14. Accessibility and Responsiveness

- Use semantic HTML.
- Provide accessible labels for form controls.
- Ensure keyboard navigation works.
- Provide visible focus states.
- Use appropriate heading hierarchy.
- Ensure sufficient text contrast.
- Make interactive elements usable on touch devices.
- Ensure tables and data-heavy sections remain usable on smaller screens.
- Do not rely on color alone to communicate scientific data status.

The application must work on desktop, tablet, and mobile screen sizes.

## 15. Development Guidelines

- Keep the frontend modular.
- Use Astro components appropriately.
- Use vanilla JavaScript.
- Centralize backend requests.
- Avoid duplicated logic.
- Avoid unnecessary dependencies.
- Do not modify the FastAPI backend unless explicitly required.
- Do not change existing API contracts.
- Keep configuration separate from implementation.
- Do not introduce abstractions without a concrete use case.
- Inspect existing project files before changing or replacing them.
- Follow the existing repository conventions where they do not conflict with these requirements.

Before adding a dependency, verify whether native browser or Astro functionality already solves the problem.

## 16. Implementation Order

Use the following order as a general implementation guide:

1. Inspect the existing frontend repository.
2. Initialize Astro if it has not already been initialized.
3. Configure Tailwind CSS v4.
4. Establish global styles and design tokens.
5. Implement the main layout.
6. Implement the horizontal navigation.
7. Implement the centralized API client.
8. Implement shared UI components and states.
9. Build the homepage.
10. Build the investigation explorer.
11. Build investigation details.
12. Build the comparison page.
13. Build the agent interface.
14. Build the dataset and about pages.
15. Test API integration, responsive behavior, and error handling.

This is a suggested order. Adjust it when the existing repository or implementation dependencies require a different sequence.

Do not implement all pages as one large component.

## 17. Acceptance Criteria

### Architecture

- Centralized backend communication through `src/lib/api.js`.
- All frontend API requests use the centralized API client.
- Client-side JavaScript owns data retrieval and UI population.
- Astro components remain modular.
- No mandatory page-specific JavaScript files.
- No duplicated API request logic.
- Clear separation between data retrieval, interactions, and presentation.

### Functionality

- Homepage Browse action works.
- Homepage Use Agent action works.
- Investigation listing works.
- Investigation filtering works.
- Investigation search works.
- Pagination works.
- Investigation details load correctly.
- Telemetry files are handled correctly.
- Comparison supports two or three investigations.
- Agent requests use the correct backend endpoint.
- Loading, empty, and error states are implemented.

### Design

- Simple horizontal navigation.
- No sidebar.
- Solid color palette.
- No gradients.
- No neon effects.
- Responsive layout.
- Consistent typography and spacing.
- No generic SaaS dashboard aesthetic.

### Data integrity

- Displayed investigation data comes from the backend or explicitly documented dataset metadata.
- Missing and unavailable values are handled correctly.
- Scientific evidence and extraction statuses are preserved.
- No fabricated statistics.
- No simulated agent responses.
- No unsupported scientific conclusions.

## Final Architectural Principle

Keep the frontend simple and modular.

- **Astro** defines the application structure.
- **Components** provide reusable presentation.
- **Client-side JavaScript** implements data functions, interactions, and UI population.
- **`src/lib/api.js`** centralizes all backend communication.
- **FastAPI** remains responsible for backend processing and data operations.

Cline is responsible for deciding the exact JavaScript organization and implementing the required functionality. Do not impose unnecessary file structures, page-specific scripts, or abstractions.
