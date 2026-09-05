"""RESTful API endpoints for the interactive teaching intelligence workflow."""
from typing import Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from backend.database import crud
from ai_engine.modules.session_orchestrator import TeachingSessionOrchestrator
from ai_engine.schemas.learner import LearnerProfileSchema, LearnerLevel, TeachingStyle
from ai_engine.schemas.session import TeachingSessionStateSchema
from ai_engine.schemas.teaching import TeachingResponseSchema
from ai_engine.schemas.question import QuestionSchema
from ai_engine.schemas.evaluation import EvaluationResultSchema
from ai_engine.schemas.adaptation import AdaptationDecisionSchema
from ai_engine.schemas.grounding import KnowledgeMode
from ai_engine.schemas.assessment import (
    FinalAssessmentSchema,
    SubmitAssessmentRequest,
    LearningReportSchema,
)

router = APIRouter(prefix="/api/v1/teaching", tags=["Teaching Intelligence"])

# In-memory active session cache (synchronized with database)
ACTIVE_SESSIONS: Dict[str, TeachingSessionStateSchema] = {}
orchestrator = TeachingSessionOrchestrator()


class CreateSessionRequest(BaseModel):
    topic: str = Field(..., description="Topic of instruction, e.g. 'Binary Trees', 'Ohm\\'s Law'")
    learner_name: str = Field("Learner", description="Student name")
    educational_level: LearnerLevel = Field(LearnerLevel.BEGINNER, description="Student knowledge level")
    available_learning_time: int = Field(15, description="Time available in minutes (e.g. 5, 15, 30, 60)")
    preferred_teaching_style: TeachingStyle = Field(TeachingStyle.ANALOGY_DRIVEN, description="Teaching style")
    preferred_language: str = Field("en", description="Language code")
    learning_objective: str = Field("Master the fundamentals and gain practical intuition")
    knowledge_mode: KnowledgeMode = Field(KnowledgeMode.TOPIC, description="Grounding mode: 'topic', 'document', 'mixed'")
    document_id: Optional[str] = Field(None, description="Optional attached document ID for document-grounded teaching")


class SubmitAnswerRequest(BaseModel):
    student_answer: str = Field(..., description="The student's response text")
    question_id: Optional[str] = Field(None, description="Optional question ID verification")


@router.post("/sessions", response_model=TeachingSessionStateSchema, status_code=status.HTTP_201_CREATED)
async def create_teaching_session(req: CreateSessionRequest, db: AsyncSession = Depends(get_db)):
    """Initialize a new pedagogical teaching session and learner profile."""
    profile = orchestrator.profiler.create_profile(
        name=req.learner_name,
        educational_level=req.educational_level,
        available_learning_time=req.available_learning_time,
        preferred_teaching_style=req.preferred_teaching_style,
        preferred_language=req.preferred_language,
        learning_objective=req.learning_objective,
    )

    session = orchestrator.initialize_session(
        topic=req.topic,
        learner_profile=profile,
        knowledge_mode=req.knowledge_mode,
        document_id=req.document_id,
    )
    ACTIVE_SESSIONS[session.session_id] = session

    # Persist in DB
    await crud.save_student_profile(db, profile)
    await crud.create_learning_session(
        db,
        session.session_id,
        profile.learner_id,
        req.topic,
        knowledge_mode=req.knowledge_mode.value,
        document_id=req.document_id,
    )

    return session


@router.get("/sessions/{session_id}", response_model=TeachingSessionStateSchema)
async def get_session(session_id: str):
    """Retrieve current state, concept mastery, and interaction history for a session."""
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Teaching session '{session_id}' not found.")
    return session


@router.post("/sessions/{session_id}/plan", response_model=TeachingSessionStateSchema)
async def generate_lesson_plan(session_id: str, db: AsyncSession = Depends(get_db)):
    """Generate a structured, time-adapted lesson plan for the session."""
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Teaching session '{session_id}' not found.")

    updated_session = await orchestrator.plan_session(session)
    ACTIVE_SESSIONS[session_id] = updated_session

    if updated_session.lesson_plan:
        await crud.save_lesson_plan(db, session_id, updated_session.lesson_plan)

    return updated_session


