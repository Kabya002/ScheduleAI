import streamlit as st
from agent_graph import build_agent
from calendar_tools import get_help_message
import traceback

st.set_page_config(page_title="🤖 TimeMate Scheduler")
st.title("🤖 TimeMate: Schedule Smarter with AI")

agent = build_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ask me to book or check your schedule")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    if user_input.lower().strip() in ["help", "?"]:
        response = get_help_message()
    else:
        try:
            result = agent.invoke({"input": user_input})
            st.code(f"📤 Raw agent result:\n{result}", language="json")

            if result is None:
                response = "❌ Agent returned None. The graph may not be running correctly."
            elif not isinstance(result, dict):
                response = f"⚠️ Agent returned non-dict: {type(result)}"
            elif "output" not in result:
                response = f"⚠️ No 'output' in result: {result}"
            else:
                response = result["output"]
        except Exception as e:
            response = f"❌ Agent failed: {str(e)}\n\n```{traceback.format_exc()}```"

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)

st.markdown("<small>Type 'help' to see example commands</small>", unsafe_allow_html=True)
