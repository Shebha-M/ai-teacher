"""Teaching session state schemas."""
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from ai_engine.schemas.learner import LearnerProfileSchema
from ai_engine.schemas.lesson import LessonPlanSchema
from ai_engine.schemas.teaching import TeachingResponseSchema
from ai_engine.schemas.question import QuestionSchema, StudentResponseSchema
from ai_engine.schemas.evaluation import EvaluationResultSchema
from ai_engine.schemas.misconception import MisconceptionReportSchema
from ai_engine.schemas.adaptation import AdaptationDecisionSchema
from ai_engine.schemas.grounding import KnowledgeMode, GroundedContextSchema


class SessionStatus(str, Enum):
    INITIALIZED = "initialized"
    PLANNING = "planning"
    TEACHING = "teaching"
    AWAITING_RESPONSE = "awaiting_response"
    EVALUATING = "evaluating"
    ADAPTING = "adapting"
    COMPLETED = "completed"


class ConceptMasterySchema(BaseModel):
    concept: str = Field(..., description="Name of the concept")
    mastery_score: float = Field(
        0.0, ge=0.0, le=1.0, description="Estimated mastery between 0.0 and 1.0"
    )
    status: str = Field("introduced", description="introduced, practicing, mastered, struggling")
    attempts: int = Field(0, description="Total attempts at answering questions on this concept")
    last_evaluated_at: Optional[str] = Field(None, description="ISO timestamp of last assessment")


class TeachingInteractionRecord(BaseModel):
    step_number: int = Field(..., description="Interaction sequence index")
    section_id: str = Field(..., description="Related section ID")
    concept: str = Field(..., description="Target concept")
    teaching_response: Optional[TeachingResponseSchema] = None
    question: Optional[QuestionSchema] = None
    student_response: Optional[StudentResponseSchema] = None
    evaluation: Optional[EvaluationResultSchema] = None
    misconception_report: Optional[MisconceptionReportSchema] = None
    adaptation_decision: Optional[AdaptationDecisionSchema] = None


class TeachingSessionStateSchema(BaseModel):
    session_id: str = Field(..., description="Unique session ID")
    learner_profile: LearnerProfileSchema = Field(..., description="Learner profile for this session")
    status: SessionStatus = Field(SessionStatus.INITIALIZED, description="Current session state")
    current_topic: str = Field(..., description="Subject or topic of instruction")
    knowledge_mode: KnowledgeMode = Field(KnowledgeMode.TOPIC, description="Grounding modality: topic, document, or mixed")
    document_id: Optional[str] = Field(None, description="Attached source document ID if document-grounded")
    grounded_context: Optional[GroundedContextSchema] = Field(None, description="Active retrieved document context")
    lesson_plan: Optional[LessonPlanSchema] = Field(None, description="Active generated lesson plan")
    current_section_index: int = Field(0, description="0-indexed position in lesson sections")
    current_section_id: Optional[str] = Field(None, description="ID of active section")
    current_concept: Optional[str] = Field(None, description="Active concept being explored")
    
    # Multilingual presentation state (preserves pedagogical session state)
    teaching_language: str = Field("en", description="Active presentation language (en, hi, ta, te, ml, kn)")
    language_mode: str = Field("bilingual", description="Presentation mode: full, bilingual, mixed")
    active_voice_id: Optional[str] = Field(None, description="Active neural voice ID")
    
    # Session learning tracking
    concepts_mastered: List[str] = Field(default_factory=list, description="Mastered concepts")
    concepts_needing_improvement: List[str] = Field(
        default_factory=list, description="Concepts flagged for reinforcement"
    )
    concept_mastery_map: Dict[str, ConceptMasterySchema] = Field(
        default_factory=dict, description="Detailed concept tracking"
    )
    
    # Full teaching audit log
    history: List[TeachingInteractionRecord] = Field(
        default_factory=list, description="Chronological record of interactions"
    )
    
    # Active interaction state
    latest_teaching: Optional[TeachingResponseSchema] = None
    latest_question: Optional[QuestionSchema] = None
    latest_evaluation: Optional[EvaluationResultSchema] = None
    latest_adaptation: Optional[AdaptationDecisionSchema] = None
