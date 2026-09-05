import math
import hashlib
import re
import uuid
from typing import Optional, Type, TypeVar, List, Any, Dict
from pydantic import BaseModel

from ai_engine.providers.base import (
    LLMProvider,
    EmbeddingProvider,
    SpeechProvider,
    AvatarProvider,
    VideoProvider,
)
from ai_engine.schemas.learner import LearnerLevel, LearnerProfileSchema
from ai_engine.schemas.lesson import (
    LessonPlanSchema,
    LessonSectionSchema,
    VisualRecommendation,
    VisualType,
    CheckpointSchema,
)
from ai_engine.schemas.teaching import (
    TeachingResponseSchema,
    TeachingAction,
)
from ai_engine.schemas.question import (
    QuestionSchema,
    QuestionType,
    QuestionOptionSchema,
)
from ai_engine.schemas.evaluation import (
    EvaluationResultSchema,
    CorrectnessLevel,
)
from ai_engine.schemas.misconception import (
    MisconceptionReportSchema,
    MisconceptionCategory,
)
from ai_engine.schemas.adaptation import (
    AdaptationDecisionSchema,
    AdaptationAction,
    DifficultyAdjustment,
)
from ai_engine.schemas.assessment import (
    AssessmentQuestionType,
    AssessmentOption,
    AssessmentQuestion,
    FinalAssessmentSchema,
)
from ai_engine.topic_classifier import classify_topic, TopicDomain

T = TypeVar("T", bound=BaseModel)


