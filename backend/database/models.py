"""SQLAlchemy declarative models for the AI Teacher platform."""
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    String,
    Text,
    Integer,
    Float,
    Boolean,
    ForeignKey,
    DateTime,
    JSON,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = "students"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"stu-{uuid.uuid4().hex[:8]}")
    username: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)

    # Relationships
    profile: Mapped[Optional["StudentProfile"]] = relationship("StudentProfile", back_populates="student", uselist=False, cascade="all, delete-orphan")
    sessions: Mapped[List["LearningSession"]] = relationship("LearningSession", back_populates="student", cascade="all, delete-orphan")
    progress: Mapped[List["LearningProgress"]] = relationship("LearningProgress", back_populates="student", cascade="all, delete-orphan")
    concept_mastery: Mapped[List["ConceptMastery"]] = relationship("ConceptMastery", back_populates="student", cascade="all, delete-orphan")


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"prof-{uuid.uuid4().hex[:8]}")
    student_id: Mapped[str] = mapped_column(String(64), ForeignKey("students.id", ondelete="CASCADE"), unique=True)
    educational_level: Mapped[str] = mapped_column(String(64), default="beginner")
    learning_objective: Mapped[str] = mapped_column(Text, default="Master fundamentals and gain practical intuition")
    preferred_teaching_style: Mapped[str] = mapped_column(String(64), default="analogy_driven")
    preferred_language: Mapped[str] = mapped_column(String(16), default="en")
    available_learning_time: Mapped[int] = mapped_column(Integer, default=15)
    desired_depth: Mapped[str] = mapped_column(String(32), default="intermediate")
    strengths: Mapped[dict] = mapped_column(JSON, default=list)
    weaknesses: Mapped[dict] = mapped_column(JSON, default=list)
    known_misconceptions: Mapped[dict] = mapped_column(JSON, default=list)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    student: Mapped["Student"] = relationship("Student", back_populates="profile")


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"sess-{uuid.uuid4().hex[:8]}")
    student_id: Mapped[str] = mapped_column(String(64), ForeignKey("students.id", ondelete="CASCADE"), index=True)
    topic: Mapped[str] = mapped_column(String(256), index=True)
    knowledge_mode: Mapped[str] = mapped_column(String(32), default="topic")
    document_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(64), default="initialized")
    current_section_index: Mapped[int] = mapped_column(Integer, default=0)
    current_concept: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    session_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    student: Mapped["Student"] = relationship("Student", back_populates="sessions")
    lessons: Mapped[List["Lesson"]] = relationship("Lesson", back_populates="session", cascade="all, delete-orphan")
    responses: Mapped[List["StudentResponse"]] = relationship("StudentResponse", back_populates="session", cascade="all, delete-orphan")


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"les-{uuid.uuid4().hex[:8]}")
    session_id: Mapped[str] = mapped_column(String(64), ForeignKey("learning_sessions.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(256))
    topic: Mapped[str] = mapped_column(String(256))
    estimated_duration: Mapped[int] = mapped_column(Integer, default=20)
    explanation_depth: Mapped[str] = mapped_column(String(64), default="intermediate")
    learning_objectives: Mapped[dict] = mapped_column(JSON, default=list)
    raw_plan_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)

    session: Mapped["LearningSession"] = relationship("LearningSession", back_populates="lessons")
    sections: Mapped[List["LessonSection"]] = relationship("LessonSection", back_populates="lesson", cascade="all, delete-orphan")


class LessonSection(Base):
    __tablename__ = "lesson_sections"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"sec-{uuid.uuid4().hex[:8]}")
    lesson_id: Mapped[str] = mapped_column(String(64), ForeignKey("lessons.id", ondelete="CASCADE"), index=True)
    section_number: Mapped[int] = mapped_column(Integer, default=1)
    concept: Mapped[str] = mapped_column(String(256))
    title: Mapped[str] = mapped_column(String(256))
    objective: Mapped[str] = mapped_column(Text)
    difficulty: Mapped[str] = mapped_column(String(32), default="beginner")
    estimated_time_minutes: Mapped[int] = mapped_column(Integer, default=5)
    explanation_outline: Mapped[str] = mapped_column(Text)
    visual_recommendation: Mapped[dict] = mapped_column(JSON, default=dict)
    expected_understanding: Mapped[str] = mapped_column(Text)

    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="sections")
    questions: Mapped[List["Question"]] = relationship("Question", back_populates="section", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"q-{uuid.uuid4().hex[:8]}")
    section_id: Mapped[str] = mapped_column(String(64), ForeignKey("lesson_sections.id", ondelete="CASCADE"), index=True)
    concept: Mapped[str] = mapped_column(String(256))
    question_type: Mapped[str] = mapped_column(String(64))
    prompt: Mapped[str] = mapped_column(Text)
    options: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    expected_answer: Mapped[str] = mapped_column(Text)
    difficulty: Mapped[str] = mapped_column(String(32), default="intermediate")
    rubric: Mapped[str] = mapped_column(Text)
    hints: Mapped[dict] = mapped_column(JSON, default=list)

    section: Mapped["LessonSection"] = relationship("LessonSection", back_populates="questions")
    responses: Mapped[List["StudentResponse"]] = relationship("StudentResponse", back_populates="question", cascade="all, delete-orphan")


