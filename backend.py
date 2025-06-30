from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import json

app = FastAPI()

# Allow all CORS (for Streamlit frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_calendar_service():
    """Authenticate using token.json and return calendar service."""
    with open("token.json", "r") as token:
        creds_data = json.load(token)
    creds = Credentials.from_authorized_user_info(creds_data)
    return build("calendar", "v3", credentials=creds)

@app.post("/book")
def book_meeting(title: str, start: str, end: str):
    """Book a calendar event."""
    service = get_calendar_service()
    event = {
        "summary": title,
        "start": {
            "dateTime": start,
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": end,
            "timeZone": "Asia/Kolkata"
        }
    }
    created = service.events().insert(calendarId="primary", body=event).execute()
    return {"message": "Event created", "htmlLink": created.get("htmlLink")}

@app.get("/available")
def get_events(start: str = None, end: str = None):
    """Fetch events from the user's calendar."""
    service = get_calendar_service()
    if not start:
        start = datetime.utcnow().isoformat() + "Z"
    if not end:
        end = (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z"
    events = service.events().list(
        calendarId="primary",
        timeMin=start,
        timeMax=end,
        singleEvents=True,
        orderBy="startTime"
    ).execute().get("items", [])
    return {"events": events}
