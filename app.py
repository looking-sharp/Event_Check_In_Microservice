from flask import Flask, jsonify, redirect, url_for, render_template, request 
from flask_cors import CORS
from database import init_db, get_db, create_form_from_json
from models import Form, FormField
import os
import uuid

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
        submission = {}

        for f in form.fields:
            name = f.field_name
            if hasattr(f, "options") and f.options:
                # Get all selected values as a list
                out = request.form.getlist(name)
                submission[name] = out if out else None
            else:
                # Single value field
                out = request.form.get(name)
                submission[name] = out if out != '' else None
        
        form.submissions.append(submission)
        db.commit()

    return jsonify({"message": f"submission for: {form_id} complete", "submission": submission}), 201

@app.route("/check-submissions", methods=["GET"])
def check_submissions():
    form_id = request.args.get("formID")
    if not form_id:
        return jsonify({"message": "no form ID provided"}), 400
    
    try:
        form_uuid = uuid.UUID(form_id.strip('"'))
    except ValueError:
        return jsonify({"message": "Invalid UUID format"}), 400

    with get_db() as db:
        form = db.query(Form).filter(Form.id == form_uuid).first()

        if not form:
            return jsonify({"message": "Form not found", "status_code": 404}), 404
        
        form_data = {
            "url_id": form.url_id,
            "event_id": form.event_id,
            "url_id": form.url_id,
            "form_name": form.form_name,
            "fields": [
                {
                    "field_id": f.field_id,
                    "field_type": f.field_type,
                    "field_name": f.field_name,
                }
                for f in form.fields]
        }

        submissions = form.submissions
        return render_template("showSubmissions.html", submissions=submissions, form=form_data)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5003"))
    init_db()
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)