class StudentResponse(Base):
    __tablename__ = "student_responses"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"resp-{uuid.uuid4().hex[:8]}")
    session_id: Mapped[str] = mapped_column(String(64), ForeignKey("learning_sessions.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[str] = mapped_column(String(64), ForeignKey("questions.id", ondelete="CASCADE"), index=True)
    student_answer: Mapped[str] = mapped_column(Text)
    correctness: Mapped[str] = mapped_column(String(64))
    score: Mapped[float] = mapped_column(Float, default=0.0)
    evaluation_data: Mapped[dict] = mapped_column(JSON, default=dict)
    misconception_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    adaptation_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)

    session: Mapped["LearningSession"] = relationship("LearningSession", back_populates="responses")
    question: Mapped["Question"] = relationship("Question", back_populates="responses")


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"asm-{uuid.uuid4().hex[:8]}")
    session_id: Mapped[str] = mapped_column(String(64), ForeignKey("learning_sessions.id", ondelete="CASCADE"), index=True)
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    summary_feedback: Mapped[str] = mapped_column(Text)
    assessment_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)


class LearningProgress(Base):
    __tablename__ = "learning_progress"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"prog-{uuid.uuid4().hex[:8]}")
    student_id: Mapped[str] = mapped_column(String(64), ForeignKey("students.id", ondelete="CASCADE"), index=True)
    topic: Mapped[str] = mapped_column(String(256), index=True)
    completion_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    total_time_spent_minutes: Mapped[int] = mapped_column(Integer, default=0)
    questions_attempted: Mapped[int] = mapped_column(Integer, default=0)
    questions_correct: Mapped[int] = mapped_column(Integer, default=0)
    last_active: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    student: Mapped["Student"] = relationship("Student", back_populates="progress")


class ConceptMastery(Base):
    __tablename__ = "concept_mastery"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"mst-{uuid.uuid4().hex[:8]}")
    student_id: Mapped[str] = mapped_column(String(64), ForeignKey("students.id", ondelete="CASCADE"), index=True)
    concept: Mapped[str] = mapped_column(String(256), index=True)
    mastery_score: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(64), default="introduced")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_evaluated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    student: Mapped["Student"] = relationship("Student", back_populates="concept_mastery")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"doc-{uuid.uuid4().hex[:8]}")
    filename: Mapped[str] = mapped_column(String(256))
    file_type: Mapped[str] = mapped_column(String(32))
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="uploaded")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64))
    extracted_text: Mapped[str] = mapped_column(Text)
    document_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)

    chunks: Mapped[List["DocumentChunk"]] = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"chk-{uuid.uuid4().hex[:8]}")
    document_id: Mapped[str] = mapped_column(String(64), ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    text_content: Mapped[str] = mapped_column(Text)
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    slide_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    heading: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    chunk_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    embedding: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    document: Mapped["Document"] = relationship("Document", back_populates="chunks")
