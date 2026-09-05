"""Adaptation decision schemas."""
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class AdaptationAction(str, Enum):
    CONTINUE = "continue"
    MOVE_TO_NEXT_CONCEPT = "move_to_next_concept"
    RE_EXPLAIN = "re_explain"
    SIMPLIFY = "simplify"
    CHANGE_ANALOGY = "change_analogy"
    GIVE_ANOTHER_EXAMPLE = "give_another_example"
    REDUCE_DIFFICULTY = "reduce_difficulty"
    INCREASE_DIFFICULTY = "increase_difficulty"
    ASK_ANOTHER_QUESTION = "ask_another_question"
    PROVIDE_GUIDED_PRACTICE = "provide_guided_practice"
    REVISIT_PREREQUISITE = "revisit_prerequisite"


class DifficultyAdjustment(str, Enum):
    DECREASE = "decrease"
    MAINTAIN = "maintain"
    INCREASE = "increase"


class AdaptationDecisionSchema(BaseModel):
    decision_id: str = Field(..., description="Unique ID for this pedagogical decision")
    action: AdaptationAction = Field(..., description="Primary educational adaptation action")
    reason: str = Field(
        ..., description="Explicit pedagogical rationale explaining why this action was chosen"
    )
    strategy: str = Field(
        ..., description="Concrete teaching strategy to execute (e.g. 'Use water-pipe analogy')"
    )
    difficulty_adjustment: DifficultyAdjustment = Field(
        DifficultyAdjustment.MAINTAIN, description="Whether to shift challenge level"
    )
    target_concept: str = Field(..., description="Concept to address in this adaptation step")
    suggested_analogy: Optional[str] = Field(
        None, description="Specific analogy if action is CHANGE_ANALOGY or RE_EXPLAIN"
    )
    suggested_scaffold: Optional[str] = Field(
        None, description="Scaffolding prompt or hint if action is PROVIDE_GUIDED_PRACTICE"
    )
    next_step_summary: str = Field(
        ..., description="Student-friendly summary of what will happen next in the lesson"
    )
