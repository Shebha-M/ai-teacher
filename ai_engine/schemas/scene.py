"""Data contracts and schemas for AI Teaching Video and Subject-Aware Visual Scenes."""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from ai_engine.schemas.grounding import CitationSchema


class VisualType(str, Enum):
    """Categorization of educational visual representations."""
    TEXT = "text"
    EQUATION = "equation"
    GRAPH = "graph"
    DIAGRAM = "diagram"
    FLOWCHART = "flowchart"
    TIMELINE = "timeline"
    MAP = "map"
    LABELED_DIAGRAM = "labeled_diagram"
    CODE = "code"
    CODE_EXECUTION = "code_execution"
    ARCHITECTURE = "architecture"
    TABLE = "table"
    TREE_DIAGRAM = "tree_diagram"
    CIRCUIT_DIAGRAM = "circuit_diagram"
    IMAGE = "image"
    ANIMATION = "animation"
    CUSTOM = "custom"


class TeacherEmotion(str, Enum):
    """Emotional and expressive state of the AI Teacher avatar."""
    WELCOMING = "welcoming"
    EXPLAINING = "explaining"
    ENCOURAGING = "encouraging"
    THOUGHTFUL = "thoughtful"
    CELEBRATING = "celebrating"


class VisualSpecification(BaseModel):
    """
    Structured specification of an on-screen educational visual.
    Contains deterministic data structures ready for client-side SVG/Canvas rendering.
    """
    visual_type: VisualType = Field(..., description="Category of the visual")
    is_deterministic: bool = Field(True, description="True if rendered algorithmically, False if generated image")
    render_engine: str = Field("svg", description="Target renderer: 'svg', 'mathjax', 'code', 'flowchart'")
    title: str = Field(..., description="Title or headline displayed on the visual stage")
    data: Dict[str, Any] = Field(default_factory=dict, description="Structured rendering data (nodes, links, code, math)")
    highlight_elements: List[str] = Field(default_factory=list, description="IDs or labels of elements to highlight in sync with narration")
    animation_steps: List[str] = Field(default_factory=list, description="Ordered animation transitions or trace steps")
    description: str = Field(..., description="Clear explanation of the visual representation")


class TeachingScene(BaseModel):
    """
    Single atomic teaching scene in a segmented educational lesson video.
    Combines synchronized narration, teacher action/emotion, and visual specification.
    """
    scene_id: str = Field(..., description="Unique ID for this scene, e.g. 'scn-1'")
    section_id: str = Field(..., description="Associated lesson section ID")
    scene_index: int = Field(1, description="Sequential position in the scene plan")
    concept: str = Field(..., description="Core concept covered in this scene")
    scene_type: str = Field(
        "visual_explanation",
        description="Type: 'intro', 'visual_explanation', 'analogy_walkthrough', 'example_demonstration', 'checkpoint_prompt', 'adaptive_remediation'",
    )
    narration: str = Field(..., description="Spoken teacher script for audio/speech synthesis")
    onscreen_text: str = Field(..., description="Key takeaway or summary text displayed alongside visual")
    teacher_action: str = Field("explain", description="Action: 'welcome', 'point_to_visual', 'trace_tree', 'ask_question', 'celebrate'")
    teacher_emotion: TeacherEmotion = Field(TeacherEmotion.EXPLAINING, description="Avatar facial expression and mood")
    visual_specification: VisualSpecification = Field(..., description="Visual presentation content")
    estimated_duration: float = Field(15.0, description="Estimated duration in seconds")
    source_references: List[CitationSchema] = Field(
        default_factory=list, description="Preserved RAG document citations with page/slide anchors"
    )
    is_checkpoint: bool = Field(False, description="True if this scene halts video to pose an assessment question")
    branch_target_if_struggling: Optional[str] = Field(
        None, description="Optional scene ID to branch to if student struggles at this checkpoint"
    )
    language: str = Field("en", description="Spoken narration language code")
    audio_asset_id: Optional[str] = Field(None, description="Generated audio asset ID")
    audio_url: Optional[str] = Field(None, description="Direct URL to stream synthesized audio")
    subtitles: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="Timestamped subtitle cues"
    )


class TeachingScenePlan(BaseModel):
    """
    Complete segmented video plan for an educational lesson section.
    Enables non-linear playback, interactive question interruption, and adaptive branching.
    """
    plan_id: str = Field(..., description="Unique identifier for this scene plan")
    section_id: str = Field(..., description="Associated lesson section ID")
    concept: str = Field(..., description="Subject concept")
    total_duration_estimate: float = Field(0.0, description="Estimated total runtime in seconds")
    scenes: List[TeachingScene] = Field(default_factory=list, description="Ordered sequence of teaching scenes")
    active_scene_index: int = Field(0, description="Currently playing scene index (0-based)")
    is_adaptive_branch: bool = Field(False, description="True if this plan represents an adaptive remediation branch")
