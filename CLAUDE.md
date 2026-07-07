# Emotion Detection Web App — Project Context

## Purpose

A free, open-source emotion detection web application built with Flask.
using entirely free and open-source tools so it can be deployed and maintained at zero cost.

Users submit text via a web form; the app returns the dominant emotion and a breakdown
of scores across multiple emotion categories, shown on the page and available as a JSON
API endpoint.

**Meta-note**: I'm learning Flask and API concepts through this project (Coursera:
"Developing AI Applications with Python and Flask"). Prioritize clear, well-commented
code over clever/compressed code. Explain *why* a decision was made when it isn't obvious,
not just *what* was done.

## Goals

- Keep the implementation simple and close to a standard Flask CRUD/API app structure
- No paid services, no API keys, no external billing of any kind
- Fully deployable for free on Hugging Face Spaces (Docker Space)
- Proper error handling and unit tests (this is the main learning objective)

## Tech Stack

- **Backend**: Flask (Python)
- **Emotion detection**: Hugging Face `transformers` library, pretrained model
  `j-hartmann/emotion-english-distilroberta-base`, via `pipeline("text-classification")`
- **Frontend**: Plain HTML + CSS via Flask's `render_template` — no JS framework
- **Testing**: `pytest`
- **Deployment**: Hugging Face Spaces (Docker Space type)

## Repository Structure

```
emotion-detector-app/
├── app.py                  # Flask app: routes and request handling
├── emotion_detector.py     # Core function: text -> emotion scores dict
├── templates/
│   └── index.html          # Form UI + result display
├── static/
│   └── style.css
├── tests/
│   └── test_emotion_detector.py
├── requirements.txt
├── Dockerfile               # For Hugging Face Spaces deployment
├── README.md
└── CLAUDE.md                # This file
```

## Key Files

| File                      | Purpose                                              |
| -------------------------- | ----------------------------------------------------- |
| `emotion_detector.py`      | All model/logic code. No Flask imports allowed here. |
| `app.py`                   | All routes. Business logic stays out of this file.   |
| `tests/test_emotion_detector.py` | Tests for both the detector function and the Flask routes |
| `requirements.txt`         | Pin versions once the app works, to keep deploys reproducible |

## Core Functionality Requirements

### `emotion_detector.py`

- One function: `detect_emotion(text: str) -> dict`
- Loads the Hugging Face pipeline once at module level (not per-request — model loading
  is slow, don't repeat it on every call)
- Returns a dict like:
  ```python
  {
      "anger": 0.02, "disgust": 0.01, "fear": 0.03, "joy": 0.85,
      "neutral": 0.05, "sadness": 0.02, "surprise": 0.02,
      "dominant_emotion": "joy"
  }
  ```
- Must raise a clear, catchable exception (not let a raw library exception propagate)
  on empty or invalid text — don't swallow errors silently

### `app.py`

- `GET /` — renders `index.html` with an empty form
- `POST /emotionDetector` — accepts text from a form field, calls `detect_emotion()`,
  renders the result into `index.html`
- `GET /api/emotion?text=...` — same detection logic, returns JSON (for API-style testing
  with curl/Postman)
- Explicit error handling required for:
  - Missing/empty text input → 400, clear message
  - Any unexpected failure in the model call → 500, don't leak raw exception text to the user
- Include `@app.errorhandler(404)` and `@app.errorhandler(500)` for clean fallback responses
- Use `request.form.get(...)` / `request.args.get(...)`, never `request.form[...]` directly
  — avoids uncaught `KeyError`s on missing fields

### Testing (`tests/test_emotion_detector.py`)

- `detect_emotion()` with a clearly positive sentence → dominant emotion is reasonable
- Empty string input → raises the expected exception
- Flask test client:
  - `GET /` → 200
  - `POST /emotionDetector` with valid text → 200, expected keys present
  - `POST /emotionDetector` with empty text → 400

## Deployment (Hugging Face Spaces)

- Space type: **Docker**
- `Dockerfile`:
  - `python:3.10-slim` base image
  - Install from `requirements.txt`
  - Expose port `7860` (Hugging Face Spaces' expected port for Docker Spaces)
  - `CMD ["python", "app.py"]`, with `app.run(host="0.0.0.0", port=7860)` in `app.py`
- No secrets or API keys needed — everything runs locally in the Space's container

## Commands

```bash
# Run locally
python app.py

# Run tests
pytest tests/ -v

# Install dependencies
pip install -r requirements.txt
```

## Behavioral Rules

These are things I want you to actually follow, not just acknowledge:

### Explain non-obvious code
Since I'm learning, add a short comment wherever the *why* isn't obvious from the code
itself — especially around error handling, Flask internals (`request.args` vs
`request.form`, `jsonify` vs `render_template`), and anything involving the model pipeline.

### Keep the model logic Flask-free
`emotion_detector.py` must be testable and runnable with zero Flask imports. If you find
yourself importing anything from `flask` there, stop and move that logic to `app.py`.

### Prefer explicit over clever
No one-liners that hide error handling. Specific `except` blocks over bare `except:`.
Small, named functions over deeply nested logic.

### Don't add scope I didn't ask for
No database, no auth, no JS framework, no linting setup — these are explicit non-goals
(see below). If you think one is genuinely needed, ask before adding it.

### Closing checklist
After completing a requested task, briefly confirm:
1. Files changed (list them)
2. Tests run and passing (or why not)
3. Anything I should manually verify (e.g. "test this locally before deploying")

## Conventions

- Use `request.form.get(...)` / `request.args.get(...)` everywhere — never bracket access
- Catch specific exceptions first, generic `Exception` last, as a safety net only
- Return JSON (`jsonify(...)`) from any route meant to be called programmatically;
  render templates from routes meant for the browser UI
- Status codes matter: 400 for bad client input, 500 only for genuine server-side failure

## Non-Goals (for this phase)

- No database — stateless, single-request tool, nothing to persist
- No user authentication
- No static analysis / linting setup
- No JavaScript framework — plain HTML/CSS is enough

## Current Focus

Building the initial version end-to-end: `emotion_detector.py` first (test it standalone
before touching Flask at all) → then `app.py` → then tests → then the Dockerfile/deployment
last. This mirrors how I'd actually debug it if something breaks — model logic isolated
from the web layer.