"""Export AI Engine core modules."""
from ai_engine.modules.learner_profiler import LearnerProfiler
from ai_engine.modules.lesson_planner import LessonPlanner
from ai_engine.modules.teaching_agent import TeachingAgent
from ai_engine.modules.question_generator import QuestionGenerator
from ai_engine.modules.answer_evaluator import AnswerEvaluator
from ai_engine.modules.misconception_detector import MisconceptionDetector
from ai_engine.modules.adaptation_engine import AdaptationEngine
from ai_engine.modules.session_orchestrator import TeachingSessionOrchestrator
from ai_engine.modules.visual_planner import VisualPlanner
from ai_engine.modules.language_controller import LanguageController
from ai_engine.modules.avatar_controller import AvatarController
from ai_engine.modules.topic_classifier import TopicDomain, classify_topic

__all__ = [
    "LearnerProfiler",
    "LessonPlanner",
    "TeachingAgent",
    "QuestionGenerator",
    "AnswerEvaluator",
    "MisconceptionDetector",
    "AdaptationEngine",
    "TeachingSessionOrchestrator",
    "VisualPlanner",
    "LanguageController",
    "AvatarController",
    "TopicDomain",
    "classify_topic",
]

