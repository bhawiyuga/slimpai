import streamlit as st
import asyncio
from google.genai import types
from google.adk.runners import Runner
from agent import root_agent
from google.adk.sessions import InMemorySessionService

# Configure the page
st.set_page_config(
    page_title="Math Learning Assistant",
    page_icon="🎓",
    layout="wide"
)

# Define constants for identifying the interaction context
APP_NAME = "slimpai_app"
USER_ID = "user_1"
SESSION_ID = "session_001"


async def initialize_runner_async(session_id: str = SESSION_ID):
    """Initialize the runner with a new session asynchronously."""
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id
    )
    return Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service
    )


def initialize_runner(session_id: str = SESSION_ID):
    """Wrapper to initialize runner in a new event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        runner = loop.run_until_complete(initialize_runner_async(session_id))
        return runner
    finally:
        loop.close()


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_id" not in st.session_state:
    st.session_state.user_id = USER_ID

if "session_id" not in st.session_state:
    st.session_state.session_id = SESSION_ID

if "runner" not in st.session_state:
    st.session_state.runner = initialize_runner(SESSION_ID)


async def send_message_async(user_input: str):
    """Send a message to the agent and get the response."""
    # Create user message content
    content = types.Content(role='user', parts=[types.Part(text=user_input)])
    
    final_response_text = "Agent did not produce a final response."
    
    # Run the agent asynchronously
    async for event in st.session_state.runner.run_async(
        user_id=st.session_state.user_id,
        session_id=st.session_state.session_id,
        new_message=content
    ):
        # Check if this is the final response
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break
    
    return final_response_text


def send_message(user_input: str):
    """Wrapper to run async function in a new event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(send_message_async(user_input))
        return result
    finally:
        loop.close()


def main():

    st.title("🎓 Math Learning Assistant")
    st.markdown("Welcome to your personalized math learning journey!")
    
    # Sidebar with information
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This is your AI-powered math tutor that will:
        - Assess your current knowledge
        - Create a personalized lesson plan
        - Teach you with fun analogies
        - Quiz you to check understanding
        """)
        
        st.divider()
        
        # Session info
        st.subheader("Session Info")
        st.text(f"User ID: {st.session_state.user_id}")
        st.text(f"Session ID: {st.session_state.session_id}")
        
        # Reset button
        if st.button("🔄 Start New Session", use_container_width=True):
            st.session_state.messages = []
            # Create new session with incremented ID
            new_session_id = f"session_{int(st.session_state.session_id.split('_')[-1]) + 1:03d}"
            st.session_state.runner = initialize_runner(new_session_id)
            st.session_state.session_id = new_session_id
            st.rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Run async function with new event loop
                response = send_message(prompt)
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Rerun to update the chat
        st.rerun()


if __name__ == "__main__":
    asyncio.run(main())
