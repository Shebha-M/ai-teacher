"""Subject-Aware Visual Planner: synthesizes structured teaching scenes and educational visuals."""
import uuid
from typing import Optional, List, Dict, Any

from ai_engine.schemas.learner import LearnerProfileSchema
from ai_engine.schemas.lesson import LessonSectionSchema
from ai_engine.schemas.teaching import TeachingResponseSchema
from ai_engine.schemas.misconception import MisconceptionReportSchema
from ai_engine.schemas.adaptation import AdaptationDecisionSchema
from ai_engine.schemas.grounding import GroundedContextSchema, CitationSchema
from ai_engine.schemas.scene import (
    VisualType,
    TeacherEmotion,
    VisualSpecification,
    TeachingScene,
    TeachingScenePlan,
)


from ai_engine.modules.topic_classifier import classify_topic, TopicDomain


class VisualPlanner:
    """
    Analyzes educational subject domains (CS, Math, Physics, Programming, ML) to synthesize
    deterministic, high-fidelity visual specifications and multi-scene video plans.
    """

    @classmethod
    def infer_subject_domain(cls, concept: str, topic: str = "") -> str:
        """Infer academic domain from concept and topic strings using centralized classifier."""
        return classify_topic(topic=topic, concept=concept).value

    @classmethod
    def determine_visual_specification(
        cls,
        concept: str,
        topic: str = "",
        section: Optional[LessonSectionSchema] = None,
    ) -> VisualSpecification:
        """
        Produce a deterministic, subject-aware visual specification with structured data.
        """
        domain = cls.infer_subject_domain(concept, topic)

        # Honor explicit visual recommendation from section/document extractor if available
        if section and section.visual_recommendation and domain in ("general", "programming"):
            vr = section.visual_recommendation
            return VisualSpecification(
                visual_type=vr.visual_type,
                is_deterministic=True,
                render_engine="svg",
                title=f"{vr.visual_type.value.replace('_', ' ').title()}: {concept}",
                data={
                    "concept": concept,
                    "description": vr.description,
                    "elements": vr.suggested_elements,
                },
                highlight_elements=vr.suggested_elements[:2] if vr.suggested_elements else ["element-1"],
                animation_steps=[f"Step {i+1}: {el}" for i, el in enumerate(vr.suggested_elements[:3])],
                description=vr.description or f"Visual representation for {concept}",
            )

        if domain == "machine_learning":
            # Deterministic Neural Network Architecture Visual
            return VisualSpecification(
                visual_type=VisualType.ARCHITECTURE_DIAGRAM,
                is_deterministic=True,
                render_engine="svg",
                title=f"Neural Architecture: {concept}",
                data={
                    "model_type": "Multi-Layer Perceptron (Forward Pass)",
                    "layers": [
                        {
                            "name": "Input Layer",
                            "nodes": [
                                {"id": "x1", "label": "Feature x₁", "val": 2.0},
                                {"id": "x2", "label": "Feature x₂", "val": 1.0},
                            ],
                        },
                        {
                            "name": "Hidden Layer (Dense + ReLU)",
                            "nodes": [
                                {"id": "h1", "label": "Neuron h₁", "weights": [0.5, -0.2], "bias": 0.1, "activation": "ReLU"},
                                {"id": "h2", "label": "Neuron h₂", "weights": [0.3, 0.8], "bias": -0.4, "activation": "ReLU"},
                                {"id": "h3", "label": "Neuron h₃", "weights": [-0.1, 0.6], "bias": 0.2, "activation": "ReLU"},
                            ],
                        },
                        {
                            "name": "Output Layer",
                            "nodes": [
                                {"id": "y", "label": "Prediction ŷ", "activation": "Sigmoid/Linear"},
                            ],
                        },
                    ],
                    "forward_pass_pipeline": [
                        "1. Inputs (x₁, x₂) fed into network",
                        "2. Synaptic weights scale signals: z = Σ(wᵢ · xᵢ) + b",
                        "3. Activation function (ReLU) introduces non-linearity",
                        "4. Output neuron combines activations for final prediction",
                    ],
                    "formula": "z = W · X + b, a = f(z)",
                },
                highlight_elements=["layer-input", "layer-hidden", "layer-output", "formula"],
                animation_steps=[
                    "Feed input signals [x₁, x₂] into input layer",
                    "Compute dot product with synaptic weights: W · X",
                    "Add baseline bias offset (+b) to adjust sensitivity",
                    "Pass weighted sum through non-linear activation f(z)",
                    "Propagate activation values to output neuron ŷ",
                ],
                description="Subject-aware neural network architecture visualizing forward propagation from input features through weighted hidden neurons to prediction output.",
            )

        elif domain == "data_structures":
            # Deterministic Binary Tree Visual
            return VisualSpecification(
                visual_type=VisualType.TREE_DIAGRAM,
                is_deterministic=True,
                render_engine="svg",
                title=f"Hierarchical Structure: {concept}",
                data={
                    "root": {
                        "id": "node-50",
                        "val": 50,
                        "label": "Root Node",
                        "x": 200,
                        "y": 40,
                        "left": {
                            "id": "node-25",
                            "val": 25,
                            "label": "Left Child (< 50)",
                            "x": 100,
                            "y": 120,
                            "left": {"id": "node-10", "val": 10, "label": "Leaf", "x": 50, "y": 200},
                            "right": {"id": "node-35", "val": 35, "label": "Leaf", "x": 150, "y": 200},
                        },
                        "right": {
                            "id": "node-75",
                            "val": 75,
                            "label": "Right Child (> 50)",
                            "x": 300,
                            "y": 120,
                            "left": {"id": "node-60", "val": 60, "label": "Leaf", "x": 250, "y": 200},
                            "right": {"id": "node-90", "val": 90, "label": "Leaf", "x": 350, "y": 200},
                        },
                    },
                    "in_order_sequence": [10, 25, 35, 50, 60, 75, 90],
                    "tree_properties": {
                        "max_children": 2,
                        "height": 3,
                        "ordering": "Left < Node < Right",
                    },
                },
                highlight_elements=["node-50", "node-25", "node-75"],
                animation_steps=[
                    "Render root node (50) at top of hierarchy",
                    "Branch left: place 25 (< 50)",
                    "Branch right: place 75 (> 50)",
                    "Perform in-order traversal: Left subtree -> Root -> Right subtree",
                ],
                description="Interactive SVG binary tree displaying parent-child relationships and logarithmic search branching.",
            )

        elif domain == "physics":
            # Deterministic Circuit & Formula Visual
            return VisualSpecification(
                visual_type=VisualType.CIRCUIT_DIAGRAM,
                is_deterministic=True,
                render_engine="svg",
                title="Closed DC Circuit: Ohm's Law (I = V / R)",
                data={
                    "voltage": "V (Volts, Driving Electrical Pressure)",
                    "current": "I (Amperes, Rate of Charge Flow)",
                    "resistance": "R (Ohms, Opposition to Current Flow)",
                    "formula": "I = V / R",
                    "proportionality": [
                        "Current (I) is directly proportional to Voltage (V)",
                        "Current (I) is inversely proportional to Resistance (R)",
                    ],
                    "circuit_components": [
                        {"type": "dc_source", "label": "Voltage Source (V)"},
                        {"type": "conductive_wire", "label": "Current Path (I)"},
                        {"type": "resistor", "label": "Load Resistor (R)"},
                    ],
                },
                highlight_elements=["formula-box", "resistor-symbol", "flow-arrows"],
                animation_steps=[
                    "Show closed circuit loop with battery",
                    "Highlight current flow arrows clockwise",
                    "Increase resistance: visually constrict electron flow channel",
                    "Derive I = V / R proportionality",
                ],
                description="Schematic circuit diagram illustrating how increasing resistance restricts current flow under constant voltage.",
            )

        elif domain in ["programming", "recursion"]:
            text = f"{concept} {topic}".lower()
            is_rec = any(w in text for w in ["recursion", "recursive", "call stack", "base case"]) or domain == "recursion"
            if is_rec:
                return VisualSpecification(
                    visual_type=VisualType.CODE,
                    is_deterministic=True,
                    render_engine="code",
                    title=f"Implementation: {concept}",
                    data={
                        "language": "python",
                        "code": (
                            "def countdown(n):\n"
                            "    # 1. Base Case: stopping condition\n"
                            "    if n <= 0:\n"
                            "        print('Blastoff!')\n"
                            "        return\n\n"
                            "    # 2. Recursive Case: progress toward base case\n"
                            "    print(f'T-minus {n}...')\n"
                            "    countdown(n - 1)\n\n"
                            "# Execution trace:\n"
                            "# countdown(3) -> countdown(2) -> countdown(1) -> 'Blastoff!'"
                        ),
                        "line_highlights": [3, 4, 5, 8, 9],
                    },
                    highlight_elements=["line-3", "line-4", "line-8", "line-9"],
                    animation_steps=[
                        "Inspect base case guard (n <= 0)",
                        "Trace recursive invocation with (n - 1)",
                        "Unwind call stack upon termination",
                    ],
                    description="Clean, syntax-highlighted Python snippet illustrating base case guard and recursive call progression.",
                )
            else:
                # Deterministic Code Block Visual
                return VisualSpecification(
                    visual_type=VisualType.CODE,
                    is_deterministic=True,
                    render_engine="code",
                    title=f"Implementation: {concept}",
                    data={
                        "language": "python",
                        "code": (
                            "def execute_task(input_data):\n"
                            "    # 1. Initialize result pipeline\n"
                            "    processed = []\n"
                            "    for item in input_data:\n"
                            "        # 2. Transform each element\n"
                            "        value = transform(item)\n"
                            "        processed.append(value)\n"
                            "    # 3. Return verified output\n"
                            "    return processed\n"
                        ),
                        "line_highlights": [1, 3, 4, 6, 7, 9],
                    },
                    highlight_elements=["line-1", "line-4", "line-6", "line-9"],
                    animation_steps=[
                        "Define primary function interface",
                        "Iterate and process elements in sequence",
                        "Aggregate and return computed result",
                    ],
                    description="Clean, syntax-highlighted Python snippet demonstrating structured function execution and transformation.",
                )

        elif domain == "mathematics":
            # Deterministic Equation Visual
            return VisualSpecification(
                visual_type=VisualType.EQUATION,
                is_deterministic=True,
                render_engine="mathjax",
                title=f"Mathematical Derivation: {concept}",
                data={
                    "latex_equation": r"\text{BalanceFactor}(N) = \text{Height}(\text{Left}) - \text{Height}(\text{Right})",
                    "invariant_condition": r"-1 \le \text{BalanceFactor}(N) \le +1",
                    "steps": [
                        r"\text{Height}(N) = 1 + \max(\text{Height}(L), \text{Height}(R))",
                        r"\text{If } |\text{BalanceFactor}(N)| > 1 \implies \text{Rotate to rebalance}",
                    ],
                },
                highlight_elements=["eq-main", "eq-invariant"],
                animation_steps=[
                    "Display balance factor equation",
                    "Highlight height calculation difference",
                    "Verify invariant boundary set {-1, 0, +1}",
                ],
                description="Formal mathematical formula displaying balance factor invariant equations.",
            )

        else:
            # General Flowchart Visual
            return VisualSpecification(
                visual_type=VisualType.FLOWCHART,
                is_deterministic=True,
                render_engine="svg",
                title=f"Conceptual Flow: {concept}",
                data={
                    "steps": [
                        {"id": "step-1", "title": "Understand", "desc": "Grasp foundational definitions"},
                        {"id": "step-2", "title": "Model", "desc": "Establish invariant relationships"},
                        {"id": "step-3", "title": "Apply", "desc": "Trace algorithmic execution"},
                    ]
                },
                highlight_elements=["step-1", "step-2"],
                animation_steps=["Step 1 -> Step 2 -> Step 3"],
                description="Step-by-step conceptual flowchart mapping the progression of ideas.",
            )

    @classmethod
    def create_scene_plan(
        cls,
        section: LessonSectionSchema,
        teaching: TeachingResponseSchema,
        profile: LearnerProfileSchema,
        grounded_context: Optional[GroundedContextSchema] = None,
    ) -> TeachingScenePlan:
        """
        Synthesize a structured 4-scene teaching video plan aligned with pedagogical narration and visual aids.
        """
        sec_id = section.section_id
        concept = section.concept
        citations = grounded_context.citations if grounded_context else []
        plan_id = f"plan-scene-{uuid.uuid4().hex[:8]}"

        # Derive subject-aware visual specification
        visual_spec = cls.determine_visual_specification(concept, section.title, section)

        scenes: List[TeachingScene] = []

        # SCENE 1: Introduction & High-Level Intuition
        s1_citations = citations[:1] if citations else []
        s1 = TeachingScene(
            scene_id=f"{sec_id}-scn-1",
            section_id=sec_id,
            scene_index=1,
            concept=concept,
            scene_type="intro",
            narration=(
                f"Hello {profile.name}! Welcome to our study of {concept}. "
                f"Today, we will build a clear mental model so this idea feels completely intuitive."
            ),
            onscreen_text=f"Welcome! Objective: {section.objective}",
            teacher_action="welcome",
            teacher_emotion=TeacherEmotion.WELCOMING,
            visual_specification=VisualSpecification(
                visual_type=VisualType.TEXT,
                is_deterministic=True,
                render_engine="svg",
                title=concept,
                data={"badge": "Core Objective", "text": section.objective},
                highlight_elements=["badge-title"],
                animation_steps=["Fade in concept title and learner welcome"],
                description="Introductory title card introducing the lesson objective.",
            ),
            estimated_duration=12.0,
            source_references=s1_citations,
            is_checkpoint=False,
        )
        scenes.append(s1)

        # SCENE 2: Core Visual Diagram & Explanation
        s2_narration = teaching.explanation
        if visual_spec.visual_type == VisualType.TREE_DIAGRAM:
            s2_narration = (
                f"Let's look at this diagram together. Notice the topmost circle: that's our Root Node. "
                f"In any Binary Tree, each node can branch into at most two children—a Left child and a Right child. "
                f"{teaching.explanation[:200]}..."
            )
        elif visual_spec.visual_type == VisualType.CIRCUIT_DIAGRAM:
            s2_narration = (
                f"Here is our complete electrical circuit. The battery provides the voltage pressure, "
                f"pushing electrical current through the wire. The resistor restricts this charge flow. "
                f"{teaching.explanation[:200]}..."
            )
        elif visual_spec.visual_type == VisualType.FLOWCHART:
            s2_narration = (
                f"Let's trace this operational workflow step by step on our screen. "
                f"{teaching.explanation[:200]}..."
            )

        s2 = TeachingScene(
            scene_id=f"{sec_id}-scn-2",
            section_id=sec_id,
            scene_index=2,
            concept=concept,
            scene_type="visual_explanation",
            narration=s2_narration,
            onscreen_text=teaching.key_takeaway or f"Key Invariant: {concept}",
            teacher_action="point_to_visual",
            teacher_emotion=TeacherEmotion.EXPLAINING,
            visual_specification=visual_spec,
            estimated_duration=22.0,
            source_references=citations,
            is_checkpoint=False,
        )
        scenes.append(s2)

        # SCENE 3: Analogy & Practical Walkthrough
        s3_narration = teaching.analogy or teaching.example or "Let's trace how this operates in practice."
        s3 = TeachingScene(
            scene_id=f"{sec_id}-scn-3",
            section_id=sec_id,
            scene_index=3,
            concept=concept,
            scene_type="analogy_walkthrough",
            narration=f"To make this memorable: {s3_narration}",
            onscreen_text=f"Analogy: {s3_narration[:100]}...",
            teacher_action="trace_visual",
            teacher_emotion=TeacherEmotion.EXPLAINING,
            visual_specification=visual_spec,
            estimated_duration=18.0,
            source_references=citations[:2] if citations else [],
            is_checkpoint=False,
        )
        scenes.append(s3)

        # SCENE 4: Diagnostic Checkpoint Question Interruption
        chk_prompt = (
            section.question_checkpoint.core_concept
            if section.question_checkpoint
            else f"Check understanding of {concept}"
        )
        s4 = TeachingScene(
            scene_id=f"{sec_id}-scn-4",
            section_id=sec_id,
            scene_index=4,
            concept=concept,
            scene_type="checkpoint_prompt",
            narration=(
                f"Now, let's test your intuition! I have a quick checkpoint question for you. "
                f"Take your time, review the visual, and select the best answer."
            ),
            onscreen_text="Checkpoint Question: Click an option to submit your understanding.",
            teacher_action="ask_question",
            teacher_emotion=TeacherEmotion.THOUGHTFUL,
            visual_specification=VisualSpecification(
                visual_type=VisualType.TEXT,
                is_deterministic=True,
                render_engine="svg",
                title="Checkpoint Check",
                data={"checkpoint_prompt": chk_prompt},
                highlight_elements=["checkpoint-box"],
                animation_steps=["Pause video and present interactive response console"],
                description="Assessment checkpoint pausing video playback for student response.",
            ),
            estimated_duration=10.0,
            source_references=citations[:1] if citations else [],
            is_checkpoint=True,
            branch_target_if_struggling=f"{sec_id}-scn-3-remediation",
        )
        scenes.append(s4)

        total_dur = sum(s.estimated_duration for s in scenes)

        return TeachingScenePlan(
            plan_id=plan_id,
            section_id=sec_id,
            concept=concept,
            total_duration_estimate=total_dur,
            scenes=scenes,
            active_scene_index=0,
            is_adaptive_branch=False,
        )

    @classmethod
    def create_remediation_scene(
        cls,
        concept: str,
        section_id: str,
        misconception: Optional[MisconceptionReportSchema] = None,
        adaptation: Optional[AdaptationDecisionSchema] = None,
    ) -> TeachingScene:
        """
        Synthesize an adaptive branching remediation scene (Scene 3-R) when student struggles.
        Uses an alternative visual analogy rather than repeating the prior explanation.
        """
        counter_analogy = (
            misconception.recommended_counter_analogy
            if misconception and misconception.recommended_counter_analogy
            else "Let's re-examine this using a physical container model."
        )
        reason = adaptation.reason if adaptation else "Let's approach this from a different angle."

        return TeachingScene(
            scene_id=f"{section_id}-scn-3-remediation",
            section_id=section_id,
            scene_index=3,
            concept=concept,
            scene_type="adaptive_remediation",
            narration=(
                f"No worries at all! That's a very common point of confusion. {reason} "
                f"Instead of our earlier example, consider this: {counter_analogy}"
            ),
            onscreen_text=f"Adaptive Help: {counter_analogy[:120]}...",
            teacher_action="encourage",
            teacher_emotion=TeacherEmotion.ENCOURAGING,
            visual_specification=VisualSpecification(
                visual_type=VisualType.FLOWCHART,
                is_deterministic=True,
                render_engine="svg",
                title=f"Alternative Perspective: {concept}",
                data={
                    "remediation_focus": "Dispel Flawed Mental Model",
                    "counter_analogy": counter_analogy,
                    "clarification": "Compare each element explicitly against the constraint rule.",
                },
                highlight_elements=["remediation-box"],
                animation_steps=["Highlight alternative perspective and scaffolding steps"],
                description="Adaptive scaffolding diagram dispelling misconception.",
            ),
            estimated_duration=20.0,
            source_references=[],
            is_checkpoint=False,
        )
