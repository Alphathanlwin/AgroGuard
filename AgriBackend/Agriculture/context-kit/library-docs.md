# AgroGuard - Library and Framework Usage Notes

## Selection rule

Use libraries to shorten a demonstrated path, not to increase the architecture surface. Pin versions in the project lockfiles, read the installed version's documentation, and record a decision before adding a new dependency.

The list below is a role map, not a request to install everything.

## Backend Python stack

| Library or tool | Role | MVP guidance |
|---|---|---|
| FastAPI | HTTP API and dependency wiring | Use routers by feature and documented response schemas |
| Pydantic | Request, response, settings, and normalized observation validation | Use explicit ranges, enums, and units |
| Uvicorn | Local ASGI server | Keep a single documented development command |
| SQLAlchemy | Database mapping and queries | Keep models separate from API schemas |
| Alembic | Schema migrations | Every schema change gets a migration |
| Psycopg | PostgreSQL driver | Use the supported async or sync mode consistently |
| GeoAlchemy2 | PostGIS types and spatial queries | Add only when geometry queries are required |
| Shapely | Geometry validation and simple transformations | Validate, do not silently repair user geometry |
| HTTPX | GIS, weather, model, and Telegram HTTP clients | Set timeouts, bounded retries, and safe error mapping |
| pytest | Unit, API, and adapter tests | Prioritize decision and fallback tests |
| Ruff or project-equivalent | Linting and formatting | Use the repository's chosen formatter consistently |
| scikit-learn or a hosted model adapter | Optional crop suitability model | Keep the deterministic scorer as the source of truth for the MVP |
| pandas/geopandas/rasterio | Data preparation or raster work | Use only if a prepared dataset makes the demo stronger; do not build a GIS ETL pipeline during the event |

### Backend usage boundaries

- `FastAPI` knows HTTP, not crop rules.
- `Pydantic` validates inputs, but domain services still enforce business invariants.
- `SQLAlchemy` and `GeoAlchemy2` stay in persistence adapters.
- `HTTPX` calls external services through adapters with timeouts.
- Model libraries return a normalized prediction object with model version and confidence.

## Frontend React stack

| Library or tool | Role | MVP guidance |
|---|---|---|
| React | Component and interaction model | Use components organized by product feature |
| Vite or equivalent React build tool | Fast local development and production bundle | Keep one supported build path |
| React Router | Dashboard, field, simulation, and alerts routes | Keep the main judge flow short |
| Fetch or one chosen HTTP client | API calls | Centralize base URL and error mapping |
| TanStack Query or one chosen server-state library | Caching and invalidation | Choose one; do not mix competing caches |
| MapLibre GL JS, Leaflet, or the approved map SDK | GIS map | Choose one map library and provide a seeded fallback |
| Recharts or a small chart library | Sensor trends and growth comparison | Prefer readable charts over dense analytics |
| Lucide or another consistent icon set | Status and navigation icons | Pair icons with text and accessible labels |
| CSS modules, plain CSS, or one design system | Styling | Keep the visual theme coherent; avoid adding a second UI framework |

### Frontend usage boundaries

- The frontend renders server decisions; it does not duplicate agronomy thresholds.
- Charts receive normalized values and labels from a shared view model.
- Map components own map initialization and cleanup.
- External provider errors become visible degraded states, not blank panels.
- The browser never receives Telegram bot tokens or private provider credentials.

## IoT and Wokwi stack

| Component | Role | Notes |
|---|---|---|
| ESP32 board | Simulated field controller | Use Wokwi for repeatable presentation |
| DHT22 | Temperature and relative humidity | Treat readings as simulated for the demo |
| Potentiometer 1 | Soil moisture control | Map raw value to a demo percentage and label it |
| Potentiometer 2 | Soil pH control | Demonstration estimate only; not a lab sensor |
| Potentiometer 3 | Light level control | Map to a demo percentage |
| LEDs | Healthy, warning, critical, and virtual pump states | Make the physical state match the API status |
| Wokwi VS Code extension | Local simulation and diagram editor | Keep the project files and start instructions in the repository |
| DHTesp and ArduinoJson | Firmware support when used | Pin versions and keep the payload contract aligned with the API |

LoRaWAN and 4G are transport options for a later gateway. They should map to the same normalized observation contract, not create a second domain model.

## Telegram integration

Use the Telegram Bot API through the backend notification adapter. A dedicated Telegram SDK is optional; a small HTTP client is usually enough for the MVP.

Required behavior:

- Store token and chat configuration outside source control.
- Send only safe, human-readable alert content.
- Keep the assessment response independent of Telegram delivery success.
- Record delivery status and a safe error code.
- Test duplicate suppression and failure fallback with a mock client.

## Data and GIS usage notes

- Use a small curated seed dataset for the demo with explicit source and retrieval metadata.
- Prefer a provider with clear usage terms and stable public endpoints.
- Cache provider results by field and retrieval time.
- Do not download large rasters or run expensive geospatial processing during the event unless already prepared.
- Store values in their native unit and convert only at defined boundaries.

## AI usage notes

The MVP should use a transparent suitability scorer with crop requirements and live observations. An optional model or hosted AI call can add narrative explanation, but it must not be the only path to a result.

Every model-related record should carry:

- Model or rules version.
- Input source mode.
- Confidence.
- Evidence factors.
- Fallback behavior.

Do not send private farmer data or secrets to an external model provider.

## Testing tools

- Use pytest for domain and API tests.
- Use a request client for endpoint contract tests.
- Use mocked HTTP responses for GIS, weather, model, and Telegram adapters.
- Use a browser smoke test or a short manual checklist for the React demo.
- Keep one recorded Wokwi scenario and one manual fallback scenario.

## Dependency hygiene

- Do not add a package for a one-line utility.
- Review transitive dependency and license concerns before committing.
- Pin versions after a successful local run.
- Document why each non-obvious dependency exists.
- Remove experiments and unused packages before final presentation.
