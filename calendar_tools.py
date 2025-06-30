# 📁 File: calendar_tools.py
from datetime import datetime, timedelta
import requests
import re
from dateutil import parser as dateutil_parser
import pytz
from parsedatetime import Calendar
from dateutil.rrule import rrule, WEEKLY, MO, TU, WE, TH, FR, SA, SU

LOCAL_TIMEZONE = pytz.timezone("Asia/Kolkata")

nonsense_keywords = ["frooday", "blarg", "xzy", "nani", "asdf"]

weekday_map = {
    "monday": MO, "tuesday": TU, "wednesday": WE, "thursday": TH,
    "friday": FR, "saturday": SA, "sunday": SU
}

def extract_duration(text):
    match = re.search(r"(\d{1,2})\s*(minutes?|hours?)", text, re.IGNORECASE)
    if match:
        value, unit = match.groups()
        if "hour" in unit.lower():
            return timedelta(hours=int(value))
        else:
            return timedelta(minutes=int(value))
    return timedelta(hours=1)

def extract_time_range(text):
    match = re.search(r"from\s+(\d{1,2}(?::\d{2})?\s*(am|pm)?)\s+to\s+(\d{1,2}(?::\d{2})?\s*(am|pm)?)", text, re.IGNORECASE)
    if match:
        return match.group(1), match.group(3)
    return None, None

def clean_ordinal_suffixes(text):
    return re.sub(r'(\d+)(st|nd|rd|th)', r'\1', text, flags=re.IGNORECASE)

