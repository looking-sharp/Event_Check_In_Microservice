from flask import Flask, jsonify, redirect, url_for, render_template, request 
from flask_cors import CORS
from database import init_db, get_db, create_form_from_json
from models import Form, FormField
from qrcode_generator import create_qr_code
from scheduler import start_scheduler
from premailer import Premailer
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

@app.route("/create-check-in-form", methods=["POST"])
def create_form():
    """ HTTP Request that takes in an JSON package and creates 
        a custom HTML form based on the reuest

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
    data = request.get_json(force=True, silent=True) or {}
    with get_db() as db:
        return create_form_from_json(db, data)

@app.route("/get-check-in-front-page", methods=["GET"])
def get_front_page():
    """ HTTP route that renders the home page for a
        form with given form ID
    """
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
        
        url = f"{request.host_url}check-in/{form.url_id}"
        qr = create_qr_code(url)
        return render_template("frontPage.html", svg_str=qr, url=url, event_name=form.form_name)


@app.route("/check-in/<url_id>", methods=["GET", "POST"])
def check_in(url_id):
    """ HTTP Request to get the check in form for a
        given url_id
    """
    if request.method == "GET":
        return render_template("checkIn.html", url_id=url_id)

@app.route("/get-form/<url_id>", methods=["GET"])
def get_event(url_id):
    """ HTTP request that gets the serialized version of a 
        form 
    """
    with get_db() as db:
        form = db.query(Form).filter(Form.url_id == url_id).first()

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
    """ HTTP request that records the submissions from a form
        and saves it to the database
        
        Args: 
            form_id (str): the form's id
    """
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

def get_submissions_html(form_uuid) -> str:
    """ HTTP request to get all the submissions from a form
        and return the HTML file as a string with embedded CSS
    """
    with get_db() as db:
        form = db.query(Form).filter(Form.id == form_uuid).first()
        if not form:
            return "Form not found"
        
        form_data = {
            "url_id": form.url_id,
            "event_id": form.event_id,
            "form_name": form.form_name,
            "fields": [
                {
                    "field_id": f.field_id,
                    "field_type": f.field_type,
                    "field_name": f.field_name,
                }
                for f in form.fields
            ]
        }
        submissions = form.submissions
        html_str = render_template("showSubmissions.html", submissions=submissions, form=form_data)
        p = Premailer(
            html_str,
            base_url=request.host_url,
            allow_loading_external_files=True,
        )
        html_inlined = p.transform()
        return html_inlined.replace("\n", "")

@app.route("/check-submissions", methods=["GET"])
def check_submissions():
    """ HTTP request to get all the submissions from a form
        and return the HTML file as a string with embedded CSS or
        render them.
    """
    form_id = request.args.get("formID")
    if not form_id:
        return jsonify({"message": "no form ID provided"}), 400
    try:
        form_uuid = uuid.UUID(form_id.strip('"'))
    except ValueError:
        return jsonify({"message": "Invalid UUID format"}), 400
    
    asString = request.args.get("asString")
    if bool(asString):
        return jsonify({"html": get_submissions_html(form_uuid)}), 200

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

@app.route("/delete-form", methods=["POST"])
def delete_form():
    """ HTTP request to delete a form with a given form id

        Args: 
            form_id (str): the form's id
    """
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
        
        db.delete(form)
        return jsonify({"message": "Form sucessfully deleted"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5003"))
    init_db()
    start_scheduler()
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)