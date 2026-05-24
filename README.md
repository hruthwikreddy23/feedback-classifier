# Feedback Classifier

One-line tagline: Customer feedback classification, prioritization, and export
with an LLM-backed FastAPI service and a Streamlit dashboard.

<!-- TOC -->
- [Badges](#badges)
- [Overview](#overview)
- [Features](#features)
- [Tech stack](#tech-stack)
- [Architecture](#architecture)
- [SOLID principles in this codebase](#solid-principles-in-this-codebase)
- [Project structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the application](#running-the-application)
- [API endpoints](#api-endpoints)
- [Usage examples](#usage-examples)
- [Testing](#testing)
- [Rate limits and free-tier notes](#rate-limits-and-free-tier-notes)
- [Troubleshooting](#troubleshooting)
- [Roadmap / future improvements](#roadmap--future-improvements)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Badges

- Python: 3.10+
- FastAPI: as used in `requirements.txt`
- Streamlit: as used in `requirements.txt`
- Tests: run locally with `pytest`

## Overview

This project provides a lightweight, production-friendly service for
classifying customer feedback using an LLM (Google Gemini via an OpenAI-
compatible endpoint), scoring items by priority and storing results in SQLite.

It is intended for product and support teams who want automated, structured
insights from free-form customer feedback. The system extracts sentiment
(positive/neutral/negative), a short topic label, a one-sentence summary,
and a severity score (1–5). A separate prioritizer computes a `priority_score`
that combines severity with recency so teams can focus on the most urgent
items.

The backend exposes REST endpoints for single and bulk classification and
provides paginated retrieval of results. A small Streamlit app offers a
developer-friendly dashboard and CSV bulk-upload UI.

## ✨ Features

- Classification
	- LLM-powered classification returning `sentiment`, `topic`, `summary`, and `severity`.
	- Single-item and CSV bulk classification endpoints.
- Storage
	- Lightweight SQLite persistence with simple schema and paginated queries.
	- Storage access through `StorageService` (single responsibility layer).
- Exporting
	- JSON, CSV, and Markdown exporters via a `BaseExporter` abstraction.
- API
	- FastAPI app with dependency injection for services and configuration.
	- OpenAPI docs available at `/docs`.
- UI
	- Streamlit dashboard for single classification, bulk CSV upload, and a simple metrics dashboard.

## Tech stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Language |
| FastAPI | REST API server (`app/main.py`) |
| Uvicorn | ASGI server |
| Streamlit | Frontend dashboard (`frontend/streamlit_app.py`) |
| SQLite | Persistent storage (under `data/`) |
| openai (OpenAI Python SDK) | Client wrapper used to call Gemini via a compatible endpoint |
| pandas | Frontend dataframes / CSV handling |

## Architecture

Layered architecture separates concerns and keeps components replaceable.

ASCII diagram:

User -> Streamlit -> FastAPI -> Services [Classifier, Prioritizer, Storage] -> SQLite + Gemini API

- `Streamlit`: frontend UI that calls FastAPI
- `FastAPI` (`app/main.py`, `app/routers/classify.py`): HTTP surface
- `Services`: `ClassificationService` (LLM interaction), `PriorityService` (scoring), `StorageService` (SQLite)
- External: Gemini via OpenAI-compatible endpoint (configured in `ClassificationService`)

## SOLID principles in this codebase

| Principle | Where it's demonstrated |
|---|---|
| Single Responsibility (SRP) | `app/services/classifier.py`, `app/services/prioritizer.py`, `app/services/storage.py` each implement a single responsibility (LLM, scoring, persistence).
| Open/Closed | `app/services/exporters.py` defines `BaseExporter` and concrete exporters (`JsonExporter`, `CsvExporter`, `MarkdownExporter`) so new formats can be added without modifying existing code.
| Liskov Substitution | `JsonExporter`, `CsvExporter`, `MarkdownExporter` can be used interchangeably where `BaseExporter` is expected (`export()` contract).
| Interface Segregation (ISP) | The dashboard requests `FeedbackSummary` (`app/models/schemas.py`) instead of the full `FeedbackOut` when a lightweight view is sufficient.
| Dependency Inversion (DIP) | `ClassificationService` receives `Settings` and a `prompt_template` at construction (`app/routers/classify.py` injects them). `StorageService` is injected into routes via FastAPI dependencies.

## Project structure

```
README.md                  # <- this file
requirements.txt           # Python dependencies
app/
	main.py                  # FastAPI entrypoint and startup lifecycle ([app/main.py](app/main.py#L1))
	core/
		config.py              # Env-based settings via pydantic ([app/core/config.py](app/core/config.py#L1))
		prompts.py             # LLM prompt templates ([app/core/prompts.py](app/core/prompts.py#L1))
	models/
		schemas.py             # Pydantic v2 request/response models ([app/models/schemas.py](app/models/schemas.py#L1))
	routers/
		classify.py            # API routes: /classify, /classify/bulk, /results ([app/routers/classify.py](app/routers/classify.py#L1))
	services/
		classifier.py          # LLM integration (OpenAI SDK + Gemini endpoint) ([app/services/classifier.py](app/services/classifier.py#L1))
		prioritizer.py         # Priority scoring logic ([app/services/prioritizer.py](app/services/prioritizer.py#L1))
		storage.py             # SQLite persistence layer ([app/services/storage.py](app/services/storage.py#L1))
		exporters.py           # JSON/CSV/Markdown exporters ([app/services/exporters.py](app/services/exporters.py#L1))
frontend/
	streamlit_app.py         # Streamlit UI for classify / bulk / dashboard ([frontend/streamlit_app.py](frontend/streamlit_app.py#L1))
data/                      # default DB path: ./data/feedback.db
tests/                     # pytest tests for services
```

## Prerequisites

- Python 3.10 or newer
- pip
- A Google Gemini API key (create at https://aistudio.google.com/apikey). Note: this project uses the `openai` Python library pointed at Gemini's OpenAI-compatible endpoint; the key should be stored in `OPENAI_API_KEY`.

## 🚀 Installation

Follow these steps for your OS to set up a virtual environment and install dependencies.

1. Clone the repository

```bash
git clone https://your-repo-url.git
cd feedback_classifier
```

2. Create and activate a virtual environment

- macOS / Linux (bash/zsh):

```bash
python -m venv .venv
source .venv/bin/activate
```

- Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

- Windows (cmd.exe):

```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

3. Install Python dependencies

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your Gemini key

If a `.env.example` is present, copy it; otherwise create `.env` manually:

```bash
# If provided
cp .env.example .env

# Or create one with these two lines (example):
echo "OPENAI_API_KEY=sk-your-gemini-key" > .env
echo "CHAT_MODEL=gemini-2.5-flash" >> .env
```

Important: The code reads `OPENAI_API_KEY` even though the underlying API is Gemini (the OpenAI SDK is used against Gemini's endpoint).

## 🛠 Configuration

| Variable | Description | Default | Example |
|---|---:|---|---|
| `OPENAI_API_KEY` | Gemini API key (stored as OpenAI-compatible key) | (none) | `OPENAI_API_KEY=sk-...` |
| `CHAT_MODEL` | Model to request from Gemini (OpenAI-compatible name) | `gemini-2.5-flash` | `gemini-2.5-flash` |
| `DB_PATH` / `db_path` | SQLite database path used by `StorageService` | `./data/feedback.db` | `./data/feedback.db` |

Note: `app/core/config.py` defines defaults; if you need to override the DB path or model, set the environment variables before starting the app.

## Running the application

Start the FastAPI server (development):

```bash
uvicorn app.main:app --reload
```

Start the Streamlit dashboard in a second terminal:

```bash
streamlit run frontend/streamlit_app.py
```

Open the API docs at `http://localhost:8000/docs` after starting the server.

## API endpoints

All endpoints are declared in [app/routers/classify.py](app/routers/classify.py#L1).

| Method | Path | Description |
|---|---|---|
| POST | `/classify` | Classify a single feedback item and persist the result |
| POST | `/classify/bulk` | Upload a CSV (must contain `text` column) and classify all rows |
| GET | `/results` | Paginated retrieval of classified feedback items |
| GET | `/health` | Simple health check returning `{status: "ok"}` |

<details>
<summary>POST /classify — example request/response</summary>

Request (JSON):

```json
{"text": "I was charged twice for my subscription.", "source": "support_ticket"}
```

Response (200):

```json
{
	"id": 1,
	"text": "I was charged twice for my subscription.",
	"sentiment": "negative",
	"topic": "billing",
	"summary": "Customer reports duplicate subscription charge.",
	"severity": 4,
	"priority_score": 3.8,
	"source": "support_ticket",
	"submitted_at": "2026-05-18T12:34:56.789000",
	"classified_at": "2026-05-18T12:34:57.123000"
}
```

The response shape comes from `FeedbackOut` in [app/models/schemas.py](app/models/schemas.py#L1).

</details>

<details>
<summary>POST /classify/bulk — example (CSV upload)</summary>

Upload a CSV with column header `text` (optional `source` column). Example CSV:

```csv
text,source
"I can't login to my account","support"
"Payment failed after update","billing"
```

Response (200) — list of `FeedbackOut` items (same fields as single endpoint).

</details>

<details>
<summary>GET /results — example request/response</summary>

Request:

```
GET /results?page=1&page_size=20&sentiment=negative&min_priority=2.0
```

Response (200):

```json
{
	"items": [ /* array of FeedbackOut */ ],
	"total": 123,
	"page": 1,
	"page_size": 20
}
```

Pagination and filters are implemented in `StorageService.get_results` ([app/services/storage.py](app/services/storage.py#L1)).

</details>

## Usage examples

Single-item classification using `curl`:

```bash
curl -X POST http://localhost:8000/classify \
	-H "Content-Type: application/json" \
	-d '{"text":"I was charged twice for my purchase","source":"email"}'
```

Python `requests` example:

```python
import requests

resp = requests.post(
		"http://localhost:8000/classify",
		json={"text": "App crashes on startup", "source": "app"},
		timeout=30,
)
resp.raise_for_status()
print(resp.json())
```

Streamlit UI usage (`frontend/streamlit_app.py`):

- `Classify` tab: paste or type text and click *Classify* to see the structured JSON returned by the API.
- `Bulk Upload` tab: upload a CSV with a `text` column (optional `source`) and click *Process CSV*.
- `Dashboard` tab: set sentiment filter and click *Load results* to show metrics and a table.

Sample CSV format for bulk upload (first line must include the header `text`):

```csv
text,source
"The UI is slow on mobile",mobile
"Can't reset password",support
"Billing page shows error",billing
```

## Testing

Run the test suite with `pytest`:

```bash
pytest tests/ -v
```

Current tests cover the `ClassificationService` (mocked OpenAI client) and
`PriorityService` logic in `tests/`.

## Rate limits and free-tier notes

Google Gemini model limits vary by tier. The project documentation suggests
the free-tier for `gemini-2.5-flash` is approximately **5 requests/minute (RPM)**
and **250 requests/day (RPD)**. For higher throughput consider using
`gemini-2.5-flash-lite` or a paid tier depending on Google Cloud quotas.

If you see `429` responses, slow down requests, add retries with backoff, or
choose a different model/plan.

## Troubleshooting

- uvicorn not recognized

	- Windows PowerShell: ensure your virtual environment is activated (`.\.venv\Scripts\Activate.ps1`).
	- Alternatively run `python -m uvicorn app.main:app --reload`.

- 401 / 400 authentication errors from LLM calls

	- Ensure a `.env` file exists in the project root and contains a valid `OPENAI_API_KEY`.
	- Confirm the key is active in your Google Cloud / AI Studio console.

- KeyError: 'text' on bulk upload

	- The CSV must include a `text` header. The bulk route relies on `csv.DictReader`.

- 429 rate limit errors

	- Wait and retry, or switch to a lower-latency/higher-throughput model.

If an issue isn't covered here, open an issue in the repository with logs and steps to reproduce.

## Roadmap / future improvements

1. Add authentication and role-based access to the API.
2. Swap SQLite for Postgres (or another managed DB) for production deployments.
3. Add streaming classification responses to support very large inputs.
4. Add multilingual prompt templates and per-language models.
5. Add background worker (Celery / RQ) for large bulk imports and retry handling.
6. Add observability: request metrics and structured logs.

## Contributing

Contributions are welcome. Suggested workflow:

1. Fork the repository and create a feature branch.
2. Run tests and add new tests for any behavior you change.
3. Open a pull request with a clear description of changes.

Please follow the existing code style and keep changes focused.

## License

This repository does not include an explicit license file. Add one (for example,
MIT) if you intend to publish. Placeholder: MIT.

## Acknowledgments

- FastAPI — fast Python API framework
- Streamlit — simple data apps and dashboards
- Google Gemini — LLM used via an OpenAI-compatible endpoint
- OpenAI Python SDK — used as a client wrapper against Gemini's endpoint

#   f e e d b a c k - c l a s s i f i e r 
 
 
