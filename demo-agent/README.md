# Math Learning Assistant - Streamlit Client

This Streamlit app connects to a Google ADK API server to provide an interactive math learning experience.

## Architecture

- **Streamlit Frontend**: User interface for chat-based interaction (this app)
- **Google ADK API Server**: Backend server running the agent logic (separate deployment)

The Streamlit UI acts as a client that sends user messages to the ADK API server and displays the agent's responses in a chat interface.

## Configuration

The app connects to the ADK API server using the following environment variable:

```bash
export ADK_API_URL="http://localhost:8000"  # Default value
```

Or set it to your deployed API server URL:

```bash
export ADK_API_URL="https://your-adk-server.example.com"
```

## Prerequisites

1. **Install dependencies** (already configured in `pyproject.toml`):
   ```bash
   uv sync
   ```

2. **Start the ADK API Server**: 
   - The Google ADK API server must be running
   - Start it with: 
     ```bash
     uv run adk api_server
     ```
   - The server will run on `http://localhost:8000` by default
   - You can verify it's running by visiting `http://localhost:8000/docs`

## Running the App

### Option 1: Using the shell script (Recommended)
```bash
chmod +x run_app.sh  # Make it executable (first time only)
./run_app.sh
```

### Option 2: Direct command
```bash
# With default API URL (http://localhost:8000)
uv run streamlit run demo-agent/app.py

# With custom API URL
ADK_API_URL="https://your-server.com" uv run streamlit run demo-agent/app.py
```

The app will open in your browser at `http://localhost:8501`

## How to Start Both Services

For a complete setup, you need two terminal windows:

**Terminal 1 - ADK API Server:**
```bash
uv run adk api_server
```

**Terminal 2 - Streamlit UI:**
```bash
./run_app.sh
```

## Features

- 💬 **Interactive Chat Interface**: Clean, modern chat UI built with Streamlit
- 🎓 **Guided Learning Flow**: Agent guides students through:
  - Student information collection
  - Diagnostic baseline test
  - Personalized lesson plan generation
  - Interactive lessons with fun explanations
  - Check-for-understanding quizzes
- 🔄 **Session Management**: 
  - Unique session IDs for each learning journey
  - Ability to start new sessions
  - Clear chat history
- 📊 **Session Info Display**: View current session details in the sidebar
- ⚡ **Async Communication**: Non-blocking API calls for smooth user experience
- 🔌 **Connection Testing**: Built-in tool to test API server connectivity
- 🎨 **Custom Styling**: Enhanced UI with custom CSS for better readability

## API Integration

### Request Format

The Streamlit app sends requests to the ADK API server in the following format:

```json
{
  "app_name": "demo-agent",
  "user_id": "user_1",
  "session_id": "session_20250128_143022",
  "new_message": {
    "role": "user",
    "parts": [{"text": "User's message here"}]
  }
}
```

**Note:** The field is `new_message` (not `message`), as per ADK API specification.

### Expected Response Formats

The `/run` endpoint returns a list of events. The app extracts text from the last model response:

**Event List Format:**
```json
[
  {
    "content": {
      "parts": [{"text": "Agent's response text"}],
      "role": "model"
    },
    "invocationId": "...",
    "author": "...",
    ...
  }
]
```

The app processes the event list and extracts all text parts from model responses.

## User Journey

1. **Welcome**: User opens the app and sees a welcome message
2. **Student Info**: Agent collects student number, name, and group
3. **Topic Selection**: User provides the math topic they want to learn
4. **Diagnostic Test**: Agent administers a 3-question baseline test
5. **Personalized Plan**: Based on results, agent creates a custom lesson plan
6. **Learning Loop**: For each lesson step:
   - Fun analogy-based explanation
   - Check-for-understanding quiz
   - Encouraging feedback
7. **Completion**: Celebration and suggestions for next steps

## Troubleshooting

### Connection Errors
If you see "Cannot connect to ADK API server":
1. Verify the ADK API server is running:
   ```bash
   # In a separate terminal, start the ADK server
   uv run adk api_server
   ```
2. Check the `ADK_API_URL` environment variable is set correctly (default: `http://localhost:8000`)
3. Use the "Test Connection" button in the sidebar to verify connectivity
4. Visit `http://localhost:8000/docs` to see the interactive API documentation

### API Errors
If you see API errors:
1. Check the server logs for error details
2. Verify the ADK server is running with `adk api_server`
3. Ensure the app name matches your agent folder name (default: `demo-agent`)
4. Check that a session was created successfully (the app does this automatically)

### Timeout Errors
If requests timeout:
1. The server might be processing a complex query
2. Check server performance and logs
3. Consider increasing the timeout in `app.py` (currently 60 seconds)

## Development Notes

- The app uses `asyncio` for asynchronous API calls
- Session state is managed by Streamlit's built-in session state
- The agent state is managed server-side by the ADK
- No local agent execution - all processing happens on the API server
