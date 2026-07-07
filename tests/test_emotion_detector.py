"""
Tests for emotion_detector.py (the model logic) and app.py (the Flask routes).

Run with: pytest tests/ -v
"""

import pytest

from emotion_detector import detect_emotion, EmotionDetectionError
from app import app as flask_app


# ---------------------------------------------------------------------------
# emotion_detector.py — plain function tests, no Flask involved
# ---------------------------------------------------------------------------

def test_detect_emotion_positive_sentence():
    result = detect_emotion("I am so incredibly happy and excited today!")
    assert result["dominant_emotion"] == "joy"


def test_detect_emotion_empty_string_raises():
    with pytest.raises(EmotionDetectionError):
        detect_emotion("")


def test_detect_emotion_whitespace_only_raises():
    with pytest.raises(EmotionDetectionError):
        detect_emotion("   ")


# ---------------------------------------------------------------------------
# app.py — Flask routes, via the test client
# ---------------------------------------------------------------------------
# pytest fixtures are reusable setup functions: any test function that takes
# `client` as an argument automatically gets whatever this fixture returns.
# Flask's test_client() sends requests straight to the app in-process (no
# real network socket, no running server needed) which is what makes route
# tests fast.

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as test_client:
        yield test_client


def test_index_get(client):
    response = client.get("/")
    assert response.status_code == 200


def test_emotion_detector_post_valid_text(client):
    response = client.post("/emotionDetector", data={"text": "I am thrilled!"})
    assert response.status_code == 200
    # The result is rendered into HTML, not JSON, for this route — check the
    # dominant emotion's label shows up on the page rather than parsing JSON.
    assert b"joy" in response.data.lower() or b"Dominant emotion" in response.data


def test_emotion_detector_post_empty_text(client):
    response = client.post("/emotionDetector", data={"text": ""})
    assert response.status_code == 400


def test_emotion_detector_post_missing_field(client):
    # No "text" field in the form at all -- exercises request.form.get()
    # returning None rather than raising KeyError.
    response = client.post("/emotionDetector", data={})
    assert response.status_code == 400


def test_api_emotion_valid_text(client):
    response = client.get("/api/emotion", query_string={"text": "I am thrilled!"})
    assert response.status_code == 200
    data = response.get_json()
    assert "dominant_emotion" in data
    assert data["dominant_emotion"] == "joy"


def test_api_emotion_missing_text(client):
    response = client.get("/api/emotion")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_404_handler(client):
    response = client.get("/this-route-does-not-exist")
    assert response.status_code == 404
    assert "error" in response.get_json()
