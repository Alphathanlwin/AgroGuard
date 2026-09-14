# AgroGuard - Progress Tracker

## How to use this file

Update this tracker after each meaningful work session. Every item should be marked `Not started`, `In progress`, `Blocked`, or `Done`, with a short evidence note. Do not mark an item done because a file exists; mark it done when the acceptance behavior works.

## Project decisions

| Decision | Current value | Owner | Verified |
|---|---|---|---|
| Primary crop | Choose one export-oriented crop before implementation | Team | Not verified |
| Demo location | One seeded region and field | Team | Not verified |
| Frontend | React.js | Team | Not verified |
| Backend | Python + FastAPI | Team | Not verified |
| Database | PostgreSQL + PostGIS-ready model | Team | Not verified |
| IoT | ESP32 + DHT22 + three potentiometers + LEDs in Wokwi | Team | Not verified |
| Alert channel | Telegram Bot API with in-app fallback | Team | Not verified |
| AI behavior | Explainable scorer with deterministic fallback | Team | Not verified |
| Growth demo | IoT-guided field versus normal-control field over one year | Team | Not verified |

## Phase 0 - Story and evidence

- [ ] Not started - Project title, one-sentence pitch, and problem statement approved.
- [ ] Not started - Primary crop and representative location selected.
- [ ] Not started - Farmer, farm manager, agronomist, and judge personas reviewed.
- [ ] Not started - Public statistics have source, date, and URL.
- [ ] Not started - Survey method, sample, questions, and limitations documented.
- [ ] Not started - Existing solutions and competitor comparison prepared.
- [ ] Not started - Business model and future expansion story prepared.

## Phase 1 - Foundation

- [ ] Not started - React application opens with the AgroGuard shell.
- [ ] Not started - FastAPI health route responds.
- [ ] Not started - Environment configuration separates secrets from source.
- [ ] Not started - Database migration and seed process are repeatable.
- [ ] Not started - Demo mode and degraded mode are visible in the UI.
- [ ] Not started - Git branch and commit workflow are agreed.

## Phase 2 - Field and GIS

- [ ] Not started - Seeded field has stable id, coordinate, region label, and demo flag.
- [ ] Not started - Map displays the seeded field.
- [ ] Not started - Field context shows soil, pH, climate, elevation, source, and freshness.
- [ ] Not started - Context provider failure falls back to seeded data with a visible label.
- [ ] Not started - Coordinate and geometry validation is tested.

## Phase 3 - Crop intelligence

- [ ] Not started - One crop profile and requirement ranges are stored as versioned data.
- [ ] Not started - Suitability result includes score, evidence, confidence, and source mode.
- [ ] Not started - Out-of-range factors are ranked and explained.
- [ ] Not started - Deterministic fallback works without a model or external provider.
- [ ] Not started - No output claims guaranteed yield, disease absence, or export approval.

## Phase 4 - IoT and observations

- [ ] Not started - Wokwi diagram contains ESP32, DHT22, potentiometers, LEDs, and virtual pump.
- [ ] Not started - Normalized observation contract is documented.
- [ ] Not started - Temperature and humidity reading path works.
- [ ] Not started - Soil moisture, pH, and light demo controls work.
- [ ] Not started - Duplicate, stale, impossible, and simulated readings are handled.
- [ ] Not started - Manual scenario fallback produces the same observation shape.

## Phase 5 - Assessments and recommendations

- [ ] Not started - Healthy scenario displays expected status.
- [ ] Not started - Dry-soil scenario displays expected risk and irrigation action.
- [ ] Not started - Heat-stress or poor-pH scenario displays expected risk and action.
- [ ] Not started - Assessment stores rule/model version, evidence, and data quality.
- [ ] Not started - UI refreshes after a new valid observation.

## Phase 6 - Alerts and Telegram

- [ ] Not started - Warning and critical thresholds are documented.
- [ ] Not started - Alert fingerprint and cooldown prevent spam.
- [ ] Not started - Telegram token is loaded only from secret configuration.
- [ ] Not started - Successful Telegram delivery is recorded.
- [ ] Not started - Telegram failure leaves an in-app alert and visible degraded status.
- [ ] Not started - Alert acknowledgement and resolution are safe state transitions.

## Phase 7 - Growth comparison

- [ ] Not started - Twelve-month timeline has named growth stages.
- [ ] Not started - IoT-guided scenario responds to interventions.
- [ ] Not started - Normal-control scenario misses selected interventions.
- [ ] Not started - Both scenarios are labeled illustrative.
- [ ] Not started - Replay/reset produces the same result twice.

## Phase 8 - UI and judging experience

- [ ] Not started - Dashboard puts map, status, action, alerts, and trend in one flow.
- [ ] Not started - Loading, empty, error, stale, and degraded states are designed.
- [ ] Not started - Status uses text, icon, and color.
- [ ] Not started - Map, charts, controls, and tables are keyboard and screen-reader usable.
- [ ] Not started - The full demo can be completed without editing files.
- [ ] Not started - Screenshots or recording exist as a provider-failure backup.

## Phase 9 - Quality and handoff

- [ ] Not started - Domain decision tests pass.
- [ ] Not started - API contract tests pass.
- [ ] Not started - Migration tests pass on empty and seeded databases.
- [ ] Not started - Adapter tests cover GIS, model, weather, and Telegram failure.
- [ ] Not started - React smoke path passes.
- [ ] Not started - Fresh setup instructions pass on the presentation machine.
- [ ] Not started - No secrets, debug dumps, or private coordinates are committed.
- [ ] Not started - Final branch is tagged or backed up.

## Acceptance gates

### Gate A - Architecture ready

The field, crop, observation, assessment, alert, notification, and simulation contracts are agreed before building screens.

### Gate B - Vertical slice ready

One field can move from location context to crop recommendation to a new sensor observation and updated status.

### Gate C - Alert ready

A critical scenario produces one alert, one Telegram attempt or safe fallback, and no duplicate spam.

### Gate D - Presentation ready

The full judge flow can be reset and replayed twice in a row.

## Session log

| Date/time | What changed | Evidence | Next step | Owner |
|---|---|---|---|---|
| 2026-07-22 | Agriculture context kit prepared from hackathon outline | Nine context files rewritten | Select crop, field, and owners | Team |
|  |  |  |  |  |
|  |  |  |  |  |

## Blocker log

| Date | Blocker | Impact | Temporary fallback | Resolution |
|---|---|---|---|---|
|  |  |  |  |  |
