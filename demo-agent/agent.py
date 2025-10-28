from google.adk.agents.llm_agent import Agent
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
import os
import json
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents.base_agent import BaseAgent

from .tools import submit_answer, start_quiz

#  we need 1. instructions 2. tools 3. llm
# tools
GEMINI_MODEL = 'gemini-2.5-flash'

# --- 1. Define the Subagents (Tools) ---

# Agent 2: Tester (Tool)
# Note: Since the prompt requires a very specific JSON output, this agent's prompt
# is designed to force that structure.
tester_agent = LlmAgent(
    name="Tester",
    description="Generates a 3-question, multiple-choice baseline diagnostic test for a given topic. It returns ONLY a valid JSON list of question objects with keys: 'question', 'options' (list of 3 strings), and 'correct_answer_index' (integer).",
    instruction="""
        You are the 'Warm-up Whiz,' a 2nd-grade math teacher. 
        Create a 3-question, multiple-choice baseline test for the topic.
        After creating the test, you MUST call the `start_quiz` tool to store the quiz state.
        Give the questions one at a time.
        Wait for user response before the next question.
        Whe user answer: Use submit_answer(answer="[user's answer]")
        Even if the user fails a question, wait till last question to assess their performance overall.
        The questions should ramp in difficulty (easy, medium, hard).
        Return ONLY a valid JSON list of question objects. DO NOT add any extra text or prose.
    """,
    model=GEMINI_MODEL,
    tools=[start_quiz, submit_answer],
)

# Agent 3: Planner (Tool)
planner_agent = LlmAgent(
    name="Planner",
    description="Takes a broad topic and the JSON results of a baseline test to create a personalized 2-3 step lesson plan. It returns ONLY a valid JSON list of lesson title strings.",
    instruction="""
        You are a 2nd-grade math curriculum expert and the 'Curriculum Designer.'
        A student is learning the current topic. Their baseline test results are: test_results_json.
        Based on what they got right and wrong, create a personalized 2-3 step lesson plan.
        *Skip* any concepts they already know.
        Return ONLY a valid JSON list of lesson title strings. DO NOT add any extra text or prose.
    """,
    model=GEMINI_MODEL
)

# Agent 4: Explainer (Tool)
explainer_agent = LlmAgent(
    name="Explainer",
    description="Receives one lesson step and explains it with a simple, primary-school-level analogy (like food, animals, or blocks). The response is kept under 50 words, is encouraging, and uses emojis.",
    instruction="""
        You are 'Professor Pizza,' a fun, creative teacher explaining math to a 7-year-old.
        Use a simple analogy (like food, animals, or blocks) to explain this concept: 'lesson_step'.
        Keep it under 50 words. Be very encouraging and use emojis! Return ONLY the text.
    """,
    model=GEMINI_MODEL
)

# Agent 5: Quizzer (Tool)
quizzer_agent = LlmAgent(
    name="Quizzer",
    description="Receives explanation text and creates a single multiple-choice question to check for understanding. It returns ONLY a valid JSON object with keys: 'question', 'options' (a list of 3 strings), and 'correct_answer_index' (an integer).",
    instruction="""
        You are 'The Question Captain.'
        Based *ONLY* on the following text: 'input_text', create one simple multiple-choice question to check for understanding.
        Return ONLY a valid JSON object. DO NOT add any extra text or prose.
    """,
    model=GEMINI_MODEL
)


# --- 2. Wrap Subagents as Tools ---
# This is the key step to allow the Guide Agent (an LlmAgent) to call them like functions.
tester_tool = AgentTool(agent=tester_agent)
planner_tool = AgentTool(agent=planner_agent)
explainer_tool = AgentTool(agent=explainer_agent)
quizzer_tool = AgentTool(agent=quizzer_agent)


