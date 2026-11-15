from datetime import datetime, timezone
import os
import re
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

TAG_PATTERN = re.compile(r"^<t:(-?\d+)(?::([tTdDfFR]))?>$")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/decode", methods=["POST"])
def decode_timestamp():
    payload = request.get_json(silent=True) or {}
    raw = str(payload.get("input", "")).strip()

    if not raw:
        return jsonify({"error": "Empty input"}), 400

    match = TAG_PATTERN.match(raw)
    style = None
    if match:
        unix_val = int(match.group(1))
        style = match.group(2) or "default"
    else:
        try:
            unix_val = int(float(raw))
        except ValueError:
            return jsonify({"error": "Invalid Discord tag or Unix timestamp"}), 400

    if abs(unix_val) >= 100_000_000_000:
        unix_val //= 1000

    dt_utc = datetime.fromtimestamp(unix_val, tz=timezone.utc)
    return jsonify(
        {
            "unix": unix_val,
            "style": style,
            "iso_utc": dt_utc.isoformat(),
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)