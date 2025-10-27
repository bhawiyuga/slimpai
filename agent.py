from typing import Dict, List, Optional, TypedDict, Literal
from google.adk.agents.llm_agent import Agent
from dataclasses import dataclass
from datetime import datetime
import json

# =========== Data Models ===========

class TestQuestion(TypedDict):
    question: str
    options: List[str]
    correct_answer_index: int

class TestResult(TypedDict):
    question: str
    selected_answer: str
    is_correct: bool
    correct_answer: str

class LessonPlan(TypedDict):
    topic: str
    steps: List[str]

class UserProfile(TypedDict):
    name: str
    grade: int
    test_results: Dict[str, List[TestResult]]
    current_lesson_plan: Optional[LessonPlan]
    current_step: int
    conversation_state: Literal[
        'WELCOME', 
        'AWAITING_TEST_START', 
        'IN_TEST', 
        'TEST_COMPLETE', 
        'IN_LESSON', 
        'IN_QUIZ',
        'LESSON_COMPLETE'
    ]

# =========== Tool Implementations ===========

def create_baseline_test(topic: str, difficulty: str = "beginner") -> List[TestQuestion]:
    """Creates a baseline test for the given topic and difficulty level."""
    test_agent = Agent(
        model='gemini-2.5-flash',
        name='test_creator',
        description='Creates educational assessment tests',
        instruction=f"""You are an expert in creating educational assessments for {topic}. 
        Create a 3-question multiple choice test that assesses basic understanding of {topic}.
        Questions should be clear, age-appropriate, and progress in difficulty.
        Return ONLY a valid JSON array of question objects, each with 'question', 'options' (array of 3 strings),
        and 'correct_answer_index' (0-2).""",
    )
    
    response = test_agent.generate(f"Create a 3-question test about {topic} for a beginner.")
    try:
        questions = json.loads(response.text)
        return [
            TestQuestion(
                question=q["question"],
                options=q["options"],
                correct_answer_index=q["correct_answer_index"]
            )
            for q in questions
        ]
    except Exception as e:
        print(f"Error parsing test questions: {e}")
        # Fallback test questions
        return [
            TestQuestion(
                question="What is a 'whole'?",
                options=[
                    "A piece of a pie",
                    "The entire pie",
                    "A hole in the ground"
                ],
                correct_answer_index=1
            ),
            TestQuestion(
                question="If you cut a pizza into 2 equal pieces, what is one piece called?",
                options=["A quarter", "A half", "A slice"],
                correct_answer_index=1
            ),
            TestQuestion(
                question="If you cut a pizza into 4 equal pieces, what is one piece called?",
                options=["A half", "A bite", "A quarter"],
                correct_answer_index=2
            )
        ]

def create_lesson_plan(topic: str, test_results: List[TestResult]) -> LessonPlan:
    """Creates a personalized lesson plan based on test results."""
    planner_agent = Agent(
        model='gemini-2.5-flash',
        name='lesson_planner',
        description='Creates personalized learning plans',
        instruction=f"""You are an expert curriculum designer for {topic}. 
        Create a 2-3 step lesson plan that addresses any knowledge gaps.
        Skip concepts the student already understands.
        Return a JSON object with 'topic' and 'steps' (array of lesson step titles).""",
    )
    
    results_summary = "\n".join(
        f"Q: {r['question']} | Correct: {r['is_correct']}" 
        for r in test_results
    )
    
    response = planner_agent.generate(
        f"Create a lesson plan for {topic} based on these test results:\n{results_summary}"
    )
    
    try:
        plan = json.loads(response.text)
        return LessonPlan(
            topic=plan.get("topic", topic),
            steps=plan.get("steps", [f"Introduction to {topic}", f"Practice with {topic}"])
        )
    except Exception as e:
        print(f"Error parsing lesson plan: {e}")
        return LessonPlan(
            topic=topic,
            steps=[f"Introduction to {topic}", f"Practice with {topic}"]
        )

