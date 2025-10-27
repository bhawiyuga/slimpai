"""
slimpAI - Multi-Agent Educational System
5 specialized agents working together for personalized learning
"""

from .guide_agent import root_agent 
from .tester_agent import tester_agent
from .planner_agent import planner_agent
from .explainer_agent import explainer_agent
from .quizzer_agent import quizzer_agent
from .slimp_ai import slimp_ai, SlimpAI

__all__ = [
    root_agent,
    'tester_agent',
    'planner_agent',
    'explainer_agent',
    'quizzer_agent',
    'slimp_ai',
    'SlimpAI'
]
