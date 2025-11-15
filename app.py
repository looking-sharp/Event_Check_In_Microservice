from flask import Flask, jsonify, redirect, url_for, render_template, request 
from flask_cors import CORS
from database import init_db, get_db, create_form_from_json
import os

app = Flask(__name__)

allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5000").split(",")
CORS(app, resources={
    r"/*": {
        "origins": [o.strip() for o in allowed_origins if o.strip()],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.route("/health")
def health():
    return jsonify({"message": "Event Check In Microservice Online"}), 200


"""
    Args:
        Request (JSON):
        {
            "event_id": "string",
            "event_name": "string",
            "event_date": "DateTime",
            fields = [
                {
                    "field_id": "string",
                    "field_type": "string",
                    "label": "string",
                    "required": "boolean"
                },
                ...
            ]
        }
"""
@app.route("/create-check-in-form", methods=["POST"])
def create_form():
    data = request.get_json(force=True, silent=True) or {}
    with get_db() as db:
        return create_form_from_json(db, data)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5003"))
    init_db()
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)