# --- 3. Define the Root Agent (The Orchestrator) ---
# Agent 1: Guide (The Supervisor)
root_agent = LlmAgent(
    name="Guide",
    description="The friendly, encouraging 'homeroom teacher' that guides the user through the lesson flow. Its sole job is to call the other specialized tools in the correct, sequential order.",
    instruction="""

        You are the 'Quest Guide' and 'Homeroom Teacher,' a highly encouraging and friendly AI assistant. Your **ONLY** job is to orchestrate the learning flow using your specialized tools and provide all the positive, connective text to the user.

        You will manage the student's entire learning journey for the current topic.

        ### Core Responsibilities and Workflow

        1.  **STARTING THE SESSION & COLLECTING INFO:**
            * **First Action:** Warmly welcome the student.
            * **Second Action:** Student Data Collection You MUST ensure you collect and store the student's number, name, and group before proceeding;
             Ask the student for their student number (e.g., "First, could you please tell me your student number?");
              Once you have the number, ask for their name; Once you have the name, ask for their group. Use the collected name in your next response to personalize the greeting.
            * **Third Action:** Wait for the user to provide current topic. Once received, store these details in the session state (e.g., 'student_name', 'student_number', 'student_group').
            * **Fourth Action:** Confirm the current topic with the student.
            * **Fifth Action:** Immediately use the **`tester_tool()`** with the current topic to generate the diagnostic test. **Do NOT write the test yourself.**
            * **Sixth Action:** Present the test questions to the user. State clearly that you are waiting for their answers to proceed.

        2.  **PROCESSING TEST RESULTS:**
            * Once the user provides their answers, you will validate them and store the result (correct/incorrect for each question) in the session state as 'test_results_json'.
            * For the question the user failed, next, you **MUST** use the **`planner_tool()`** at the end of the 3 questions on the areas the user got wrong  with the topic and the new 'test_results_json' to get the personalized list of lesson steps. Store this plan in the session state as 'lesson_plan'.
            * Provide an encouraging transition (e.g., "Great job finishing the quiz, student_name! Based on that, I've designed your custom learning path.").

        3.  **THE LESSON LOOP (Iterating through 'lesson_plan'):**
            * For each lesson step in the 'lesson_plan', you must follow this sequence:
                a. **EXPLAIN:** Use the **`explainer_tool()`** with the lesson step to get a fun, analogy-based explanation.
                b. **PRESENT:** Print the explanation to the user. Add a comment like "Professor Pizza says:" to introduce it, and then be encouraging.
                c. **QUIZ:** Immediately use the **`quizzer_tool()`** with the **EXACT text** from the Explainer's response to get a check-for-understanding question. **Do NOT write the question yourself.**
                d. **EVALUATE:** Present the quiz question and wait for the user's answer. Provide feedback (e.g., "Perfect!" or "Let's review that pizza concept.") before moving to the next lesson step.

        4.  **FINISHING THE QUEST:**
            * When the last lesson step is complete, provide a final, triumphant message of congratulations. Suggest a next step, such as trying another practice quiz or moving to a new topic.

        ### Tone & Constraints
        * **Encouragement is Key:** Use words like "Amazing," "You've got this," and "Fantastic."
        * **DO NOT GENERATE CONTENT:** Your core instruction is to use the four specialized tools for **all** testing, planning, explaining, and quizzing. Your words should only be for flow and encouragement.


    """,
    model=GEMINI_MODEL,
    # Make all subagents available as tools
    tools=[tester_tool, planner_tool, explainer_tool, quizzer_tool],
    # The ADK automatically manages session state (current_topic, test_results, etc.)
    # which the LlmAgent's prompt can reference when deciding which tool to call.
)

# --- 4. System Usage (Conceptual) ---

def run_learning_session(topic, initial_query):
    # In a real ADK application, you would initialize a Runner and Session
    # to start the conversation with the Guide Agent.
    
    print(f"--- Starting Learning Session on: {topic} ---")
    
    # 1. Set initial state (conceptually)
    # session.state["current_topic"] = topic 
    
    # 2. Run the main agent with the user's first query
    # response = runner.run(guide_agent, initial_query)
    
    # 3. The guide agent's LLM will start calling its tools (Tester, Planner, etc.)
    # and the system will proceed step-by-step, prompting the user for input
    # after each test and quiz.
    
    print("\n[INFO: Guide Agent begins execution flow...]")
    print(f"User Query: '{initial_query}'")
    print("\n[...ADK Runner executes sequential LlmAgent calls to subagents/tools...]")
    print("\n[Example: Guide calls Tester. Tester returns JSON test. Guide formats response and asks user to answer.]")
    print("\n[Example: Guide calls Planner with user results. Planner returns lesson plan. Guide calls Explainer/Quizzer in a loop.]")
    print("\n[INFO: Session Complete.]")

# Example of how the script would be used:
# if __name__ == "__main__":
#     # The user starts the conversation
#     run_learning_session(
#         topic="Fractions",
#         initial_query="I want to learn about fractions today."
#     )

# quizzler_agent = LlmAgent(
#     model='gemini-2.5-flash',
#     name='quizzler_agent',
#     descrption=,
#     instructions='You are a 2nd-grade math teacher. Create a 3-question, multiple-choice baseline test for the topic: "{topic}". The questions should ramp in difficulty (easy, medium, hard). Return ONLY a valid JSON list of question objects. Each object needs keys: "question", "options" (list of 3 strings), and "correct_answer_index" (integer).'

# quizzler_tool = AgentTool(agent=)
# root_agent = Agent(
#     model='gemini-2.5-flash',
#     name='root_agent',
#     description='A helpful assistant for user questions.',
#     instruction='use the quizzler agent when the student needs a quiz',
#     tools=[quizzler_tool]
# )

# supervisor_guide_agent = LlmAgent(
#     model='gemini-2.5-flash',
#     name='supervisor_guide_agent',
#     description=' The friendly, encouraging "homeroom teacher" or "quest guide."',
#     instruction='You are an agent thatmotivates students with  supervisor',
#     tools=[do_something])

