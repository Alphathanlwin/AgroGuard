# AgroGuard - 24-Hour Build Plan

## Delivery rule

Build one complete story that can be reset and replayed. Do not start with every possible crop, sensor, provider, or admin feature. The judge should see a reliable cause-and-effect chain before seeing optional breadth.

## Scope tiers

### Must have

- React dashboard with field selection and current status.
- FastAPI service with fields, context, observations, assessment, alerts, and simulation endpoints.
- One seeded location and one primary crop profile.
- Explainable suitability and risk rules with confidence and data mode.
- Wokwi ESP32 with DHT22, three potentiometers, LEDs, and virtual pump indicator.
- Reading ingestion or a simulator adapter.
- Telegram warning/critical path, with credentials kept out of source control.
- IoT-guided versus normal-control one-year growth comparison.
- Seeded fallback when GIS, model, weather, or Telegram is unavailable.
- Repeatable demo reset.

### Should have

- PostGIS field point or polygon.
- Context provenance panel.
- Sensor trend chart.
- Alert history and acknowledgement.
- Three replay scenarios: healthy, dry soil, and heat stress.
- Basic authentication or a clear demo mode boundary.

### If time remains

- Crop comparison for a second crop.
- Weather forecast overlay.
- Satellite or vegetation-index placeholder with source label.
- Device health card and stale sensor warning.
- Export-readiness checklist.
- Lightweight survey results panel.

### Out of scope

- Full LoRaWAN/4G fleet operations.
- Training a deep model from scratch.
- Pesticide or fertilizer prescriptions.
- Payment, marketplace, or supply-chain modules.
- Multi-tenant billing.
- Production-grade observability platform.

## Hour-by-hour schedule

Adjust for team size, but preserve the checkpoints.

| Time | Focus | Exit condition |
|---|---|---|
| 00:00-01:00 | Align on crop, location, personas, pitch, and demo scenario | One-page decision sheet and named MVP owner |
| 01:00-03:00 | Create React/FastAPI structure, environment settings, database connection, and seed plan | Backend health route and frontend shell open |
| 03:00-05:00 | Model field, crop profile, context snapshot, device, and observation | Seeded field and crop can be loaded |
| 05:00-07:00 | Implement normalized observation and deterministic assessment contract | A dry-soil input returns the expected critical result |
| 07:00-09:00 | Connect Wokwi/ESP32 payload or manual simulator adapter | Sensor change reaches backend or documented adapter boundary |
| 09:00-11:00 | Add GIS map and context panel with seeded fallback | Clicking the field shows location evidence and freshness |
| 11:00-13:00 | Build dashboard status, recommendation, and sensor trend views | Judge can understand the current state without narration |
| 13:00-15:00 | Add alert lifecycle, Telegram adapter, cooldown, and mock fallback | One new critical event produces one safe notification |
| 15:00-17:00 | Build the two-field growth comparison and replay controls | One-year timeline is visually clear and repeatable |
| 17:00-19:00 | Integrate the full vertical slice and improve visual hierarchy | Location -> reading -> assessment -> alert -> comparison works |
| 19:00-21:00 | Add error, loading, stale, empty, and degraded states | Provider and Telegram failure do not blank the dashboard |
| 21:00-22:30 | Run tests, seed reset, and presentation rehearsal | Demo can be reset and replayed twice |
| 22:30-23:30 | Prepare slides, evidence sources, competitor comparison, and business case | Hackathon outline sections are covered |
| 23:30-24:00 | Freeze scope, tag demo build, back up, and rehearse final narration | No risky feature work remains |

## Vertical slices

### Slice 1: location to crop plan

Input: seeded field or map selection.

Output: field context, selected crop, suitability score, evidence, provenance, and limitation note.

Acceptance: no external provider is required for the seeded path.

### Slice 2: sensor to decision

Input: DHT22 and potentiometer reading from Wokwi or manual scenario.

Output: normalized observation, updated assessment, status LED/pump state, and UI update.

Acceptance: dry soil and heat stress produce deterministic expected results.

### Slice 3: decision to alert

Input: a status crossing a warning or critical threshold.

Output: one alert record, one Telegram attempt or safe degraded status, and alert history.

Acceptance: repeated readings do not spam Telegram.

### Slice 4: intervention to growth story

Input: replay clock and scenario.

Output: IoT-guided and normal-control growth stages across twelve months.

Acceptance: both scenarios are labeled illustrative and the guided scenario visibly responds to interventions.

## Demo scenarios

### Scenario A: healthy baseline

- Moderate temperature and humidity.
- Soil moisture, pH, and light within the crop range.
- Status is healthy.
- Green LED is active; pump is off.

### Scenario B: dry soil

- Lower soil moisture with other values unchanged.
- Status becomes critical or warning according to the documented threshold.
- Virtual pump activates.
- Critical Telegram alert is generated once.
- Guided growth path records irrigation; normal-control path misses it.

### Scenario C: heat stress or poor pH

- Raise temperature or move pH outside the target range.
- Status and recommendation identify the primary factor.
- Warning/critical LED changes accordingly.
- Telegram message includes action and evidence.

## Presentation runbook

1. Introduce the team and farmer problem.
2. Select a field on the map.
3. Explain the baseline context and crop fit.
4. Start the Wokwi simulation.
5. Turn the soil potentiometer down.
6. Show the updated evidence and recommendation.
7. Show the LED/pump response and Telegram alert.
8. Open the one-year guided versus normal-control growth comparison.
9. Explain contribution, business potential, limitations, and next steps.

Keep a screen recording or screenshots of the full path in case a live provider fails.

## Risk and fallback matrix

| Risk | Early signal | Fallback |
|---|---|---|
| GIS provider key or quota fails | Map or context call errors | Seeded field and cached context with source label |
| Model call fails | Timeout or invalid response | Deterministic suitability scorer |
| Telegram fails | Delivery error | In-app alert, delivery-failed status, and screenshot of prepared message |
| Wokwi compile or transport fails | No new reading | Manual scenario controls with the same observation contract |
| Database setup fails | Migration or connection error | Use a documented seeded fixture for the presentation path; do not switch dialects mid-build or pretend SQLite provides PostGIS behavior |
| UI integration slips | Components are disconnected late | Use one dashboard route and harden the main vertical slice |
| Scope expands | New crop/provider/admin request | Add to future work and protect the must-have list |

## Change-control rule

Before adding a feature, answer:

1. Which judge-visible outcome does it improve?
2. Which context file and contract does it affect?
3. What is its fallback if the integration fails?
4. How will it be tested before the next checkpoint?
5. What existing demo path could it break?

If the answers are unclear, defer the feature.

## Final checklist

- [ ] Fresh setup instructions work on the demo machine.
- [ ] Environment secrets are excluded from version control.
- [ ] Seed/reset can be run without deleting non-demo data.
- [ ] Healthy, dry-soil, and heat/pH scenarios are repeatable.
- [ ] API and database changes are migrated and tested.
- [ ] Loading, error, stale, empty, and degraded UI states are visible.
- [ ] Telegram token is not in screenshots, logs, or source control.
- [ ] Evidence sources and survey limitations are ready for the presentation.
- [ ] The team can explain what is real, simulated, estimated, and future work.