@router.post("/sessions/{session_id}/explain", response_model=TeachingResponseSchema)
async def teach_section(session_id: str):
    """Generate teacher explanation, analogy, example, and visual plan for current section."""
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Teaching session '{session_id}' not found.")

    try:
        teaching = await orchestrator.teach_current_section(session)
        return teaching
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sessions/{session_id}/question", response_model=QuestionSchema)
async def get_checkpoint_question(session_id: str, db: AsyncSession = Depends(get_db)):
    """Generate a diagnostic checkpoint question testing the current section concept."""
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Teaching session '{session_id}' not found.")

    try:
        question = await orchestrator.get_checkpoint_question(session)
        await crud.save_question(db, question)
        return question
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sessions/{session_id}/evaluate")
async def evaluate_student_answer(
    session_id: str, req: SubmitAnswerRequest, db: AsyncSession = Depends(get_db)
):
    """
    Evaluate student answer, diagnose misconceptions, select pedagogical adaptation,
    and update concept mastery.
    """
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Teaching session '{session_id}' not found.")

    try:
        outcome = await orchestrator.process_student_response(
            session=session,
            student_answer=req.student_answer,
            question_id=req.question_id,
        )

        evaluation: EvaluationResultSchema = outcome["evaluation"]
        misconception: MisconceptionReportSchema = outcome["misconception"]
        adaptation: AdaptationDecisionSchema = outcome["adaptation"]

        # Persist student response and evaluation
        if session.latest_question:
            await crud.save_student_response(
                db=db,
                session_id=session_id,
                question_id=session.latest_question.question_id,
                student_answer=req.student_answer,
                evaluation=evaluation,
                misconception=misconception,
                adaptation=adaptation,
            )
        await crud.save_student_profile(db, session.learner_profile)

        return {
            "evaluation": evaluation,
            "misconception": misconception,
            "adaptation": adaptation,
            "current_concept": session.current_concept,
            "concepts_mastered": session.concepts_mastered,
            "concepts_needing_improvement": session.concepts_needing_improvement,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sessions/{session_id}/advance")
async def advance_or_adapt(session_id: str):
    """Execute the adaptation decision: advance to next section, or re-explain with new analogy."""
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Teaching session '{session_id}' not found.")

    try:
        result = await orchestrator.advance_or_adapt(session)
        return {
            "result": result,
            "status": session.status.value,
            "current_section_index": session.current_section_index,
            "current_concept": session.current_concept,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sessions/{session_id}/assessment", response_model=FinalAssessmentSchema)
async def get_final_assessment(session_id: str):
    """Generate or retrieve the cumulative final assessment for the lesson."""
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Teaching session '{session_id}' not found.")

    try:
        assessment = await orchestrator.generate_final_assessment(session)
        return assessment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate assessment: {str(e)}")


@router.post("/sessions/{session_id}/assessment/submit", response_model=LearningReportSchema)
async def submit_final_assessment(session_id: str, req: SubmitAssessmentRequest, db: AsyncSession = Depends(get_db)):
    """Grade final assessment, compute overall score, and generate comprehensive learning report."""
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Teaching session '{session_id}' not found.")

    try:
        report = await orchestrator.evaluate_final_assessment(session, req.answers)
        await crud.save_student_profile(db, session.learner_profile)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate assessment: {str(e)}")


@router.get("/sessions/{session_id}/report", response_model=Optional[LearningReportSchema])
async def get_learning_report(session_id: str):
    """Retrieve the generated LearningReportSchema for a completed session."""
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Teaching session '{session_id}' not found.")

    report = orchestrator.get_learning_report(session)
    if not report:
        raise HTTPException(status_code=404, detail="Learning report not yet generated for this session.")
    return report


@router.get("/sessions/{session_id}/dashboard")
async def get_learner_dashboard(session_id: str):
    """Retrieve structured progress, concept mastery, recommendations, and history for the learner dashboard."""
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Teaching session '{session_id}' not found.")

    dashboard = orchestrator.get_learner_progress_dashboard(session)
    return dashboard
