from flask import Flask, jsonify, redirect, url_for, render_template, request 
from flask_cors import CORS
from database import init_db, get_db, create_form_from_json
from models import Form, FormField
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
                    "field_name": "string",
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

@app.route("/check-in/<form_id>", methods=["GET", "POST"])
def check_in(form_id):
    if request.method == "GET":
        return render_template("checkIn.html", form_id=form_id)

@app.route("/get-form/<form_id>", methods=["GET"])
def get_event(form_id):
    with get_db() as db:
        form = db.query(Form).filter(Form.url_id == form_id).first()

        if not form:
            return jsonify({"message": "Form not found", "status_code": 404}), 404
        
        result = {
            "id": str(form.id),
            "event_id": form.event_id,
            "url_id": form.url_id,
            "form_name": form.form_name,
            "submissions": form.submissions or [],
            "fields": [
                {
                    "id": str(f.id),
                    "field_id": f.field_id,
                    "field_type": f.field_type,
                    "field_name": f.field_name,
                    "label": f.label,
                    "value": f.value,
                    "required": f.required,
                    "options": f.options
                }
                for f in form.fields
            ],
            "status_code": 200
        }
        return jsonify(result), 200

@app.route("/submit-check-in-form", methods=["POST"])
def submit_check_in_form():
    form_id = request.form.get("form_id")
    with get_db() as db:
        form = db.query(Form).filter(Form.url_id == form_id).first()

        if not form:
            return jsonify({"message": "Form not found", "status_code": 404}), 404
        
        # create list of all the names of th fields in the form
        field_names = [f.field_name for f in form.fields]
        submission = {}
        for name in field_names:
            out = request.form.get(f"{name}")
            submission[f"{name}"] = out if out != '' else None
        
        form.submissions.append(submission)

    return jsonify({"message": f"submission for: {form_id} complete", "submission": submission}), 201

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5003"))
    init_db()
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)