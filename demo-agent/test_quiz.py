import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # For creating message Content/

from agent import tester_agent
from runner import call_agent_async

import dotenv
dotenv.load_dotenv()

# Define constants for identifying the interaction context
APP_NAME = "slimpai_app"
USER_ID = "user_1"
SESSION_ID = "session_001" # Using a fixed ID for simplicity

session_service = InMemorySessionService()

# We need an async function to await our interaction helper
async def run_conversation():
    # Create the specific session where the conversation will happen
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

    # --- Runner ---
    # Key Concept: Runner orchestrates the agent execution loop.
    runner = Runner(
        agent=tester_agent, # The agent we want to run
        app_name=APP_NAME,   # Associates runs with our app
        session_service=session_service, # Uses our session manager
        
    )
    print(f"Runner created for agent '{runner.agent.name}'.")
    
    await call_agent_async("Lets start a quiz about the halving topic.",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

if __name__ == "__main__":
    try:
        asyncio.run(run_conversation())
    except Exception as e:
        print(f"An error occurred: {e}")