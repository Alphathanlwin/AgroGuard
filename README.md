# AgroGuard

Full-stack crop intelligence platform that turns soil/weather data and live IoT sensor readings into actionable farming decisions for Myanmar agriculture.

## Overview

Myanmar farmers lack access to data-driven crop management tools. AgroGuard combines ML-based crop recommendation, disease detection, and sensor-driven field assessment into a single platform with bilingual (English/Burmese) support.

The system ingests sensor data from IoT devices (or simulated sources), scores field conditions against crop requirements, detects plant diseases from leaf images, and streams AI-generated advice through an LLM-powered chat interface.

## Key Features

- **Crop Suggestion** — ML model (RandomForest) recommends crops based on soil pH, rainfall, and temperature, with market value estimates from regional agricultural data
- **Disease Detection** — ResNet18-based image classifier identifies 11 plant diseases from leaf photos, with LLM-generated treatment advice in English or Burmese
- **Field Assessment** — Rule-based scoring engine compares sensor readings against crop requirements, generates health scores, risk factors, and recommendations
- **IoT Sensor Simulation** — Real-time random-walk simulation of soil moisture, pH, and light sensors with Wokwi hardware integration via LoRaWAN/4G
- **Growth Simulation** — 12-month crop growth comparison between IoT-guided and unmanaged scenarios
- **AI Chat** — SSE-streamed LLM conversations for agricultural advice, with fallback responses when no API key is configured
- **NDVI Analysis** — Satellite vegetation index time-series for 18 Myanmar regions with rainfall correlation
- **Telegram Alerting** — Automated notifications when field assessments reach warning or critical status
- **Bilingual UI** — Full English/Burmese translations across all frontend components

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 19, Vite 8, Tailwind CSS 4, Chart.js 4, React Router 7, Lucide Icons |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy 2 (async), Alembic, Pydantic Settings |
| **Database** | PostgreSQL (asyncpg), GeoAlchemy2 |
| **AI/ML** | scikit-learn (RandomForest), PyTorch (ResNet18), joblib, pandas |
| **External APIs** | OpenAI-compatible LLM (default: Ollama), OpenWeatherMap, Telegram Bot API |
| **Dev Tooling** | concurrently, ruff, pytest, Vite dev proxy |

## Architecture

```
┌─────────────┐     ┌──────────────────────────────────────────┐
│   React UI  │────▶│              FastAPI Backend               │
│  (Vite dev) │◀────│                                          │
└─────────────┘     │  ┌──────────┐  ┌───────────┐  ┌────────┐ │
                    │  │ Endpoints │→ │ Services  │→ │  DB    │ │
                    │  │ (21)      │  │ (9)       │  │ (14    │ │
                    │  └──────────┘  └─────┬─────┘  │ tables)│ │
                    │                      │         └────────┘ │
                    │              ┌───────┴───────┐            │
                    │              │               │            │
                    │         ┌────▼───┐    ┌──────▼─────┐     │
                    │         │   ML   │    │  External  │     │
                    │         │ Models │    │  Services  │     │
                    │         └────────┘    └────────────┘     │
                    └──────────────────────────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
               ┌────▼────┐    ┌─────▼─────┐   ┌─────▼─────┐
               │ OpenWeather│  │ Telegram  │   │  LLM      │
               │   Map API  │  │ Bot API   │   │ (Ollama)  │
               └───────────┘  └───────────┘   └───────────┘
```

### Data Flow: Sensor Reading → Assessment → Alert

1. IoT device (or simulator) sends sensor observation via `POST /observations/ingest`
2. `observation.py` validates readings against plausible ranges, deduplicates by event_id
3. `assessment.py` compares readings against crop requirements per factor
4. Scoring engine computes health score: `100 - Σ(gap × criticality_weight)`
5. If status is warning/critical, `alerting.py` creates alert with 1-hour cooldown
6. `telegram.py` sends notification to configured chat

### Data Flow: Disease Detection

1. User uploads leaf image (JPG/PNG/WEBP, max 8MB)
2. `disease_detection.py` preprocesses image (Resize → CenterCrop → Normalize)
3. ResNet18 forward pass → softmax → top prediction
4. Class name parsed from "Plant___Disease" format
5. `llm.py` generates treatment and prevention advice via LLM
6. Response returned in user's language (EN/MY)

## Project Structure

```
AgroGuard/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # 21 endpoint modules
│   │   ├── core/config.py       # Pydantic settings (env-driven)
│   │   ├── db/models/           # 14 SQLAlchemy models
│   │   ├── ml/                  # ML inference + training
│   │   ├── schemas/             # 20 Pydantic response models
│   │   └── services/            # 9 business logic modules
│   ├── migrations/              # 6 Alembic migrations
│   ├── tests/                   # pytest test suite
│   └── pyproject.toml           # Dependencies + ruff/pytest config
├── frontend/
│   └── src/
│       ├── components/          # 9 React components
│       ├── contexts/            # Auth + Language contexts
│       ├── layouts/             # Dashboard layout
│       └── pages/               # Disease detection page
├── docs/                        # Architecture + API standards
├── scripts/                     # Dev startup script
└── package.json                 # concurrently runner
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL
- (Optional) Ollama for local LLM

### Installation

```bash
# Clone
git clone https://github.com/your-username/AgroGuard.git
cd AgroGuard

# Backend
cd backend
python -m venv .venv
.venv/Scripts/activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -e ".[dev]"