def extract_time_phrase(text):
    patterns = [
        r"(this|next)\s+weekend",  # ✅ NEW pattern for "this weekend", "next weekend"
        r"every\s+\w+",
        r"\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+from\s+\d{1,2}(:\d{2})?\s?(am|pm)?\s+to\s+\d{1,2}(:\d{2})?\s?(am|pm)?",
        r"\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+between\s+\d{1,2}(:\d{2})?\s?(am|pm)?\s+and\s+\d{1,2}(:\d{2})?\s?(am|pm)?",
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
    if "standup" in raw.lower(): return "Weekly Standup"
    if "demo" in raw.lower(): return "Product Demo"
    if "1:1" in raw.lower() or "one-on-one" in raw.lower(): return "1:1 Sync"
    if "catchup" in raw.lower(): return "Team Catch-up"
    return cleaned or "Meeting with TimeMate"

def book_event(input_text):
    cal = Calendar()
    print(f"📥 Original input: {input_text}")
    
    if any(word in input_text.lower() for word in nonsense_keywords):
        return "❌ That doesn't seem like a real date or time. Please rephrase."

    time_phrase = extract_time_phrase(input_text)
    print(f"⏳ Extracted time phrase: {time_phrase}")
    cleaned_phrase = clean_ordinal_suffixes(time_phrase)
    print(f"🧼 Cleaned time phrase: {cleaned_phrase}")

    parsed_time = None
    recurrence = None

    # Handle recurring logic like "every Monday"
    if "every" in cleaned_phrase:
        match = re.search(r"every\s+(\w+)", cleaned_phrase)
        if match and match.group(1).lower() in weekday_map:
            rule = rrule(WEEKLY, byweekday=weekday_map[match.group(1).lower()], dtstart=datetime.now())
            parsed_time = rule[0].replace(hour=10, minute=0)
            recurrence = [f"RRULE:FREQ=WEEKLY;BYDAY={match.group(1)[:2].upper()}"]

    if not parsed_time and cleaned_phrase:
        try:
            lower_input = input_text.lower()
            relative_keywords = ["tomorrow", "today", "next", "this"]

            if any(word in cleaned_phrase.lower() for word in relative_keywords):
                parsed_time, success = cal.parseDT(cleaned_phrase, sourceTime=datetime.now())
                if not success or parsed_time < datetime.now():
                    parsed_time = None
            if not parsed_time:
                if "this weekend" in lower_input:
                    today = datetime.now()
                    weekday = today.weekday()
                    if weekday >= 5:  # Today is already the weekend
                        parsed_time = today.replace(hour=10, minute=0)
                    else:
                        days_ahead = (5 - weekday) % 7  # Move to Saturday
                        parsed_time = today + timedelta(days=days_ahead)
                        parsed_time = parsed_time.replace(hour=10, minute=0)
                elif "weekend" in lower_input:
                    today = datetime.now()
                    days_ahead = (5 - today.weekday()) % 7
                    parsed_time = today + timedelta(days=days_ahead)
                    parsed_time = parsed_time.replace(hour=10, minute=0)

                elif "this friday" in lower_input:
                    today = datetime.now()
                    days_ahead = (4 - today.weekday()) % 7
                    parsed_time = today + timedelta(days=days_ahead)
                    parsed_time = parsed_time.replace(hour=10, minute=0)

            if not parsed_time:
                parsed_time = dateutil_parser.parse(cleaned_phrase, fuzzy=True)

        except Exception as e:
            print(f"❌ Parsing error: {e}")
            parsed_time = None

    # Final fallback for time-only like "at 3 PM"
    if not parsed_time:
        start_str, end_str = extract_time_range(input_text)
        if start_str and end_str:
            try:
                now = datetime.now()
                today_fmt = now.strftime('%Y-%m-%d')
                test_start = dateutil_parser.parse(f"{today_fmt} {start_str}")
                if test_start < now:
                    test_start += timedelta(days=1)
                parsed_time = test_start.replace(minute=0, second=0, microsecond=0)
            except:
                parsed_time = datetime.now() + timedelta(days=1)
                parsed_time = parsed_time.replace(hour=10, minute=0)
    # Final backup
    if not parsed_time:
        return "❌ Sorry, I couldn’t understand the date or time. Please rephrase."

    # Set timezone
    parsed_time = parsed_time if parsed_time.tzinfo else LOCAL_TIMEZONE.localize(parsed_time)
    now = datetime.now(LOCAL_TIMEZONE)

    # Sanity checks
    if parsed_time.year < now.year or parsed_time < now - timedelta(days=1):
        return "❌ The date you mentioned seems incorrect. Please try again."
    if parsed_time < now:
        parsed_time += timedelta(days=1)

    # Time range or duration
    start_str, end_str = extract_time_range(input_text)
    if start_str and end_str:
        try:
            today_fmt = parsed_time.strftime('%Y-%m-%d')
            start_dt = dateutil_parser.parse(f"{today_fmt} {start_str}")
            end_dt = dateutil_parser.parse(f"{today_fmt} {end_str}")
        except Exception as e:
            print(f"⚠️ Time range parse failed: {e}")
            start_dt = parsed_time
            end_dt = start_dt + extract_duration(input_text)
    else:
        start_dt = parsed_time
        end_dt = start_dt + extract_duration(input_text)

    start = start_dt.isoformat()
    end = end_dt.isoformat()

    title = extract_title(input_text, time_phrase)
    print(f"📌 Final title: {title}")

    try:
        payload = {
            "title": title,
            "start": start,
            "end": end,
            "location": re.search(r"at\s+(Zoom|Meet|Skype|\w+\.com)", input_text, re.IGNORECASE).group(1)
                if re.search(r"at\s+(Zoom|Meet|Skype|\w+\.com)", input_text, re.IGNORECASE) else "",
            "description": input_text
        }
        if recurrence:
            payload["recurrence"] = recurrence

        res = requests.post("http://127.0.0.1:8000/book", params=payload)
        res.raise_for_status()
        event = res.json()
        return (
            f"✅ Meeting booked for {parsed_time.strftime('%A, %d %B %Y at %I:%M %p')}\n"
            f"📅 [View in Google Calendar]({event.get('htmlLink')})"
        )
    except requests.RequestException as e:
        print(f"🌐 Google Calendar failed (likely on cloud): {e}")
        return (
            f"✅ Chatbot parsed your request for {parsed_time.strftime('%A, %d %B %Y at %I:%M %p')}.\n"
            f"⚠️ Google Calendar booking is only available in the **local version**.\n"
            f"🌐 This deployed demo shows the assistant workflow."
        )

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
    
def get_help_message():
    return (
        "📝 **Need help?** You can try these formats:\n"
        "• Book a meeting tomorrow at 3 PM\n"
        "• Schedule 2nd July at 10 AM\n"
        "• Plan something next Monday\n"
        "• Meeting at 2 PM\n"
        "• Demo call for 30 minutes\n"
        "• Meeting with Ali at Zoom\n"
        "• Set a call this weekend"
    )

