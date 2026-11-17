"""Run the research assistant locally with ``python app.py``."""

from pathlib import Path
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv(Path(__file__).with_name(".env"))

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/research")
def research():
    data = request.get_json(silent=True)
    topic = data.get("topic") if isinstance(data, dict) else None
    if not isinstance(topic, str) or not topic.strip():
        return jsonify(error="Please enter a research topic."), 400
    topic = topic.strip()
    if len(topic) > 500:
        return jsonify(error="Please keep your topic within 500 characters."), 400

    if not all(os.getenv(key) for key in ("OPENAI_API_KEY", "TAVILY_API_KEY")):
        return jsonify(error="Set OPENAI_API_KEY and TAVILY_API_KEY in your .env file, then restart the app."), 503

    try:
        # Load agents only when needed so the UI can open before keys are set.
        from src.pipelines.agents_pipeline import research_pipeline

        result = research_pipeline(topic=topic)
        return jsonify(topic=topic, **result)
    except Exception:
        app.logger.exception("Research pipeline failed")
        return jsonify(error="Research could not be completed. Check the server logs and your API configuration, then try again."), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
