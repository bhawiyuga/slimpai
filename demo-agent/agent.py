from google.adk.agents.llm_agent import Agent
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
import os
import json
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents.base_agent import BaseAgent

#  we need 1. instructions 2. tools 3. llm
# tools

# --- 1. Define the Subagents (Tools) ---

# Agent 2: Tester (Tool)
# Note: Since the prompt requires a very specific JSON output, this agent's prompt
# is designed to force that structure.
tester_agent = LlmAgent(
    name="Tester",
    description="Generates a 3-question, multiple-choice baseline diagnostic test for a given topic. It returns ONLY a valid JSON list of question objects with keys: 'question', 'options' (list of 3 strings), and 'correct_answer_index' (integer).",
    instruction="""
        You are the 'Warm-up Whiz,' a 2nd-grade math teacher.
        Create a 3-question, multiple-choice baseline test for the topic: {topic}.
        The questions should ramp in difficulty (easy, medium, hard).
        Return ONLY a valid JSON list of question objects. DO NOT add any extra text or prose.
    """,
    # model=GEMINI_MODEL
)

# Agent 3: Planner (Tool)
planner_agent = LlmAgent(
    name="Planner",
    description="Takes a broad topic and the JSON results of a baseline test to create a personalized 2-3 step lesson plan. It returns ONLY a valid JSON list of lesson title strings.",
    instruction="""
        You are a 2nd-grade math curriculum expert and the 'Curriculum Designer.'
        A student is learning '{topic}'. Their baseline test results are: {test_results_json}.
        Based on what they got right and wrong, create a personalized 2-3 step lesson plan.
        *Skip* any concepts they already know.
        Return ONLY a valid JSON list of lesson title strings. DO NOT add any extra text or prose.
    """,
    # model=GEMINI_MODEL
)

# Agent 4: Explainer (Tool)
explainer_agent = LlmAgent(
    name="Explainer",
    description="Receives one lesson step and explains it with a simple, primary-school-level analogy (like food, animals, or blocks). The response is kept under 50 words, is encouraging, and uses emojis.",
    instruction="""
        You are 'Professor Pizza,' a fun, creative teacher explaining math to a 7-year-old.
        Use a simple analogy (like food, animals, or blocks) to explain this concept: '{lesson_step}'.
        Keep it under 50 words. Be very encouraging and use emojis! Return ONLY the text.
    """,
    # model=GEMINI_MODEL
)

# Agent 5: Quizzer (Tool)
quizzer_agent = LlmAgent(
    name="Quizzer",
    description="Receives explanation text and creates a single multiple-choice question to check for understanding. It returns ONLY a valid JSON object with keys: 'question', 'options' (a list of 3 strings), and 'correct_answer_index' (an integer).",
    instruction="""
        You are 'The Question Captain.'
        Based *ONLY* on the following text: '{input_text}', create one simple multiple-choice question to check for understanding.
        Return ONLY a valid JSON object. DO NOT add any extra text or prose.
    """,
    # model=GEMINI_MODEL
)


# --- 2. Wrap Subagents as Tools ---
# This is the key step to allow the Guide Agent (an LlmAgent) to call them like functions.
tester_tool = AgentTool(agent=tester_agent)
planner_tool = AgentTool(agent=planner_agent)
explainer_tool = AgentTool(agent=explainer_agent)
quizzer_tool = AgentTool(agent=quizzer_agent)


# --- 3. Define the Root Agent (The Orchestrator) ---
# Agent 1: Guide (The Supervisor)
guide_agent = LlmAgent(
    name="Guide",
    description="The friendly, encouraging 'homeroom teacher' that guides the user through the lesson flow. Its sole job is to call the other specialized tools in the correct, sequential order.",
    instruction="""
        You are the 'Quest Guide' and 'homeroom teacher.' Your tone is friendly, encouraging, and highly supportive.
        Your job is to manage the user's learning session and provide all the positive, connective text. You ask the name student number and group of the user.

        The user is currently learning a topic. Follow this plan:
        1. **Start:** Welcome the user and introduce the topic.
        2. **Test:** Use the `tester_tool` with the current topic to get a baseline test.
        3. **Plan:** Wait for the user to submit their test answers. Use the `planner_tool` with the topic and the user's test results to get the lesson plan.
        4. **Lesson Loop (The core logic):** Iterate through the lesson plan list from the planner. For each lesson step:
            a. **Explain:** Use the `explainer_tool` with the lesson step to get a simple analogy explanation. Present this explanation to the user, providing encouraging commentary like "Ready for the next step?".
            b. **Quiz:** Use the `quizzer_tool` with the *exact text* from the explainer's response to generate a single quiz question. Present this question to the user.
            c. **Check:** Wait for the user's answer. Provide feedback (e.g., "Great job!" or "Let's review that.") and then move to the next step.
        5. **Finish:** Once all lesson steps are complete, provide a final message of encouragement and suggest a next topic.
    """,
    # model=GEMINI_MODEL,
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

