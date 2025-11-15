from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from contextlib import contextmanager
from flask import jsonify
from datetime import datetime, timedelta
import os
import secrets

from models import Base, Form, FormField # Import from models.py

# ------------------------
#   ENV + ENGINE SETUP
# ------------------------

load_dotenv()

# Path setup
basedir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.dirname(basedir)
db_filename = "checkin.db"

# Full absolute path to the database inside the container
default_db_path = os.path.join(parent_dir, "data", db_filename)
print(default_db_path)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{default_db_path}")

# Ensure folder exists
os.makedirs(os.path.dirname(default_db_path), exist_ok=True)

# Database engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Create session 
SessionLocal = sessionmaker(
    bind=engine, 
    autocommit=False, 
    autoflush=False
)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Session:
    """
    Return a new database session.
    Use `with get_db() as db:` to close automatically
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def add_to_db(session, instance, return_bool=False):
    """
    Add and commit a new record to the database.

    Returns:
        If return_bool=True: (bool): True on success, False on failure.
        Else: (instance) returns the instance.
    """
    try:
        session.add(instance)
        session.commit()
        session.refresh(instance)
        return True if return_bool else instance
    except Exception as e:
        session.rollback()
        if return_bool:
            return False
        raise e

def create_url_id(session: Session, length: int = 12) -> str:
    """Create short for URL"""
    _id = secrets.token_urlsafe(length)[:length]
    while session.query(Form).filter(Form.url_id == _id).first() is not None:
        _id = secrets.token_urlsafe(length)[:length]
    return _id
    

def create_form_from_json(session: Session, data: dict):
    #Verify data
    expected_keys = ["event_id", "event_name", "event_date", "fields"]
    for key in expected_keys:
        if data.get(key) is None:
            return jsonify({"message": f"Request must include {key}"}), 400

    for key, value in data.items():
        if key not in expected_keys:
            return jsonify({"message": f"Unexpcted Key: {key} found"}), 400
        elif value == None:
            return jsonify({"message": f"{key} cannot be None"}), 400

    for field in data.get("fields"):
        if field.get("label") is None:
            return jsonify({"message": "All fields must have a label"}), 400

    # Create Form
    form = Form(
        event_id=data.get("event_id"),
        url_id = create_url_id(session),
        form_name=data.get("event_name"),
        delete_on= datetime.fromisoformat(data.get("event_date")) + timedelta(days=1),
        submissions=[]
    )

    session.add(form)
    session.flush()

    id_itr = 0
    for field in data.get("fields", []):
        id_itr = id_itr + 1
        new_field = FormField(
            form_id = form.id,
            field_id = field.get("field_id", id_itr),
            field_type = field.get("field_type", "text"),
            label = field.get("label"),
            required = field.get("required", False)
        )
        session.add(new_field)
    
    session.commit()
    data = {
        "message": "form created successfully",
        "form_id": form.id,
        "form_url_id": form.url_id,
        "form_expires_on": form.delete_on
    }
    return jsonify(data), 200