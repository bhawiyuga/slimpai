"""
slimpAI - Multi-Agent Educational System
Orchestrates 5 specialized agents for personalized learning
"""

from google.adk.agents.llm_agent import Agent
from google.adk import Runner
from google import genai
from google.genai import types
import json
from typing import Dict, List, Any
import os
import uuid

# Import all agents
from .guide_agent import guide_agent
from .tester_agent import tester_agent
from .planner_agent import planner_agent
from .explainer_agent import explainer_agent
from .quizzer_agent import quizzer_agent

# Import question bank from quizbank folder
import sys
from pathlib import Path
# Add parent directory to path to access quizbank
sys.path.insert(0, str(Path(__file__).parent.parent))
from quizbank import get_baseline_test, get_lesson_content, get_available_topics


def clean_json_response(response: str) -> str:
    """Remove markdown code blocks from JSON responses."""
    cleaned = response.strip()
    if cleaned.startswith('```'):
        # Remove markdown code blocks
        lines = cleaned.split('\n')
        cleaned = '\n'.join([line for line in lines if not line.startswith('```')])
        cleaned = cleaned.strip()
    return cleaned


class SlimpAI:
    """
    Main orchestrator for the slimpAI multi-agent learning system.
    Manages conversation flow and coordinates between 5 specialized agents.
    """
    
    def __init__(self):
        # Set API key from environment
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
        # Initialize genai client with API key
        self.client = genai.Client(api_key=api_key)
        
        # Session state
        self.state = {
            'current_topic': 'Fractions',
            'conversation_stage': 'WELCOME',  # WELCOME, TESTING, PLANNING, LEARNING, QUIZ, COMPLETE
            'test_results': [],
            'lesson_plan': [],
            'current_lesson_step': 0,
            'quiz_results': []
        }
        
        # Agent instances
        self.guide = guide_agent
        self.tester = tester_agent
        self.planner = planner_agent
        self.explainer = explainer_agent
        self.quizzer = quizzer_agent
    
    async def process_message(self, user_message: str) -> str:
        """
        Process user input and coordinate between agents.
        """
        stage = self.state['conversation_stage']
        
        if stage == 'WELCOME':
            return await self._handle_welcome(user_message)
        elif stage == 'TESTING':
            return await self._handle_testing(user_message)
        elif stage == 'PLANNING':
            return await self._handle_planning()
        elif stage == 'LEARNING':
            return await self._handle_learning(user_message)
        elif stage == 'QUIZ':
            return await self._handle_quiz(user_message)
        elif stage == 'COMPLETE':
            return await self._handle_complete(user_message)
        else:
            return "I'm not sure what to do next. Let's start over!"
    
    async def _handle_welcome(self, user_message: str) -> str:
        """Handle welcome stage - introduce and start test"""
        # Check if user wants to start (more flexible matching)
        positive_keywords = ['yes', 'go', 'ready', 'start', 'ok', 'sure', 'yeah', 'yep']
        negative_keywords = ['no', 'not', 'later', 'wait']
        
        msg_lower = user_message.lower()
        wants_to_start = any(keyword in msg_lower for keyword in positive_keywords)
        wants_to_wait = any(keyword in msg_lower for keyword in negative_keywords)
        
        if wants_to_start and not wants_to_wait:
            # Use predefined questions from question bank
            test_data = get_baseline_test(self.state['current_topic'])
            
            if test_data:
                print(f"✅ Using question bank for topic: {self.state['current_topic']}")
                self.state['test_questions'] = test_data
                self.state['current_question'] = 0
                self.state['conversation_stage'] = 'TESTING'
                
                # Return first question
                first_question = test_data[0]
                options_text = '\n'.join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(first_question['options'])])
                
                return f"Great! Let's start with a quick warm-up! 🎯\n\n**Question 1:**\n{first_question['question']}\n\n{options_text}"
            else:
                return f"Sorry, I don't have questions for '{self.state['current_topic']}' yet. Available topics: {', '.join(get_available_topics())} 📚"
        else:
            return "No problem! When you're ready to start learning, just let me know! 😊"
    
    async def _handle_testing(self, user_message: str) -> str:
        """Handle testing stage - process answers and move to planning"""
        # Get current question
        current_q_idx = self.state['current_question']
        questions = self.state['test_questions']
        current_question = questions[current_q_idx]
        
        # Parse answer (A, B, or C)
        answer_map = {'a': 0, 'b': 1, 'c': 2}
        user_answer = user_message.lower().strip()
        
        if user_answer in answer_map:
            selected_idx = answer_map[user_answer]
            correct_idx = current_question['correct_answer_index']
            is_correct = (selected_idx == correct_idx)
            
            # Debug logging
            print(f"🔍 DEBUG - Question {current_q_idx + 1}:")
            print(f"   User selected: {user_answer.upper()} (index {selected_idx})")
            print(f"   Correct answer: {chr(65 + correct_idx)} (index {correct_idx})")
            print(f"   User's answer: {current_question['options'][selected_idx]}")
            print(f"   Correct answer text: {current_question['options'][correct_idx]}")
            print(f"   Result: {'✅ CORRECT' if is_correct else '❌ WRONG'}")
            
            # Store result
            self.state['test_results'].append({
                'question': current_question['question'],
                'user_answer': current_question['options'][selected_idx],
                'correct_answer': current_question['options'][correct_idx],
                'correct': is_correct
            })
            
            # Move to next question or finish test
            self.state['current_question'] += 1
            
            if self.state['current_question'] < len(questions):
                # Next question
                next_q = questions[self.state['current_question']]
                options_text = '\n'.join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(next_q['options'])])
                
                feedback = "Great job! ✨" if is_correct else "Good try! 💪"
                return f"{feedback}\n\n**Question {self.state['current_question'] + 1}:**\n{next_q['question']}\n\n{options_text}"
            else:
                # Test complete, move to planning
                self.state['conversation_stage'] = 'PLANNING'
                return await self._handle_planning()
        else:
            return "Please answer with A, B, or C! 😊"
    
    async def _handle_planning(self) -> str:
        """Create personalized lesson plan using Planner agent"""
        # Calculate score
        correct_count = sum(1 for r in self.state['test_results'] if r['correct'])
        total = len(self.state['test_results'])
        
        # Get lesson plan from Planner
        planner_prompt = f"""Topic: {self.state['current_topic']}
Test Results: {json.dumps(self.state['test_results'])}

Create a personalized lesson plan."""
        
        full_prompt = f"{self.planner.instruction}\n\n{planner_prompt}"
        result = self.client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=full_prompt
        )
        response = result.text
        
        try:
            if response:
                lesson_plan = json.loads(clean_json_response(response))
            else:
                raise ValueError("Empty response from Planner agent")
            self.state['lesson_plan'] = lesson_plan
            self.state['current_lesson_step'] = 0
            self.state['conversation_stage'] = 'LEARNING'
            
            # Start first lesson
            return await self._start_lesson()
        except Exception as e:
            print(f"Error parsing lesson plan: {e}")
            # Fallback
            self.state['lesson_plan'] = ["Understanding Fractions Basics"]
            self.state['conversation_stage'] = 'LEARNING'
            return await self._start_lesson()
    
    async def _start_lesson(self) -> str:
        """Start current lesson step using Explainer agent"""
        lesson_title = self.state['lesson_plan'][self.state['current_lesson_step']]
        
        # Get explanation from Explainer (Professor Pizza)
        explainer_prompt = f"{self.explainer.instruction}\n\nExplain this concept: {lesson_title}"
        result = self.client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=explainer_prompt
        )
        explanation = result.text
        self.state['current_explanation'] = explanation
        
        # Generate quiz question from Quizzer
        quizzer_prompt = f"{self.quizzer.instruction}\n\nInput Text: {explanation}"
        result = self.client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=quizzer_prompt
        )
        quiz_response = result.text
        
        try:
            if quiz_response:
                quiz_data = json.loads(clean_json_response(quiz_response))
            else:
                raise ValueError("Empty response from Quizzer agent")
            self.state['current_quiz'] = quiz_data
            self.state['conversation_stage'] = 'QUIZ'
            
            # Return explanation + quiz
            options_text = '\n'.join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(quiz_data['options'])])
            
            return f"📚 **Lesson {self.state['current_lesson_step'] + 1}: {lesson_title}**\n\n{explanation}\n\n---\n\n**Quick Check! 🎯**\n{quiz_data['question']}\n\n{options_text}"
        except Exception as e:
            print(f"Error parsing quiz: {e}")
            return f"{explanation}\n\nReady to continue? (Type 'next')"
    
    async def _handle_learning(self, user_message: str) -> str:
        """Handle learning stage"""
        return await self._start_lesson()
    
    async def _handle_quiz(self, user_message: str) -> str:
        """Handle quiz response"""
        answer_map = {'a': 0, 'b': 1, 'c': 2}
        user_answer = user_message.lower().strip()
        
        if user_answer in answer_map:
            selected_idx = answer_map[user_answer]
            quiz = self.state['current_quiz']
            correct_idx = quiz['correct_answer_index']
            is_correct = (selected_idx == correct_idx)
            
            # Debug logging
            print(f"🔍 DEBUG - Quiz for Lesson {self.state['current_lesson_step'] + 1}:")
            print(f"   User selected: {user_answer.upper()} (index {selected_idx})")
            print(f"   Correct answer: {chr(65 + correct_idx)} (index {correct_idx})")
            print(f"   User's answer: {quiz['options'][selected_idx]}")
            print(f"   Correct answer text: {quiz['options'][correct_idx]}")
            print(f"   Result: {'✅ CORRECT' if is_correct else '❌ WRONG'}")
            
            # Store result
            self.state['quiz_results'].append({
                'lesson': self.state['lesson_plan'][self.state['current_lesson_step']],
                'user_answer': quiz['options'][selected_idx],
                'correct_answer': quiz['options'][correct_idx],
                'correct': is_correct
            })
            
            # Move to next lesson or complete
            self.state['current_lesson_step'] += 1
            
            if self.state['current_lesson_step'] < len(self.state['lesson_plan']):
                # Next lesson
                self.state['conversation_stage'] = 'LEARNING'
                feedback = "Excellent! You got it! 🎉" if is_correct else "Good try! Let's keep learning! 💪"
                next_lesson = await self._start_lesson()
                return f"{feedback}\n\n{next_lesson}"
            else:
                # All lessons complete
                self.state['conversation_stage'] = 'COMPLETE'
                return await self._handle_complete("")
        else:
            return "Please answer with A, B, or C! 😊"
    
    async def _handle_complete(self, user_message: str) -> str:
        """Handle completion"""
        test_correct = sum(1 for r in self.state['test_results'] if r['correct'])
        test_total = len(self.state['test_results'])
        
        quiz_correct = sum(1 for r in self.state['quiz_results'] if r['correct'])
        quiz_total = len(self.state['quiz_results'])
        
        return f"""🎉 **Congratulations!** 🎉

You've completed your {self.state['current_topic']} learning journey!

📊 **Your Progress:**
- Warm-up Score: {test_correct}/{test_total}
- Quiz Score: {quiz_correct}/{quiz_total}

You're doing amazing! Keep up the great work! 🌟

Would you like to learn another topic? Just let me know! 😊"""


# Create global instance
slimp_ai = SlimpAI()
