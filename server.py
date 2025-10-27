#!/usr/bin/env python3
"""
slimpAI - Google ADK Web Server
Multi-agent educational system with 5 specialized agents
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables FIRST before importing agents
load_dotenv()

from flask import Flask, request, jsonify, send_from_directory
from my_agent.slimp_ai import slimp_ai

app = Flask(__name__, static_folder='.')

@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('.', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from the frontend."""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Process the message with slimpAI multi-agent system
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(slimp_ai.process_message(user_message))
        loop.close()
        
        return jsonify({
            'response': response,
            'state': slimp_ai.state['conversation_stage']
        })
        
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'response': "I'm sorry, I encountered an error. Please try again. 😊",
            'error': str(e)
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset the conversation."""
    try:
        # Reset the educational agent
        global educational_agent
        from agent import EducationalAgent
        educational_agent = EducationalAgent()
        
        return jsonify({'status': 'success', 'message': 'Conversation reset'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    print("=" * 60)
    print("🎓 Starting Google ADK Educational Agent Server...")
    print("=" * 60)
    print(f"Server running at: http://localhost:5000")
    print("Open your browser and navigate to the URL above to start learning!")
    print("=" * 60)
    app.run(host='localhost', port=5000, debug=True)
