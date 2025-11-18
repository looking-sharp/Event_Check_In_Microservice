import threading
import time
from datetime import datetime, timezone, timedelta

from models import Form
from database import get_db

CHECK_INTERVAL_SECONDS = 60

def purge_logs(db):
    purge_date = datetime.now(timezone.utc)

    #Delete all logs after purge date
    db.query(Form).filter(
        Form.delete_on <= purge_date
    ).delete()

    db.commit()


def purge_outdated_thread():
    """ This function is the main loop for the scheduler. It looks
        through all the scheduled elogs to find ones that need to be
        deleted
    """
    while True:
        try:
            with get_db() as db:
                print(f"[scheduler] now={datetime.now(timezone.utc).isoformat()}")
                purge_logs(db)

        except Exception as outer:
            print(f"[scheduler] unexpected error: {outer}")

        time.sleep(CHECK_INTERVAL_SECONDS)


def start_scheduler():
    """Start a background thread that stops when the app stops."""
    t = threading.Thread(target=purge_outdated_thread, daemon=True)
    t.start()
    print("Check in purge started")
