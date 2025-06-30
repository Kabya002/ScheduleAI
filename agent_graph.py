from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from calendar_tools import book_event, check_availability

class AgentState(dict):
    pass

def detect_intent(state: AgentState) -> str:
    user_input = state.get("input", "").lower()
    if any(word in user_input for word in ["book", "schedule", "set up", "meeting"]):
        return "book"
    elif any(word in user_input for word in ["free", "available", "availability", "check", "calendar", "busy"]):
        return "check"
    else:
        return "fallback"

def do_booking(state: AgentState):
    input_text = state.get("input", "")
    if not input_text:
        return {"output": "❌ No input provided for booking."}
    result = book_event(input_text)
    return {"output": result}

def do_availability(state: AgentState):
    result = check_availability()
    return {"output": result}

def fallback_response(state: AgentState):
    return {"output": "🤔 I'm not sure what you meant. Try: 'Book a meeting tomorrow at 3 PM' or 'Check availability this week'."}

def passthrough(state: AgentState):
    return state

def build_agent():
    builder = StateGraph(AgentState)

    builder.add_node("router", RunnableLambda(passthrough))
    builder.add_node("book", RunnableLambda(do_booking))
    builder.add_node("check", RunnableLambda(do_availability))
    builder.add_node("fallback", RunnableLambda(fallback_response))

    builder.set_entry_point("router")

    builder.add_conditional_edges("router", detect_intent, {
        "book": "book",
        "check": "check",
        "fallback": "fallback"
    })

    builder.add_edge("book", END)
    builder.add_edge("check", END)
    builder.add_edge("fallback", END)

    return builder.compile()