class DeterministicTeachingProvider(LLMProvider, EmbeddingProvider, SpeechProvider, AvatarProvider, VideoProvider):
    """
    Deterministic teaching intelligence engine.
    Ensures the system operates reliably without requiring external cloud API keys,
    while enforcing the full educational teaching loop and valid schema outputs.
    """

    async def generate_text(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> str:
        return f"[Deterministic AI Teacher Response]: Processed prompt of {len(prompt)} characters."

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> T:
        """Route to schema-specific generator."""
        if response_schema == LessonPlanSchema:
            topic = kwargs.get("topic", "Binary Trees")
            profile = kwargs.get("profile")
            grounded_context = kwargs.get("grounded_context")
            return self._generate_lesson_plan(topic, profile, grounded_context)  # type: ignore

        elif response_schema == TeachingResponseSchema:
            section = kwargs.get("section")
            profile = kwargs.get("profile")
            grounded_context = kwargs.get("grounded_context")
            return self._generate_teaching_response(section, profile, grounded_context)  # type: ignore

        elif response_schema == QuestionSchema:
            section = kwargs.get("section")
            profile = kwargs.get("profile")
            grounded_context = kwargs.get("grounded_context")
            return self._generate_question(section, profile, grounded_context)  # type: ignore

        elif response_schema == EvaluationResultSchema:
            question = kwargs.get("question")
            student_answer = kwargs.get("student_answer", "")
            profile = kwargs.get("profile")
            return self._evaluate_answer(question, student_answer, profile)  # type: ignore

        elif response_schema == MisconceptionReportSchema:
            question = kwargs.get("question")
            student_answer = kwargs.get("student_answer", "")
            return self._detect_misconception(question, student_answer)  # type: ignore

        elif response_schema == AdaptationDecisionSchema:
            evaluation = kwargs.get("evaluation")
            misconception = kwargs.get("misconception")
            profile = kwargs.get("profile")
            return self._decide_adaptation(evaluation, misconception, profile)  # type: ignore

        elif response_schema == FinalAssessmentSchema:
            topic = kwargs.get("topic", "Binary Trees")
            profile = kwargs.get("profile")
            session_id = kwargs.get("session_id", "sess-default")
            return self._generate_final_assessment(topic, profile, session_id)  # type: ignore

        raise ValueError(f"No deterministic builder available for schema: {response_schema}")

    def _generate_lesson_plan(
        self,
        topic: str,
        profile: Optional[LearnerProfileSchema] = None,
        grounded_context: Optional[Any] = None,
    ) -> LessonPlanSchema:
        time_limit = profile.available_learning_time if profile else 20
        level = profile.educational_level if profile else LearnerLevel.BEGINNER
        lesson_id = f"plan-{uuid.uuid4().hex[:8]}"

        domain = classify_topic(topic=topic)

        has_document_grounding = (
            grounded_context is not None
            and hasattr(grounded_context, "retrieved_chunks")
            and bool(grounded_context.retrieved_chunks)
            and getattr(grounded_context, "document_relevance", "HIGH") != "LOW"
            and not getattr(grounded_context, "insufficient_grounding", False)
        )

        specialized_topics = [
            "binary tree",
            "binary trees",
            "recursion",
            "neural network",
            "neural networks",
            "ohm's law",
            "ohms law",
        ]
        if has_document_grounding and (
            domain in (TopicDomain.GENERAL, TopicDomain.PROGRAMMING)
            or topic.lower() not in specialized_topics
        ):
            from ai_engine.rag.concept_extractor import extract_document_curriculum_concepts

            sections = extract_document_curriculum_concepts(
                grounded_context=grounded_context,
                time_limit=time_limit,
                topic=topic,
                level=level,
                lesson_id=lesson_id,
            )
            cit_fn = (
                grounded_context.citations[0].filename
                if grounded_context.citations
                else "Source Document"
            )
            lesson_title = f"{topic} (Grounded in {cit_fn})"
            ordering = [s.section_id for s in sections]
            learning_objectives = [
                f"Master core operational principles and rules of {topic} grounded in {cit_fn}",
                f"Understand sequential workflows and state transitions documented in {cit_fn}",
                f"Apply practical guidelines, validation checks, and operational policies from {cit_fn}",
            ]
            depth = "document_grounded_curriculum"

        # 1. Machine Learning & Neural Networks Domain
        elif domain == TopicDomain.MACHINE_LEARNING:
            if time_limit <= 10:
                sections = [
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-1",
                        section_number=1,
                        concept="Core Mental Model of Neural Networks & The Forward Pass",
                        title="The Essence of Neural Networks: Inputs, Weights & Outputs",
                        objective="Understand how an artificial neuron computes a weighted sum of inputs plus bias and applies an activation function",
                        difficulty="beginner",
                        estimated_time_minutes=time_limit,
                        explanation_outline="What a neural network is: biological inspiration, feature inputs (x), connection weights (w), bias offset (b), and non-linear activation functions that produce an output prediction.",
                        example_context="Predicting house price: multiplying square footage and bedrooms by learned weights plus baseline bias.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.ARCHITECTURE_DIAGRAM,
                            description="Single neuron forward pass pipeline: inputs x_i -> weights w_i -> sum + bias -> activation f(z) -> output",
                            suggested_elements=["Input Features (x1, x2)", "Synaptic Weights (w1, w2)", "Sum & Bias (z)", "Activation Function", "Output (y)"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-1",
                            core_concept="Neuron forward computation pipeline (Inputs * Weights + Bias)",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student explains that an artificial neuron calculates a weighted sum of inputs plus bias and passes it through an activation function.",
                    )
                ]
                depth = "essential_concepts"
            elif time_limit <= 30:
                sections = [
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-1",
                        section_number=1,
                        concept="The Artificial Neuron: Inputs, Weights, and Biases",
                        title="1. The Artificial Neuron: Inputs, Weights & Biases",
                        objective="Grasp the structural anatomy of an artificial neuron and understand how inputs, weights, and biases interact",
                        difficulty="beginner",
                        estimated_time_minutes=int(time_limit * 0.3),
                        explanation_outline="Biological inspiration to mathematical abstraction. Dissecting the core equation z = sum(w_i * x_i) + b: inputs as feature sensors, weights as learnable signal multipliers, and bias as the baseline activation threshold.",
                        example_context="Credit card fraud scoring: weighting transaction amount, distance, and merchant category with a base threshold.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.ARCHITECTURE_DIAGRAM,
                            description="Neuron computation anatomy showing input dendrites, weighted synapses, summing junction, and bias offset",
                            suggested_elements=["Inputs [x1, x2]", "Weights [w1, w2]", "Summation Node (Σ)", "Bias Offset (+b)", "Weighted Sum (z)"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-1",
                            core_concept="Role of weights and bias in neuron calculations",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student can explain how weights scale input importance and bias shifts the baseline threshold.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-2",
                        section_number=2,
                        concept="Activation Functions & Non-Linearity: ReLU & Sigmoid",
                        title="2. The Activation Function & Non-Linearity",
                        objective="Understand why non-linear activation functions are necessary and compare common functions like ReLU and Sigmoid",
                        difficulty="intermediate" if level != LearnerLevel.BEGINNER else "beginner",
                        estimated_time_minutes=int(time_limit * 0.4),
                        explanation_outline="The linearity trap: why stacking pure linear equations collapses into a single line. Introducing non-linearity: ReLU (max(0, z)) for fast deep training, and Sigmoid (1/(1+e^-z)) for probability squashing between 0 and 1.",
                        example_context="Deciding whether an email is spam: squashing the weighted score between 0% and 100% confidence.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.GRAPH,
                            description="Activation function curves contrasting ReLU ramp vs Sigmoid S-curve response",
                            suggested_elements=["ReLU: max(0, z)", "Sigmoid: 1 / (1 + e^-z)", "Threshold at z=0", "Output Range [0, 1]"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-2",
                            core_concept="Purpose of activation functions in introducing non-linear decision boundaries",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student explains why non-linear activations allow networks to learn complex curves rather than simple straight lines.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-3",
                        section_number=3,
                        concept="The Forward Propagation Pipeline: Trace & Numerical Walkthrough",
                        title="3. The Forward Propagation Pipeline",
                        objective="Trace end-to-end data flow through a network to produce an inference prediction",
                        difficulty="intermediate",
                        estimated_time_minutes=int(time_limit * 0.3),
                        explanation_outline="Step-by-step forward pass execution: Input layer feeds features -> Hidden neurons compute weighted sums -> Non-linear activations fire -> Output neuron synthesizes final prediction. Concrete numerical walkthrough.",
                        example_context="Numerical trace: Inputs [2.0, 1.0], Weights [0.4, 0.8], Bias -0.5 -> z = 1.1 -> ReLU(1.1) = 1.1.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.EXECUTION_TRACE,
                            description="Interactive forward propagation trace showing intermediate signal values flowing left to right",
                            suggested_elements=["Input Layer [2.0, 1.0]", "Dot Product Calculation", "ReLU Activation Step", "Output Prediction ŷ"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-3",
                            core_concept="Tracing forward pass execution: input -> weighted sum -> activation -> prediction",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student can trace and calculate the forward pass output given inputs, weights, bias, and an activation function.",
                    ),
                ]
                depth = "standard_curriculum"
            else:
                sections = [
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-1",
                        section_number=1,
                        concept="Foundations & Philosophy: Biological Inspiration to Artificial Neurons",
                        title="1. Foundations: From Biology to Artificial Neurons",
                        objective="Understand the foundational principles and historical evolution of artificial neural networks",
                        difficulty="beginner",
                        estimated_time_minutes=10,
                        explanation_outline="McCulloch-Pitts neurons, perceptron model, and how interconnected processing units mimic brain signal propagation.",
                        example_context="Biological synapses transmitting neurotransmitters vs mathematical dot products.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.LABELED_DIAGRAM,
                            description="Side-by-side comparison diagram of biological neuron vs mathematical perceptron model",
                            suggested_elements=["Dendrites -> Inputs", "Synapse -> Weights", "Cell Body -> Summation", "Axon -> Output"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-1",
                            core_concept="Biological analogy and perceptron model definition",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student articulates the conceptual mapping from biological neurons to mathematical computational units.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-2",
                        section_number=2,
                        concept="Mathematical Anatomy: Dot Products, Weights, and Biases",
                        title="2. Mathematical Anatomy: Dot Products, Weights & Biases",
                        objective="Master linear algebra representations of neural layers using matrices and bias vectors",
                        difficulty="intermediate",
                        estimated_time_minutes=15,
                        explanation_outline="Vectorized formulation z = W · X + b: matrix multiplication, weight matrices representing layer connections, and bias offset vectors.",
                        example_context="Batch processing 3 samples simultaneously using matrix multiplication.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.EQUATION,
                            description="Matrix multiplication dimension alignment diagram for z = WX + b",
                            suggested_elements=["Weight Matrix W (m x n)", "Input Vector X (n x 1)", "Bias Vector b (m x 1)", "Pre-activation Vector z"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-2",
                            core_concept="Vectorized forward pass and weight matrix dimensions",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student can verify matrix dimensions and calculate pre-activation vectors.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-3",
                        section_number=3,
                        concept="Activation Functions & Representation Power: ReLU, Sigmoid, Softmax",
                        title="3. Activation Functions & Representation Power",
                        objective="Analyze non-linear transformation properties across ReLU, Leaky ReLU, Sigmoid, and Softmax",
                        difficulty="intermediate",
                        estimated_time_minutes=15,
                        explanation_outline="Universal approximation theorem intuition, vanishing gradient pitfalls with Sigmoid, and why ReLU became the industry default.",
                        example_context="Multi-class image classification using Softmax probabilities for 10 classes.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.GRAPH,
                            description="Multi-curve comparison graph of ReLU, Sigmoid, Tanh, and Softmax distributions",
                            suggested_elements=["ReLU Curve", "Sigmoid Curve", "Gradient Vanishing Region", "Softmax Probability Bar"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-3",
                            core_concept="Non-linearity properties and activation selection criteria",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student explains why non-linearity is required to learn arbitrary function boundaries.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-4",
                        section_number=4,
                        concept="Multi-Layer Architectures & The Forward Propagation Pass",
                        title="4. Multi-Layer Architectures & Forward Propagation",
                        objective="Trace multi-layer forward propagation across input, hidden, and output layers",
                        difficulty="advanced" if level != LearnerLevel.BEGINNER else "intermediate",
                        estimated_time_minutes=10,
                        explanation_outline="Feature hierarchy: early layers learning primitive edges, middle layers composing textures, and late layers identifying complete objects.",
                        example_context="Face detection network composing edges -> eyes/nose -> whole face prediction.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.ARCHITECTURE_DIAGRAM,
                            description="Multi-layer deep network showing hierarchical feature abstraction across layers",
                            suggested_elements=["Input Pixels", "Low-Level Edge Filters", "Part Detectors", "Class Prediction Output"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-4",
                            core_concept="Layer-by-layer feature abstraction and forward flow",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student traces how each subsequent hidden layer builds higher-level abstract representations.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-5",
                        section_number=5,
                        concept="Loss Computation, Error Intuition & Real-World ML Systems",
                        title="5. Loss Computation, Error Intuition & Real-World ML",
                        objective="Connect forward pass predictions to loss functions (MSE, Cross-Entropy) and optimization setup",
                        difficulty="advanced",
                        estimated_time_minutes=10,
                        explanation_outline="Quantifying prediction error: Mean Squared Error (MSE) for regression vs Cross-Entropy Loss for classification. Preparing for backpropagation.",
                        example_context="Comparing model prediction 0.85 against ground truth label 1.0 to compute loss.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.FLOWCHART,
                            description="End-to-end ML lifecycle loop: Forward Pass -> Loss Function -> Backpropagation -> Weight Update",
                            suggested_elements=["Forward Prediction ŷ", "Target Label y", "Loss Function L(y, ŷ)", "Optimization Signal"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-5",
                            core_concept="Loss function calculation and connection to learning",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student explains how the forward pass output is evaluated against ground truth via a loss function.",
                    ),
                ]
                depth = "deep_dive_masterclass"

            ordering = [s.section_id for s in sections]
            lesson_title = f"Mastering {topic}: An Intuitive Journey"
            learning_objectives = [
                "Demystify the core mental model of artificial neurons, feature inputs, weights, and biases",
                "Understand why non-linear activation functions (ReLU, Sigmoid) are essential for representation power",
                "Trace end-to-end forward propagation from input features to output prediction through numerical calculation",
            ]

        # 2. Recursion & Call Stacks Domain
        elif domain == TopicDomain.RECURSION:
            if time_limit <= 10:
                sections = [
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-1",
                        section_number=1,
                        concept="Core Definition of Recursion: Base Cases & Self-Reference",
                        title="The Essence of Recursion: Base Cases & Self-Reference",
                        objective="Understand how a function solves a problem by breaking it into a smaller version of itself with a stopping condition",
                        difficulty="beginner",
                        estimated_time_minutes=time_limit,
                        explanation_outline="What recursion is: functions calling themselves, the essential role of a base case, and why stopping conditions prevent infinite loops.",
                        example_context="Countdown function from 3 to 1: counting down until reaching 0 (base case).",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.FLOWCHART,
                            description="Decision flowchart contrasting base case return vs recursive call branch",
                            suggested_elements=["Function Call", "Is Base Case Met?", "Return Direct Value", "Recursive Call with n-1"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-1",
                            core_concept="Base case termination requirement",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student explains that every recursive function needs a base case to stop and a recursive case that moves toward it.",
                    )
                ]
                depth = "essential_concepts"
            elif time_limit <= 30:
                sections = [
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-1",
                        section_number=1,
                        concept="Foundational Intuition: Self-Reference & Base Cases",
                        title="1. Foundational Intuition: Self-Reference & Base Cases",
                        objective="Grasp the core mental model of recursion and identify the two mandatory components: base case and recursive step",
                        difficulty="beginner",
                        estimated_time_minutes=int(time_limit * 0.3),
                        explanation_outline="Demystifying recursion through nested problem solving. Structure of a recursive function: when to stop (base case) and how to reduce the problem (recursive step).",
                        example_context="Russian nesting dolls and computing factorial: 3! = 3 * 2!.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.LABELED_DIAGRAM,
                            description="Diagram showing nested problems shrinking until reaching the base case anchor",
                            suggested_elements=["Outer Problem (n=3)", "Subproblem (n=2)", "Base Case Anchor (n=1)", "Return Propagation"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-1",
                            core_concept="Base case and recursive case structure",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student identifies the base case and explains how each step reduces toward it.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-2",
                        section_number=2,
                        concept="The Call Stack: How Functions Remember & Return",
                        title="2. The Call Stack & Execution Tracing",
                        objective="Trace how computer memory manages recursive calls using stack frames",
                        difficulty="intermediate" if level != LearnerLevel.BEGINNER else "beginner",
                        estimated_time_minutes=int(time_limit * 0.4),
                        explanation_outline="Understanding the call stack: pushing new stack frames for each call, local variable isolation, waiting for child calls to return, and popping frames during unwinding.",
                        example_context="Step-by-step trace of factorial(3) pushing frames onto the stack and resolving values upon unwinding.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.EXECUTION_TRACE,
                            description="Call stack memory visualization showing stack frames being pushed then popped",
                            suggested_elements=["Stack Frame factorial(3)", "Stack Frame factorial(2)", "Stack Frame factorial(1)", "Return Value Unwinding"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-2",
                            core_concept="Call stack memory allocation and unwinding order",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student can trace how stack frames pause, wait for child calls, and unwind in LIFO order.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-3",
                        section_number=3,
                        concept="Practical Recursion & Avoiding Common Pitfalls",
                        title="3. Practical Patterns & Avoiding Stack Overflow",
                        objective="Write bug-free recursive logic and recognize common mistakes like missing base cases or improper reduction",
                        difficulty="intermediate",
                        estimated_time_minutes=int(time_limit * 0.3),
                        explanation_outline="Debugging recursive code: diagnosing stack overflow errors, ensuring inputs always progress towards the base case, and comparing recursion vs loops.",
                        example_context="Searching nested file system directories and diagnosing an infinite recursion bug.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.FLOWCHART,
                            description="Decision flowchart comparing safe terminating recursion vs unbounded stack overflow",
                            suggested_elements=["Input Progression Check", "Base Case Guard", "Safe Termination", "Stack Overflow Trap"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-3",
                            core_concept="Stack overflow causes and recursion termination guards",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student explains how missing or unreachable base cases cause stack overflow and how to prevent it.",
                    ),
                ]
                depth = "standard_curriculum"
            else:
                sections = [
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-1",
                        section_number=1,
                        concept="Core Philosophy: Self-Reference & Function Anatomy",
                        title="1. Core Philosophy: Self-Reference & Function Anatomy",
                        objective="Rigorous understanding of recursive problem decomposition, base cases, and recursive steps",
                        difficulty="beginner",
                        estimated_time_minutes=10,
                        explanation_outline="Mathematical induction foundations, formal definition of recursion, separating the base case from the induction step, and writing first clean recursive functions.",
                        example_context="Mathematical induction and recursive countdown/sum of integers.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.LABELED_DIAGRAM,
                            description="Anatomy diagram of a recursive function highlighting base case guard, argument decrement, and return statement",
                            suggested_elements=["Function Signature", "Base Case Guard Clause", "Self-Referential Call", "Return Value Assembler"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-1",
                            core_concept="Recursive function structure and base case invariants",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student can define a recursive function with guaranteed base case termination.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-2",
                        section_number=2,
                        concept="The Call Stack: Memory Allocation & Frame Mechanics",
                        title="2. Call Stack Mechanics & Memory Frames",
                        objective="Understand how the OS and language runtime manage recursive calls in memory",
                        difficulty="intermediate",
                        estimated_time_minutes=15,
                        explanation_outline="Call stack memory architecture: stack frames, return address storage, parameter passing, stack pointers, and LIFO unwinding behavior.",
                        example_context="Memory snapshot tracing a 4-level recursive call stack with local variable frames.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.EXECUTION_TRACE,
                            description="Call stack memory frame diagram showing push order, return pointer addresses, and frame deallocation",
                            suggested_elements=["Active Stack Frame", "Previous Frame (Paused)", "Stack Pointer", "Frame Deallocation"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-2",
                            core_concept="Stack frame allocation and LIFO return order",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student explains how memory is allocated per call and why local variables do not overwrite each other.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-3",
                        section_number=3,
                        concept="Tracing Recursive Calls: Call Trees & Execution Paths",
                        title="3. Tracing Execution: Linear vs Branching Recursion",
                        objective="Trace complex recursive executions and visualize branching call trees",
                        difficulty="intermediate",
                        estimated_time_minutes=15,
                        explanation_outline="Visualizing execution: single linear recursion vs multi-branch recursion (e.g. Fibonacci, divide & conquer). Understanding call trees, evaluation order, and redundant subproblem calculation.",
                        example_context="Tracing Fibonacci(4) call tree to visualize overlapping subproblems.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.CONCEPT_MAP,
                            description="Recursive call tree illustrating branching invocations and intermediate returned values",
                            suggested_elements=["Root Call", "Left Branch Call", "Right Branch Call", "Leaf Base Returns"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-3",
                            core_concept="Branching call tree evaluation order and redundant computation",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student draws and evaluates recursive call trees, predicting intermediate outputs.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-4",
                        section_number=4,
                        concept="Common Pitfalls: Stack Overflow & Debugging",
                        title="4. Common Pitfalls: Stack Overflow & Debugging",
                        objective="Identify, prevent, and debug recursion failure modes like missing base cases and stack exhaustion",
                        difficulty="advanced" if level != LearnerLevel.BEGINNER else "intermediate",
                        estimated_time_minutes=10,
                        explanation_outline="Detailed inspection of recursion bugs: missing base case, incorrect base case boundary conditions, infinite recursive loops, and maximum call stack size limits.",
                        example_context="Debugging a broken recursion that loops indefinitely on negative indices.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.CODE_BLOCK,
                            description="Side-by-side code diff showing buggy infinite recursion vs corrected bounded recursion",
                            suggested_elements=["Missing Base Case Bug", "Stack Overflow Error", "Corrected Base Condition", "Boundary Check"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-4",
                            core_concept="Stack overflow diagnosis and termination guarantees",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student diagnoses why a broken recursive snippet crashes and writes the corrective termination guard.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-5",
                        section_number=5,
                        concept="Performance, Space-Time Complexity & Optimization",
                        title="5. Space-Time Complexity, Tail Recursion & Optimization",
                        objective="Analyze space and time complexity of recursive algorithms and understand optimization techniques",
                        difficulty="advanced",
                        estimated_time_minutes=10,
                        explanation_outline="Recursion vs iteration trade-offs: call overhead, O(N) auxiliary stack space vs O(1) loop space, introduction to tail-call optimization and memoization principles.",
                        example_context="Transforming an exponential O(2^N) recursive Fibonacci into a memoized O(N) solution.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.GRAPH,
                            description="Performance growth curve comparing naive branching recursion vs memoized recursive execution time",
                            suggested_elements=["Exponential O(2^N) Curve", "Linear O(N) Curve", "Call Stack Depth Axis", "Execution Time"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-5",
                            core_concept="Auxiliary stack space complexity and optimization trade-offs",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student calculates call stack space complexity and explains when to optimize or convert recursion.",
                    ),
                ]
                depth = "deep_dive_masterclass"

            ordering = [s.section_id for s in sections]
            lesson_title = f"Mastering {topic}: An Intuitive Journey"
            learning_objectives = [
                "Demystify the core mental model of self-referential problem solving and base cases",
                "Master call stack execution tracing, frame allocations, and LIFO unwinding",
                "Learn to debug infinite recursion, prevent stack overflows, and analyze space-time trade-offs",
            ]

        # 3. Data Structures & Binary Trees Domain
        elif domain == TopicDomain.DATA_STRUCTURES:
            if time_limit <= 10:
                sections = [
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-1",
                        section_number=1,
                        concept=f"Core Definition of {topic}",
                        title=f"The Essence of {topic}",
                        objective=f"Understand the fundamental hierarchy and branching rules of {topic}",
                        difficulty="beginner",
                        estimated_time_minutes=time_limit,
                        explanation_outline=f"Clear definition, mental model, and why {topic} matters for hierarchical data organization.",
                        example_context="Minimal visual scenario isolating the core branching principle.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.LABELED_DIAGRAM,
                            description=f"High-contrast structural schematic of {topic}",
                            suggested_elements=["Root Node", "Left Branch", "Right Branch", "Leaf Values"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-1",
                            core_concept=f"Definition of {topic}",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding=f"Student can explain what {topic} is in plain English.",
                    )
                ]
                depth = "essential_concepts"
            elif time_limit <= 30:
                sections = [
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-1",
                        section_number=1,
                        concept=f"Intuition & Fundamentals of {topic}",
                        title="1. Foundational Intuition",
                        objective=f"Grasp the structural anatomy and rules of {topic}",
                        difficulty="beginner",
                        estimated_time_minutes=int(time_limit * 0.3),
                        explanation_outline=f"Breakdown of {topic}: node anatomy, hierarchy, and basic properties.",
                        example_context="Everyday decision tree and folder hierarchy comparison.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.LABELED_DIAGRAM,
                            description=f"Hierarchical tree diagram showing parent-child node relationships",
                            suggested_elements=["Root Node (50)", "Left Child (25)", "Right Child (75)", "Leaf Nodes"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-1",
                            core_concept="Node hierarchy and max child constraints",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student understands node relationships and hierarchy.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-2",
                        section_number=2,
                        concept=f"Core Operations & Properties of {topic}",
                        title="2. How It Works: Traversal & Operations",
                        objective=f"Trace how elements are placed, searched, and traversed in {topic}",
                        difficulty="intermediate" if level != LearnerLevel.BEGINNER else "beginner",
                        estimated_time_minutes=int(time_limit * 0.4),
                        explanation_outline="Step-by-step traversal mechanics: In-order, Pre-order, and logarithmic search.",
                        example_context="Searching for a contact in an alphabetized address book.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.FLOWCHART,
                            description="Decision flowchart for binary search decision branching (left if less, right if greater)",
                            suggested_elements=["Compare target with current", "Branch Left if <", "Branch Right if >"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-2",
                            core_concept="Search and traversal ordering rules",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student can predict traversal order and search comparisons.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-3",
                        section_number=3,
                        concept=f"Practical Real-World Application of {topic}",
                        title="3. Practical Application & Trade-offs",
                        objective=f"Recognize when to choose {topic} over alternative data structures",
                        difficulty="intermediate",
                        estimated_time_minutes=int(time_limit * 0.3),
                        explanation_outline="Performance comparison: Array vs Linked List vs Tree. Time complexity O(log N).",
                        example_context="Database index lookups and file system directories.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.GRAPH,
                            description="Time complexity growth curve comparing O(N) linear search vs O(log N) tree search",
                            suggested_elements=["Linear O(N) Curve", "Logarithmic O(log N) Curve", "Input size N axis"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-3",
                            core_concept="Time complexity and data structure selection",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student explains why logarithmic time enables massive scale.",
                    ),
                ]
                depth = "standard_curriculum"
            else:
                sections = [
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-1",
                        section_number=1,
                        concept=f"Anatomy and Mathematical Principles of {topic}",
                        title="1. Mathematical & Structural Anatomy",
                        objective=f"Rigorous breakdown of {topic} invariants, height definitions, and properties",
                        difficulty="beginner",
                        estimated_time_minutes=10,
                        explanation_outline=f"Formal definitions, inductive definitions, and tree terminology.",
                        example_context="Geometric branching structures in nature and computation.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.LABELED_DIAGRAM,
                            description="Detailed taxonomy diagram highlighting height, depth, level, and balance factor",
                            suggested_elements=["Depth 0 Root", "Internal Nodes", "Subtrees", "Leaf Nodes"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-1",
                            core_concept="Tree height and node counting theorems",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student can compute tree height and maximum nodes at level K.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-2",
                        section_number=2,
                        concept=f"Algorithm Traversal Paradigms in {topic}",
                        title="2. Traversal Deep-Dive: DFS vs BFS",
                        objective="Compare Depth-First Search (In-order, Pre-order, Post-order) with Breadth-First Level-Order",
                        difficulty="intermediate",
                        estimated_time_minutes=15,
                        explanation_outline="Call stack recursion mechanics during DFS vs Queue-based BFS traversal.",
                        example_context="Serializing a tree for cloud storage vs rendering UI hierarchies.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.EXECUTION_TRACE,
                            description="Call stack execution trace visualization showing recursive frame allocations",
                            suggested_elements=["Stack Frame 1", "Stack Frame 2", "Base Case Return", "Visited Array"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-2",
                            core_concept="Call stack behavior and traversal ordering",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student can write and trace recursive traversal without infinite loops.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-3",
                        section_number=3,
                        concept=f"Self-Balancing and Pathological Edge Cases in {topic}",
                        title="3. Balance, Skewed Trees, and Invariants",
                        objective="Analyze worst-case degradation to linked lists O(N) and the necessity of balancing",
                        difficulty="advanced",
                        estimated_time_minutes=15,
                        explanation_outline="Degenerate trees, insertion order sensitivity, and AVL/Red-Black rotation intuition.",
                        example_context="Inserting already-sorted numbers [1, 2, 3, 4, 5] into an unmanaged tree.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.ARCHITECTURE_DIAGRAM,
                            description="Before-and-after tree rotation diagram demonstrating AVL balance restoration",
                            suggested_elements=["Unbalanced Skewed Branch", "Pivot Node", "Rebalanced Tree"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-3",
                            core_concept="Degenerate tree complexity and tree rotations",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student explains how sorted input degrades BST performance to O(N).",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-4",
                        section_number=4,
                        concept=f"Production Implementation & Memory Layout of {topic}",
                        title="4. Memory Layout, Pointers, and Implementation",
                        objective="Understand pointer overhead, cache locality, and array-based binary heaps",
                        difficulty="advanced",
                        estimated_time_minutes=10,
                        explanation_outline="Pointer dereference cache misses vs continuous memory layout in array heaps.",
                        example_context="High-frequency trading order books and OS process priority schedulers.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.CODE_BLOCK,
                            description="Memory representation mapping node pointers to contiguous array indices [2i + 1, 2i + 2]",
                            suggested_elements=["Pointer Node Struct", "Contiguous Array Buffer", "Index Arithmetic Formula"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-4",
                            core_concept="Memory layout and array-based tree indexing",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student derives parent/child indices in array-backed binary trees.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-5",
                        section_number=5,
                        concept=f"Comprehensive Synthesis & Architectural Design for {topic}",
                        title="5. System Design Synthesis & Mastery",
                        objective="Architect real-world solutions combining trees with persistence and indexing",
                        difficulty="advanced",
                        estimated_time_minutes=10,
                        explanation_outline="B-Trees and LSM Trees in distributed databases (PostgreSQL, SQLite, Cassandra).",
                        example_context="Designing an ultra-fast indexing engine for millions of records.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.CONCEPT_MAP,
                            description="Comprehensive taxonomy connecting Binary Trees, BSTs, AVL, Heaps, and B-Trees",
                            suggested_elements=["Binary Tree", "Binary Search Tree", "Self-Balancing", "B-Tree Disk Storage"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-5",
                            core_concept="System design trade-offs across tree variants",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding="Student articulates how database storage engines leverage tree invariants.",
                    ),
                ]
                depth = "deep_dive_masterclass"

            ordering = [s.section_id for s in sections]
            lesson_title = f"Mastering {topic}: An Intuitive Journey"
            learning_objectives = [
                f"Demystify the core mental model and invariants of {topic}",
                f"Master practical navigation and operational mechanics",
                f"Develop intuition for performance trade-offs and real-world applications",
            ]

        # 4. Universal / General Domain Fallback (Safe, domain-neutral curriculum)
        else:
            if time_limit <= 10:
                sections = [
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-1",
                        section_number=1,
                        concept=f"Core Essence & Principles of {topic}",
                        title=f"The Essence of {topic}: Core Principles",
                        objective=f"Understand the fundamental motivation, core principle, and primary purpose of {topic}",
                        difficulty="beginner",
                        estimated_time_minutes=time_limit,
                        explanation_outline=f"Clear definition, mental model, and real-world significance of {topic} without extraneous jargon.",
                        example_context=f"Real-world scenario illustrating the primary utility of {topic}.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.LABELED_DIAGRAM,
                            description=f"High-contrast schematic diagram outlining the core components of {topic}",
                            suggested_elements=["Input / Context", "Core Transformation", "Output / Result"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-1",
                            core_concept=f"Definition and primary purpose of {topic}",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding=f"Student can explain what {topic} is and why it matters in plain English.",
                    )
                ]
                depth = "essential_concepts"
            elif time_limit <= 30:
                sections = [
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-1",
                        section_number=1,
                        concept=f"Foundational Intuition & Core Principles of {topic}",
                        title="1. Foundational Intuition & Core Principles",
                        objective=f"Grasp the foundational rules, key definitions, and structural anatomy of {topic}",
                        difficulty="beginner",
                        estimated_time_minutes=int(time_limit * 0.3),
                        explanation_outline=f"Comprehensive breakdown of {topic}: core components, relationships, and governing principles.",
                        example_context=f"Everyday parallel and intuitive mental model for {topic}.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.LABELED_DIAGRAM,
                            description=f"Conceptual diagram showing the primary structural building blocks of {topic}",
                            suggested_elements=["Foundational Rule", "Core Component", "System Boundary"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-1",
                            core_concept=f"Core components and foundational rules of {topic}",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding=f"Student understands the core components and foundational rules of {topic}.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-2",
                        section_number=2,
                        concept=f"Operational Mechanics & Execution Flow in {topic}",
                        title="2. Operational Mechanics & Execution Flow",
                        objective=f"Trace how {topic} operates step-by-step to process information and achieve results",
                        difficulty="intermediate" if level != LearnerLevel.BEGINNER else "beginner",
                        estimated_time_minutes=int(time_limit * 0.4),
                        explanation_outline=f"Step-by-step workflow of {topic}: inputs, internal processing stages, state transitions, and expected outputs.",
                        example_context=f"Walkthrough of a representative execution pipeline in {topic}.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.FLOWCHART,
                            description=f"Step-by-step procedural flowchart mapping the execution flow of {topic}",
                            suggested_elements=["Initial Input", "Processing Stage", "Decision Gate", "Final Output"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-2",
                            core_concept=f"Step-by-step operational mechanics of {topic}",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding=f"Student can trace the sequential operational flow of {topic}.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-3",
                        section_number=3,
                        concept=f"Practical Application & Real-World Trade-offs in {topic}",
                        title="3. Practical Application & Trade-offs",
                        objective=f"Analyze practical use cases, best practices, and performance trade-offs of {topic}",
                        difficulty="intermediate",
                        estimated_time_minutes=int(time_limit * 0.3),
                        explanation_outline=f"Real-world engineering scenarios: performance considerations, common pitfalls, and practical implementation tips for {topic}.",
                        example_context=f"Industry case study demonstrating when and how to leverage {topic}.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.GRAPH,
                            description=f"Analytical trade-off comparison diagram evaluating efficiency vs complexity in {topic}",
                            suggested_elements=["Efficiency Metric", "Complexity Axis", "Optimal Operating Zone"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-3",
                            core_concept=f"Practical implementation trade-offs of {topic}",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding=f"Student can articulate real-world advantages, limitations, and trade-offs of {topic}.",
                    ),
                ]
                depth = "standard_curriculum"
            else:
                sections = [
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-1",
                        section_number=1,
                        concept=f"Theoretical Foundations & First Principles of {topic}",
                        title="1. Theoretical Foundations & First Principles",
                        objective=f"Rigorous mathematical, scientific, or conceptual foundation of {topic}",
                        difficulty="beginner",
                        estimated_time_minutes=10,
                        explanation_outline=f"First-principles derivation, formal definitions, and foundational axioms governing {topic}.",
                        example_context=f"Theoretical formulation isolating the governing invariants of {topic}.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.LABELED_DIAGRAM,
                            description=f"Formal taxonomic diagram structuring the core theoretical principles of {topic}",
                            suggested_elements=["Axiom / Base", "Governing Invariant", "Theoretical Boundary"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-1",
                            core_concept=f"Foundational axioms and invariants of {topic}",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding=f"Student understands the formal first principles of {topic}.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-2",
                        section_number=2,
                        concept=f"Structural Mechanics & Core Architecture of {topic}",
                        title="2. Structural Mechanics & Core Architecture",
                        objective=f"Analyze the internal architecture and operational dynamics of {topic}",
                        difficulty="intermediate",
                        estimated_time_minutes=15,
                        explanation_outline=f"Detailed structural breakdown: subsystem interactions, state management, and execution protocols in {topic}.",
                        example_context=f"Architectural walkthrough of an industrial-grade implementation of {topic}.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.EXECUTION_TRACE,
                            description=f"Execution trace diagram mapping internal interactions within {topic}",
                            suggested_elements=["Subsystem A", "Subsystem B", "Interaction Bus", "Verified Output"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-2",
                            core_concept=f"Internal architecture and subsystem interactions in {topic}",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding=f"Student can trace internal communication and state transitions in {topic}.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-3",
                        section_number=3,
                        concept=f"Practical Implementation & Execution Flow in {topic}",
                        title="3. Practical Implementation & Execution Flow",
                        objective=f"Implement and trace practical workflows in {topic} with concrete examples",
                        difficulty="intermediate",
                        estimated_time_minutes=15,
                        explanation_outline=f"Hands-on implementation walkthrough: setting up pipelines, executing operations, and verifying outcomes in {topic}.",
                        example_context=f"Step-by-step practical implementation snippet in {topic}.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.CODE_BLOCK,
                            description=f"Structured code block or workflow diagram illustrating concrete implementation of {topic}",
                            suggested_elements=["Configuration", "Execution Call", "Assertion / Check"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-3",
                            core_concept=f"Practical execution pipeline and outcome verification in {topic}",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding=f"Student can implement and verify a working solution in {topic}.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-4",
                        section_number=4,
                        concept=f"Edge Cases, Diagnostics & Troubleshooting in {topic}",
                        title="4. Edge Cases, Diagnostics & Troubleshooting",
                        objective=f"Identify failure modes, pathological edge cases, and debugging strategies for {topic}",
                        difficulty="advanced" if level != LearnerLevel.BEGINNER else "intermediate",
                        estimated_time_minutes=10,
                        explanation_outline=f"Troubleshooting manual: common anti-patterns, boundary condition failures, and diagnostic procedures in {topic}.",
                        example_context=f"Diagnosing and resolving a subtle production bug in {topic}.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.FLOWCHART,
                            description=f"Diagnostic decision tree for isolating and resolving faults in {topic}",
                            suggested_elements=["Symptom Check", "Root Cause Test", "Corrective Action"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-4",
                            core_concept=f"Failure mode diagnostics and edge-case handling in {topic}",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding=f"Student can diagnose and remedy edge-case failures in {topic}.",
                    ),
                    LessonSectionSchema(
                        section_id=f"{lesson_id}-sec-5",
                        section_number=5,
                        concept=f"System Integration & Advanced Mastery of {topic}",
                        title="5. System Integration & Advanced Mastery",
                        objective=f"Integrate {topic} into large-scale production architectures and analyze scaling limits",
                        difficulty="advanced",
                        estimated_time_minutes=10,
                        explanation_outline=f"High-level synthesis: horizontal scaling, distributed architectures, and long-term maintenance of {topic}.",
                        example_context=f"Deploying {topic} in an enterprise distributed cloud environment.",
                        visual_recommendation=VisualRecommendation(
                            visual_type=VisualType.CONCEPT_MAP,
                            description=f"Comprehensive architectural map showing {topic} integrated into enterprise systems",
                            suggested_elements=["Service Gateway", f"{topic} Core Engine", "Persistence Layer", "Monitoring"],
                        ),
                        question_checkpoint=CheckpointSchema(
                            checkpoint_id="chk-5",
                            core_concept=f"System design trade-offs and scaling strategies in {topic}",
                            trigger_condition="after_section_explanation",
                        ),
                        expected_understanding=f"Student can architect scalable production systems incorporating {topic}.",
                    ),
                ]
                depth = "deep_dive_masterclass"

            ordering = [s.section_id for s in sections]
            lesson_title = f"Mastering {topic}: An Intuitive Journey"
            learning_objectives = [
                f"Demystify the foundational mental model and core principles of {topic}",
                f"Master the step-by-step operational mechanisms and workflow of {topic}",
                f"Analyze practical trade-offs, real-world applications, and best practices in {topic}",
            ]

        if has_document_grounding and not lesson_title.endswith(f"(Grounded in {cit_fn})"):
            lesson_title = f"{topic} (Grounded in {cit_fn})"
            learning_objectives.insert(0, f"Master core curriculum grounded in source: {cit_fn}")
            if sections and not sections[0].objective.startswith("Master"):
                first_chunk = grounded_context.retrieved_chunks[0]
                loc = grounded_context.citations[0].location if grounded_context.citations else "Excerpt"
                sections[0].objective = f"Grounded Study ({loc}): Master concepts from {cit_fn}"
                sections[0].explanation_outline = f"Source text: {first_chunk.text_content[:140]}..."

        return LessonPlanSchema(
            lesson_id=lesson_id,
            topic=topic,
            lesson_title=lesson_title,
            learning_objectives=learning_objectives,
            estimated_duration=time_limit,
            learner_level=level,
            sections=sections,
            section_ordering=ordering,
            explanation_depth=depth,
            examples=[s.example_context for s in sections],
            questions=[s.concept for s in sections],
            checkpoints=[s.question_checkpoint.core_concept for s in sections if s.question_checkpoint],
            final_assessment_direction="Interactive scenario-based checkpoint and adaptive synthesis review.",
        )

    def _generate_teaching_response(
        self,
        section: Optional[LessonSectionSchema],
        profile: Optional[LearnerProfileSchema],
        grounded_context: Optional[Any] = None,
    ) -> TeachingResponseSchema:
        concept = section.concept if section else "Core Principles"
        section_id = section.section_id if section else "sec-1"
        style = profile.preferred_teaching_style if profile else "analogy_driven"

        # Topic & Concept tailored educational narratives
        domain = classify_topic(concept=concept, topic=section.title if section else concept)
        if domain == TopicDomain.MACHINE_LEARNING:
            explanation = (
                "A Neural Network is a computational architecture inspired by biological nervous systems, designed to "
                "approximate complex functions through interconnected layers of neurons. In a forward pass, an artificial "
                "neuron receives numerical inputs, scales each input by a learnable **Weight** (representing feature importance), "
                "adds a **Bias** term (shifting the activation threshold), and passes the sum through a non-linear "
                "**Activation Function** (such as ReLU) to produce an output signal."
            )
            analogy = (
                "Think of an artificial neuron like a Decision Committee voting on a proposal. Each committee member "
                "(input feature) casts a vote, but each member carries a specific credibility weight. The bias is the "
                "committee's baseline skepticism before hearing any votes. If the combined weighted score exceeds the "
                "threshold, the committee approves the proposal!"
            )
            example = (
                "Consider a concrete forward pass for a single neuron: Inputs X = [2.0, 1.0], Weights W = [0.4, 0.8], "
                "and Bias b = -0.5. First, compute the weighted linear combination: "
                "z = (2.0 * 0.4) + (1.0 * 0.8) + (-0.5) = 0.8 + 0.8 - 0.5 = 1.1. "
                "Next, pass z through a ReLU activation: a = max(0, 1.1) = 1.1. The neuron fires an output signal of 1.1!"
            )
            key_takeaway = "The forward pass transforms inputs via z = W·X + b, followed by non-linear activation a = f(z)."
            visual = VisualRecommendation(
                visual_type=VisualType.ARCHITECTURE_DIAGRAM,
                description="Multi-layer neural network forward pass showing inputs, weights, bias offset, and ReLU activation",
                suggested_elements=["Input Features [X1, X2]", "Synaptic Weights [W1, W2]", "Weighted Sum Node (z = W·X + b)", "ReLU Non-Linear Output (a)"],
            )
        elif domain == TopicDomain.RECURSION:
            explanation = (
                "Recursion is a problem-solving technique where a function solves a problem by calling a smaller "
                "version of itself. Every valid recursive function rests on two critical pillars: the **Base Case** "
                "(the condition that stops the recursion) and the **Recursive Step** (the self-referential call that moves "
                "closer to the base case). Without a base case, calls repeat endlessly until system memory is exhausted!"
            )
            analogy = (
                "Think of recursion like a set of Russian nesting dolls (Matryoshka). To reach the golden prize in the center, "
                "you open an outer doll to find a slightly smaller doll inside. You repeat this until you reach the smallest solid doll "
                "that cannot be opened—that is your Base Case! Only then do you close the dolls back up, one by one."
            )
            example = (
                "Consider computing 3! (factorial of 3). factorial(3) pauses and calls 3 * factorial(2). "
                "factorial(2) pauses and calls 2 * factorial(1). factorial(1) hits the base case and returns 1 immediately. "
                "Now the call stack unwinds: factorial(2) gets 1 and returns 2 * 1 = 2; factorial(3) gets 2 and returns 3 * 2 = 6."
            )
            key_takeaway = "Recursion breaks problems into identical subproblems; the base case terminates the call stack."
            visual = VisualRecommendation(
                visual_type=VisualType.EXECUTION_TRACE,
                description="Step-by-step recursive call stack trace showing frame allocation and LIFO unwinding",
                suggested_elements=["factorial(3) [Waiting]", "factorial(2) [Waiting]", "factorial(1) [Base Case: Return 1]", "Stack Unwinding"],
            )
        elif domain == TopicDomain.DATA_STRUCTURES:
            explanation = (
                "Imagine you are organizing a tournament or a family tree. At the very top, you have one starting "
                "point called the **Root Node**. From there, every single item can branch into at most two paths: "
                "a **Left Child** and a **Right Child**. This simple constraint—never more than two branches—is what "
                "gives a Binary Tree its immense power: by making just one decision at each step, you cut the remaining "
                "possibilities in half!"
            )
            analogy = (
                "Think of a Binary Tree like playing a game of '20 Questions'. Instead of scanning through a million "
                "possibilities one by one, each question eliminates half of the universe. In 20 steps, you can pinpoint "
                "one item out of over one million!"
            )
            example = (
                "Consider searching for the number 35 in a Binary Search Tree where the root is 50. Because 35 < 50, "
                "you immediately discard the entire right subtree without ever inspecting it. You step left to node 25. "
                "Since 35 > 25, you step right. In two comparisons, you've narrowed your search!"
            )
            key_takeaway = "A Binary Tree enforces a 2-way hierarchical branching rule, enabling logarithmic efficiency."
            visual = VisualRecommendation(
                visual_type=VisualType.LABELED_DIAGRAM,
                description="Visual schematic of a Binary Search Tree with highlighted search path from Root(50) to 35",
                suggested_elements=["Root Node (50)", "Left Branch (Green Path)", "Discarded Right Subtree (Greyed Out)", "Target Node (35)"],
            )
        elif domain == TopicDomain.PHYSICS_ELECTRONICS or "Ohm" in concept or "Circuit" in concept or "Resistance" in concept:
            explanation = (
                "Ohm's Law is the foundational law of electricity, governed by the formula **V = I × R**. "
                "Voltage (V) is the electrical pressure pushing charge, Current (I) is the actual flow rate of electrons, "
                "and Resistance (R) is the friction or narrowing of the pathway pushing back against that flow."
            )
            analogy = (
                "Think of water flowing through a garden hose. Voltage is how wide you open the tap (water pressure). "
                "Current is the volume of water gushing out per second. Resistance is your foot stepping on the hose: "
                "if you press harder (increase resistance) while water pressure is constant, less water can flow!"
            )
            example = (
                "If a 9-volt battery is connected to a 3-ohm resistor, the current flowing through is I = V / R = 9V / 3Ω = 3 Amperes. "
                "If you swap in a higher 9-ohm resistor, the current drops down to 1 Ampere."
            )
            key_takeaway = "Current is inversely proportional to resistance when voltage is constant (I = V / R)."
            visual = VisualRecommendation(
                visual_type=VisualType.EQUATION,
                description="Ohm's Law triangle with interactive sliders for Voltage, Current, and Resistance",
                suggested_elements=["V = I x R", "I = V / R", "Water pipe cross-section diagram"],
            )
        else:
            # Extract source excerpt if this section is document-grounded
            source_excerpt = ""
            if section and "Source excerpt:" in (section.explanation_outline or ""):
                parts = section.explanation_outline.split("Source excerpt:")
                if len(parts) > 1:
                    source_excerpt = parts[1].split("Key operational")[0].strip()
            elif (
                grounded_context
                and hasattr(grounded_context, "retrieved_chunks")
                and grounded_context.retrieved_chunks
                and getattr(grounded_context, "document_relevance", "HIGH") != "LOW"
            ):
                source_excerpt = grounded_context.retrieved_chunks[0].text_content[:260].strip()

            if source_excerpt:
                clean_excerpt = re.sub(r"\s+", " ", source_excerpt).strip()
                explanation = (
                    f"In this section, we study **{concept}** directly from the verified operational procedures in your course documentation. "
                    f"Core excerpt: \"{clean_excerpt}\" "
                    f"Understanding these rules ensures correct execution, state synchronization, and reliable outcomes."
                )
                analogy = (
                    f"Think of {concept} like a secure checkpoint or gatekeeper: each entry must have verified parameters, "
                    "a clean timestamp, and explicit approval before transitioning to the next active state."
                )
                example = (
                    f"For example, during day-to-day operations for {concept}: when an action is initiated, the system validates the "
                    "inputs against policy boundaries, executes the state transition, and logs the outcome for auditability."
                )
                key_takeaway = f"Key Invariant: {concept} enforces verifiable, step-by-step execution and state tracking."
                visual = (
                    section.visual_recommendation
                    if section and section.visual_recommendation
                    else VisualRecommendation(
                        visual_type=VisualType.FLOWCHART,
                        description=f"Operational process flow for {concept}",
                        suggested_elements=["Action Trigger", "Validation Rule", "State Transition", "Audit Log"],
                    )
                )
            else:
                explanation = (
                    f"Let's break down **{concept}** into its core fundamental components. At its heart, {concept} "
                    "is designed to solve a specific challenge by breaking complex behavior into simple, predictable rules. "
                    "When you master the underlying invariant, every advanced application becomes straightforward."
                )
                analogy = (
                    f"Think of {concept} like an efficient assembly line: every station has a dedicated role, ensuring "
                    "work flows smoothly without bottlenecks."
                )
                example = (
                    f"In a real-world scenario, applying {concept} streamlines operations from ad-hoc effort into "
                    "a clean, predictable pipeline."
                )
                key_takeaway = f"The fundamental rule of {concept} guarantees predictability, modularity, and scalability."
                visual = (
                    section.visual_recommendation
                    if section
                    else VisualRecommendation(
                        visual_type=VisualType.LABELED_DIAGRAM,
                        description=f"Conceptual breakdown diagram of {concept}",
                        suggested_elements=["Input Context", "Core Transformation", "Verified Output"],
                    )
                )

        if (
            grounded_context
            and hasattr(grounded_context, "retrieved_chunks")
            and grounded_context.retrieved_chunks
            and not getattr(grounded_context, "insufficient_grounding", False)
        ):
            cit = grounded_context.citations[0] if (hasattr(grounded_context, "citations") and grounded_context.citations) else None
            first_chunk = grounded_context.retrieved_chunks[0]
            doc_file = cit.filename if cit else getattr(first_chunk, "filename", "Uploaded Material")
            cit_label = f"{cit.filename} ({cit.location})" if (cit and hasattr(cit, "location")) else doc_file
            grounding_banner = (
                f"📖 **Directly from your uploaded course material ({cit_label}):**\n"
                f"> \"{first_chunk.text_content[:240]}...\"\n\n"
            )
            if doc_file not in explanation and grounding_banner not in explanation:
                explanation = grounding_banner + explanation

        return TeachingResponseSchema(
            section_id=section_id,
            concept=concept,
            teaching_action=TeachingAction.EXPLAIN,
            explanation=explanation,
            analogy=analogy,
            example=example,
            key_takeaway=key_takeaway,
            visual_instruction=visual,
            should_ask_question=True,
            audio_script=f"Welcome to {section.title if section else concept}. {explanation} {analogy}",
        )

    def _generate_question(
        self,
        section: Optional[LessonSectionSchema],
        profile: Optional[LearnerProfileSchema],
        grounded_context: Optional[Any] = None,
    ) -> QuestionSchema:
        concept = section.concept if section else "General Concept"
        section_id = section.section_id if section else "sec-1"
        q_id = f"q-{uuid.uuid4().hex[:8]}"

        domain = classify_topic(concept=concept, topic=section.title if section else concept)
        if domain == TopicDomain.MACHINE_LEARNING:
            q = QuestionSchema(
                question_id=q_id,
                section_id=section_id,
                concept="Role of Synaptic Weights and Biases in a Neuron",
                question_type=QuestionType.MULTIPLE_CHOICE,
                prompt="In an artificial neuron's forward pass, what is the role of the 'weight' applied to an input?",
                options=[
                    QuestionOptionSchema(key="A", text="It sets the number of layers in the network"),
                    QuestionOptionSchema(key="B", text="It scales the input signal to reflect that feature's relative importance"),
                    QuestionOptionSchema(key="C", text="It guarantees that all outputs are rounded to integers"),
                    QuestionOptionSchema(key="D", text="It deletes irrelevant inputs from memory"),
                ],
                expected_answer="B",
                difficulty="beginner",
                rubric="The student must identify that weights scale and modulate the strength/importance of incoming input signals.",
                hints=["Think about the Decision Committee analogy: what gives one expert's opinion more influence than another?"],
            )
        elif domain == TopicDomain.RECURSION:
            q = QuestionSchema(
                question_id=q_id,
                section_id=section_id,
                concept="Base Case Invariant in Recursion",
                question_type=QuestionType.MULTIPLE_CHOICE,
                prompt="What is the primary purpose of the 'base case' in a recursive function?",
                options=[
                    QuestionOptionSchema(key="A", text="To allocate a new stack frame for each call"),
                    QuestionOptionSchema(key="B", text="To provide a stopping condition that prevents infinite recursion"),
                    QuestionOptionSchema(key="C", text="To speed up loop execution by doubling memory usage"),
                    QuestionOptionSchema(key="D", text="To convert recursive calls directly into tree nodes"),
                ],
                expected_answer="B",
                difficulty="beginner",
                rubric="The student must identify that the base case is the essential guard condition that terminates recursive calls.",
                hints=["Think about what would happen if a countdown never checked whether n reached 0."],
            )
        elif domain == TopicDomain.DATA_STRUCTURES:
            q = QuestionSchema(
                question_id=q_id,
                section_id=section_id,
                concept="Binary Tree Node Constraint & Hierarchy",
                question_type=QuestionType.MULTIPLE_CHOICE,
                prompt="What is the maximum number of children any single node can have in a Binary Tree?",
                options=[
                    QuestionOptionSchema(key="A", text="Exactly 1 child"),
                    QuestionOptionSchema(key="B", text="At most 2 children (0, 1, or 2)"),
                    QuestionOptionSchema(key="C", text="Must always have exactly 2 children"),
                    QuestionOptionSchema(key="D", text="Any arbitrary number of children"),
                ],
                expected_answer="B",
                difficulty="beginner",
                rubric="The student must identify that 'binary' allows 0, 1, or 2 children, but never more than 2.",
                hints=["Remember what the prefix 'bi-' means in bicycle or binary."],
            )
        elif domain == TopicDomain.PHYSICS_ELECTRONICS or "Ohm" in concept or "Circuit" in concept or "Resistance" in concept:
            q = QuestionSchema(
                question_id=q_id,
                section_id=section_id,
                concept="Relationship between Current and Resistance under constant Voltage",
                question_type=QuestionType.SHORT_ANSWER,
                prompt="In a simple circuit with a constant voltage source, what happens to the electrical current if you increase the resistance?",
                expected_answer="The current decreases (it is inversely proportional to resistance: I = V / R).",
                difficulty="intermediate",
                rubric="The student must clearly state that current decreases because resistance opposes the flow of charge (I = V / R).",
                hints=["Think about the water hose analogy: what happens to the flow when you step on the hose?"],
            )
        else:
            is_grounded = (
                (section and "Source excerpt:" in (section.explanation_outline or ""))
                or (
                    grounded_context
                    and hasattr(grounded_context, "retrieved_chunks")
                    and grounded_context.retrieved_chunks
                    and getattr(grounded_context, "document_relevance", "HIGH") != "LOW"
                    and not getattr(grounded_context, "insufficient_grounding", False)
                )
            )
            if is_grounded:
                q = QuestionSchema(
                    question_id=q_id,
                    section_id=section_id,
                    concept=concept,
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    prompt=f"According to the source documentation for {concept}, what is the essential operational rule or requirement?",
                    options=[
                        QuestionOptionSchema(
                            key="A",
                            text="Operations can bypass authorization without recording timestamps",
                        ),
                        QuestionOptionSchema(
                            key="B",
                            text="State changes must follow structured validation, verifiable tracking, and status updates",
                        ),
                        QuestionOptionSchema(
                            key="C",
                            text="All historical session records are automatically discarded upon exit",
                        ),
                        QuestionOptionSchema(
                            key="D",
                            text="Unrestricted concurrent modifications without validation safeguards",
                        ),
                    ],
                    expected_answer="B",
                    difficulty="beginner",
                    rubric=f"Student identifies that {concept} enforces structured validation and verifiable tracking based on the documentation.",
                    hints=[f"Think about the validation steps and status checks required for {concept}."],
                )
            else:
                q = QuestionSchema(
                    question_id=q_id,
                    section_id=section_id,
                    concept=concept,
                    question_type=QuestionType.EXPLAIN_IN_OWN_WORDS,
                    prompt=f"Explain in your own words the primary purpose of {concept} and why it is useful.",
                    expected_answer=f"{concept} provides a structured mechanism to organize and process information efficiently.",
                    difficulty="intermediate",
                    rubric="Student explains the core motivation and at least one practical advantage.",
                    hints=["Think back to our analogy about streamlining an assembly line."],
                )

        if grounded_context and hasattr(grounded_context, "citations") and grounded_context.citations:
            cit = grounded_context.citations[0]
            q.hints.append(f"Refer to {cit.filename} ({cit.location}) for review.")

        return q

    def _evaluate_answer(
        self, question: Optional[QuestionSchema], student_answer: str, profile: Optional[LearnerProfileSchema]
    ) -> EvaluationResultSchema:
        answer_clean = student_answer.strip().lower()
        eval_id = f"eval-{uuid.uuid4().hex[:8]}"
        q_id = question.question_id if question else "q-unknown"
        concept = question.concept if question else "Target Concept"

        # Check for Multiple Choice question evaluation
        if question and question.question_type == QuestionType.MULTIPLE_CHOICE:
            q_domain = classify_topic(concept=question.concept, topic=question.prompt)
            if q_domain == TopicDomain.MACHINE_LEARNING:
                if (
                    answer_clean in ["b", "option b", "scales the input", "relative importance", "feature importance"]
                    or "option b" in answer_clean
                    or "importance" in answer_clean
                    or "scales" in answer_clean
                    or (answer_clean.startswith("b") and len(answer_clean) <= 3)
                ):
                    return EvaluationResultSchema(
                        evaluation_id=eval_id,
                        question_id=q_id,
                        correctness=CorrectnessLevel.CORRECT,
                        score=1.0,
                        strengths=["Accurately recognized that weights scale input signals based on feature importance."],
                        error_summary=None,
                        missing_concepts=[],
                        misconception_suspected=False,
                        detected_misconception_id=None,
                        rubric_feedback="Spot on! Weights modulate the contribution of each feature in the linear combination z = W·X + b.",
                        recommended_teacher_action="Advance to activation functions and non-linear thresholding.",
                    )
                elif (
                    answer_clean in ["a", "option a", "number of layers", "layer count"]
                    or "option a" in answer_clean
                    or "layers" in answer_clean
                    or (answer_clean.startswith("a") and len(answer_clean) <= 3)
                ):
                    return EvaluationResultSchema(
                        evaluation_id=eval_id,
                        question_id=q_id,
                        correctness=CorrectnessLevel.INCORRECT_MISCONCEPTION,
                        score=0.2,
                        strengths=["Recognized that weights are an architectural parameter in neural networks."],
                        error_summary="Confused individual connection weights with architectural network depth (layer count).",
                        missing_concepts=["Synaptic weight as feature coefficient", "Layer depth vs connection weights"],
                        misconception_suspected=True,
                        detected_misconception_id="misc-ml-weight-vs-layers",
                        rubric_feedback="Careful! Network depth (number of layers) is a structural hyperparameter. Weights are numerical multipliers on individual connections.",
                        recommended_teacher_action="Revisit the Decision Committee analogy showing how weights represent voter credibility.",
                    )
                else:
                    return EvaluationResultSchema(
                        evaluation_id=eval_id,
                        question_id=q_id,
                        correctness=CorrectnessLevel.INCORRECT_LACK_OF_KNOWLEDGE,
                        score=0.0,
                        strengths=[],
                        error_summary=f"Selected '{student_answer}' which does not reflect neural network fundamentals.",
                        missing_concepts=["Weight modulation in forward pass"],
                        misconception_suspected=False,
                        detected_misconception_id=None,
                        rubric_feedback="Not quite. In a neural network forward pass, weights scale each input signal to determine how strongly it influences the neuron's activation.",
                        recommended_teacher_action="Review the linear transformation formula z = W·X + b.",
                    )
            elif q_domain == TopicDomain.RECURSION or any(w in question.concept.lower() for w in ["recursion", "base case", "call stack"]):
                if (
                    answer_clean in ["b", "option b", "stopping condition", "prevents infinite recursion", "stop"]
                    or "option b" in answer_clean
                    or "stopping" in answer_clean
                    or "infinite" in answer_clean
                    or (answer_clean.startswith("b") and len(answer_clean) <= 3)
                ):
                    return EvaluationResultSchema(
                        evaluation_id=eval_id,
                        question_id=q_id,
                        correctness=CorrectnessLevel.CORRECT,
                        score=1.0,
                        strengths=["Accurately recognized that the base case provides the stopping condition to prevent infinite recursion."],
                        error_summary=None,
                        missing_concepts=[],
                        misconception_suspected=False,
                        detected_misconception_id=None,
                        rubric_feedback="Spot on! Without a base case, recursive calls would continue pushing frames onto the stack until memory is exhausted.",
                        recommended_teacher_action="Advance to call stack tracing and frame deallocation.",
                    )
                elif (
                    answer_clean in ["a", "option a", "allocate stack frame", "stack frame"]
                    or "option a" in answer_clean
                    or "allocate" in answer_clean
                    or (answer_clean.startswith("a") and len(answer_clean) <= 3)
                ):
                    return EvaluationResultSchema(
                        evaluation_id=eval_id,
                        question_id=q_id,
                        correctness=CorrectnessLevel.INCORRECT_MISCONCEPTION,
                        score=0.2,
                        strengths=["Recognized that stack frames are part of recursive execution."],
                        error_summary="Confused the base case with the recursive step; stack frames are allocated on recursive calls, not at the base case.",
                        missing_concepts=["Base case as stopping condition", "Stack unwinding on base case return"],
                        misconception_suspected=True,
                        detected_misconception_id="misc-recursion-base-case-role",
                        rubric_feedback="Close, but careful! New stack frames are allocated when a function makes another call. The base case stops that process and begins unwinding.",
                        recommended_teacher_action="Clarify base case termination using the countdown stopping condition.",
                    )
                else:
                    return EvaluationResultSchema(
                        evaluation_id=eval_id,
                        question_id=q_id,
                        correctness=CorrectnessLevel.INCORRECT_LACK_OF_KNOWLEDGE,
                        score=0.0,
                        strengths=[],
                        error_summary=f"Selected '{student_answer}' which does not reflect recursion fundamentals.",
                        missing_concepts=["Base case termination guard"],
                        misconception_suspected=False,
                        detected_misconception_id=None,
                        rubric_feedback="Not quite. In recursion, the base case is the essential guard condition that stops the function from calling itself forever.",
                        recommended_teacher_action="Revisit the countdown or Russian doll analogy to show why a stopping point is mandatory.",
                    )
            elif q_domain == TopicDomain.DATA_STRUCTURES or any(
                w in (question.concept.lower() if question else "")
                for w in ["tree", "node", "branch", "child", "traversal"]
            ):
                if (
                    answer_clean
                    in ["b", "option b", "at most 2", "at most 2 children", "0, 1, or 2"]
                    or "option b" in answer_clean
                    or "at most 2" in answer_clean
                    or (answer_clean.startswith("b") and len(answer_clean) <= 3)
                ):
                    return EvaluationResultSchema(
                        evaluation_id=eval_id,
                        question_id=q_id,
                        correctness=CorrectnessLevel.CORRECT,
                        score=1.0,
                        strengths=[
                            "Accurately recognized that a binary tree node can have 0, 1, or 2 children."
                        ],
                        error_summary=None,
                        missing_concepts=[],
                        misconception_suspected=False,
                        detected_misconception_id=None,
                        rubric_feedback="Spot on! A node doesn't have to be completely full—it can have zero (leaf), one, or two children.",
                        recommended_teacher_action="Advance to traversal mechanics or increase difficulty.",
                    )
                elif (
                    answer_clean in ["c", "option c", "must always have exactly 2", "always 2"]
                    or "option c" in answer_clean
                    or "always have exactly 2" in answer_clean
                    or "must always have" in answer_clean
                    or "exactly 2" in answer_clean
                    or (answer_clean.startswith("c") and len(answer_clean) <= 3)
                ):
                    return EvaluationResultSchema(
                        evaluation_id=eval_id,
                        question_id=q_id,
                        correctness=CorrectnessLevel.INCORRECT_MISCONCEPTION,
                        score=0.25,
                        strengths=["Understands that 2 is the governing upper bound for binary branching."],
                        error_summary="Believed that nodes MUST always have 2 children, overlooking leaf nodes and single-child nodes.",
                        missing_concepts=["Leaf nodes (0 children)", "Degenerate/Single-child branches"],
                        misconception_suspected=True,
                        detected_misconception_id="misc-tree-must-have-two",
                        rubric_feedback="Common trap! While 'binary' means the maximum is 2, leaf nodes at the bottom have 0 children.",
                        recommended_teacher_action="Clarify leaf nodes with a visual diagram showing empty branches.",
                    )
                elif (
                    answer_clean in ["d", "option d", "arbitrary", "any number", "3 or 4", "unlimited"]
                    or "option d" in answer_clean
                    or "arbitrary" in answer_clean
                    or "any number" in answer_clean
                    or "unlimited" in answer_clean
                    or (answer_clean.startswith("d") and len(answer_clean) <= 3)
                ):
                    return EvaluationResultSchema(
                        evaluation_id=eval_id,
                        question_id=q_id,
                        correctness=CorrectnessLevel.INCORRECT_MISCONCEPTION,
                        score=0.1,
                        strengths=[],
                        error_summary="Confused general unconstrained tree structures with binary trees, assuming unlimited children per node.",
                        missing_concepts=["Binary branching constraint (maximum 2)", "Left/Right child topology"],
                        misconception_suspected=True,
                        detected_misconception_id="misc-tree-arbitrary-children",
                        rubric_feedback="Careful! While a general tree can have any number of children, a *Binary* Tree strictly caps branching at a maximum of two.",
                        recommended_teacher_action="Re-explain the 2-way hierarchical branching rule using a fork-in-the-road analogy.",
                    )
                else:
                    return EvaluationResultSchema(
                        evaluation_id=eval_id,
                        question_id=q_id,
                        correctness=CorrectnessLevel.INCORRECT_LACK_OF_KNOWLEDGE,
                        score=0.0,
                        strengths=[],
                        error_summary=f"Selected '{student_answer}' which does not reflect binary tree rules.",
                        missing_concepts=["Binary branching constraint (maximum of 2)"],
                        misconception_suspected=False,
                        detected_misconception_id=None,
                        rubric_feedback="Not quite. In computer science, 'binary' means each node can branch into at most two directions: left and right.",
                        recommended_teacher_action="Re-explain the binary prefix and provide a visual branching diagram.",
                    )
            else:
                # Universal / Document-Grounded MCQ Evaluation
                if (
                    answer_clean
                    in [
                        "b",
                        "option b",
                        "structured validation",
                        "verifiable tracking",
                        "validation",
                    ]
                    or "option b" in answer_clean
                    or "structured" in answer_clean
                    or "tracking" in answer_clean
                    or "validation" in answer_clean
                    or (answer_clean.startswith("b") and len(answer_clean) <= 3)
                ):
                    return EvaluationResultSchema(
                        evaluation_id=eval_id,
                        question_id=q_id,
                        correctness=CorrectnessLevel.CORRECT,
                        score=1.0,
                        strengths=[
                            f"Accurately identified that {concept} requires structured validation and verifiable tracking."
                        ],
                        error_summary=None,
                        missing_concepts=[],
                        misconception_suspected=False,
                        detected_misconception_id=None,
                        rubric_feedback="Spot on! The operational workflow requires verified tracking and authorized state updates.",
                        recommended_teacher_action="Advance to practical execution or next section.",
                    )
                elif answer_clean in [
                    "a",
                    "option a",
                    "c",
                    "option c",
                    "d",
                    "option d",
                ] or any(k in answer_clean for k in ["bypass", "discarded", "unrestricted"]):
                    return EvaluationResultSchema(
                        evaluation_id=eval_id,
                        question_id=q_id,
                        correctness=CorrectnessLevel.INCORRECT_MISCONCEPTION,
                        score=0.2,
                        strengths=["Attempted to identify operational constraints."],
                        error_summary=f"Selected '{student_answer}' which violates the governance and audit requirements of {concept}.",
                        missing_concepts=["State validation", "Audit trail / record-keeping"],
                        misconception_suspected=True,
                        detected_misconception_id="misc-general-unconstrained-flow",
                        rubric_feedback="Careful! Operational procedures require rigorous validation and verifiable tracking—actions cannot bypass authorization.",
                        recommended_teacher_action="Review the workflow steps and status check rules.",
                    )
                else:
                    return EvaluationResultSchema(
                        evaluation_id=eval_id,
                        question_id=q_id,
                        correctness=CorrectnessLevel.INCORRECT_LACK_OF_KNOWLEDGE,
                        score=0.0,
                        strengths=[],
                        error_summary=f"Selected '{student_answer}' which does not reflect {concept} rules.",
                        missing_concepts=["Core workflow rules"],
                        misconception_suspected=False,
                        detected_misconception_id=None,
                        rubric_feedback=f"Not quite. Remember that {concept} is governed by structured validation and status tracking.",
                        recommended_teacher_action=f"Re-explain the core rules of {concept}.",
                    )

        # Non-MCQ Evaluation
        non_mcq_domain = classify_topic(
            concept=concept, topic=question.prompt if question else ""
        )
        if non_mcq_domain == TopicDomain.PHYSICS_ELECTRONICS or any(
            k in (question.concept.lower() if question else "")
            for k in ["ohm", "circuit", "resistance"]
        ):
            if (
                "increases" in answer_clean
                or "goes up" in answer_clean
                or "more current" in answer_clean
            ):
                return EvaluationResultSchema(
                    evaluation_id=eval_id,
                    question_id=q_id,
                    correctness=CorrectnessLevel.INCORRECT_MISCONCEPTION,
                    score=0.1,
                    strengths=["Identified that changing resistance impacts current."],
                    error_summary="Stated that current increases when resistance increases, reversing the inverse relationship.",
                    missing_concepts=[
                        "Inverse proportionality",
                        "Ohm's Law formula I = V / R",
                        "Resistance as friction",
                    ],
                    misconception_suspected=True,
                    detected_misconception_id="misc-inverse-proportionality-ohm",
                    rubric_feedback="Careful! Resistance is an obstacle that *resists* the flow of current. When resistance goes up, flow drops!",
                    recommended_teacher_action="Deploy the water-pipe constriction analogy to physically ground resistance.",
                )
            elif (
                "decreases" in answer_clean
                or "drops" in answer_clean
                or "less current" in answer_clean
                or "goes down" in answer_clean
            ):
                has_formula_or_reason = (
                    "invers" in answer_clean
                    or "v = i" in answer_clean
                    or "i = v" in answer_clean
                    or "oppose" in answer_clean
                    or "resist" in answer_clean
                )
                if has_formula_or_reason:
                    return EvaluationResultSchema(
                        evaluation_id=eval_id,
                        question_id=q_id,
                        correctness=CorrectnessLevel.CORRECT,
                        score=1.0,
                        strengths=[
                            "Correctly identified that current decreases and explained the inverse relationship."
                        ],
                        error_summary=None,
                        missing_concepts=[],
                        misconception_suspected=False,
                        detected_misconception_id=None,
                        rubric_feedback="Excellent deduction! Because I = V / R, increasing the denominator R naturally forces current I down.",
                        recommended_teacher_action="Proceed to practical calculation or next lesson section.",
                    )
                else:
                    return EvaluationResultSchema(
                        evaluation_id=eval_id,
                        question_id=q_id,
                        correctness=CorrectnessLevel.PARTIALLY_CORRECT,
                        score=0.75,
                        strengths=["Correctly identified that current decreases."],
                        error_summary="Did not explain the governing physical principle or mathematical relationship (I = V / R).",
                        missing_concepts=[
                            "Formulaic justification (I = V / R)",
                            "Concept of inverse proportionality",
                        ],
                        misconception_suspected=False,
                        detected_misconception_id=None,
                        rubric_feedback="Good intuition! Current indeed decreases. To make your understanding rock-solid, remember *why*: I = V / R.",
                        recommended_teacher_action="Acknowledge correctness and reinforce the mathematical justification.",
                    )
            else:
                return EvaluationResultSchema(
                    evaluation_id=eval_id,
                    question_id=q_id,
                    correctness=CorrectnessLevel.INCORRECT_LACK_OF_KNOWLEDGE,
                    score=0.2,
                    strengths=["Attempted the question."],
                    error_summary="Did not articulate the relationship between resistance and current.",
                    missing_concepts=["Current response to resistance shift", "Ohm's Law"],
                    misconception_suspected=False,
                    detected_misconception_id=None,
                    rubric_feedback="Let's revisit this step-by-step. Remember that resistance measures how hard it is for electricity to flow.",
                    recommended_teacher_action="Re-explain the fundamental interaction between voltage, current, and resistance.",
                )
        else:
            # Universal / General Conceptual Answer Evaluation
            if len(answer_clean.split()) >= 4:
                return EvaluationResultSchema(
                    evaluation_id=eval_id,
                    question_id=q_id,
                    correctness=CorrectnessLevel.CORRECT,
                    score=1.0,
                    strengths=[
                        f"Articulated the primary purpose and utility of {concept}."
                    ],
                    error_summary=None,
                    missing_concepts=[],
                    misconception_suspected=False,
                    detected_misconception_id=None,
                    rubric_feedback=f"Well said! You clearly conveyed how {concept} provides structured execution and reliability.",
                    recommended_teacher_action="Advance to the next section or synthesize mastery.",
                )
            else:
                return EvaluationResultSchema(
                    evaluation_id=eval_id,
                    question_id=q_id,
                    correctness=CorrectnessLevel.PARTIALLY_CORRECT,
                    score=0.6,
                    strengths=["Recognized the topic name."],
                    error_summary=f"Provided a very brief response for {concept} without elaborating on operational advantages.",
                    missing_concepts=["Practical utility and operational workflow"],
                    misconception_suspected=False,
                    detected_misconception_id=None,
                    rubric_feedback="Good start! Try expanding with one concrete example of how this applies in practice.",
                    recommended_teacher_action="Prompt for an applied scenario.",
                )

    def _detect_misconception(
        self, question: Optional[QuestionSchema], student_answer: str
    ) -> MisconceptionReportSchema:
        answer_clean = student_answer.strip().lower()
        concept = question.concept if question else "General Concept"
        misc_id = f"misc-{uuid.uuid4().hex[:8]}"

        q_domain = classify_topic(concept=concept, topic=question.prompt if question else "")
        if q_domain == TopicDomain.MACHINE_LEARNING:
            if (
                answer_clean in ["a", "option a", "number of layers", "layer count"]
                or "option a" in answer_clean
                or "layers" in answer_clean
                or (answer_clean.startswith("a") and len(answer_clean) <= 3)
            ):
                return MisconceptionReportSchema(
                    misconception_id=misc_id,
                    concept="Synaptic Weights vs Network Depth",
                    category=MisconceptionCategory.CONFUSING_CONCEPTS,
                    is_misconception=True,
                    flawed_mental_model="Student confuses connection weights with the macroscopic structural depth (number of layers) of the network.",
                    correct_mental_model="Weights are learnable scalar multipliers assigned to individual input edges; network depth is determined by the total number of sequential layers.",
                    evidence_from_response=f"Student answered: '{student_answer}'",
                    recommended_counter_analogy="Think of a committee: each member has a microphone volume knob (weight), which is completely separate from how many committees exist in the organization.",
                    prerequisite_to_review="Anatomy of an artificial neuron: inputs, weights, bias, and layers.",
                )

        if question and any(w in question.concept.lower() for w in ["recursion", "base case", "call stack"]):
            if (
                answer_clean in ["a", "option a", "allocate", "stack frame"]
                or "option a" in answer_clean
                or (answer_clean.startswith("a") and len(answer_clean) <= 3)
            ):
                return MisconceptionReportSchema(
                    misconception_id=misc_id,
                    concept="Base Case Invariant in Recursion",
                    category=MisconceptionCategory.CONFUSING_CONCEPTS,
                    is_misconception=True,
                    flawed_mental_model="Student believes the base case triggers further recursive execution and frame allocation.",
                    correct_mental_model="The base case is the stopping condition that immediately returns without further recursive invocations.",
                    evidence_from_response=f"Student answered: '{student_answer}'",
                    recommended_counter_analogy="Think of a countdown timer: reaching zero triggers the buzzer and stops the clock, rather than starting a new countdown.",
                    prerequisite_to_review="Base case vs recursive case anatomy.",
                )

        if "increases" in answer_clean or "goes up" in answer_clean:
            return MisconceptionReportSchema(
                misconception_id=misc_id,
                concept="Ohm's Law & Circuit Flow",
                category=MisconceptionCategory.INVERSE_RELATION_CONFUSION,
                is_misconception=True,
                flawed_mental_model="Student believes current is directly proportional to resistance ('more resistance means more electricity').",
                correct_mental_model="Current is inversely proportional to resistance when voltage is constant (I = V / R). Higher resistance chokes flow.",
                evidence_from_response=f"Student answered: '{student_answer}'",
                recommended_counter_analogy="Water-pipe analogy: Squeezing a hose increases resistance, visibly reducing water outflow.",
                prerequisite_to_review="Basic definition of electrical resistance as opposition to charge movement.",
            )
        elif (
            answer_clean in ["c", "option c", "must always have exactly 2", "always 2"]
            or "option c" in answer_clean
            or "always 2" in answer_clean
            or "must have 2" in answer_clean
            or "always have exactly 2" in answer_clean
            or "must always have" in answer_clean
            or "exactly 2" in answer_clean
            or (answer_clean.startswith("c") and len(answer_clean) <= 3)
        ):
            return MisconceptionReportSchema(
                misconception_id=misc_id,
                concept="Binary Tree Node Topology",
                category=MisconceptionCategory.OVERGENERALIZATION,
                is_misconception=True,
                flawed_mental_model="Student assumes 'binary' strictly mandates that every node must possess exactly 2 children at all times.",
                correct_mental_model="Binary denotes an upper bound constraint: each node can have 0, 1, or 2 children (at most 2).",
                evidence_from_response=f"Student answered: '{student_answer}'",
                recommended_counter_analogy="Think of a bicycle rack designed for at most 2 bikes: having 0 or 1 bike is perfectly valid.",
                prerequisite_to_review="Leaf nodes vs internal node definitions.",
            )
        elif (
            answer_clean in ["d", "option d", "arbitrary", "any number", "3 or 4", "unlimited"]
            or "option d" in answer_clean
            or "arbitrary" in answer_clean
            or "any number" in answer_clean
            or "3 or 4" in answer_clean
            or "unlimited" in answer_clean
            or (answer_clean.startswith("d") and len(answer_clean) <= 3)
        ):
            return MisconceptionReportSchema(
                misconception_id=misc_id,
                concept="Binary Tree Node Topology",
                category=MisconceptionCategory.OVERGENERALIZATION,
                is_misconception=True,
                flawed_mental_model="Student confuses general tree branching with binary trees, assuming nodes can have unlimited or arbitrary children.",
                correct_mental_model="Binary denotes a strict upper bound: each node can have at most 2 children (0, 1, or 2).",
                evidence_from_response=f"Student answered: '{student_answer}'",
                recommended_counter_analogy="Think of a fork in the road: you can branch left or right, but you cannot drive in four directions at once.",
                prerequisite_to_review="Definition of binary vs general tree structures.",
            )
        else:
            return MisconceptionReportSchema(
                misconception_id=misc_id,
                concept=concept,
                category=MisconceptionCategory.OTHER,
                is_misconception=False,
                flawed_mental_model="Incomplete grasp of concept terminology rather than an active contradictory mental model.",
                correct_mental_model=f"Standard scientific formulation of {concept}.",
                evidence_from_response=f"Student answered: '{student_answer}'",
                recommended_counter_analogy="Step-by-step everyday workflow analogy.",
                prerequisite_to_review=f"Prerequisite foundations for {concept}.",
            )

    def _decide_adaptation(
        self,
        evaluation: Optional[EvaluationResultSchema],
        misconception: Optional[MisconceptionReportSchema],
        profile: Optional[LearnerProfileSchema],
    ) -> AdaptationDecisionSchema:
        dec_id = f"adapt-{uuid.uuid4().hex[:8]}"

        if not evaluation:
            return AdaptationDecisionSchema(
                decision_id=dec_id,
                action=AdaptationAction.CONTINUE,
                reason="Initial lesson start, proceeding with introductory instruction.",
                strategy="Present planned section material with engaging visual.",
                difficulty_adjustment=DifficultyAdjustment.MAINTAIN,
                target_concept="Introduction",
                next_step_summary="Let's dive into the core concepts.",
            )

        # 1. Misconception Detected: Highest priority intervention
        if evaluation.correctness == CorrectnessLevel.INCORRECT_MISCONCEPTION or (misconception and misconception.is_misconception):
            return AdaptationDecisionSchema(
                decision_id=dec_id,
                action=AdaptationAction.CHANGE_ANALOGY,
                reason=(
                    f"Student holds a specific flawed mental model: {misconception.flawed_mental_model if misconception else 'Inverse relationship confusion'}. "
                    "Continuing without correcting this mental model will compromise downstream learning."
                ),
                strategy=(
                    f"Replace abstract formula with a tangible sensory analogy: "
                    f"{misconception.recommended_counter_analogy if misconception else 'Water flow in constricted pipes'}."
                ),
                difficulty_adjustment=DifficultyAdjustment.MAINTAIN,
                target_concept=misconception.concept if misconception else "Target Concept",
                suggested_analogy=misconception.recommended_counter_analogy if misconception else "Water pipe constriction",
                suggested_scaffold="Ask student what happens to water flow when a valve is partially closed.",
                next_step_summary="Let's look at this from a fresh angle using an intuitive analogy to clear up the confusion.",
            )

        # 2. Incorrect due to Lack of Knowledge
        elif evaluation.correctness == CorrectnessLevel.INCORRECT_LACK_OF_KNOWLEDGE:
            return AdaptationDecisionSchema(
                decision_id=dec_id,
                action=AdaptationAction.SIMPLIFY,
                reason="Student struggled with the fundamental definition without holding a stubborn misconception.",
                strategy="Break the concept down into two smaller sub-steps and provide guided scaffolding.",
                difficulty_adjustment=DifficultyAdjustment.DECREASE,
                target_concept="Foundation Principles",
                suggested_scaffold="First identify the components before analyzing their interaction.",
                next_step_summary="No worries at all! We'll simplify this concept and break it down into easy, digestible pieces.",
            )

        # 3. Partially Correct Answer
        elif evaluation.correctness == CorrectnessLevel.PARTIALLY_CORRECT:
            return AdaptationDecisionSchema(
                decision_id=dec_id,
                action=AdaptationAction.GIVE_ANOTHER_EXAMPLE,
                reason=f"Student grasped the core direction ({evaluation.strengths[0] if evaluation.strengths else 'Good intuition'}), but missed formal details: {evaluation.missing_concepts}.",
                strategy="Reinforce with a concrete numerical or visual walkthrough demonstrating the missing component.",
                difficulty_adjustment=DifficultyAdjustment.MAINTAIN,
                target_concept="Concept Nuance",
                suggested_scaffold="Connect the student's correct direction with the governing formula.",
                next_step_summary="You're on the right track! Let's examine one quick applied example to complete the picture.",
            )

        # 4. Correct Answer: Progression and Challenge
        else:
            return AdaptationDecisionSchema(
                decision_id=dec_id,
                action=AdaptationAction.MOVE_TO_NEXT_CONCEPT,
                reason="Student demonstrated clear mastery of the concept and articulated key rubric requirements.",
                strategy="Advance to next progressive lesson section and slightly increase challenge level.",
                difficulty_adjustment=DifficultyAdjustment.INCREASE if profile and profile.educational_level != LearnerLevel.BEGINNER else DifficultyAdjustment.MAINTAIN,
                target_concept="Next Section",
                next_step_summary="Great work! You've mastered this concept. Let's move forward to the next exciting section!",
            )

    # Embedding provider interface
    @classmethod
    def _compute_deterministic_embedding(cls, text: str, dim: int = 256) -> List[float]:
        """
        Computes a normalized dense vector using token hashing and character 3-grams.
        Produces stable, realistic cosine similarity without external dependencies.
        """
        if not text or not text.strip():
            return [0.0] * dim

        tokens = re.findall(r"\b\w+\b", text.lower())
        vec = [0.0] * dim

        for token in tokens:
            # Hash full token
            h = int(hashlib.sha256(token.encode("utf-8")).hexdigest()[:8], 16) % dim
            vec[h] += 1.0

            # Hash character 3-grams for subword similarity
            if len(token) >= 3:
                for i in range(len(token) - 2):
                    ng = token[i : i + 3]
                    h_ng = int(hashlib.md5(ng.encode("utf-8")).hexdigest()[:8], 16) % dim
                    vec[h_ng] += 0.5

        # L2 Unit Normalization for cosine similarity
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            return [round(x / norm, 6) for x in vec]
        return [0.0] * dim

    async def embed_text(self, text: str) -> List[float]:
        return self._compute_deterministic_embedding(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self._compute_deterministic_embedding(t) for t in texts]

    # Speech provider interface
    async def synthesize_speech(self, text: str, voice_id: Optional[str] = None, language: str = "en") -> bytes:
        """
        Synthesize spoken audio. Returns mock audio payload with duration and word metadata.
        """
        words = text.split()
        duration_est = max(2.0, round(len(words) / 2.6, 2))
        header = f"RIFF_MOCK_WAV:words={len(words)}:dur={duration_est}:lang={language}:voice={voice_id or 'default_teacher'}"
        return header.encode("utf-8")

    async def synthesize_speech_asset(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: str = "en",
        scene_id: Optional[str] = None,
        emotion: Optional[str] = None,
    ) -> Any:
        from ai_engine.providers.speech_provider import MockSpeechProvider
        provider = MockSpeechProvider()
        return await provider.synthesize_speech_asset(
            text=text,
            voice_id=voice_id,
            language=language,
            scene_id=scene_id,
            emotion=emotion,
        )


    # Avatar provider interface
    async def generate_avatar_frames(self, audio_bytes: bytes, avatar_id: Optional[str] = None) -> dict:
        """
        Generate synchronized avatar animation frames and visemes matching speech audio.
        """
        return {
            "avatar_id": avatar_id or "teacher_prof_sophia",
            "model_type": "vector_animated_human",
            "lip_sync_visemes": ["rest", "open_wide", "half_open", "narrow", "rest"],
            "expressions": {
                "default": "explaining",
                "blink_interval_seconds": 3.5,
                "eye_contact_ratio": 0.92,
                "head_nod_points": [1.5, 4.0, 7.5],
            },
            "status": "ready",
        }

    def derive_avatar_state(
        self, scene_dict: dict, playback_time: float = 0.0, is_playing: bool = False
    ) -> dict:
        """Derive structured presentation state for the active frame."""
        from ai_engine.schemas.scene import TeachingScene
        from ai_engine.modules.avatar_controller import AvatarController
        if isinstance(scene_dict, dict):
            scene = TeachingScene.model_validate(scene_dict)
        else:
            scene = scene_dict
        state = AvatarController.get_avatar_state_for_scene(
            scene=scene, playback_time=playback_time, is_playing=is_playing
        )
        return state.model_dump()

    # Video provider interface
    async def composite_lesson_video(
        self, audio_stream: bytes, visual_plan: dict, output_format: str = "mp4"
    ) -> str:
        """
        Composite synchronized teaching video packaging audio, visual plan, and avatar.
        """
        return f"/media/rendered_lessons/{visual_plan.get('plan_id', 'plan-default')}.{output_format}"

    def _generate_final_assessment(
        self, topic: str, profile: Optional[LearnerProfileSchema] = None, session_id: Optional[str] = None
    ) -> FinalAssessmentSchema:
        """Generate 2-3 tailored assessment questions assessing core concepts and practical application."""
        level = profile.educational_level.value if profile else "beginner"
        s_id = session_id or f"sess-{uuid.uuid4().hex[:8]}"
        asmt_id = f"asmt-{uuid.uuid4().hex[:8]}"

        domain = classify_topic(topic=topic)
        if domain == TopicDomain.MACHINE_LEARNING:
            questions = [
                AssessmentQuestion(
                    question_id=f"{asmt_id}-q1",
                    concept="Forward Pass & Weighted Sum",
                    question_type=AssessmentQuestionType.MULTIPLE_CHOICE,
                    prompt="Given an artificial neuron with input X = 2.0, weight W = 0.5, and bias b = 0.5, what is the output before activation (z = W·X + b)?",
                    options=[
                        AssessmentOption(key="A", text="z = 1.0"),
                        AssessmentOption(key="B", text="z = 1.5"),
                        AssessmentOption(key="C", text="z = 2.5"),
                        AssessmentOption(key="D", text="z = 0.5"),
                    ],
                    expected_answer="B",
                    difficulty="beginner",
                    explanation="The weighted linear combination is z = (2.0 * 0.5) + 0.5 = 1.0 + 0.5 = 1.5.",
                ),
                AssessmentQuestion(
                    question_id=f"{asmt_id}-q2",
                    concept="Non-Linear Activation Function",
                    question_type=AssessmentQuestionType.MULTIPLE_CHOICE,
                    prompt="Why must a multi-layer neural network use non-linear activation functions (like ReLU) between layers?",
                    options=[
                        AssessmentOption(key="A", text="To double the storage space of weights"),
                        AssessmentOption(key="B", text="Without non-linearity, multiple layers collapse into a single linear transformation"),
                        AssessmentOption(key="C", text="To guarantee that all weights become negative"),
                        AssessmentOption(key="D", text="To eliminate the need for an input layer"),
                    ],
                    expected_answer="B",
                    difficulty="intermediate",
                    explanation="A linear combination of linear functions is still linear; non-linear activations allow networks to approximate arbitrary non-linear functions.",
                ),
                AssessmentQuestion(
                    question_id=f"{asmt_id}-q3",
                    concept="Role of Bias in Neurons",
                    question_type=AssessmentQuestionType.MULTIPLE_CHOICE,
                    prompt="What is the primary operational role of the 'bias' parameter in a neural network layer?",
                    options=[
                        AssessmentOption(key="A", text="It shifts the activation function curve independently of the input features"),
                        AssessmentOption(key="B", text="It counts how many hidden layers exist in the architecture"),
                        AssessmentOption(key="C", text="It permanently resets the learning rate to zero"),
                        AssessmentOption(key="D", text="It converts floats into strings"),
                    ],
                    expected_answer="A",
                    difficulty="intermediate",
                    explanation="The bias provides an offset that shifts the activation threshold, allowing the neuron to fire even when all input features are zero.",
                ),
            ]
        elif domain == TopicDomain.RECURSION:
            questions = [
                AssessmentQuestion(
                    question_id=f"{asmt_id}-q1",
                    concept="Base Case Invariant",
                    question_type=AssessmentQuestionType.MULTIPLE_CHOICE,
                    prompt="In a recursive algorithm, what happens if the base case is omitted or unreachable?",
                    options=[
                        AssessmentOption(key="A", text="The function immediately returns null"),
                        AssessmentOption(key="B", text="The call stack grows indefinitely until a Stack Overflow error occurs"),
                        AssessmentOption(key="C", text="The compiler automatically replaces the recursion with a for-loop"),
                        AssessmentOption(key="D", text="The algorithm executes in constant O(1) space"),
                    ],
                    expected_answer="B",
                    difficulty="beginner",
                    explanation="Without a terminating base case, each self-invocation adds a new stack frame until available call stack memory is exhausted.",
                ),
                AssessmentQuestion(
                    question_id=f"{asmt_id}-q2",
                    concept="Call Stack Memory Execution Order",
                    question_type=AssessmentQuestionType.MULTIPLE_CHOICE,
                    prompt="Which data structure does the runtime environment use internally to track active recursive function calls and return addresses?",
                    options=[
                        AssessmentOption(key="A", text="FIFO Queue"),
                        AssessmentOption(key="B", text="LIFO Call Stack"),
                        AssessmentOption(key="C", text="Hash Table"),
                        AssessmentOption(key="D", text="Min-Heap"),
                    ],
                    expected_answer="B",
                    difficulty="beginner",
                    explanation="The execution environment allocates stack frames on a LIFO (Last-In, First-Out) call stack, unwinding in reverse invocation order.",
                ),
                AssessmentQuestion(
                    question_id=f"{asmt_id}-q3",
                    concept="Recursive Complexity & State Progression",
                    question_type=AssessmentQuestionType.MULTIPLE_CHOICE,
                    prompt="What is the minimum requirement for the recursive step to ensure eventual termination?",
                    options=[
                        AssessmentOption(key="A", text="The argument passed must strictly progress toward the base case condition"),
                        AssessmentOption(key="B", text="The function must make at least two recursive calls"),
                        AssessmentOption(key="C", text="The function must return an integer"),
                        AssessmentOption(key="D", text="Local variables must be declared as global state"),
                    ],
                    expected_answer="A",
                    difficulty="intermediate",
                    explanation="Every recursive step must reduce or modify the problem state toward the base case (e.g. n - 1), otherwise infinite recursion occurs.",
                ),
            ]
        elif domain == TopicDomain.DATA_STRUCTURES:
            questions = [
                AssessmentQuestion(
                    question_id=f"{asmt_id}-q1",
                    concept="Binary Branching Invariant",
                    question_type=AssessmentQuestionType.MULTIPLE_CHOICE,
                    prompt="What is the maximum number of children any single node can have in a Binary Tree?",
                    options=[
                        AssessmentOption(key="A", text="Exactly 1 child"),
                        AssessmentOption(key="B", text="At most 2 children (0, 1, or 2)"),
                        AssessmentOption(key="C", text="Must always have exactly 2 children"),
                        AssessmentOption(key="D", text="Unlimited children"),
                    ],
                    expected_answer="B",
                    difficulty="beginner",
                    explanation="By mathematical definition, each node in a binary tree has a degree of at most 2.",
                ),
                AssessmentQuestion(
                    question_id=f"{asmt_id}-q2",
                    concept="Leaf Node Topology",
                    question_type=AssessmentQuestionType.MULTIPLE_CHOICE,
                    prompt="A node at the bottom of a tree that has 0 child nodes is known as a:",
                    options=[
                        AssessmentOption(key="A", text="Root Node"),
                        AssessmentOption(key="B", text="Internal Node"),
                        AssessmentOption(key="C", text="Leaf Node"),
                        AssessmentOption(key="D", text="Null Edge"),
                    ],
                    expected_answer="C",
                    difficulty="beginner",
                    explanation="Leaf nodes (external nodes) are terminating endpoints with zero children.",
                ),
                AssessmentQuestion(
                    question_id=f"{asmt_id}-q3",
                    concept="Binary Search Tree Invariant & Efficiency",
                    question_type=AssessmentQuestionType.MULTIPLE_CHOICE,
                    prompt="In a Binary Search Tree (BST), what property enables O(log n) search performance?",
                    options=[
                        AssessmentOption(key="A", text="All nodes are stored in random order"),
                        AssessmentOption(key="B", text="Left subtree values are smaller, right subtree values are larger"),
                        AssessmentOption(key="C", text="Every node has identical keys"),
                        AssessmentOption(key="D", text="Search examines every leaf sequentially"),
                    ],
                    expected_answer="B",
                    difficulty="intermediate",
                    explanation="The BST ordering property (left < root < right) eliminates half the search space at each comparison step.",
                ),
            ]
        elif domain == TopicDomain.PHYSICS_ELECTRONICS or "Ohm" in topic or "Circuit" in topic:
            questions = [
                AssessmentQuestion(
                    question_id=f"{asmt_id}-q1",
                    concept="Ohm's Law Proportionality",
                    question_type=AssessmentQuestionType.MULTIPLE_CHOICE,
                    prompt="According to Ohm's Law (V = I × R), if resistance increases while voltage is constant, what happens to current?",
                    options=[
                        AssessmentOption(key="A", text="Current increases"),
                        AssessmentOption(key="B", text="Current decreases"),
                        AssessmentOption(key="C", text="Current stays the same"),
                        AssessmentOption(key="D", text="Current oscillates"),
                    ],
                    expected_answer="B",
                    difficulty="beginner",
                    explanation="Current is inversely proportional to resistance: I = V / R.",
                ),
                AssessmentQuestion(
                    question_id=f"{asmt_id}-q2",
                    concept="Circuit Calculation",
                    question_type=AssessmentQuestionType.MULTIPLE_CHOICE,
                    prompt="If a 12V power supply is connected to a 4-ohm resistor, what is the current flowing?",
                    options=[
                        AssessmentOption(key="A", text="48 Amperes"),
                        AssessmentOption(key="B", text="3 Amperes"),
                        AssessmentOption(key="C", text="0.33 Amperes"),
                        AssessmentOption(key="D", text="8 Amperes"),
                    ],
                    expected_answer="B",
                    difficulty="intermediate",
                    explanation="I = V / R = 12V / 4Ω = 3 Amperes.",
                ),
            ]
        else:
            questions = [
                AssessmentQuestion(
                    question_id=f"{asmt_id}-q1",
                    concept=f"{topic} Fundamentals",
                    question_type=AssessmentQuestionType.MULTIPLE_CHOICE,
                    prompt=f"What is the foundational principle underlying {topic}?",
                    options=[
                        AssessmentOption(
                            key="A",
                            text="Structured, verifiable workflow and standard operational rules",
                        ),
                        AssessmentOption(
                            key="B", text="Unconstrained random execution without validation"
                        ),
                        AssessmentOption(
                            key="C", text="Eliminating all audit records and state tracking"
                        ),
                        AssessmentOption(
                            key="D", text="Bypassing system verification entirely"
                        ),
                    ],
                    expected_answer="A",
                    difficulty="beginner",
                    explanation=f"{topic} relies on structured, predictable rules to achieve consistency and reliability.",
                ),
                AssessmentQuestion(
                    question_id=f"{asmt_id}-q2",
                    concept=f"{topic} Practical Application",
                    question_type=AssessmentQuestionType.MULTIPLE_CHOICE,
                    prompt=f"When applying {topic} in practice, what is the primary operational benefit?",
                    options=[
                        AssessmentOption(
                            key="A",
                            text="Higher error rate and unverified state modifications",
                        ),
                        AssessmentOption(
                            key="B",
                            text="Efficient, reliable execution with clear status tracking and compliance",
                        ),
                        AssessmentOption(
                            key="C", text="Unbounded memory consumption"
                        ),
                        AssessmentOption(
                            key="D", text="Removal of all validation safeguards"
                        ),
                    ],
                    expected_answer="B",
                    difficulty="intermediate",
                    explanation=f"Applying {topic} ensures structured efficiency, compliance, and predictable outcomes.",
                ),
            ]

        return FinalAssessmentSchema(
            assessment_id=asmt_id,
            session_id=s_id,
            topic=topic,
            learner_level=level,
            estimated_time_minutes=5,
            questions=questions,
        )