# Frontend
cd ../frontend
npm install

# Root (for concurrent dev)
cd ..
npm install
```

### Environment Variables

```bash
# backend/.env
AGROGUARD_DATABASE_URL=postgresql+psycopg://postgres:change-me@localhost:5432/agroguard
AGROGUARD_INITIALIZE_DATABASE=true
AGROGUARD_CORS_ORIGINS=["http://localhost:5173"]
AGROGUARD_LLM_API_KEY=              # Optional: for AI chat/explanations
AGROGUARD_LLM_ENDPOINT=http://localhost:11434/v1
AGROGUARD_LLM_MODEL=gemma3:latest
AGROGUARD_OPENWEATHER_API_KEY=      # Optional: for live weather data
AGROGUARD_TELEGRAM_BOT_TOKEN=       # Optional: for alert notifications
AGROGUARD_TELEGRAM_CHAT_ID=         # Optional: for alert notifications

# frontend/.env
VITE_API_BASE_URL=/api/v1
VITE_ENABLE_API=true
VITE_DEMO_FIELD_ID=1
```

### Run Locally

```bash
# Start both backend and frontend
npm run dev

# Or separately:
npm run dev:backend    # uvicorn on :8000
npm run dev:frontend   # vite on :5173
```

The backend auto-seeds demo data (regions, crop profiles, demo field) when `AGROGUARD_INITIALIZE_DATABASE=true`.

## API

All routes under `/api/v1`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/crop-suggestion` | ML-based crop recommendation |
| `POST` | `/disease-detect` | Plant disease detection from image |
| `POST` | `/chat` | SSE-streamed AI chat |
| `POST` | `/crop-explanation` | SSE-streamed crop explanation |
| `POST` | `/crop-suitability` | Score field against crop profile |
| `POST` | `/observations/ingest` | Ingest sensor reading |
| `POST` | `/observations/simulate` | Generate simulated reading |
| `POST` | `/location-weather` | Weather data by coordinates |
| `GET`  | `/fields/{id}/current-status` | Latest field assessment |
| `GET`  | `/fields/{id}/growth/timeline` | Growth simulation timeline |
| `GET`  | `/analytics/ndvi-regions` | List NDVI regions |
| `GET`  | `/ndvi/{pcode}` | NDVI time series |
| `GET`  | `/dashboard/stats` | Dashboard overview |
| `GET`  | `/regions` | 18 Myanmar regions |
| `GET`  | `/crop-profiles` | Crop profiles with requirements |
| `GET`  | `/alerts` | Field alerts |
| `PATCH`| `/alerts/{id}/acknowledge` | Acknowledge alert |
| `PATCH`| `/alerts/{id}/resolve` | Resolve alert |
| `POST` | `/demo/reset` | Reset demo data |

## Engineering Highlights

**Rule-based scoring engine with configurable criticality weights.** Field conditions are evaluated against crop-specific requirements with three severity tiers (critical × 3.0, important × 1.5, advisory × 0.5). The same engine powers both real-time assessment and pre-planting suitability scoring.

**Dual ML pipeline.** Crop recommendation uses a trained RandomForest classifier (scikit-learn) for fast inference, while disease detection uses transfer learning on ResNet18 (PyTorch). Both models are serialized as artifacts and loaded on first request.

**SSE streaming with LLM fallback.** Chat and crop explanation endpoints stream responses via Server-Sent Events. When no LLM API key is configured, the system returns deterministic fallback responses — the platform remains functional without external AI services.

**IoT sensor integration with hardware simulation.** The Wokwi integration connects real ESP32 sensor readings via LoRaWAN/4G to the assessment pipeline. The frontend simulates sensor data with random-walk algorithms for demo purposes, feeding the same ingestion path as production devices.

**Async PostgreSQL with Alembic migrations.** All database operations use asyncpg via SQLAlchemy 2's async interface. Six sequential migrations handle schema evolution with seed data for 18 regions, crop profiles, and demo devices.

**Bilingual architecture.** English/Burmese support spans the entire stack — frontend translations (~200 keys), LLM system prompts, weather advisories, and Telegram notifications all respect the user's language selection.

## Challenges & Technical Decisions

**Problem:** Sensor readings arrive at irregular intervals and may contain duplicates or out-of-range values.
**Decision:** Validation layer in `observation.py` checks plausible ranges per sensor type and deduplicates by `event_id`. Invalid readings are rejected before reaching the assessment engine.
**Why:** Prevents corrupted data from triggering false alerts while maintaining a clean audit trail.

**Problem:** LLM availability is unpredictable — users may not have API keys configured.
**Decision:** Every LLM-dependent feature (chat, crop explanation, disease advice) has a fallback path that returns useful static responses.
**Why:** The platform must function as a standalone tool without external AI dependencies.

**Problem:** Crop assessment needs to work both for real-time sensor data and static field context snapshots.
**Decision:** Two scoring implementations — `assessment.py` (sensor-driven, async) and `suitability.py` (static, sync) — share the same algorithm but accept different input types.
**Why:** Avoids forcing sensor-dependent code paths into the pre-planting planning flow.

## Future Improvements

- Add JWT-based authentication to replace localStorage demo auth
- Dockerize backend and frontend for consistent deployment
- Implement batch sensor ingestion for high-frequency IoT data
- Add historical trend analysis for field assessments
- Expand disease detection classes beyond the current 11

## License

MIT License — see [LICENSE](LICENSE)
