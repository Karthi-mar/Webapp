# Emotion Detector

A free, open-source Flask web app that detects the emotion expressed in a
piece of text, using the Hugging Face `transformers` pipeline with the
pretrained [`j-hartmann/emotion-english-distilroberta-base`](https://huggingface.co/j-hartmann/emotion-english-distilroberta-base)
model. No paid services, no API keys.

Submit text through the web form (or the JSON API) and get back a score for
each of seven emotions — anger, disgust, fear, joy, neutral, sadness,
surprise — plus the dominant one.

## Project structure

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
└── README.md
```

## Running locally

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
python app.py
```

The app runs at http://localhost:7860.

- `GET /` — the web form
- `POST /emotionDetector` — form submission handler
- `GET /api/emotion?text=...` — JSON API, e.g.
  `curl "http://localhost:7860/api/emotion?text=I%20am%20thrilled"`

## Running tests

```bash
pytest tests/ -v
```

## Deploying to Hugging Face Spaces

1. Create a new Space, type **Docker**.
2. Push this repo's contents to the Space's git remote.
3. The included `Dockerfile` builds and runs the app automatically — no
   secrets or API keys needed, everything runs inside the container.

## Tech stack

- **Backend**: Flask
- **Emotion detection**: Hugging Face `transformers`, `j-hartmann/emotion-english-distilroberta-base`
- **Frontend**: Plain HTML + CSS (no JS framework)
- **Testing**: pytest
- **Deployment**: Hugging Face Spaces (Docker Space)

## License

MIT — see [LICENSE](LICENSE).
