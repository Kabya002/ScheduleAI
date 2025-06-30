from datetime import datetime, timedelta
import dateparser
import requests

def book_event(input_text):
    parsed_time = dateparser.parse(input_text, settings={'PREFER_DATES_FROM': 'future'})
    if not parsed_time:
        return "❌ I couldn't understand the date/time. Try something like 'Book a meeting tomorrow at 4 PM'."

    start = parsed_time.isoformat()
    end = (parsed_time + timedelta(hours=1)).isoformat()

    try:
        res = requests.post("http://127.0.0.1:8000/book", params={
            "title": "Meeting with TimeMate",
            "start": start,
            "end": end
        })
        if res.status_code == 200:
            event = res.json()
            return f"✅ Meeting booked for {parsed_time.strftime('%A, %d %B %Y at %I:%M %p')}\n📅 [View in Google Calendar]({event.get('htmlLink')})"
        else:
            return f"❌ Booking failed. Status code: {res.status_code}. Message: {res.text}"
    except Exception as e:
        return f"❌ Booking failed: {e}"

def check_availability():
    try:
        res = requests.get("http://127.0.0.1:8000/available")
        if res.status_code != 200:
            return f"❌ Failed to fetch events. Status code: {res.status_code}"
        events = res.json().get("events", [])
        if not events:
            return "🎉 You're totally free in the next few days!"
        response = "📅 Here are your upcoming events:\n"
        for e in events:
            name = e.get("summary", "No Title")
            start = e.get("start", {}).get("dateTime", "")
            if start:
                readable = start.replace("T", " ").split("+")[0]
                response += f"- **{name}** at `{readable}`\n"
        return response
    except Exception as e:
        return f"❌ Error fetching availability: {e}"
