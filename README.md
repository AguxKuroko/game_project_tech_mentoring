# 🎮 Worst Game Meme Generator

> *Enter a year. Receive a cursed meme about the game that made players question everything.*
---
[![CI - Detect changes -> Lint -> Test -> CI_status](https://github.com/AguxKuroko/worst-games-memed/actions/workflows/ci.yml/badge.svg)](https://github.com/AguxKuroko/worst-games-memed/actions/workflows/ci.yml)
[![Scheduled Tests](https://github.com/AguxKuroko/worst-games-memed/actions/workflows/scheduled_tests.yml/badge.svg)](https://github.com/AguxKuroko/worst-games-memed/actions/workflows/scheduled_tests.yml)
---
![Python](https://img.shields.io/badge/Python-3.14-FF6B6B?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-FF9F43?logo=fastapi&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-ASGI-FFEAA7?logo=uvicorn&logoColor=black)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--Image-A29BFE?logo=openai&logoColor=white)
![SQLModel](https://img.shields.io/badge/SQLModel-0.0.37-FD79A8?logo=sqlite&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-Package%20Manager-74B9FF?logo=poetry&logoColor=white)
![Ruff](https://img.shields.io/badge/Ruff-Linter-55EFC4?logo=ruff&logoColor=black)
![Pre-commit](https://img.shields.io/badge/Pre--commit-Code%20Quality-6C5CE7?logo=pre-commit&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-Unit%20Tests-FDCB6E?logo=pytest&logoColor=black)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-81ECEC?logo=githubactions&logoColor=black)
![Logfire](https://img.shields.io/badge/Logfire-Observability-FF7675?logo=pydantic&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-Validation-E17055?logo=pydantic&logoColor=white)
![RAWG](https://img.shields.io/badge/RAWG-Games%20API-00B894?logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Container-2496ED?logo=docker&logoColor=white)
![Fly.io](https://img.shields.io/badge/Fly.io-Backend%20Host-7B2CBF?logo=flydotio&logoColor=white)
![Streamlit Cloud](https://img.shields.io/badge/Streamlit%20Cloud-Frontend%20Host-FF4B4B?logo=streamlit&logoColor=white)
---
## 💡 What Is This?

A **Python backend + data engineering** project disguised as a meme generator.

Under the fun surface, this app demonstrates a real-world data pipeline: it **ingests** raw data from an external API, **normalizes and validates** it into strict typed models, **transforms** images for AI consumption, **persists** results in a relational database, and **serves** everything through a clean REST API — with caching to avoid redundant work.

**What it does:**

1. **Fetches the worst-rated game** of any given year from the [RAWG Video Games API](https://rawg.io/apidocs)
2. **Normalizes raw API data** into validated Pydantic models (genres, release year, screenshots, metascore)
3. **Generates an AI meme** using OpenAI's `gpt-image-1` model — with a dynamically built prompt and real game screenshots
4. **Stores meme records** in a SQLite database via SQLModel, with file-based caching to skip expensive API calls on repeat requests
5. **Tracks access analytics** (view count, timestamps) powering a *Hall of Shame* leaderboard

All with ironic, slightly unhinged energy. 🔥

---
## 🚀 Demo
Example API usage via Swagger UI:

https://github.com/user-attachments/assets/67ea92a1-87ff-42b4-8031-c60b0507d3a4

---

## 🔬 Backend + Data Engineering Flavor

This isn't just a simple API wrapper — it touches on real **data engineering** patterns:

| Concept | Where It Happens |
|---------|------------------|
| **Data ingestion** | Raw JSON fetched from the RAWG external API |
| **Data normalization** | API responses are parsed, cleaned, and mapped into strict Pydantic models (`RawgApiData`) — ensuring consistent types, extracting nested fields (genres, release year, screenshots) |
| **Data validation** | Pydantic v2 enforces type safety at every boundary — invalid data never reaches the business logic |
| **Data transformation** | Screenshots are downloaded, converted to `BytesIO` streams, and prepared for the OpenAI API format |
| **Caching / deduplication** | Memes are stored in SQLite on first generation — subsequent requests for the same year skip all external API calls and serve directly from the file system |
| **Access tracking & analytics** | Every meme request updates `MemeStats` (access count, last accessed timestamp) — enabling the Hall of Shame leaderboard |
| **Input sanitization** | Game names are sanitized into safe filenames via regex to prevent path issues |
| **Configuration management** | Environment variables managed through `pydantic-settings` with `.env` support — no hardcoded secrets |

---

## 🏗 Architecture

```mermaid
flowchart TD
    A(["🌐 Client sends GET /worst_game/{year}"])
    B{"📋 Is the year valid?<br/>(not in the future)"}
    C["🎮 Call RAWG API (free)<br/>Fetch worst game of that year"]
    D{"🔍 Game found?"}
    E["🧹 Normalize & validate data<br/>(Pydantic model)"]
    F{"💾 Meme already<br/>in database?"}
    G["🤖 Call OpenAI API<br/>Send built-in prompt + up to 3 screenshots"]
    H["💾 Save generated meme<br/>to file system (.png)"]
    I["📀 Store meme record<br/>in DB (SQLModel → SQLite)"]
    J["📊 Update MemeStats<br/>(access count + timestamp)"]
    K(["✅ Return response<br/>(JSON or Image)"])
    ERR1(["❌ 400 — Year is in the future"])
    ERR2(["❌ 404 — No game found"])

    A --> B
    B -->|"❌ No"| ERR1
    B -->|"✅ Yes"| C
    C --> D
    D -->|"❌ None"| ERR2
    D -->|"✅ Game data"| E
    E --> F
    F -->|"✅ Yes — skip OpenAI"| J
    F -->|"❌ No — first time"| G
    G --> H
    H --> I
    I --> J
    J --> K
```

> **How caching works:** The RAWG API is called on every request (it's free and fast — we need the game data to build the file path). The **expensive OpenAI call** is the one that gets skipped when a meme already exists in the DB. On a cache hit, the saved `.png` is served directly — no image generation, no waiting. Caching the RAWG response was intentionally skipped — the call is free, lightweight, and always returns fresh data if game metadata changes over time.

### 🤖 A Note on Meme Generation

The prompt is **built dynamically** from real game data (title, genre, metascore, drop count, release year) and is carefully crafted to produce funny, readable meme images. It's not a simple one-liner — it includes detailed instructions for visual style, text placement, humor logic, and metascore badges.

---

## 🌐 Deployment Architecture

The app runs as two independent services that communicate over HTTPS — backend hosted on **Fly.io** (Dockerized), frontend hosted on **Streamlit Community Cloud**.

```mermaid
flowchart LR
    User(["👤 User Browser"])
    Frontend["🎨 Streamlit Frontend<br/>(Streamlit Community Cloud)"]
    Backend["⚡ FastAPI Backend<br/>(Docker on Fly.io · Amsterdam)"]
    Volume[("📀 SQLite + memes<br/>Fly persistent volume")]
    RAWG["🎮 RAWG API"]
    OpenAI["🤖 OpenAI gpt-image-1"]
    Logfire["📊 Logfire"]

    User -->|"HTTPS"| Frontend
    Frontend -->|"HTTPS + X-BACKEND-KEY"| Backend
    Backend <--> Volume
    Backend -->|"game data"| RAWG
    Backend -->|"image generation"| OpenAI
    Backend -->|"traces & metrics"| Logfire
```

| Concern | How it's handled |
|---------|------------------|
| **Frontend deploy** | Streamlit Community Cloud auto-deploys from `main` whenever `streamlit_frontend/` changes |
| **Backend deploy** | GitHub Actions runs `flyctl deploy` only on push to `main` AND only when backend files actually changed (paths-filter gate) |
| **Secrets — backend** | `fly secrets set ...` — encrypted in Fly's vault, injected as env vars at container startup |
| **Secrets — frontend** | Streamlit Cloud's dashboard secrets form — `BACKEND_URL` points at the Fly URL in production, `localhost:8000` locally |
| **Shared `BACKEND_API_KEY`** | Same value in both Fly secrets and Streamlit Cloud secrets — backend rejects callers without it (401) |
| **Persistent data** | Fly volume mounted at `/data` — SQLite DB + generated memes survive deploys and restarts |
| **Cost discipline** | `auto_stop_machines = 'stop'` + `min_machines_running = 0` — backend sleeps when idle, wakes on incoming request (~3s cold start) |

---

## 🚀 Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/` | Welcome screen (serves the home image) |
| `GET` | `/worst_game/{year}` | Get the worst game of a year — as JSON or a generated meme image |
| `GET` | `/hall_of_shame` | Leaderboard of the most-accessed memes |

### `/worst_game/{year}`

| Parameter | Type | Description |
|-----------|------|-------------|
| `year` *(path)* | `int` | The year to look up |
| `format` *(query)* | `json` \| `image` | Response format (default: `json`) |



<details>
<summary>📦 Example JSON Response</summary>

```json
{
  "game_name": "Some Questionable Game",
  "game_meme": "http://localhost:8000/worst_game/2015?format=image"
}
```
</details>

### `/hall_of_shame`

Returns the most-viewed meme(s) — the games that were memed so hard they achieved immortality.
<details>
<summary>📦 Example JSON Response</summary>

```json
[
  {
    "game_name": "That One Game",
    "game_metascore": 42,
    "year": 2012,
    "image_url": "http://localhost:8000/worst_game/2012?format=image",
    "access_count": 15
  }
]
```
</details>
---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.14 |
| **Backend framework** | FastAPI + Uvicorn |
| **Frontend** | Streamlit |
| **Validation** | Pydantic v2 |
| **Database** | SQLite via SQLModel |
| **AI / Image Gen** | OpenAI API (`gpt-image-1`) |
| **Game Data** | RAWG Video Games API |
| **Observability** | Logfire (OpenTelemetry under the hood) |
| **Package Manager** | Poetry |
| **Container** | Docker |
| **Backend hosting** | Fly.io (Amsterdam region, scale-to-zero) |
| **Frontend hosting** | Streamlit Community Cloud |
| **CI/CD** | GitHub Actions |
| **Linting & formatting** | Ruff |
| **Testing** | pytest |
| **Git Hooks** | pre-commit |

---

## ⚡ Quick Start

### 🌍 Try it live (no install needed)

| What | Where |
|------|-------|
| Frontend (Streamlit UI) | `https://<your-subdomain>.streamlit.app` *(deployed to Streamlit Community Cloud)* |
| Backend Swagger docs | https://worst-game-meme.fly.dev/docs |

> The Fly.io backend sleeps when idle to save cost. First request after a while takes ~3-5s while the machine wakes up.

---

### 🖥 Run locally

#### Prerequisites

- Python 3.14
- [Poetry](https://python-poetry.org/)
- API keys for **RAWG** and **OpenAI**
- A **Logfire** token (free at [logfire.pydantic.dev](https://logfire.pydantic.dev))

#### Setup

```bash
# Clone the repo
git clone https://github.com/AguxKuroko/worst-games-memed.git
cd worst-games-memed

# Install dependencies
poetry install
```

#### Environment variables (`.env`)

Copy `.env.example` to `.env` and fill in your own values:

```bash
cp .env.example .env
```

Then edit `.env` with:

- **`RAWG_API_KEY`** — free key from [rawg.io/apidocs](https://rawg.io/apidocs)
- **`OPEN_AI_API_KEY`** — from [platform.openai.com](https://platform.openai.com/api-keys) *(image generation costs real money per call)*
- **`BACKEND_API_KEY`** — generate any random string to protect the API from random callers:
  ```bash
  poetry run python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
  Use the **same value** in your Streamlit frontend config — backend and frontend share this secret.
- **`LOGFIRE_TOKEN`** — write token from the [Logfire dashboard](https://logfire.pydantic.dev)
- **`DB_DIR`** *(optional)* — override the storage path for the SQLite DB + memes. Defaults to `app/db` if unset. Only needed when running against a persistent volume (e.g. Fly.io, Docker bind mount). On Fly.io this is already set via `fly.toml`, so you don't touch it for normal deploys.

---

### Option 1 — Backend only (FastAPI + Swagger UI)

If you just want to poke the API directly without the Streamlit frontend:

```bash
poetry run uvicorn app.fast_api_endpoints:app --reload
```

Then open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger UI. Click **Authorize** at the top right and paste your `BACKEND_API_KEY` to call protected endpoints.

### Option 2 — Backend + Streamlit frontend (full app)

You'll need **two terminals**.

**First — create the frontend's local secrets file:**

`.streamlit/secrets.toml`:

```toml
BACKEND_API_KEY = "same-value-as-in-your-.env"
BACKEND_URL = "http://localhost:8000"
```

This file is gitignored — only for local dev. In production, secrets live in Streamlit Cloud's dashboard.

**Terminal 1 — backend:**

```bash
poetry run uvicorn app.fast_api_endpoints:app --reload
```

**Terminal 2 — frontend:**

```bash
poetry run streamlit run streamlit_frontend/streamlit_app.py
```

Then open [http://localhost:8501](http://localhost:8501). The Streamlit UI makes HTTP calls to your local backend on `8000` — both processes must be running.

---

## 📂 Project Structure

```
app/                              # FastAPI backend (deployed to Fly.io in Docker)
├── fast_api_endpoints.py         # API routes & main FastAPI app
├── api_keys_config.py            # Pydantic-settings config (.env loader)
├── app_config.py                 # Paths + DB_DIR override for Fly volume
├── auth.py                       # X-BACKEND-KEY header verification
├── logging_config.py             # Logfire + rotating file + console logging
├── meme_generator.py             # OpenAI image generation logic
├── models.py                     # Pydantic models (RawgApiData, MemeGeneratorJsonData)
├── rawg_api.py                   # RAWG API integration
├── utils.py                      # Helpers: prompts, filename cleanup, lifespan
├── home_endpoint_image/
│   └── welcome.png               # Backend home screen image (served at GET /)
└── db/
    ├── db_config.py              # Database URL config
    ├── db_models.py              # SQLModel tables (Meme, MemeStats)
    ├── db_utils.py               # UTC timestamp helper
    └── engine.py                 # SQLModel engine setup

streamlit_frontend/               # Streamlit frontend (deployed to Streamlit Community Cloud)
├── streamlit_app.py              # Main UI entry point
├── st_config.py                  # Frontend-local path config (assets folder)
├── st_utilis.py                  # Misc helpers (current year, etc.)
├── content.py                    # Waiting messages shown while generating
├── requirements.txt              # Slim deps for Streamlit Cloud (streamlit + requests only)
└── assets/
    └── welcome.png               # Frontend sidebar image (frontend owns its own copy)

.streamlit/
├── config.toml                   # Theme (committed)
└── secrets.toml                  # Local-only secrets (gitignored — production uses Cloud dashboard)

.github/workflows/
├── ci.yml                        # Detect changes → Lint → Test → Deploy backend → Status
└── scheduled_tests.yml           # Monthly health-check test runs

Dockerfile                        # Backend container build (Python 3.14-slim + Poetry)
fly.toml                          # Fly.io app config (volume, region, auto-stop, scale)
pyproject.toml                    # Backend deps + tooling config (Poetry)
```

---

## 🥚 Easter Egg & 🐾 Kuroko

Kuroko is my dog and the real co-creator of this project. She's currently kicking cancer's ass through chemotherapy — for the second time — like the absolute fighter she is. 🐾 She deserved to be immortalized somewhere, so she became the welcome screen, got turned into a cursed AI meme with hypnotic glowing eyes, and somewhere in this project there's a secret mode dedicated to her.
If you're curious enough to find it, you'll know it when you see it. 🐾

---

## 🧪 Development

```bash
# Run linting
poetry run ruff check .

# Run tests
poetry run pytest

# Install pre-commit hooks
poetry run pre-commit install
```

---

## ⚙️ CI/CD Pipeline

A single GitHub Actions workflow handles detect → lint → test → deploy. The backend deploys to Fly.io only when its files actually changed; the Streamlit frontend is deployed by Streamlit Community Cloud directly from `main`.

### Workflows

| Workflow | File | Triggers | What it does |
|----------|------|----------|--------------|
| **CI → Deploy** | `ci.yml` | Push / PR to `main`, manual | Detects changes, runs Ruff + pytest, deploys backend to Fly.io on push to `main` (when backend files changed) |
| **Scheduled Tests** | `scheduled_tests.yml` | 1st, 15th & 29th monthly (09:00 UTC), manual | Periodic test suite health check |

### Pipeline stages (`ci.yml`)

```
changes ─▶ quality-check ─▶ tests ─▶ deploy-backend ─▶ ci-status
   │           │              │             │
   │           │              │             ├─ only on push to main (never on PRs)
   │           │              │             ├─ only if backend/Docker/fly files changed
   │           │              │             ├─ only if lint + tests passed
   │           │              │             └─ runs `flyctl deploy --remote-only`
   │           │              │
   │           │              └─ pytest (skipped on docs-only changes)
   │           │
   │           └─ Ruff lint + format check (skipped on docs-only changes)
   │
   └─ paths-filter — emits two boolean flags as job outputs:
        • code     = anything non-`.md` changed   → gates lint + tests
        • backend  = files Fly cares about changed → gates deploy
```

Two filters → two different gates:
- **Frontend-only edit** (e.g. `streamlit_frontend/streamlit_app.py`) → lint + tests run, Fly deploy **skipped** (Streamlit Cloud handles the frontend redeploy on its own).
- **Backend edit** (e.g. `app/...`, `Dockerfile`, `fly.toml`) → full pipeline including Fly deploy.
- **Docs-only edit** (e.g. `README.md`) → everything skipped, `ci-status` still passes.

### Secrets used by CI/CD

| Secret | Where it lives | Used by |
|--------|----------------|---------|
| `FLY_API_TOKEN` | GitHub Actions repository secret | `deploy-backend` job — authenticates `flyctl deploy` |

---

<p align="center">
  <i>Built with questionable taste during the <b>Tech Leaders Mentoring Program</b></i><br>
  <sub>Mentored by the one and only <a href="https://github.com/Dombearx">Dominik</a> 🐐</sub>
</p>