def explain_concept(concept: str) -> str:
    """Explains a concept using simple analogies."""
    explainer_agent = Agent(
        model='gemini-2.5-flash',
        name='explainer',
        description='Explains concepts using simple analogies',
        instruction=f"""You are 'Professor Pizza', a fun and engaging teacher for young students.
        Explain the concept of {concept} using a simple, relatable analogy (like food, animals, or toys).
        Keep it under 50 words. Be encouraging and use emojis!""",
    )
    
    response = explainer_agent.generate(f"Explain {concept} to a 7-year-old.")
    return response.text

def create_quiz_question(explanation: str) -> Dict:
    """Creates a quiz question based on the given explanation."""
    quizzer_agent = Agent(
        model='gemini-2.5-flash',
        name='quizzer',
        description='Creates quiz questions',
        instruction="""Create one multiple-choice question to test understanding of the given explanation.
        Return a JSON object with 'question', 'options' (array of 3 strings), and 'correct_answer_index' (0-2).
        Make the question clear and the incorrect answers plausible.""",
    )
    
    response = quizzer_agent.generate(
        f"Create a quiz question based on this explanation:\n{explanation}"
    )
    
    try:
        return json.loads(response.text)
    except:
        return {
            "question": f"What was the main idea of the explanation about {explanation[:20]}...?",
            "options": ["Option 1", "Option 2", "Option 3"],
            "correct_answer_index": 0
        }

# =========== Main Agent ===========

