# Feedback Classifier

Sentiment-aware customer feedback classifier powered by an LLM, with a FastAPI backend and a Streamlit dashboard.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Google Gemini](https://img.shields.io/badge/LLM-Google%20Gemini-4285F4?logo=google&logoColor=white)
![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [SOLID Principles](#solid-principles)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Testing](#testing)
- [Rate Limits](#rate-limits)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

Feedback Classifier is a lightweight, production-friendly service for turning free-form customer feedback into structured, actionable insights using a Large Language Model.

For each piece of feedback, the system extracts:

- **Sentiment** — `positive`, `neutral`, or `negative`
- **Topic** — a short category label (e.g. `billing`, `UI/UX`, `performance`)
- **Summary** — a one-sentence summary of the feedback
- **Severity** — an integer score from 1 (trivial) to 5 (critical)
- **Priority Score** — computed by a separate prioritizer that combines severity with recency, so teams can focus on the most urgent items first

The backend exposes a REST API for single and bulk classification with paginated result retrieval, while a Streamlit dashboard provides a friendly UI for classifying feedback and exploring results.

The LLM used is **Google Gemini**, accessed through its OpenAI-compatible endpoint — the project uses the standard `openai` Python library pointed at Gemini's API, making the provider easy to swap.

---

## Features

- **Classification** — LLM-powered classification returning sentiment, topic, summary, and severity for any feedback text.
- **Single & bulk processing** — classify one item via JSON, or upload a CSV to classify many entries at once.
- **Persistent storage** — results are stored in SQLite with a simple schema and paginated, filterable queries.
- **Pluggable exporters** — export results as JSON, CSV, or Markdown through a common `BaseExporter` abstraction.
- **Interactive REST API** — built with FastAPI, with auto-generated OpenAPI docs at `/docs`.
- **Streamlit dashboard** — a clean UI for single classification, bulk CSV upload, and result browsing.
- **Tested** — unit tests for the classification and prioritization logic using `pytest`.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core language |
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| Streamlit | Frontend dashboard |
| SQLite | Persistent storage |
| Google Gemini | LLM for classification |
| OpenAI Python SDK | Client used to call Gemini's OpenAI-compatible endpoint |
| Pydantic | Request/response validation and settings |
| pandas | CSV handling and dataframes |
| pytest | Testing |

---

## Architecture

The application uses a layered architecture that separates concerns and keeps each component independently replaceable.

```
User
  |
  v
Streamlit dashboard
  |
  v
FastAPI (REST API)
  |
  v
Service layer
  +-- ClassificationService  -->  Google Gemini API
  +-- PriorityService
  +-- StorageService         -->  SQLite
  +-- Exporters (CSV / JSON / Markdown)
```

- **Streamlit** — the frontend UI; communicates with the backend over HTTP.
- **FastAPI** — the HTTP surface; defines routes and handles request/response validation.
- **Service layer** — the core logic, split into focused services:
  - `ClassificationService` handles all LLM interaction.
  - `PriorityService` computes priority scores.
  - `StorageService` handles SQLite persistence.
  - Exporters convert stored results into different output formats.

---

## SOLID Principles

This codebase is structured to demonstrate the five SOLID principles.

| Principle | Where it is demonstrated |
|---|---|
| **Single Responsibility** | `classifier.py`, `prioritizer.py`, and `storage.py` each own exactly one responsibility — LLM calls, scoring, and persistence respectively. |
| **Open/Closed** | `BaseExporter` allows new output formats to be added without modifying any existing exporter. |
| **Liskov Substitution** | The CSV, JSON, and Markdown exporters are fully interchangeable through the `BaseExporter.export()` contract. |
| **Interface Segregation** | The dashboard depends on the lightweight `FeedbackSummary` model rather than the full storage model. |
| **Dependency Inversion** | `ClassificationService` receives its settings and prompt template via constructor injection rather than hardcoding them. |

---

## Project Structure

```
feedback_classifier/
├── app/
│   ├── core/
│   │   ├── config.py          # Environment-based settings
│   │   └── prompts.py         # LLM prompt templates
│   ├── models/
│   │   └── schemas.py         # Pydantic request/response models
│   ├── routers/
│   │   └── classify.py        # API routes
│   ├── services/
│   │   ├── classifier.py      # LLM classification logic
│   │   ├── prioritizer.py     # Priority scoring logic
│   │   ├── storage.py         # SQLite persistence layer
│   │   └── exporters.py       # CSV / JSON / Markdown exporters
│   └── main.py                # FastAPI application entrypoint
├── frontend/
│   └── streamlit_app.py       # Streamlit dashboard
├── tests/
│   ├── test_classifier.py
│   └── test_prioritizer.py
├── data/                      # SQLite database (created at runtime)
├── .env.example               # Example environment variables
├── requirements.txt
└── README.md
```

---

## Prerequisites

- **Python 3.10 or newer**
- **pip**
- A free **Google Gemini API key** — create one at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/hruthwikreddy23/feedback-classifier.git
cd feedback-classifier
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS / Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy the example file and add your API key:

```bash
cp .env.example .env
```

Then open `.env` and fill in the values (see [Configuration](#configuration) below).

---

## Configuration

The application reads its settings from a `.env` file in the project root.

| Variable | Description | Example |
|---|---|---|
| `OPENAI_API_KEY` | Your Google Gemini API key. The variable is named `OPENAI_API_KEY` because the project uses the OpenAI SDK against Gemini's OpenAI-compatible endpoint. | `AIzaSy...` |
| `CHAT_MODEL` | The Gemini model to use. | `gemini-2.5-flash` |
| `DB_PATH` | Path to the SQLite database file. | `./data/feedback.db` |

Example `.env`:

```dotenv
OPENAI_API_KEY=AIzaSyYourKeyHere
CHAT_MODEL=gemini-2.5-flash
DB_PATH=./data/feedback.db
```

> **Note:** Never commit your `.env` file. It is excluded via `.gitignore`. Only `.env.example` (with no real key) should be committed.

---

## Running the Application

### Start the API server

```bash
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Interactive documentation is available at `http://127.0.0.1:8000/docs`.

### Start the Streamlit dashboard

In a **second terminal** (with the virtual environment activated):

```bash
streamlit run frontend/streamlit_app.py
```

The dashboard opens at `http://localhost:8501`.

> Both the API server and the dashboard must be running at the same time, since the dashboard calls the API.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/classify` | Classify a single feedback item and store the result. |
| `POST` | `/classify/bulk` | Upload a CSV file and classify every row. |
| `GET` | `/results` | Retrieve stored results with pagination and filtering. |
| `GET` | `/health` | Health check endpoint. |

<details>
<summary><b>POST /classify — example</b></summary>

**Request:**

```json
{
  "text": "I was charged twice for my subscription.",
  "source": "support_ticket"
}
```

**Response:**

```json
{
  "id": 1,
  "text": "I was charged twice for my subscription.",
  "sentiment": "negative",
  "topic": "billing",
  "summary": "Customer reports being charged twice for their subscription.",
  "severity": 4,
  "priority_score": 4.0,
  "source": "support_ticket",
  "submitted_at": "2026-05-18T12:34:56.789000",
  "classified_at": "2026-05-18T12:34:57.123000"
}
```

</details>

<details>
<summary><b>POST /classify/bulk — example</b></summary>

Upload a CSV file containing a `text` column (a `source` column is optional):

```csv
text,source
"I can't log in to my account",support
"Payment failed after the update",billing
```

The response is a list of classified feedback items in the same shape as the single-classify response.

</details>

<details>
<summary><b>GET /results — example</b></summary>

**Request:**

```
GET /results?page=1&page_size=20&sentiment=negative
```

**Response:**

```json
{
  "items": [ "...array of classified feedback items..." ],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

</details>

---

## Usage Examples

### Single classification with curl

```bash
curl -X POST http://127.0.0.1:8000/classify \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"The app crashes every time I open it.\", \"source\": \"app\"}"
```

### Single classification with Python

```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/classify",
    json={"text": "The app crashes every time I open it.", "source": "app"},
    timeout=30,
)
response.raise_for_status()
print(response.json())
```

### Using the Streamlit dashboard

- **Classify tab** — paste feedback text and click *Classify* to see the structured result.
- **Bulk Upload tab** — upload a CSV with a `text` column to classify many entries at once.
- **Dashboard tab** — browse and filter all stored classifications.

### Sample CSV for bulk upload

The first row must be a header containing a `text` column:

```csv
text
"Love the new update, the app feels so much faster now!"
"The checkout page keeps freezing on mobile."
"Customer service was rude when I called about my refund."
"Just wanted to ask if you support PayPal as a payment option?"
"My account got hacked and no one has contacted me. Urgent."
```

---

## Testing

Run the test suite with:

```bash
pytest tests/ -v
```

The tests cover the classification service (with a mocked LLM client) and the priority scoring logic.

---

## Rate Limits

This project uses the free tier of the Google Gemini API. Free-tier limits are approximate and depend on the model:

| Model | Approx. requests/minute | Approx. requests/day |
|---|---|---|
| `gemini-2.5-flash` | 5 | 250 |
| `gemini-2.5-flash-lite` | 15 | 1000 |

If you hit a `429` rate-limit error during bulk uploads, wait a minute and retry, switch to `gemini-2.5-flash-lite`, or upload smaller batches.

---

## Troubleshooting

| Issue | Cause & Fix |
|---|---|
| `uvicorn` is not recognized | The virtual environment is not active. Activate it, or run `python -m uvicorn app.main:app --reload`. |
| `400 / 401` authentication error | The API key is missing or invalid. Confirm `.env` exists in the project root and contains a valid `OPENAI_API_KEY`. |
| `KeyError: 'text'` on bulk upload | The CSV is missing a `text` column header. The first row must include `text`. |
| `429` rate-limit error | The Gemini free-tier limit was exceeded. Wait and retry, or switch to `gemini-2.5-flash-lite`. |

---

## Roadmap

- Add authentication and role-based access control to the API.
- Replace SQLite with PostgreSQL for production deployments.
- Add a background worker (Celery or RQ) for large bulk imports with retry handling.
- Support multilingual feedback classification.
- Add observability: structured logging and request metrics.

---

## Contributing

Contributions are welcome.

1. Fork the repository and create a feature branch.
2. Make your changes and add tests where appropriate.
3. Run `pytest` to confirm all tests pass.
4. Open a pull request with a clear description of your changes.

---

## License

This project is released under the MIT License. See the `LICENSE` file for details.

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) — the API framework
- [Streamlit](https://streamlit.io/) — the dashboard framework
- [Google Gemini](https://ai.google.dev/) — the LLM
- [OpenAI Python SDK](https://github.com/openai/openai-python) — the client library used against Gemini's compatible endpoint
