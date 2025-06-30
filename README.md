🤖 TimeMate: AI Meeting Scheduler
TimeMate is an AI-powered chatbot built with Streamlit + LangGraph that understands natural language to schedule meetings, check your calendar, and handle smart patterns like next weekend, every Monday, and 4 July from 10 AM to 11 AM.

It works even without Google Calendar API — perfect for deployed demos!

🚀 Features
✅ Natural language scheduling
✅ Recurring meetings like every Monday
✅ Time range detection: from 10 AM to 11 AM
✅ Duration support: for 30 minutes, 1 hour call
✅ Location detection: at Zoom, with team at Skype
✅ Fallback safety without Google API (local-only booking notice)
✅ Deployable on Streamlit Cloud

💬 Sample Commands You Can Use
Try typing these into the chatbot:

Example Command	What It Does
Book a meeting tomorrow at 3 PM	Schedules a 1-hour meeting tomorrow
Schedule 2nd July at 10 AM	Books on a specific future date
Set a call this weekend	Automatically chooses Saturday 10 AM
Plan something next Monday	Finds next Monday at 10 AM
Book 4 July from 10 AM to 11 AM	Detects exact time range
Demo call for 30 minutes	Handles custom duration
Meeting with Ali at Zoom	Adds “Zoom” as the meeting location
Standup every Monday	Creates a recurring weekly meeting

⚠️ No Google API? No Problem
If Google Calendar isn’t connected, TimeMate will:

Still parse your intent

Show you a friendly note that booking works in local version only

Let you test the full AI scheduling workflow

Example:

text
Copy
Edit
✅ Chatbot parsed your request for Saturday, 06 July 2025 at 10:00 AM.
⚠️ Google Calendar booking is only available in the local version.
🌐 This deployed demo shows the assistant workflow.
🛠 Setup (Local)
bash
Copy
Edit
git clone https://github.com/Kabya002/SchedulerAI.git
cd SchedulerAI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
🌍 Deploying to Streamlit Cloud
Push this repo to GitHub

Go to streamlit.io/cloud

Select your GitHub repo

Click “Deploy” 🎉

On cloud, bookings won’t hit Google API — but all logic will still run!

📂 Folder Structure
graphql
Copy
Edit
.
├── app.py                 # Streamlit app entry point
├── agent_graph.py         # LangGraph logic with router
├── calendar_tools.py      # Time parsing + booking logic
├── backend.py             # Optional FastAPI backend (for local booking)
├── requirements.txt
└── README.md
✨ Future Ideas
Add authentication and Google Calendar OAuth flow

Store meetings in MongoDB or Supabase for fallback

Add voice-to-text or chatbot speech support

👩‍💻 Built by
Kabyashree Gogoi