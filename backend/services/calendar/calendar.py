from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import set_key
import logging
from backend.services.courses.canvas_scraper import Assignment, get_canvas_assignments

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

SCOPES = ["https://www.googleapis.com/auth/calendar"]

BASE_DIR = Path(__file__).parent
TOKEN_PATH = BASE_DIR / "token.json"
CREDENTIALS_PATH = BASE_DIR / "credentials.json"


def get_calendar_service():
    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(
            str(TOKEN_PATH), SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH),
                SCOPES,
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)

def get_or_create_canvas_calendar(service=None):
    if service is None:
        service = get_calendar_service()

    calendars = service.calendarList().list().execute()

    for calendar in calendars["items"]:
        if calendar["summary"] == "Canvas Assignments":
            logger.info(f"Using existing calendar: {calendar['id']}")
            return calendar["id"]

    # Doesn't exist, create it
    new_calendar = {
        "summary": "Canvas Assignments",
        "timeZone": "Asia/Hong_Kong",
    }

    created = service.calendars().insert(body=new_calendar).execute()

    logger.info(f"Created new calendar: {created['id']}")
    return created["id"]


def add_assignments_to_calendar(assignments : list[Assignment]):
    """This function adds a list of assignments to the Google Calendar that has the specified calendar id"""
    service = get_calendar_service()
    calendar_id = get_or_create_canvas_calendar(service)
    logger.info(f"Fetching existing events from calendar with ID: {calendar_id}")
    existing_events = service.events().list(calendarId=calendar_id).execute().get("items", [])
    existing = {(event["summary"], datetime.fromisoformat(

            event["start"]["dateTime"].replace("Z", "+00:00")

        ).astimezone(timezone.utc)) for event in existing_events}
    logger.info(f"Found {len(existing)} existing events in the calendar to avoid duplicates.")
    for i, assignment in enumerate(assignments):
        print(f"\nAssignment {i}: {assignment.title}")
        if assignment.due_date is None: # skip assignments without due dates
            logger.info(f"Skipping assignment '{assignment.title}' as it has no due date.")
            continue
        if (assignment.title, assignment.due_date.astimezone(timezone.utc)) in existing:
            logger.info(f"Skipping duplicate assignment '{assignment.title}' with due date '{assignment.due_date.isoformat()}'.")
            continue
        key = (assignment.title, assignment.due_date.astimezone(timezone.utc))
        existing.add(key)  # Add to existing to prevent duplicates in the same run
        event = {
            "summary": assignment.title,
            "description": assignment.description,
            "start": {
                "dateTime": assignment.due_date.isoformat(),
                "timeZone": "Asia/Hong_Kong",
            },
            "end": {
                "dateTime": (assignment.due_date + timedelta(minutes=60)).isoformat(),
                "timeZone": "Asia/Hong_Kong",
            },
        }

        print("Inserting...")
        try:
            service.events().insert(calendarId=calendar_id, body=event,).execute()
        except Exception as e:
            logger.error(f"Failed to insert assignment '{assignment.title}': {e}")
            continue

    print("Done.")
    logger.info(f"Added {len(assignments)} assignments to Google Calendar with ID: {calendar_id}")

def debug_google_calendar():

    print("\n========== GOOGLE CALENDAR DEBUG ==========\n")

    print("Token exists:", TOKEN_PATH.exists())

    print("Credentials exists:", CREDENTIALS_PATH.exists())

    if not TOKEN_PATH.exists():

        print("No token.json found.")

        return

    creds = Credentials.from_authorized_user_file(

        str(TOKEN_PATH),

        SCOPES

    )

    print("\n--- Credential state ---")

    print("valid          :", creds.valid)

    print("expired        :", creds.expired)

    print("refresh_token  :", creds.refresh_token is not None)

    print("token_uri      :", creds.token_uri)

    print("client_id      :", creds.client_id[:20] + "...")

    print("scopes         :", creds.scopes)

    print("\n--- Refreshing if needed ---")

    try:

        if creds.expired and creds.refresh_token:

            print("Refreshing...")

            creds.refresh(Request())

            print("Refresh successful.")

        else:

            print("No refresh needed.")

    except Exception as e:

        print("Refresh failed:")

        print(type(e).__name__, e)

        return

    print("\n--- Building service ---")

    try:

        service = build("calendar", "v3", credentials=creds)

        print("Service built.")

    except Exception as e:

        print("Build failed:")

        print(type(e).__name__, e)

        return

    print("\n--- Listing calendars ---")

    try:

        calendars = service.calendarList().list().execute()

        print("Calendar request succeeded.")

        print("Found", len(calendars.get("items", [])), "calendars")

    except Exception as e:

        print("Calendar request failed:")

        print(type(e).__name__, e)

        return

    print("\n--- Creating test calendar ---")

    try:

        created = service.calendars().insert(

            body={

                "summary": "DEBUG TEST",

                "timeZone": "Asia/Hong_Kong",

            }

        ).execute()

        print("Created:", created["id"])

    except Exception as e:

        print("Create calendar failed:")

        print(type(e).__name__, e)

        return

    print("\n========== END DEBUG ==========\n")


if __name__ == "__main__":
    assignments_list = get_canvas_assignments()
    add_assignments_to_calendar(assignments_list)
