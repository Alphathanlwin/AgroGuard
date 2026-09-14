# AgroGuard - API Standards

## API purpose

The API supports the field decision loop: discover a field, load its baseline context, ingest observations, assess crop conditions, deliver alerts, and replay the demo. The API is a contract between React, the ESP32/Wokwi adapter, and the backend domain services.

No endpoint should expose database implementation details or require the frontend to understand provider-specific GIS, weather, model, or Telegram formats.

## General rules

| Rule | Standard |
|---|---|
| Protocol | HTTPS in deployment; HTTP is acceptable for local development |
| Base path | `/api/v1` |
| Format | JSON with UTF-8 encoding |
| Naming | Plural, kebab-case resource names; camelCase JSON fields |
| Time | ISO 8601 timestamps in UTC |
| Coordinates | WGS84 latitude/longitude; latitude first in JSON fields |
| Units | Celsius, percent, pH units, millimeters for rainfall, hectares for area |
| Authentication | Protected routes use a bearer token when multi-user access is enabled; demo routes may use a clearly labeled demo mode |
| Content type | `application/json` for JSON bodies |
| Pagination | Cursor or page/limit for collections; never return unbounded histories |
| Versioning | Additive changes within `/v1`; breaking changes require a new version |

## Resource model

| Resource | Responsibility |
|---|---|
| `fields` | Field identity, geometry, owner/team, and selected crop |
| `field-context` | Soil, pH, climate, elevation, and source metadata for a field |
| `crops` | Crop profiles and requirement ranges |
| `observations` | Normalized device or manual sensor readings |
| `assessments` | Current crop status, suitability score, evidence, and recommendation |
| `alerts` | Risk events and lifecycle state |
| `notifications` | Telegram delivery records and attempts |
| `growth-simulations` | One-year comparison scenarios and timeline events |
| `devices` | Sensor identity, transport, last-seen time, and health |
| `demo-scenarios` | Repeatable seeded scenarios and reset controls |

## Endpoint catalog

The following is the MVP contract. A route may be deferred, but the naming and response intent should remain stable.

| Method | Path | Purpose | Success |
|---|---|---|---|
| GET | `/fields` | List accessible fields with current status | 200 |
| POST | `/fields` | Create a field from coordinates or polygon | 201 |
| GET | `/fields/{fieldId}` | Load field detail | 200 |
| GET | `/fields/{fieldId}/context` | Load baseline GIS/soil/climate context | 200 |
| POST | `/fields/{fieldId}/context/refresh` | Refresh optional provider data | 202 or 200 |
| GET | `/crops` | List crop profiles | 200 |
| GET | `/crops/{cropId}` | Load crop requirements and provenance | 200 |
| POST | `/fields/{fieldId}/crop-selection` | Select the crop for an assessment | 200 |
| POST | `/observations` | Ingest one normalized reading | 202 or 201 |
| GET | `/fields/{fieldId}/observations` | Read a bounded observation history | 200 |
| GET | `/fields/{fieldId}/assessment` | Get current status, evidence, and action | 200 |
| POST | `/fields/{fieldId}/assessment/recompute` | Recompute after a manual or device reading | 200 |
| GET | `/alerts` | List alert events with filters | 200 |
| POST | `/alerts/{alertId}/acknowledge` | Mark an alert acknowledged | 200 |
| GET | `/notifications` | Read notification delivery status | 200 |
| GET | `/fields/{fieldId}/growth-simulations` | Load available scenario comparisons | 200 |
| POST | `/fields/{fieldId}/growth-simulations/replay` | Start or reset a deterministic replay | 202 or 200 |
| POST | `/demo-scenarios/{scenarioId}/reset` | Reset only demo data and clock | 200 |
| GET | `/health` | Liveness and dependency summary | 200 or 503 |

The device ingestion route may be separated under `/api/v1/device-ingest` when a gateway needs a different authentication mechanism. Keep the normalized observation contract identical.

## Request and response conventions

### Resource response

Responses should contain the resource fields, stable ids, timestamps, and a `dataQuality` object when the value may be simulated, stale, estimated, or provider-derived.

### Collection response

Collections should provide items plus pagination metadata. Filters should be explicit and composable: field id, status, crop id, time range, device id, and source mode.

### Assessment response

An assessment must expose:

- `status`: `healthy`, `warning`, or `critical`.
- `healthScore`: an integer from 0 to 100 only when the score is meaningful.
- `primaryRisk`: the most important limiting factor.
- `recommendation`: one prioritized action in plain language.
- `evidence`: observed value, target range, source, and freshness.
- `confidence`: `high`, `medium`, `low`, or `unknown`.
- `mode`: `live`, `simulated`, `seeded`, `replay`, or `degraded`.
- `updatedAt`: the assessment timestamp.

Do not return a naked score without the reason and data-quality context.

## Validation rules

Validate before business logic:

- Latitude is between -90 and 90; longitude is between -180 and 180.
- Field area is positive and bounded for the deployment context.
- Temperature, humidity, moisture, pH, light, and rainfall are within plausible physical ranges.
- A sensor reading contains a device or source id and timestamp.
- The timestamp is not unreasonably far in the future.
- The crop id and field id exist and are accessible to the caller.
- The same observation event is not processed twice.
- Manual/demo values are explicitly marked as simulated.

Validation should distinguish `invalid_input`, `out_of_range`, `stale_data`, and `duplicate_event`.

## Status codes

| Code | Use |
|---|---|
| 200 | Successful read, update, assessment, or acknowledgement |
| 201 | New field, device, or resource created |
| 202 | Accepted for refresh, replay, or asynchronous notification work |
| 204 | Successful action with no response body |
| 400 | Malformed or semantically invalid request |
| 401 | Missing or invalid authentication |
| 403 | Authenticated but not allowed for the field or action |
| 404 | Field, crop, device, or alert not found |
| 409 | Duplicate event or conflicting state transition |
| 422 | Valid JSON but failed domain validation |
| 429 | Rate limit exceeded |
| 500 | Unexpected server failure |
| 502/503 | Optional provider or dependency unavailable |

## Error contract

All errors should include:

- A stable machine-readable `code`.
- A short human-readable `message`.
- The HTTP `status`.
- A UTC `timestamp`.
- A request or correlation id.
- Field-level details only when safe and useful.

Never expose stack traces, SQL, provider tokens, or Telegram credentials to the client.

## Alerting contract

The assessment service creates an alert intent when a status crosses a configured threshold or a critical condition persists. The notification service applies:

- Alert fingerprint: field + crop + risk + severity.
- Cooldown window to prevent repeated messages.
- Escalation only when severity increases or the cooldown expires.
- Idempotent delivery key.
- Delivery status: pending, sent, failed, suppressed, or acknowledged.

Telegram delivery must not block the primary assessment response. The API returns the assessment and notification status separately.

## Query and filtering rules

- Use query parameters for filters, not ad hoc path segments.
- Use ISO dates and explicit timezone handling.
- Limit observation history and allow a maximum time window.
- Return stable sort order, normally newest first for observations and alerts.
- Reject unknown filter names rather than silently ignoring them.

## Compatibility rules

- Add fields without renaming existing fields.
- Treat unknown response fields as forward-compatible on the React side.
- Do not make a previously optional field required without a version change.
- Record a contract change in the progress tracker and test it before merging.
- Keep demo mode available while live integrations evolve.
