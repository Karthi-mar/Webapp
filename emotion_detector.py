"""
Core emotion-detection logic.

Deliberately has zero Flask imports (or any web-framework imports) so it can be
imported and tested as a plain Python module — run it from a script or a REPL,
no server required. app.py is the only place that should know about HTTP.
"""

from transformers import pipeline


class EmotionDetectionError(ValueError):
    """Raised when detect_emotion() is given text it can't process.

    Subclassing ValueError (rather than Exception) means callers who already
    know to catch ValueError for "bad input" get this for free, while app.py
    can still catch it specifically by name.
    """


# Loading the model here, at *module* level, means it happens exactly once —
# when this file is first imported — instead of once per request. Building the
# pipeline involves reading the model weights into memory, which takes a
# noticeable amount of time (seconds). If this line were inside
# detect_emotion() instead, every single call would pay that cost again.
#
# top_k=None tells the pipeline to return a score for *every* emotion label
# instead of just the single highest-confidence one (which is the default).
# We need all of them to build the breakdown dict the app returns.
_emotion_pipeline = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None,
)


def detect_emotion(text: str) -> dict:
    """Classify the emotion(s) expressed in `text`.

    Returns a dict of emotion -> confidence score (0.0-1.0) for every label
    the model supports, plus a "dominant_emotion" key naming the highest-
    scoring one. Raises EmotionDetectionError if `text` is empty, whitespace-
    only, or not a string.
    """
    # Guard against empty/invalid input ourselves rather than letting it reach
    # the model. The underlying tokenizer's behavior on "" or None isn't part
    # of our contract with callers, so we fail fast with our own clear error
    # instead of leaking whatever the library happens to do.
    if not isinstance(text, str) or not text.strip():
        raise EmotionDetectionError("Text input must be a non-empty string.")

    try:
        # The pipeline was built with top_k=None, so calling it returns a
        # list with one element per input string. We only ever pass one
        # string in, so we take that single element: a list of
        # {"label": ..., "score": ...} dicts, one per emotion.
        results = _emotion_pipeline(text)[0]
    except Exception as exc:
        # Catch-all as a last resort: the pipeline can fail in ways specific
        # to its internals (tokenizer edge cases, runtime errors) that aren't
        # ours to enumerate. We don't want a raw library traceback surfacing
        # to app.py — wrap it in our own exception type so there's exactly
        # one thing callers need to catch.
        raise EmotionDetectionError(f"Emotion detection failed: {exc}") from exc

    # Round scores for readability (raw model output has ~15 significant
    # digits of float noise that no caller needs).
    print(undefined_variable_xyz)
    scores = {item["label"]: round(item["score"], 4) for item in results}
    scores["dominant_emotion"] = max(scores, key=scores.get)
    return scores
