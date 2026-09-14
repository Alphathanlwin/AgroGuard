# AgroGuard - Project Overview

## Product identity

| Field | Decision |
|---|---|
| Project title | AgroGuard: GIS + AI + IoT Crop Intelligence |
| Product type | Full-stack decision-support web application with a live hardware simulation |
| Hackathon setting | University of Information Technology Innovative Hackathon 2026 |
| Time constraint | 24-hour MVP; every feature must have a visible demo value |
| Frontend | React.js, with one consistent state-management approach |
| Backend | Python with FastAPI |
| Data platform | PostgreSQL with PostGIS when available; a small seeded fallback dataset for the demo |
| Hardware demo | ESP32, DHT22, three potentiometers, LEDs, and Wokwi simulation |
| Alerts | Telegram Bot API through a controlled notification service |
| Primary demo crop | Choose one export-oriented crop before implementation and keep the story focused |

## One-sentence pitch

AgroGuard turns a farm location and live field readings into an explainable crop-readiness plan, then warns the farmer through Telegram before conditions damage yield or export quality.

## Problem statement

Small and medium farms often have access to weather, soil, and field information in separate places, but not to one practical answer to three questions:

1. What crop is appropriate for this location and season?
2. What should the farmer do today when soil moisture, pH, temperature, or light changes?
3. How can a farmer see the risk early enough to protect quality, water, and income?

The result is over-irrigation, missed heat or disease-risk windows, unsuitable crop selection, and late action. The project must not claim to replace agronomists or laboratory soil tests. It should demonstrate a transparent decision-support loop that combines baseline location data with live sensor readings and clear recommended actions.

## Vision, mission, and values

### Vision

Make location-aware, export-quality crop planning understandable and actionable for every farmer, even when the available connectivity and hardware are limited.

### Mission

Provide one trustworthy view of field conditions: map the field, explain the crop fit, monitor the live environment, recommend the next action, and notify the farmer when a threshold is crossed.

### Core values

- Explainability before impressive-sounding AI.
- Farmer action before dashboard decoration.
- Water, soil, and chemical stewardship.
- Honest uncertainty and visible data provenance.
- Graceful fallback when a sensor, API, or network is unavailable.
- Small, testable changes that do not break existing features.

### Long-term objectives

- Add more crops, regions, seasons, and locally validated agronomy rules.
- Support LoRaWAN and 4G gateways after the hackathon, without changing the field and reading domain model.
- Add satellite or remote-sensing layers and field history.
- Track harvest quality and export compliance evidence.
- Support multiple farms, agronomists, cooperatives, and buyers.

## What the 24-hour MVP must demonstrate

The judge should be able to follow one complete vertical slice:

1. Select a field on a map or choose a seeded location.
2. See soil, pH, temperature, rainfall or climate baseline, and the recommended crop profile.
3. Start or connect the Wokwi ESP32 simulation.
4. Change a potentiometer or DHT22 value and watch the field status update.
5. See the reason for the status and the recommended action.
6. Receive a Telegram warning or critical notification, with duplicate suppression.
7. Compare two growth scenarios across a one-year timeline:
   - IoT-guided field: responds to alerts and follows the recommended actions.
   - Normal-control field: follows a fixed routine and misses changing conditions.
8. Reset the demo and repeat it reliably in under two minutes.

## Core capabilities

| Capability | MVP behavior | Later extension |
|---|---|---|
| GIS field selection | Map click or seeded field returns a stable field id and coordinates | Draw field polygons and import boundaries |
| Location intelligence | Shows baseline soil, pH, climate, elevation, and data source | Raster layers, satellite indices, and historical trends |
| Crop suitability | Scores the selected crop against the available baseline and displays reasons | Multi-crop ranking and economic optimization |
| IoT ingestion | Accepts normalized ESP32 readings from Wokwi or a simulator adapter | LoRaWAN, 4G, device provisioning, and offline queues |
| Crop health status | Healthy, warning, or critical based on explainable rules and optional model score | Calibrated ML model with local validation |
| Recommendation | Gives one prioritized action, expected effect, and confidence | Agronomist review and intervention tracking |
| Telegram alerting | Sends warning/critical alerts and suppresses duplicates | Escalation rules and team channels |
| Growth comparison | Shows stage-by-stage visual growth over 12 months | Crop-specific growth curves and real observations |

