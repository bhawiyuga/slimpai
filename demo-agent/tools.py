from typing import Any, Dict
from google.adk.tools.tool_context import ToolContext


def store_user_info(tool_context: ToolContext, student_number: str, name: str, grade: int) -> Dict[str, Any]:
    """
    Store user information such as name, age, and grade in the tool context state.
    
    Args:
        student_number (str): The student's identification number.
        name (str): The name of the user.
        grade (int): The grade level of the user.
    
    Returns:
        Dict[str, Any]: A dictionary confirming the stored user information.
    """
    state = tool_context.state
    state["student_number"] = student_number
    state["name"] = name
    state["grade"] = grade
    return {
        "status": "success",
        "stored_info": {
            "name": name,
            "age": age,
            "grade": grade
        }
    }

def submit_answer(tool_context: ToolContext, question: str, answer: str, is_correct: bool) -> Dict[str, Any]:
    """
    Record a user's answer submission and update quiz state tracking.
    
    This function processes a submitted answer by updating the user's quiz progress
    metrics in their context state. It tracks both the total number of answers
    submitted and the count of correct answers.
    
    Args:
        question (str): The question text that was answered.
        answer (str): The user's submitted answer.
        is_correct (bool): Whether the submitted answer is correct.
    
    Returns:
        Dict[str, Any]: A dictionary containing the result of the answer submission.
    
    State Variables Updated:
        - total_answered (int): Incremented by 1 for each answer submitted
        - correct_answers (int): Incremented by 1 only when is_correct is True
    """
    state = tool_context.state
    state["question"] = question
    state["answer"] = answer
    state["total_answered"] = state.get("total_answered", 0) + 1
    if is_correct:
        state["correct_answers"] = state.get("correct_answers", 0) + 1

def start_quiz(tool_context: ToolContext, quiz: list) -> Dict[str, Any]:
    """
    Initialize and start a quiz session by storing quiz state information for a user.
    
    Args:
        quiz (list): A list of quiz questions, where each question is a tuple of
                     (question_text, correct_answer).
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - status (str): "started" if successful, "error" if failed
            - first_question (str): The text of the first question (if successful)
            - question_number (int): Current question number (1-indexed, if successful)
            - total_questions (int): Total number of questions in the quiz (if successful)
            - error_message (str): Error description (if failed)
    
    State Variables Set:
        - quiz_started (bool): Set to True to indicate quiz is active
        - current_question_index (int): Set to 0 (first question)
        - correct_answers (int): Set to 0 (no correct answers yet)
        - total_answered (int): Set to 0 (no questions answered yet)
        - score_percentage (int): Set to 0 (initial score)
    """
    state = tool_context.state
    # Initialize quiz state
    state["quiz_started"] = True
    state["current_question_index"] = 0
    state["correct_answers"] = 0
    state["total_answered"] = 0
    state["score_percentage"] = 0
    if quiz:
        data = {
            "status": "started",
            "questions": quiz,
            "question_number": 1,
            "total_questions": len(quiz),
        }
        state["quiz"] = quiz
        print(f"Quiz started: {data}")
        return data
    return {"status": "error", "error_message": "No questions available"}