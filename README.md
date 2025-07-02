TimeMate: AI Meeting Scheduler
---
TimeMate is an AI-powered chatbot built with Streamlit + LangGraph that understands natural language to schedule meetings, check your calendar, and handle smart patterns like next weekend, every Monday, and 4 July from 10 AM to 11 AM.

It works even without Google Calendar API — perfect for deployed demos!

Features
---
✅ Natural language scheduling
✅ Location detection: at Zoom, with team at Skype
✅ Fallback safety without Google API (local-only booking notice)
✅ Deployable on Streamlit Cloud

Example Command	: What It Does:
---
Book a meeting tomorrow at 3 PM: Schedules a 1-hour meeting tomorrow
Schedule 2nd July at 10 AM:	Books on a specific future date
Set a call this weeken:	Automatically chooses Saturday 10 AM
Plan something next Monday:	Finds next Monday at 10 AM
Book 4 July from 10 AM to 11 AM: Detects exact time range
Demo call for 30 minutes:	Handles custom duration
Meeting with Ali at Zoom:	Adds “Zoom” as the meeting location
Standup every Monday:	Creates a recurring weekly meeting

Folder Structure
---
├── app.py                 # Streamlit app entry point
├── agent_graph.py         # LangGraph logic with router
├── calendar_tools.py      # Time parsing + booking logic
├── backend.py             # Optional FastAPI backend (for local booking)
├── requirements.txt
└── README.md

Built by
Kabyashree Gogoi
