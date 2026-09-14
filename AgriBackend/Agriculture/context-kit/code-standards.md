# AgroGuard - Code and Change Standards

## Purpose

These rules protect the project from feature drift during a 24-hour hackathon. They are implementation constraints, not source code. New features must preserve the decision loop, explainability, and the repeatable demo path.

## General principles

- Prefer a small vertical slice that works end to end over a broad set of disconnected screens.
- Keep domain decisions deterministic and testable.
- Make data provenance and freshness visible.
- Fail gracefully at integration boundaries.
- Avoid hidden global state and magic thresholds.
- Do not mix simulated values with live values without labeling the mode.
- Keep public contracts stable and document changes before implementation.
- Do not add a dependency unless its role, owner, fallback, and removal cost are understood.

## Backend Python and FastAPI standards

### Structure

Organize by feature with clear separation between API, application services, domain rules, adapters, and persistence. Recommended feature areas are:

- `fields`
- `crops`
- `observations`
- `assessments`
- `alerts`
- `notifications`
- `growth_simulations`
- `demo`
- `common`

Do not create one giant router, one giant service, or a catch-all utilities module.

### Typing and validation

- Type every public function, service boundary, and adapter result.
- Use request and response schemas that are separate from database entities.
- Validate values and units at the API boundary.
- Validate domain invariants again in the service or domain layer when a use case can bypass HTTP.
- Make nullable fields intentional; do not use null to mean unknown, stale, or not applicable without documentation.
- Use enums for finite states such as severity, source mode, and lifecycle status.

### FastAPI boundary rules

- Routers parse requests, apply access checks, call a service, and map results to responses.
- Routers must not contain SQL, crop thresholds, Telegram calls, or provider-specific transformations.
- Return documented status codes and stable error codes.
- Use request correlation ids in logs.
- Apply timeouts to outbound calls.
- Never return stack traces, credentials, SQL, or raw provider errors.

### Service and domain rules

- Put crop suitability, risk classification, alert fingerprinting, and recommendation priority in pure domain functions or small domain services.
- Store thresholds in versioned crop requirement data, not scattered literals.
- An assessment must be reproducible from its input observation, field context snapshot, crop profile version, and decision mode.
- A model score is advisory. The system must provide a deterministic fallback and an explanation.
- The recommendation should identify one next action and any safety limitation.

### Database and transaction rules

- Repositories perform data access only.
- Services own transaction boundaries for multi-record changes.
- Use migrations for schema changes.
- Never update observations, assessments, alerts, and notifications in a way that can create duplicate events when a request is retried.
- Use unique event or delivery keys for idempotency.
- Avoid N+1 queries on dashboard endpoints.
- Bound all history queries by field and time range.

## IoT and ingestion standards

- Normalize every device reading to the internal units before it reaches decision logic.
- Require device id, event id, observed time, source mode, and field association.
- Treat potentiometer-derived soil moisture, pH, and light as demo estimates.
- Reject impossible values and mark suspect values rather than silently clamping them.
- Detect stale devices using last-seen time.
- Do not let a malformed device message crash the ingestion process.
- Log a safe reason for rejected readings.

## GIS standards

- Use WGS84 latitude/longitude at API boundaries unless a route explicitly documents another CRS.
- Keep coordinate order consistent: latitude then longitude in JSON; follow provider-specific order only inside an adapter.
- Validate polygon closure, size, and self-intersection when polygons are accepted.
- Never calculate distance or area from rounded display coordinates.
- Include source, retrieval time, resolution, and quality for location-derived values.
- Use approximate or masked coordinates in public demo views when exact farm privacy matters.

## AI and agronomy standards

- Label every output as rule-based, model-based, provider-derived, seeded, or simulated.
- Show the top factors that helped and hurt suitability.
- Store model or rule version with every assessment.
- Include confidence and freshness; do not show false precision.
- Never claim that a score guarantees yield, disease absence, export approval, or profit.
- Do not auto-prescribe pesticides, fertilizer amounts, or other high-risk treatment without qualified review and source evidence.
- Use a rule-based fallback when the model or external service fails.
- New crop thresholds require a source reference or an explicit demo-assumption note.

## React.js standards

### Component design

- Prefer small components with one visual or interaction responsibility.
- Keep domain calculations in shared logic or API responses, not duplicated across screens.
- Use stable keys and avoid index keys for dynamic sensor, alert, or timeline rows.
- Keep map lifecycle and cleanup inside a dedicated map component.
- Keep growth visualization separate from the field status cards so each can be tested independently.

### State and data fetching

- Choose one server-state approach and use it consistently.
- Keep URL, selected field, crop, and replay mode shareable when practical.
- Invalidate or refresh assessment data after a new observation.
- Do not optimistic-update an alert as sent before the notification service confirms it.
- Display loading, stale, degraded, empty, and error states distinctly.
- Do not store secrets in browser storage.

### UI safety

- Render user or provider text as text, not unsafe HTML.
- Disable duplicate submit and reset actions while a request is in flight.
- Confirm destructive actions, and never allow demo reset to affect non-demo data.
- Keep alert severity color paired with text and icon; never rely on color alone.
- Make keyboard focus, labels, contrast, and screen-reader names part of acceptance testing.

## Naming and formatting

| Item | Standard |
|---|---|
| Python modules | lowercase snake case |
| Python classes | PascalCase |
| Python functions/variables | snake_case |
| React components | PascalCase |
| React hooks | `use` prefix and descriptive name |
| API resources | plural kebab-case |
| JSON fields | camelCase |
| Database tables/columns | lowercase snake case |
| Status values | documented lowercase strings at API boundary |
| Time fields | suffix with `At` in API, explicit timestamp type in database |

Use the repository formatter and linter configured by the project. Do not reformat unrelated files in a feature commit.

## Testing standards

Every feature should have the smallest useful test set:

- Domain tests for thresholds, scoring, severity, and alert deduplication.
- API contract tests for validation, status codes, and response shape.
- Persistence tests for migrations, unique keys, and critical queries.
- Adapter tests using mocked GIS, weather, model, and Telegram responses.
- One end-to-end smoke path: field selection -> observation -> assessment -> alert state.
- One UI smoke path for the judge demo.

Required edge cases:

- No live GIS provider.
- No ML/model provider.
- Stale sensor.
- Duplicate observation.
- Telegram failure.
- pH or sensor value outside range.
- Two repeated critical readings inside the cooldown window.
- Demo reset while a request is pending.

## Logging and observability

- Log structured event names, ids, status, duration, and source mode.
- Use warning level for degraded integrations and error level for failed use cases.
- Do not log secrets, tokens, full authorization headers, or sensitive exact locations.
- Include correlation id from API request through notification delivery where possible.
- Expose health status for the API, database, and optional integrations.

## Git and feature-change safety

- Work on a named feature branch such as `Backend` or `feature/alerts`.
- Keep commits small and describe the behavior changed.
- Do not force-push shared branches.
- Before adding a feature, update the relevant API, schema, UI, and progress context if the contract changes.
- Before merging, run formatting, tests, migration validation, and the demo smoke path.
- Use feature flags for incomplete integrations.
- Preserve a working demo seed and a known-good replay scenario.
- If a change cannot be tested in the remaining hackathon time, reduce its scope or defer it.

## Definition of done

A feature is done only when:

1. Its user outcome and failure behavior are documented.
2. Its API and data changes are consistent with the context kit.
3. Its domain rule has a test.
4. Its UI has loading, error, empty, and degraded states when relevant.
5. It does not break the resettable demo path.
6. It does not introduce secrets or unbounded external calls.
7. The team can explain what is measured, simulated, estimated, and future work.
