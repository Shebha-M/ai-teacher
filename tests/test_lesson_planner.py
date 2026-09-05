"""Tests for the Lesson Planner module verifying structural time and level adaptation."""
import pytest
from ai_engine.modules.lesson_planner import LessonPlanner
from ai_engine.modules.learner_profiler import LearnerProfiler
from ai_engine.schemas.learner import LearnerLevel, TeachingStyle


@pytest.mark.asyncio
async def test_lesson_planner_adapts_to_short_time():
    """5-10 minutes must produce a streamlined 1-section sprint."""
    profiler = LearnerProfiler()
    profile = profiler.create_profile(
        name="Alex",
        educational_level=LearnerLevel.BEGINNER,
        available_learning_time=5,
    )
    planner = LessonPlanner()
    plan = await planner.plan_lesson(topic="Binary Trees", profile=profile)

    assert plan.topic == "Binary Trees"
    assert len(plan.sections) == 1
    assert plan.estimated_duration == 5
    assert plan.explanation_depth == "essential_concepts"
    assert "sec-1" in plan.sections[0].section_id
    assert plan.sections[0].visual_recommendation is not None


@pytest.mark.asyncio
async def test_lesson_planner_adapts_to_standard_time():
    """15-30 minutes must produce a balanced 3-section curriculum."""
    profiler = LearnerProfiler()
    profile = profiler.create_profile(
        name="Alex",
        educational_level=LearnerLevel.INTERMEDIATE,
        available_learning_time=20,
    )
    planner = LessonPlanner()
    plan = await planner.plan_lesson(topic="Binary Trees", profile=profile)

    assert len(plan.sections) == 3
    assert plan.estimated_duration == 20
    assert plan.explanation_depth == "standard_curriculum"
    assert len(plan.section_ordering) == 3
    assert "sec-1" in plan.section_ordering[0]
    # Verify each section has an attached visual recommendation and checkpoint
    for sec in plan.sections:
        assert sec.visual_recommendation.visual_type is not None
        assert sec.question_checkpoint is not None


@pytest.mark.asyncio
async def test_lesson_planner_adapts_to_masterclass_time():
    """45-60+ minutes must produce a 5-section comprehensive deep dive."""
    profiler = LearnerProfiler()
    profile = profiler.create_profile(
        name="Alex",
        educational_level=LearnerLevel.ADVANCED,
        available_learning_time=60,
    )
    planner = LessonPlanner()
    plan = await planner.plan_lesson(topic="Binary Trees", profile=profile)

    assert len(plan.sections) == 5
    assert plan.estimated_duration == 60
    assert plan.explanation_depth == "deep_dive_masterclass"
    assert len(plan.section_ordering) == 5


@pytest.mark.asyncio
async def test_lesson_planner_recursion_topic_alignment():
    """
    Regression test: Topic = 'Recursion' (Beginner, 60 min, Deep/First Principles)
    must produce genuine recursion & call stack curriculum, NOT binary tree / traversal / heap content.
    """
    profiler = LearnerProfiler()
    profile = profiler.create_profile(
        name="Alex",
        educational_level=LearnerLevel.BEGINNER,
        available_learning_time=60,
        preferred_teaching_style=TeachingStyle.FIRST_PRINCIPLES,
    )
    planner = LessonPlanner()
    plan = await planner.plan_lesson(topic="Recursion", profile=profile)

    assert plan.topic == "Recursion"
    assert len(plan.sections) == 5
    assert plan.estimated_duration == 60
    assert plan.explanation_depth == "deep_dive_masterclass"

    # Verify lesson title and objectives focus on recursion
    assert "Recursion" in plan.lesson_title

    # Aggregated text across all generated sections
    all_text = " ".join([
        f"{s.title} {s.concept} {s.objective} {s.explanation_outline} {s.example_context}"
        for s in plan.sections
    ]).lower()

    # Must contain recursion and call-stack core concepts
    assert "recursion" in all_text or "recursive" in all_text
    assert "base case" in all_text
    assert "call stack" in all_text
    assert "stack overflow" in all_text

    # Must NOT be dominated by binary tree concepts
    forbidden_tree_terms = [
        "binary tree",
        "binary heap",
        "dfs vs bfs",
        "in-order",
        "pre-order",
        "post-order",
        "avl",
        "b-tree",
        "skewed tree",
    ]
    for term in forbidden_tree_terms:
        assert term not in all_text, f"Forbidden tree term '{term}' found in Recursion curriculum!"


@pytest.mark.asyncio
async def test_lesson_planner_binary_trees_curriculum_intact():
    """
    Regression test: Topic = 'Binary Trees' must still produce the existing Binary Tree curriculum.
    """
    profiler = LearnerProfiler()
    profile = profiler.create_profile(
        name="Alex",
        educational_level=LearnerLevel.ADVANCED,
        available_learning_time=60,
    )
    planner = LessonPlanner()
    plan = await planner.plan_lesson(topic="Binary Trees", profile=profile)

    assert plan.topic == "Binary Trees"
    assert len(plan.sections) == 5
    assert "Binary Trees" in plan.lesson_title

    all_text = " ".join([
        f"{s.title} {s.concept} {s.objective} {s.explanation_outline} {s.example_context}"
        for s in plan.sections
    ]).lower()

    # Must contain binary tree concepts
    assert "binary tree" in all_text or "tree" in all_text
    assert "traversal" in all_text or "node" in all_text


