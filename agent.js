// This file serves as a bridge between the Google ADK agent and the JavaScript frontend
// It uses the ADK's built-in API to communicate with the agent

class EducationalAgentBridge {
    constructor() {
        this.shouldShowNextButton = false;
        this.current_quiz_question = null;
        this.conversationState = 'WELCOME';
    }

    async process_message(input) {
        try {
            // Send message to the ADK agent via the built-in API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: input,
                    stream: false
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Extract the agent's response
            const agentResponse = data.response || data.message || "I'm sorry, I didn't understand that.";
            
            // Update state based on response content
            this._updateState(agentResponse);
            
            return agentResponse;
            
        } catch (error) {
            console.error('Error communicating with agent:', error);
            return "I'm sorry, I encountered an error. Please try again. 😊";
        }
    }

    _updateState(response) {
        // Determine if we should show the next button based on response
        const lowerResponse = response.toLowerCase();
        
        // Show next button after explanations or when explicitly mentioned
        if (lowerResponse.includes('next') || 
            lowerResponse.includes('continue') ||
            lowerResponse.includes('ready to move on')) {
            this.shouldShowNextButton = true;
        } else {
            this.shouldShowNextButton = false;
        }

        // Check if there's a quiz question in the response
        if (lowerResponse.includes('a)') && lowerResponse.includes('b)')) {
            // Parse quiz options from the response
            const options = this._parseQuizOptions(response);
            if (options.length > 0) {
                this.current_quiz_question = {
                    question: response,
                    options: options
                };
            }
        } else {
            this.current_quiz_question = null;
        }
    }

    _parseQuizOptions(text) {
        const options = [];
        const optionPattern = /([A-D])\)\s*([^\n]+)/gi;
        let match;
        
        while ((match = optionPattern.exec(text)) !== null) {
            options.push(match[1]); // Just the letter (A, B, C, D)
        }
        
        return options;
    }
}

// Create and export the educational agent bridge
export const educational_agent = new EducationalAgentBridge();

// Also expose it globally for non-module scripts
window.educational_agent = educational_agent;

console.log('Educational agent bridge loaded and ready!');
