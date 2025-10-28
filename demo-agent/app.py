import streamlit as st
import aiohttp
import asyncio
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
ADK_API_URL = os.getenv("ADK_API_URL", "http://localhost:8000")
API_ENDPOINT = f"{ADK_API_URL}/run"

# Page configuration
st.set_page_config(
    page_title="Math Learning Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        color: #721c24;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        color: #0c5460;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
if "user_id" not in st.session_state:
    st.session_state.user_id = "user_1"
if "app_name" not in st.session_state:
    st.session_state.app_name = "demo-agent"
if "session_created" not in st.session_state:
    st.session_state.session_created = False


async def create_session() -> bool:
    """
    Create a new session with the ADK API server.
    
    Returns:
        True if session was created successfully, False otherwise
    """
    session_url = f"{ADK_API_URL}/apps/{st.session_state.app_name}/users/{st.session_state.user_id}/sessions/{st.session_state.session_id}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                session_url,
                json={"state": {}},
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status in [200, 201]:
                    return True
                else:
                    error_text = await response.text()
                    st.error(f"Failed to create session ({response.status}): {error_text}")
                    return False
    except Exception as e:
        st.error(f"Error creating session: {str(e)}")
        return False


async def send_message_to_adk(message: str) -> Optional[str]:
    """
    Send a message to the ADK API server and return the response.
    
    Args:
        message: The user's message to send
        
    Returns:
        The agent's response text, or None if there was an error
    """
    # Create session if not already created
    if not st.session_state.session_created:
        success = await create_session()
        if not success:
            return None
        st.session_state.session_created = True
    
    payload = {
        "app_name": st.session_state.app_name,
        "user_id": st.session_state.user_id,
        "session_id": st.session_state.session_id,
        "new_message": {
            "role": "user",
            "parts": [{"text": message}]
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                API_ENDPOINT,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Handle event list response format from /run endpoint
                    if isinstance(data, list):
                        # Extract text from the last model response in the event list
                        for event in reversed(data):
                            if isinstance(event, dict) and "content" in event:
                                content = event["content"]
                                if "parts" in content and content.get("role") == "model":
                                    parts = content["parts"]
                                    # Collect all text parts
                                    text_parts = []
                                    for part in parts:
                                        if "text" in part:
                                            text_parts.append(part["text"])
                                    if text_parts:
                                        return "\n".join(text_parts)
                        return "No response from agent"
                    
                    # Handle other possible response formats
                    elif isinstance(data, dict):
                        if "response" in data and "parts" in data["response"]:
                            parts = data["response"]["parts"]
                            if parts and len(parts) > 0 and "text" in parts[0]:
                                return parts[0]["text"]
                        elif "final_response" in data:
                            return data["final_response"]
                        elif "text" in data:
                            return data["text"]
                        else:
                            st.error(f"Unexpected response format: {json.dumps(data, indent=2)}")
                            return None
                    else:
                        st.error(f"Unexpected response type: {type(data)}")
                        return None
                else:
                    error_text = await response.text()
                    st.error(f"API Error ({response.status}): {error_text}")
                    return None
                    
    except aiohttp.ClientConnectorError:
        st.error(f"❌ Cannot connect to ADK API server at {ADK_API_URL}")
        st.info("Please ensure the ADK API server is running and accessible.")
        return None
    except asyncio.TimeoutError:
        st.error("⏱️ Request timed out. The server took too long to respond.")
        return None
    except Exception as e:
        st.error(f"❌ Error communicating with ADK API: {str(e)}")
        return None


def reset_session():
    """Reset the current session and start a new one."""
    st.session_state.messages = []
    st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    st.session_state.session_created = False
    st.rerun()


# Sidebar
with st.sidebar:
    st.title("🎓 Math Learning Assistant")
    st.markdown("---")
    
    # Session information
    st.subheader("📋 Session Info")
    st.text(f"Session ID: {st.session_state.session_id}")
    st.text(f"User ID: {st.session_state.user_id}")
    st.text(f"Messages: {len(st.session_state.messages)}")
    
    st.markdown("---")
    
    # API Configuration
    st.subheader("⚙️ API Configuration")
    st.text(f"API URL: {ADK_API_URL}")
    st.text(f"App Name: {st.session_state.app_name}")
    st.text(f"Endpoint: /run")
    
    # Connection test
    if st.button("🔌 Test Connection"):
        with st.spinner("Testing connection..."):
            async def test_connection():
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            ADK_API_URL,
                            timeout=aiohttp.ClientTimeout(total=5)
                        ) as response:
                            return response.status
                except Exception as e:
                    return None
            
            status = asyncio.run(test_connection())
            if status:
                st.success(f"✅ Server is reachable (Status: {status})")
            else:
                st.error("❌ Cannot reach server")
    
    st.markdown("---")
    
    # Session controls
    st.subheader("🔄 Session Controls")
    if st.button("🆕 Start New Session", use_container_width=True):
        reset_session()
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    
    # Instructions
    st.subheader("📖 How to Use")
    st.markdown("""
    1. **Start chatting** by typing a message below
    2. The agent will guide you through:
        - Student information collection
        - Diagnostic test
        - Personalized lesson plan
        - Interactive learning steps
    3. Use **Start New Session** to begin fresh
    """)
    
    st.markdown("---")
    st.caption(f"ADK API Server: {ADK_API_URL}")


# Main chat interface
st.title("💬 Math Learning Chat")

# Display welcome message if no messages
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="info-box">
        <h3>👋 Welcome to the Math Learning Assistant!</h3>
        <p>I'm here to help you learn math in a fun and personalized way. Let's get started!</p>
        <p><strong>What happens next:</strong></p>
        <ul>
            <li>I'll ask for your student information</li>
            <li>You'll take a quick diagnostic test</li>
            <li>I'll create a personalized lesson plan just for you</li>
            <li>We'll work through lessons with fun explanations and quizzes</li>
        </ul>
        <p><em>Type your message below to begin!</em></p>
    </div>
    """, unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = asyncio.run(send_message_to_adk(prompt))
            
            if response:
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                error_msg = "I'm having trouble connecting to the learning system. Please check the connection and try again."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.caption("Powered by Google ADK and Streamlit | Math Learning Assistant v0.1.0")
