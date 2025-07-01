from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from calendar_tools import book_event, check_availability
from textblob import TextBlob


def detect_intent(state: dict) -> str:
    raw_input = state.get("input", "").strip()

    # ✨ Auto-correct typos using TextBlob
    corrected_input = str(TextBlob(raw_input).correct()).lower().strip()
    print(f"🔍 Corrected input: {corrected_input}")

    book_keywords = [
        "book", "schedule", "meeting", "set up", "call", "meet", "appointment", "arrange",
        "reserve", "organize", "setup", "fix", "make", "plan", "invite", "slot", "reserve time",
        "block", "calendar", "schedule call", "book time", "set meeting", "create meeting", "meeting"
    ]

    check_keywords = [
        "free", "available", "availability", "calendar", "check", "show", "see", "open",
        "do i have", "what's on", "my schedule", "my meetings", "upcoming", "do i have time",
        "any meetings", "any events", "when", "am i free", "my calendar"
    ]

    greeting_keywords = ["hi", "hello", "hey", "yo", "sup","greetings", "Hello", "Hi", "Hey", "Greetings", "howdy", "welcome", "good morning", "good afternoon", "good evening", "Welcome", "Thanks", "thank you", "thanks for your help", "thanks for helping me", "thank you for your help", "thank you for helping me", "thankyou", "Thank you", "Thank You","Wewlcome"]

    if any(kw in corrected_input for kw in book_keywords):
        return "book"
    elif any(kw in corrected_input for kw in check_keywords):
        return "check"
    elif any(corrected_input.startswith(greet) for greet in greeting_keywords):
        return "greeting"
    elif len(corrected_input.split()) <= 2:
        return "fallback"
    else:
        return "fallback"

def do_booking(state: dict):
    input_text = state.get("input", "")
    if not input_text:
        return {"input": input_text, "output": "❌ No input provided for booking."}
    result = book_event(input_text)
    return {"input": input_text, "output": result}


def do_availability(state: dict):
    input_text = state.get("input", "")
    result = check_availability()
    return {"input": input_text, "output": result}

def greeting_response(state: dict):
    return {
        "input": state.get("input", ""),
        "output": "👋 Hello! I'm your AI scheduling assistant.\nYou can say things like:\n- 'Book a meeting tomorrow at 3 PM'\n - Or type 'help' to see more examples!"
    }

def fallback_response(state: dict):
    input_text = state.get("input", "")
    return {
        "input": input_text,
        "output": "🤔 I'm not sure what you meant. Try: 'Book a meeting tomorrow at 3 PM'."
    }

def passthrough(state: dict):
    return state


def build_agent():
    builder = StateGraph(dict)
    builder.add_node("router", RunnableLambda(passthrough))
    builder.add_node("book", RunnableLambda(do_booking))
    builder.add_node("check", RunnableLambda(do_availability))
    builder.add_node("greeting", RunnableLambda(greeting_response))
    builder.add_node("fallback", RunnableLambda(fallback_response))

    builder.set_entry_point("router")

    builder.add_conditional_edges("router", detect_intent, {
        "book": "book",
        "check": "check",
        "greeting": "greeting",
        "fallback": "fallback"
    })

    builder.add_edge("book", END)
    builder.add_edge("check", END)
    builder.add_edge("greeting", END)
    builder.add_edge("fallback", END)

    return builder.compile()