class EducationalAgent:
    def __init__(self):
        self.user_profile: UserProfile = {
            "name": "Student",
            "grade": 2,
            "test_results": {},
            "current_lesson_plan": None,
            "current_step": 0,
            "conversation_state": "WELCOME"
        }
        
        self.current_test: List[TestQuestion] = []
        self.current_test_answers: List[TestResult] = []
        self.current_explanation: Optional[str] = None
        
        # Initialize the guide agent
        self.guide_agent = Agent(
            model='gemini-2.5-flash',
            name='guide',
            description='The friendly guide that coordinates the learning experience',
            instruction="""You are a friendly, encouraging guide helping students learn math through fun, interactive lessons.
            Your tone should be warm, patient, and supportive. Use emojis to make it engaging!
            Keep responses concise and focused on one concept at a time.""",
        )
    
    def process_message(self, user_message: str) -> str:
        """Processes a user message and returns the agent's response."""
        state = self.user_profile["conversation_state"]
        
        if state == "WELCOME":
            return self._handle_welcome()
        elif state == "AWAITING_TEST_START":
            return self._handle_test_start(user_message)
        elif state == "IN_TEST":
            return self._handle_test_response(user_message)
        elif state == "TEST_COMPLETE":
            return self._handle_lesson_start()
        elif state == "IN_LESSON":
            return self._handle_lesson_step(user_message)
        elif state == "IN_QUIZ":
            return self._handle_quiz_response(user_message)
        else:
            return "I'm not sure what to do next. Let's start over!"
    
    def _handle_welcome(self) -> str:
        self.user_profile["conversation_state"] = "AWAITING_TEST_START"
        return (
            "I can help with fractions! 🍕 To find out what you already know, "
            "can we start with a super quick 3-question warm-up? It's not for a grade, "
            "just to help me build the perfect lesson for you!"
        )
    
    def _handle_test_start(self, user_message: str) -> str:
        if user_message.lower() not in ["ok", "okay", "sure", "yes", "yep"]:
            return "Just say 'ok' when you're ready to start the warm-up! 😊"
        
        self.current_test = create_baseline_test("fractions")
        self.user_profile["conversation_state"] = "IN_TEST"
        return self._ask_test_question(0)
    
    def _handle_test_response(self, user_message: str) -> str:
        # Process the answer
        current_question = self.current_test[len(self.current_test_answers)]
        selected_index = ord(user_message.upper()) - ord('A')
        is_correct = (selected_index == current_question["correct_answer_index"])
        
        self.current_test_answers.append({
            "question": current_question["question"],
            "selected_answer": current_question["options"][selected_index],
            "is_correct": is_correct,
            "correct_answer": current_question["options"][current_question["correct_answer_index"]]
        })
        
        # Move to next question or finish test
        if len(self.current_test_answers) < len(self.current_test):
            return self._ask_test_question(len(self.current_test_answers))
        else:
            return self._finish_test()
    
    def _handle_lesson_start(self) -> str:
        # Create lesson plan based on test results
        lesson_plan = create_lesson_plan("fractions", self.current_test_answers)
        self.user_profile["current_lesson_plan"] = lesson_plan
        self.user_profile["current_step"] = 0
        self.user_profile["conversation_state"] = "IN_LESSON"
        
        return (
            f"Great job on the warm-up! 🎉 I've created a personalized lesson plan for you.\n\n"
            f"First up: {lesson_plan['steps'][0]}"
        )
    
    def _handle_lesson_step(self, user_message: str) -> str:
        lesson_plan = self.user_profile["current_lesson_plan"]
        current_step = self.user_profile["current_step"]
        
        if current_step < len(lesson_plan["steps"]):
            # Explain the current concept
            concept = lesson_plan["steps"][current_step]
            explanation = explain_concept(concept)
            self.current_explanation = explanation
            
            # Create a quiz question for this concept
            quiz_question = create_quiz_question(explanation)
            self.current_quiz_question = quiz_question
            
            # Format the response with explanation and quiz question
            response = f"{explanation}\n\n"
            response += f"{quiz_question['question']}\n"
            for i, option in enumerate(quiz_question['options']):
                response += f"{chr(65+i)}. {option}\n"
            
            self.user_profile["conversation_state"] = "IN_QUIZ"
            return response
        else:
            # Lesson complete!
            self.user_profile["conversation_state"] = "LESSON_COMPLETE"
            return "Great job! You've completed the lesson. Would you like to learn something else?"
    
    def _handle_quiz_response(self, user_message: str) -> str:
        if not hasattr(self, 'current_quiz_question'):
            return "Let's move on to the next concept!"
        
        # Check the answer
        selected_index = ord(user_message.upper()) - ord('A')
        is_correct = (selected_index == self.current_quiz_question['correct_answer_index'])
        
        # Provide feedback
        if is_correct:
            response = "🎉 That's correct! Great job! 🎉\n\n"
        else:
            correct_answer = self.current_quiz_question['options'][self.current_quiz_question['correct_answer_index']]
            response = f"Almost! The correct answer is: {correct_answer}\n\n"
        
        # Move to next step
        self.user_profile["current_step"] += 1
        self.user_profile["conversation_state"] = "IN_LESSON"
        
        # Add a prompt for the next step
        lesson_plan = self.user_profile["current_lesson_plan"]
        if self.user_profile["current_step"] < len(lesson_plan["steps"]):
            response += f"Ready to learn about {lesson_plan['steps'][self.user_profile['current_step']]}? Just say 'yes' when you're ready!"
        else:
            response += "You've completed all the lessons! Great work! 🎊"
            self.user_profile["conversation_state"] = "LESSON_COMPLETE"
        
        return response
    
    def _ask_test_question(self, question_index: int) -> str:
        question = self.current_test[question_index]
        options = "\n".join(
            f"{chr(65+i)}. {option}" 
            for i, option in enumerate(question["options"])
        )
        return f"Question {question_index + 1}: {question['question']}\n\n{options}"
    
    def _finish_test(self) -> str:
        # Save test results
        self.user_profile["test_results"]["fractions"] = self.current_test_answers
        self.user_profile["conversation_state"] = "TEST_COMPLETE"
        
        # Calculate score
        correct = sum(1 for r in self.current_test_answers if r["is_correct"])
        total = len(self.current_test_answers)
        
        return (
            f"Great job on the warm-up! You got {correct} out of {total} questions right. 🎉\n\n"
            "Based on your answers, I'll create a personalized lesson plan for you. One moment..."
        )

# Create a global instance of the educational agent
educational_agent = EducationalAgent()

# The main agent that will be used by the web interface
root_agent = educational_agent.root_agent