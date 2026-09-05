"""Database persistence operations for learning sessions, lessons, questions, and responses."""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import (
    Student,
    StudentProfile,
    LearningSession,
    Lesson,
    LessonSection,
    Question,
    StudentResponse,
    ConceptMastery,
    Document,
    DocumentChunk,
)
from ai_engine.schemas.learner import LearnerProfileSchema
from ai_engine.schemas.lesson import LessonPlanSchema
from ai_engine.schemas.question import QuestionSchema
from ai_engine.schemas.evaluation import EvaluationResultSchema
from ai_engine.schemas.misconception import MisconceptionReportSchema
from ai_engine.schemas.adaptation import AdaptationDecisionSchema
from ai_engine.schemas.grounding import DocumentMetadataSchema, DocumentChunkSchema


async def get_or_create_student(db: AsyncSession, student_id: str, name: str) -> Student:
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        student = Student(id=student_id, username=student_id, full_name=name)
        db.add(student)
        await db.flush()
    return student


async def save_student_profile(db: AsyncSession, profile: LearnerProfileSchema) -> StudentProfile:
    student = await get_or_create_student(db, profile.learner_id, profile.name or "Learner")
    result = await db.execute(select(StudentProfile).where(StudentProfile.student_id == student.id))
    db_profile = result.scalar_one_or_none()
    if not db_profile:
        db_profile = StudentProfile(
            student_id=student.id,
            educational_level=profile.educational_level.value,
            learning_objective=profile.learning_objective,
            preferred_teaching_style=profile.preferred_teaching_style.value,
            preferred_language=profile.preferred_language,
            available_learning_time=profile.available_learning_time,
            desired_depth=profile.desired_depth,
            strengths=profile.strengths,
            weaknesses=profile.weaknesses,
            known_misconceptions=profile.known_misconceptions,
        )
        db.add(db_profile)
    else:
        db_profile.educational_level = profile.educational_level.value
        db_profile.learning_objective = profile.learning_objective
        db_profile.preferred_teaching_style = profile.preferred_teaching_style.value
        db_profile.preferred_language = profile.preferred_language
        db_profile.available_learning_time = profile.available_learning_time
        db_profile.desired_depth = profile.desired_depth
        db_profile.strengths = profile.strengths
        db_profile.weaknesses = profile.weaknesses
        db_profile.known_misconceptions = profile.known_misconceptions
    await db.flush()
    return db_profile


async def create_learning_session(
    db: AsyncSession,
    session_id: str,
    student_id: str,
    topic: str,
    knowledge_mode: str = "topic",
    document_id: Optional[str] = None,
) -> LearningSession:
    session = LearningSession(
        id=session_id,
        student_id=student_id,
        topic=topic,
        knowledge_mode=knowledge_mode,
        document_id=document_id,
        status="initialized",
        current_section_index=0,
    )
    db.add(session)
    await db.flush()
    return session


async def save_lesson_plan(
    db: AsyncSession, session_id: str, plan: LessonPlanSchema
) -> Lesson:
    lesson = Lesson(
        id=plan.lesson_id,
        session_id=session_id,
        title=plan.lesson_title,
        topic=plan.topic,
        estimated_duration=plan.estimated_duration,
        explanation_depth=plan.explanation_depth,
        learning_objectives=plan.learning_objectives,
        raw_plan_data=plan.model_dump(),
    )
    db.add(lesson)
    await db.flush()

    for sec in plan.sections:
        sec_id = sec.section_id if lesson.id in sec.section_id else f"{lesson.id}-{sec.section_id}"
        db_section = LessonSection(
            id=sec_id,
            lesson_id=lesson.id,
            section_number=sec.section_number,
            concept=sec.concept,
            title=sec.title,
            objective=sec.objective,
            difficulty=sec.difficulty,
            estimated_time_minutes=sec.estimated_time_minutes,
            explanation_outline=sec.explanation_outline,
            visual_recommendation=sec.visual_recommendation.model_dump(),
            expected_understanding=sec.expected_understanding,
        )
        db.add(db_section)
    await db.flush()
    return lesson


