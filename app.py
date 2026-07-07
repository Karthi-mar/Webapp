"""
Flask app: routes and request handling only.

All emotion-detection logic lives in emotion_detector.py. This file's job is
strictly HTTP: parsing requests, calling detect_emotion(), and shaping
responses (HTML or JSON). Keeping that split means emotion_detector.py stays
testable with zero Flask involved, and app.py stays easy to scan for anyone
looking at "what does this endpoint do".
"""

import os

from flask import Flask, render_template, request, jsonify

from emotion_detector import detect_emotion, EmotionDetectionError

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    """Render the empty form. No emotion data yet on first load."""
    return render_template("index.html", result=None)


@app.route("/emotionDetector", methods=["POST"])
def emotion_detector_route():
    """Handle the HTML form submission and re-render the page with results.

    Uses request.form.get(...) instead of request.form["text"] — bracket
    access raises an uncaught KeyError (-> ugly 500) if the field is ever
    missing, e.g. a malformed request or a future template change that
    renames the input. .get() just returns None, which we can check for
    ourselves and turn into a clean 400.
    """
    text = request.form.get("text")

    if not text or not text.strip():
        # Re-render the same page with an error message and a 400 status,
        # rather than redirecting or returning bare JSON — the user is
        # sitting in a browser looking at the form, so the response should
        # still be the page they were on.
        return render_template(
            "index.html", result=None, error="Please enter some text."
        ), 400

    try:
        result = detect_emotion(text)
    except EmotionDetectionError as exc:
        # Our own exception type means "the input was bad" or "the model
        # call failed cleanly" — either way it's safe to show the message.
        return render_template("index.html", result=None, error=str(exc)), 400
    except Exception:
        # Anything else is unexpected (out-of-memory, a bug, etc.). Don't
        # leak internal exception details to the browser — that can expose
        # implementation details or stack traces to end users. Log it
        # server-side instead so we (the developer) can still debug it.
        app.logger.exception("Unexpected error in /emotionDetector")
        return render_template(
            "index.html", result=None, error="Something went wrong. Please try again."
        ), 500

    return render_template("index.html", result=result, error=None, text=text)


@app.route("/api/emotion", methods=["GET"])
def api_emotion():
    """JSON API endpoint, e.g. GET /api/emotion?text=hello.

    Mirrors /emotionDetector's logic but for programmatic callers (curl,
    Postman, another service) rather than a browser form — so it takes a
    query parameter via request.args and always returns JSON, never HTML.
    """
    text = request.args.get("text")

    if not text or not text.strip():
        return jsonify({"error": "Missing or empty 'text' query parameter."}), 400

    try:
        result = detect_emotion(text)
    except EmotionDetectionError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        app.logger.exception("Unexpected error in /api/emotion")
        return jsonify({"error": "Internal server error."}), 500

    return jsonify(result)


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Not found."}), 404


@app.errorhandler(500)
def server_error(_error):
    return jsonify({"error": "Internal server error."}), 500


if __name__ == "__main__":
    # host="0.0.0.0" so the server is reachable from outside the container
    # (required for Hugging Face Spaces / Docker); port 7860 is the port
    # Hugging Face Spaces expects Docker Spaces to listen on.
    #
    # debug defaults to off. Flask's debug mode exposes an interactive
    # debugger in the browser on unhandled exceptions -- great locally, but
    # a remote code execution risk if it's ever reachable on the public
    # internet (as it would be once deployed to a Space). Opt into it
    # explicitly for local dev with: FLASK_DEBUG=1 python app.py
    debug_mode = os.environ.get("FLASK_DEBUG") == "1"
    app.run(host="0.0.0.0", port=7860, debug=debug_mode)
