"""Teaching response schemas for the Teaching Agent."""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from ai_engine.schemas.lesson import VisualRecommendation


class TeachingAction(str, Enum):
    INTRODUCE = "introduce"
    EXPLAIN = "explain"
    DEMONSTRATE = "demonstrate"
    RE_EXPLAIN = "re_explain"
    SIMPLIFY = "simplify"
    SUMMARIZE = "summarize"


class TeachingResponseSchema(BaseModel):
    section_id: str = Field(..., description="ID of the section being taught")
    concept: str = Field(..., description="The concept covered in this teaching block")
    teaching_action: TeachingAction = Field(
        TeachingAction.EXPLAIN, description="Pedagogical action performed"
    )
    explanation: str = Field(..., description="Engaging, clear educational explanation")
    analogy: str = Field(..., description="Intuitive real-world analogy grounding the concept")
    example: str = Field(..., description="Concrete applied example or code snippet")
    key_takeaway: str = Field(..., description="One-sentence core principle to remember")
    visual_instruction: VisualRecommendation = Field(
        ..., description="Visual instruction ready for canvas, slide, or video renderer"
    )
    should_ask_question: bool = Field(
        True, description="Whether an evaluation question should be presented next"
    )
    audio_script: Optional[str] = Field(
        None, description="Spoken teacher narration script formatted for future TTS"
    )