@pytest.mark.asyncio
async def test_lesson_planner_neural_networks_topic_alignment():
    """
    Topic = 'Neural Networks' (Beginner, 20 min) must produce genuine neural network
    curriculum (inputs, weights, bias, activation, forward pass) with NO tree/traversal content.
    """
    profiler = LearnerProfiler()
    profile = profiler.create_profile(
        name="Sam",
        educational_level=LearnerLevel.BEGINNER,
        available_learning_time=20,
    )
    planner = LessonPlanner()
    plan = await planner.plan_lesson(topic="Neural Networks", profile=profile)

    assert plan.topic == "Neural Networks"
    assert len(plan.sections) == 3
    assert plan.estimated_duration == 20
    assert "Neural Network" in plan.lesson_title

    all_text = " ".join([
        f"{s.title} {s.concept} {s.objective} {s.explanation_outline} {s.example_context}"
        for s in plan.sections
    ]).lower()

    # Must contain neural network forward pass concepts
    assert "neuron" in all_text or "neural" in all_text
    assert "weight" in all_text or "bias" in all_text
    assert "activation" in all_text or "forward pass" in all_text

    # Forbidden tree / data structure terms
    forbidden_terms = [
        "binary tree",
        "binary heap",
        "traversal",
        "in-order",
        "pre-order",
        "post-order",
        "avl",
        "b-tree",
        "skewed tree",
        "left child",
        "right child",
    ]
    for term in forbidden_terms:
        assert term not in all_text, f"Forbidden term '{term}' found in Neural Networks curriculum!"


@pytest.mark.asyncio
async def test_neural_networks_visual_and_teaching_integration():
    """
    Verifies VisualPlanner and MockProvider generate machine learning visual architecture
    and pedagogical explanations without falling back to binary trees.
    """
    from ai_engine.modules.visual_planner import VisualPlanner
    from ai_engine.modules.teaching_agent import TeachingAgent
    from ai_engine.modules.question_generator import QuestionGenerator
    from ai_engine.modules.answer_evaluator import AnswerEvaluator
    from ai_engine.providers.mock_provider import DeterministicTeachingProvider
    from ai_engine.schemas.lesson import VisualType
    from ai_engine.schemas.question import StudentResponseSchema
    from ai_engine.schemas.assessment import FinalAssessmentSchema

    vp = VisualPlanner()
    domain = vp.infer_subject_domain("Neural Networks", "Neuron Forward Pass")
    assert domain == "machine_learning"

    provider = DeterministicTeachingProvider()

    # Test teaching response
    profiler = LearnerProfiler()
    profile = profiler.create_profile(name="Sam", educational_level=LearnerLevel.BEGINNER, available_learning_time=20)
    planner = LessonPlanner(provider=provider)
    plan = await planner.plan_lesson(topic="Neural Networks", profile=profile)
    first_sec = plan.sections[0]

    teaching_agent = TeachingAgent(provider=provider)
    teaching = await teaching_agent.explain_section(section=first_sec, profile=profile)
    assert "Neural Network" in teaching.explanation or "neuron" in teaching.explanation.lower()
    assert "Decision Committee" in teaching.analogy
    assert "z = " in teaching.example or "ReLU" in teaching.example
    assert teaching.visual_instruction.visual_type == VisualType.ARCHITECTURE_DIAGRAM

    # Test checkpoint question & answer evaluation
    q_gen = QuestionGenerator(provider=provider)
    question = await q_gen.generate_checkpoint_question(section=first_sec, profile=profile)
    assert "weight" in question.prompt.lower()

    # Correct answer
    evaluator = AnswerEvaluator(provider=provider)
    resp_corr = StudentResponseSchema(response_id="r-corr", question_id=question.question_id, student_answer="Option B: scales the input signal")
    eval_corr = await evaluator.evaluate_response(question=question, student_response=resp_corr, profile=profile)
    assert eval_corr.score == 1.0
    assert not eval_corr.misconception_suspected

    # Misconception answer (confusing weights with layer count)
    resp_misc = StudentResponseSchema(response_id="r-misc", question_id=question.question_id, student_answer="Option A: sets the number of layers")
    eval_misc = await evaluator.evaluate_response(question=question, student_response=resp_misc, profile=profile)
    assert eval_misc.misconception_suspected
    assert eval_misc.detected_misconception_id == "misc-ml-weight-vs-layers"

    # Test final assessment questions
    assessment = await provider.generate_structured(
        prompt="Generate assessment",
        response_schema=FinalAssessmentSchema,
        topic="Neural Networks",
        profile=profile,
    )
    assert len(assessment.questions) == 3
    asmt_text = " ".join([q.prompt for q in assessment.questions]).lower()
    assert "neuron" in asmt_text or "activation" in asmt_text or "bias" in asmt_text
    assert "tree" not in asmt_text


@pytest.mark.asyncio
async def test_lesson_planner_general_topic_safe_neutral_curriculum():
    """
    Verifies that unknown or non-CS topics receive a domain-neutral curriculum
    with zero binary tree / traversal artifacts.
    """
    profiler = LearnerProfiler()
    profile = profiler.create_profile(name="Jordan", educational_level=LearnerLevel.BEGINNER, available_learning_time=20)
    planner = LessonPlanner()
    plan = await planner.plan_lesson(topic="Agile Project Management", profile=profile)

    assert plan.topic == "Agile Project Management"
    assert len(plan.sections) == 3

    all_text = " ".join([
        f"{s.title} {s.concept} {s.objective} {s.explanation_outline} {s.example_context}"
        for s in plan.sections
    ]).lower()

    forbidden_terms = [
        "binary tree",
        "binary heap",
        "traversal",
        "in-order",
        "pre-order",
        "post-order",
        "left child",
        "right child",
        "avl",
    ]
    for term in forbidden_terms:
        assert term not in all_text, f"Forbidden term '{term}' leaked into general curriculum!"
