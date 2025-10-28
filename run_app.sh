#!/bin/bash

# Math Learning Assistant - Streamlit App Runner
# This script starts the Streamlit chat UI that connects to Google ADK API server

# Set default ADK API URL if not already set
if [ -z "$ADK_API_URL" ]; then
    export ADK_API_URL="http://localhost:8000"
    echo "ℹ️  ADK_API_URL not set, using default: $ADK_API_URL"
else
    echo "✓ Using ADK_API_URL: $ADK_API_URL"
fi

echo ""
echo "🚀 Starting Math Learning Assistant (Streamlit UI)..."
echo "📡 Connecting to ADK API Server at: $ADK_API_URL"
echo ""
echo "⚠️  Important: Ensure the ADK API server is running!"
echo "   Start it with: uv run adk api_server"
echo ""

# Run the Streamlit app
uv run streamlit run demo-agent/app.py
