# 📁 File: calendar_tools.py
from datetime import datetime, timedelta
import requests
import re
from dateutil import parser as dateutil_parser
import pytz

LOCAL_TIMEZONE = pytz.timezone("Asia/Kolkata")

nonsense_keywords = ["frooday", "blarg", "xzy", "nani", "asdf"]

def clean_ordinal_suffixes(text):
    return re.sub(r'(\d+)(st|nd|rd|th)', r'\1', text, flags=re.IGNORECASE)

def extract_time_phrase(text):
    patterns = [
        r"\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+at\s+\d{1,2}(:\d{2})?\s?(am|pm)?",
        r"\w+\s+\d{1,2}(?:st|nd|rd|th)?\s+at\s+\d{1,2}(:\d{2})?\s?(am|pm)?",
        r"(tomorrow|today|next\s+\w+)(\s+at\s+\d{1,2}(:\d{2})?\s?(am|pm)?)?",
        r"\d{1,2}(?:st|nd|rd|th)?\s+\w+",
        r"\w+\s+\d{1,2}(?:st|nd|rd|th)?",
        r"\d{1,2}(:\d{2})?\s?(am|pm)"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group()
    return ""

def extract_title(text, time_phrase):
    raw = text.replace(time_phrase, "").strip().title()
    cleaned = re.sub(r'\b(at|on|by|to|for)\b$', '', raw, flags=re.IGNORECASE).strip()
    return cleaned or "Meeting with TimeMate"

def book_event(input_text):
    from parsedatetime import Calendar
    cal = Calendar()

    print(f"📥 Original input: {input_text}")

    if any(word in input_text.lower() for word in nonsense_keywords):
        return "❌ That doesn't seem like a real date or time. Please rephrase."

    time_phrase = extract_time_phrase(input_text)
    print(f"⏳ Extracted time phrase: {time_phrase}")
    cleaned_phrase = clean_ordinal_suffixes(time_phrase)
    print(f"🧼 Cleaned time phrase: {cleaned_phrase}")

    parsed_time = None
    if cleaned_phrase:
        try:
            relative_keywords = ["tomorrow", "today", "next", "this"]
            if any(word in cleaned_phrase.lower() for word in relative_keywords):
                parsed_time, success = cal.parseDT(cleaned_phrase, sourceTime=datetime.now())
                if not success or parsed_time < datetime.now():
                    parsed_time = None
                    print("⚠️ parsedatetime failed or returned past date")
            if not parsed_time:
                    # Custom logic for "weekend", "this Friday", etc.
                    lower_input = input_text.lower()
                    if "weekend" in lower_input:
                        today = datetime.now()
                        days_ahead = (5 - today.weekday()) % 7  # Saturday
                        parsed_time = today + timedelta(days=days_ahead)
                        parsed_time = parsed_time.replace(hour=10, minute=0)
                    elif "this friday" in lower_input:
                        today = datetime.now()
                        days_ahead = (4 - today.weekday()) % 7  # Friday
                        parsed_time = today + timedelta(days=days_ahead)
                        parsed_time = parsed_time.replace(hour=10, minute=0)
                    if not parsed_time:
                        parsed_time = dateutil_parser.parse(cleaned_phrase, fuzzy=True)
        except Exception as e:
            print(f"❌ Parsing error: {e}")

    if not parsed_time:
        parsed_time = datetime.now() + timedelta(days=1)
        parsed_time = parsed_time.replace(hour=10, minute=0, second=0, microsecond=0)
        print("⏰ No valid time found, defaulting to tomorrow at 10 AM")

    if parsed_time.tzinfo is None:
        parsed_time = LOCAL_TIMEZONE.localize(parsed_time)
    else:
        parsed_time = parsed_time.astimezone(LOCAL_TIMEZONE)

    if parsed_time.year < datetime.now().year or parsed_time < datetime.now() - timedelta(days=1):
        return "❌ The date you mentioned seems incorrect. Please try again."

    # ⏰ Handle time-only fallback if in past
    if parsed_time and parsed_time < datetime.now():
        print("⚠️ Parsed time is in the past. Shifting to tomorrow same time.")
        parsed_time = parsed_time + timedelta(days=1)

    start = parsed_time.isoformat()
    end = (parsed_time + timedelta(hours=1)).isoformat()

    title = extract_title(input_text, time_phrase)
    print(f"📌 Final title: {title}")

    try:
        res = requests.post("http://127.0.0.1:8000/book", params={
            "title": title,
            "start": start,
            "end": end
        })
        res.raise_for_status()
        event = res.json()
        return (
            f"✅ Meeting booked for {parsed_time.strftime('%A, %d %B %Y at %I:%M %p')}\n"
            f"📅 [View in Google Calendar]({event.get('htmlLink')})"
        )
    except requests.RequestException as e:
        print(f"❌ Error booking event: {e}")
        return "❌ Failed to book the meeting. Please try again later."

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