async def save_question(db: AsyncSession, question: QuestionSchema) -> Question:
    result = await db.execute(select(Question).where(Question.id == question.question_id))
    db_q = result.scalar_one_or_none()
    if not db_q:
        db_q = Question(
            id=question.question_id,
            section_id=question.section_id,
            concept=question.concept,
            question_type=question.question_type.value,
            prompt=question.prompt,
            options=[o.model_dump() for o in question.options] if question.options else None,
            expected_answer=question.expected_answer,
            difficulty=question.difficulty,
            rubric=question.rubric,
            hints=question.hints,
        )
        db.add(db_q)
        await db.flush()
    return db_q


async def save_student_response(
    db: AsyncSession,
    session_id: str,
    question_id: str,
    student_answer: str,
    evaluation: EvaluationResultSchema,
    misconception: Optional[MisconceptionReportSchema] = None,
    adaptation: Optional[AdaptationDecisionSchema] = None,
) -> StudentResponse:
    resp = StudentResponse(
        id=f"resp-{evaluation.evaluation_id}",
        session_id=session_id,
        question_id=question_id,
        student_answer=student_answer,
        correctness=evaluation.correctness.value,
        score=evaluation.score,
        evaluation_data=evaluation.model_dump(),
        misconception_data=misconception.model_dump() if misconception else None,
        adaptation_data=adaptation.model_dump() if adaptation else None,
    )
    db.add(resp)
    await db.flush()
    return resp


async def save_document(
    db: AsyncSession, doc_meta: DocumentMetadataSchema, extracted_text: str = ""
) -> Document:
    result = await db.execute(select(Document).where(Document.id == doc_meta.document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        doc = Document(
            id=doc_meta.document_id,
            filename=doc_meta.filename,
            file_type=doc_meta.file_type,
            file_size_bytes=doc_meta.file_size_bytes,
            page_count=doc_meta.page_count,
            chunk_count=doc_meta.chunk_count,
            status=doc_meta.status.value,
            error_message=doc_meta.error_message,
            content_hash=doc_meta.content_hash,
            extracted_text=extracted_text,
            document_metadata=doc_meta.metadata,
        )
        db.add(doc)
    else:
        doc.status = doc_meta.status.value
        doc.page_count = doc_meta.page_count
        doc.chunk_count = doc_meta.chunk_count
        doc.error_message = doc_meta.error_message
        doc.document_metadata = doc_meta.metadata
        if extracted_text:
            doc.extracted_text = extracted_text

    await db.flush()
    return doc


async def get_document(db: AsyncSession, document_id: str) -> Optional[Document]:
    result = await db.execute(select(Document).where(Document.id == document_id))
    return result.scalar_one_or_none()


async def list_documents(db: AsyncSession) -> List[Document]:
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return list(result.scalars().all())


async def save_document_chunks(
    db: AsyncSession, document_id: str, chunks: List[DocumentChunkSchema]
) -> None:
    from sqlalchemy import delete
    await db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))
    for chunk in chunks:
        db_chunk = DocumentChunk(
            id=chunk.chunk_id,
            document_id=document_id,
            chunk_index=chunk.chunk_index,
            text_content=chunk.text_content,
            page_number=chunk.page_number,
            slide_number=chunk.slide_number,
            heading=chunk.heading,
            chunk_metadata=chunk.chunk_metadata,
            embedding={"dim": len(chunk.embedding)} if chunk.embedding else None,
        )
        db.add(db_chunk)
    await db.flush()


async def get_document_chunks(
    db: AsyncSession, document_id: str
) -> List[DocumentChunk]:
    result = await db.execute(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index.asc())
    )
    return list(result.scalars().all())