## Target users and personas

| Persona | Need | Demo proof |
|---|---|---|
| Smallholder farmer | A simple next action and a reliable warning | Telegram alert plus plain-language recommendation |
| Farm manager | Compare field conditions and decide where to intervene | Map, status cards, and field comparison |
| Agronomist or extension officer | Explain why a crop or treatment is recommended | Evidence panel with source, threshold, and confidence |
| Export buyer or cooperative | See whether production is managed for consistent quality | Export-readiness indicators and intervention history |
| Hackathon judge | Understand the impact in less than three minutes | One guided demo path with visible cause and effect |

## Product boundaries

### In scope for the hackathon

- One primary crop and one representative location or region.
- Seeded baseline data with source and timestamp metadata.
- One GIS map view.
- ESP32/DHT22/potentiometer Wokwi simulation.
- FastAPI endpoints for fields, readings, recommendations, alerts, and simulations.
- React dashboard and growth comparison.
- Telegram warning and critical notification path.
- Rule-based fallback that works without a live ML or external data service.

### Explicitly out of scope for the 24-hour MVP

- Medical, legal, financial, or guaranteed agronomic claims.
- Automatic pesticide or fertilizer prescriptions.
- Full farm ERP, marketplace, payments, or supply-chain management.
- Production-grade IoT fleet management.
- Training a new deep-learning model during the hackathon.
- Supporting every crop, soil type, country, or satellite provider.
- Claiming laboratory-grade pH or nutrient accuracy from a potentiometer.

## Innovation and differentiation

AgroGuard is differentiated by the connected story rather than one isolated feature:

- GIS provides the starting context.
- AI or a transparent suitability scorer turns raw context into a crop decision.
- IoT proves that the recommendation changes when the field changes.
- Telegram turns insight into an action outside the dashboard.
- The two-field growth view makes the value understandable over a year in seconds.

The system must label demo values as simulated, estimated, or externally sourced. It must never present synthetic readings as measured farm truth.

## Hackathon presentation alignment

| Required outline section | AgroGuard evidence |
|---|---|
| Introduction | Team, title, farmer problem, one-sentence pitch |
| Vision, mission, values | Climate-resilient, explainable, farmer-first decision support |
| Innovation | GIS + crop suitability + live ESP32 simulation + Telegram + growth comparison |
| Contribution | Social, educational, environmental, and economic benefits |
| Statistics and survey analysis | Use cited public agriculture data plus a small clearly labeled user survey; do not invent numbers |
| Competitive analysis | Compare static weather apps, soil dashboards, and generic farm management tools |
| Realistic implementation | FastAPI modular monolith, React dashboard, PostGIS-ready model, Wokwi adapter, fallback path |
| Target audience | Farmer, farm manager, agronomist, cooperative, export buyer |
| Business potential | Freemium field monitoring, cooperative plans, agronomist services, sensor bundles |
| Demonstration | Location -> recommendation -> sensor change -> alert -> one-year growth comparison |
| Conclusion | Expected water/yield/decision benefits, limitations, and next steps |

## Evidence and statistics policy

- Cite every external statistic with the organization, title, date, and URL in presentation notes.
- Separate global, national, and local figures.
- Record survey sample size, audience, questions, collection date, and limitations.
- Never use a convenient percentage without a source.
- If evidence is not available in time, say "data collection in progress" and use a qualitative finding instead of fabricating precision.

## Success criteria

The MVP is successful when:

- A judge can complete the full demo without editing files or restarting services manually.
- Every recommendation shows the input evidence and rule or model reason.
- A dry-soil or heat-stress simulation produces the expected status, pump/LED response, and Telegram alert.
- The system remains usable if GIS, ML, or Telegram is unavailable by showing a clear degraded state.
- A new crop, sensor field, or alert rule can be added through a documented change path without breaking existing behavior.

## Context-kit rule

These files are product and engineering context only. They describe decisions, contracts, and acceptance criteria. They must not be treated as a request to generate production source code automatically.
