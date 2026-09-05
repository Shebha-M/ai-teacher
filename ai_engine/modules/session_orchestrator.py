"""Teaching Session Orchestrator: coordinates the complete human-like teaching lifecycle."""
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from ai_engine.providers.base import LLMProvider
from ai_engine.providers import get_default_llm_provider
from ai_engine.modules.learner_profiler import LearnerProfiler
from ai_engine.modules.lesson_planner import LessonPlanner
from ai_engine.modules.teaching_agent import TeachingAgent
from ai_engine.modules.question_generator import QuestionGenerator
from ai_engine.modules.answer_evaluator import AnswerEvaluator
from ai_engine.modules.misconception_detector import MisconceptionDetector
from ai_engine.modules.adaptation_engine import AdaptationEngine

from ai_engine.schemas.learner import LearnerProfileSchema
from ai_engine.schemas.lesson import LessonPlanSchema, LessonSectionSchema
from ai_engine.schemas.teaching import TeachingResponseSchema, TeachingAction
from ai_engine.schemas.question import QuestionSchema, StudentResponseSchema
from ai_engine.schemas.evaluation import EvaluationResultSchema, CorrectnessLevel
from ai_engine.schemas.misconception import MisconceptionReportSchema
from ai_engine.schemas.adaptation import AdaptationDecisionSchema, AdaptationAction
from ai_engine.schemas.session import (
    TeachingSessionStateSchema,
    SessionStatus,
    ConceptMasterySchema,
    TeachingInteractionRecord,
)
from ai_engine.schemas.grounding import KnowledgeMode, GroundedContextSchema
from ai_engine.schemas.scene import TeachingScene, TeachingScenePlan
from ai_engine.modules.visual_planner import VisualPlanner
from ai_engine.schemas.assessment import (
    FinalAssessmentSchema,
    AssessmentAnswerItem,
    QuestionGradingResult,
    LearningReportSchema,
    AssessmentQuestion,
)
from ai_engine.modules.topic_classifier import classify_topic, TopicDomain


class TeachingSessionOrchestrator:
    """
    Stateful coordinator for the educational loop:
    Understand → Plan → Explain → Demonstrate → Question → Evaluate → Adapt → Continue.
    """

    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or get_default_llm_provider()
        self.profiler = LearnerProfiler()
        self.planner = LessonPlanner(self.provider)
        self.teacher = TeachingAgent(self.provider)
        self.questioner = QuestionGenerator(self.provider)
        self.evaluator = AnswerEvaluator(self.provider)
        self.detector = MisconceptionDetector(self.provider)
        self.adapter = AdaptationEngine(self.provider)
        self.visual_planner = VisualPlanner()
        from ai_engine.modules.language_controller import LanguageController
        from ai_engine.providers.speech_provider import get_speech_provider
        self.language_controller = LanguageController()
        self.speech_provider = get_speech_provider()
        self.scene_plans_cache: Dict[str, TeachingScenePlan] = {}
        self.assessments_cache: Dict[str, FinalAssessmentSchema] = {}
        self.reports_cache: Dict[str, LearningReportSchema] = {}

    def initialize_session(
        self,
        topic: str,
        learner_profile: LearnerProfileSchema,
        session_id: Optional[str] = None,
        knowledge_mode: KnowledgeMode = KnowledgeMode.TOPIC,
        document_id: Optional[str] = None,
    ) -> TeachingSessionStateSchema:
        """Step 1: Initialize session state with learner profile and target topic."""
        s_id = session_id or f"sess-{uuid.uuid4().hex[:8]}"
        learner_profile.current_topic = topic
        learner_profile.current_session_id = s_id

        target_lang = learner_profile.preferred_language or "en"
        decision = self.language_controller.resolve_language(target_lang)

        return TeachingSessionStateSchema(
            session_id=s_id,
            learner_profile=learner_profile,
            status=SessionStatus.INITIALIZED,
            current_topic=topic,
            knowledge_mode=knowledge_mode,
            document_id=document_id,
            current_section_index=0,
            teaching_language=decision.resolved_language.value,
            language_mode=learner_profile.language_mode or "bilingual",
            active_voice_id=learner_profile.preferred_voice_id or decision.voice_id,
            concepts_mastered=[],
            concepts_needing_improvement=[],
            concept_mastery_map={},
            history=[],
        )

    async def plan_session(
        self, session: TeachingSessionStateSchema, knowledge_context: Optional[str] = None
    ) -> TeachingSessionStateSchema:
        """Step 2: Generate structured, time-adapted lesson plan."""
        session.status = SessionStatus.PLANNING

        # Perform RAG retrieval if document grounding is requested
        if session.knowledge_mode in (KnowledgeMode.DOCUMENT, KnowledgeMode.MIXED) and session.document_id:
            try:
                from ai_engine.rag.document_service import get_document_service
                doc_service = get_document_service()
                session.grounded_context = await doc_service.retrieve_grounded_context(
                    query=session.current_topic,
                    document_id=session.document_id,
                    knowledge_mode=session.knowledge_mode,
                )
            except Exception as e:
                import logging
                logging.getLogger("ai_teacher.session").warning(f"Could not retrieve grounding context: {e}")

        plan = await self.planner.plan_lesson(
            topic=session.current_topic,
            profile=session.learner_profile,
            knowledge_context=knowledge_context,
            grounded_context=session.grounded_context,
        )
        session.lesson_plan = plan
        session.current_section_index = 0
        if plan.sections:
            session.current_section_id = plan.sections[0].section_id
            session.current_concept = plan.sections[0].concept
            # Initialize mastery map
            for sec in plan.sections:
                session.concept_mastery_map[sec.concept] = ConceptMasterySchema(
                    concept=sec.concept,
                    mastery_score=0.0,
                    status="introduced",
                    attempts=0,
                )
        session.status = SessionStatus.TEACHING
        return session

    async def teach_current_section(
        self,
        session: TeachingSessionStateSchema,
        custom_action: Optional[TeachingAction] = None,
        custom_strategy: Optional[str] = None,
    ) -> TeachingResponseSchema:
        """Step 3: Deliver educational explanation for the current section."""
        if not session.lesson_plan or not session.lesson_plan.sections:
            raise ValueError("Cannot teach without an active lesson plan.")

        current_sec = session.lesson_plan.sections[session.current_section_index]
        action = custom_action or TeachingAction.EXPLAIN

        teaching_response = await self.teacher.explain_section(
            section=current_sec,
            profile=session.learner_profile,
            teaching_action=action,
            custom_adaptation_strategy=custom_strategy,
            grounded_context=session.grounded_context,
        )

        session.latest_teaching = teaching_response
        session.current_concept = current_sec.concept
        session.status = SessionStatus.AWAITING_RESPONSE
        return teaching_response

    async def get_checkpoint_question(
        self, session: TeachingSessionStateSchema
    ) -> QuestionSchema:
        """Step 4: Generate or retrieve the diagnostic checkpoint question."""
        if not session.lesson_plan or not session.lesson_plan.sections:
            raise ValueError("Cannot generate question without an active lesson plan.")

        current_sec = session.lesson_plan.sections[session.current_section_index]
        question = await self.questioner.generate_checkpoint_question(
            section=current_sec,
            profile=session.learner_profile,
            grounded_context=session.grounded_context,
        )

        if session.teaching_language and session.teaching_language != "en":
            question = self.language_controller.localize_question(
                question, target_lang=session.teaching_language
            )

        session.latest_question = question
        return question

    async def process_student_response(
        self,
        session: TeachingSessionStateSchema,
        student_answer: str,
        question_id: Optional[str] = None,
    ) -> Dict[str, any]:
        """
        Step 5, 6, 7 & 8:
        Evaluate answer -> Detect misconception -> Decide adaptation -> Update mastery & profile.
        """
        if not session.latest_question:
            raise ValueError("No active question to evaluate.")

        question = session.latest_question

        # Multilingual normalization for semantic evaluation
        norm_answer = student_answer
        if session.teaching_language and session.teaching_language != "en":
            norm_answer = self.language_controller.normalize_student_answer(
                student_answer, student_lang=session.teaching_language
            )

        response_schema = StudentResponseSchema(
            response_id=f"resp-{uuid.uuid4().hex[:8]}",
            question_id=question.question_id,
            student_answer=norm_answer,
        )

        # Step 6: Multi-dimensional evaluation
        evaluation = await self.evaluator.evaluate_response(
            question=question,
            student_response=response_schema,
            profile=session.learner_profile,
        )
        session.latest_evaluation = evaluation

        # Step 7: Cognitive misconception detection
        misconception_report = await self.detector.detect_misconception(
            question=question,
            student_response=response_schema,
        )

        # Step 8: Pedagogical adaptation decision
        adaptation = await self.adapter.decide_adaptation(
            profile=session.learner_profile,
            question=question,
            evaluation=evaluation,
            misconception=misconception_report,
        )
        session.latest_adaptation = adaptation

        # Update Concept Mastery
        concept = question.concept
        now_iso = datetime.now(timezone.utc).isoformat()
        if concept in session.concept_mastery_map:
            mastery = session.concept_mastery_map[concept]
            mastery.attempts += 1
            mastery.mastery_score = max(mastery.mastery_score, evaluation.score)
            mastery.last_evaluated_at = now_iso
            if evaluation.score >= 0.85:
                mastery.status = "mastered"
                if concept not in session.concepts_mastered:
                    session.concepts_mastered.append(concept)
                if concept in session.concepts_needing_improvement:
                    session.concepts_needing_improvement.remove(concept)
            else:
                mastery.status = "struggling" if evaluation.score < 0.5 else "practicing"
                if concept not in session.concepts_needing_improvement:
                    session.concepts_needing_improvement.append(concept)
        else:
            is_mastered = evaluation.score >= 0.85
            session.concept_mastery_map[concept] = ConceptMasterySchema(
                concept=concept,
                mastery_score=evaluation.score,
                status="mastered" if is_mastered else "struggling",
                attempts=1,
                last_evaluated_at=now_iso,
            )
            if is_mastered:
                if concept not in session.concepts_mastered:
                    session.concepts_mastered.append(concept)
            else:
                if concept not in session.concepts_needing_improvement:
                    session.concepts_needing_improvement.append(concept)

        # Update Learner Profile Strengths / Weaknesses / Misconceptions
        self.profiler.record_concept_outcome(
            profile=session.learner_profile,
            concept=concept,
            is_mastered=(evaluation.score >= 0.85),
            misconception=misconception_report.flawed_mental_model if misconception_report.is_misconception else None,
        )

        # Append to interaction audit log
        interaction = TeachingInteractionRecord(
            step_number=len(session.history) + 1,
            section_id=question.section_id,
            concept=concept,
            teaching_response=session.latest_teaching,
            question=question,
            student_response=response_schema,
            evaluation=evaluation,
            misconception_report=misconception_report,
            adaptation_decision=adaptation,
        )
        session.history.append(interaction)
        session.status = SessionStatus.ADAPTING

        return {
            "evaluation": evaluation,
            "misconception": misconception_report,
            "adaptation": adaptation,
            "session_state": session,
        }

    async def advance_or_adapt(
        self, session: TeachingSessionStateSchema
    ) -> Dict[str, any]:
        """
        Step 9: Continue or adapt based on latest adaptation decision.
        """
        if not session.latest_adaptation:
            raise ValueError("Cannot advance without an active adaptation decision.")

        action = session.latest_adaptation.action

        if action in [AdaptationAction.CONTINUE, AdaptationAction.MOVE_TO_NEXT_CONCEPT]:
            # Advance to next section if available
            if session.lesson_plan and session.current_section_index + 1 < len(session.lesson_plan.sections):
                session.current_section_index += 1
                next_sec = session.lesson_plan.sections[session.current_section_index]
                session.current_section_id = next_sec.section_id
                session.current_concept = next_sec.concept
                session.status = SessionStatus.TEACHING
                # Generate new teaching for next section
                teaching = await self.teach_current_section(session)
                return {"action_taken": "advanced_to_next_section", "teaching": teaching}
            else:
                session.status = SessionStatus.COMPLETED
                return {"action_taken": "lesson_completed", "teaching": None}

        elif action in [AdaptationAction.CHANGE_ANALOGY, AdaptationAction.RE_EXPLAIN]:
            # Re-explain current concept using the new strategy
            session.status = SessionStatus.TEACHING
            teaching = await self.teach_current_section(
                session,
                custom_action=TeachingAction.RE_EXPLAIN,
                custom_strategy=session.latest_adaptation.strategy,
            )
            return {"action_taken": "re_explained_with_analogy", "teaching": teaching}

        elif action == AdaptationAction.SIMPLIFY:
            session.status = SessionStatus.TEACHING
            teaching = await self.teach_current_section(
                session,
                custom_action=TeachingAction.SIMPLIFY,
                custom_strategy=session.latest_adaptation.strategy,
            )
            return {"action_taken": "simplified_concept", "teaching": teaching}

        else:
            # Default fallback: reinforce with another example
            session.status = SessionStatus.TEACHING
            teaching = await self.teach_current_section(
                session,
                custom_action=TeachingAction.DEMONSTRATE,
                custom_strategy=session.latest_adaptation.strategy,
            )
            return {"action_taken": "demonstrated_new_example", "teaching": teaching}

    async def generate_scene_plan(
        self, session: TeachingSessionStateSchema, force_regenerate: bool = False
    ) -> TeachingScenePlan:
        """
        Produce or retrieve the structured TeachingScenePlan for the active lesson section.
        """
        sec_id = session.current_section_id or "sec-1"
        cache_key = f"{session.session_id}_{sec_id}"

        if not force_regenerate and cache_key in self.scene_plans_cache:
            return self.scene_plans_cache[cache_key]

        # Ensure active teaching explanation exists
        if not session.latest_teaching or session.latest_teaching.section_id != sec_id:
            await self.teach_current_section(session)

        # Get active section schema
        section = None
        if session.lesson_plan and session.lesson_plan.sections:
            for s in session.lesson_plan.sections:
                if s.section_id == sec_id:
                    section = s
                    break
            if not section:
                section = session.lesson_plan.sections[session.current_section_index]

        if not section:
            # Fallback section
            section = LessonSectionSchema(
                section_id=sec_id,
                section_number=session.current_section_index + 1,
                concept=session.current_concept or session.current_topic,
                title=f"{session.current_topic} Fundamentals",
                objective=f"Understand core principles of {session.current_topic}",
                difficulty=session.learner_profile.educational_level.value,
                estimated_time_minutes=5,
                explanation_outline="Core concept introduction and walkthrough.",
                example_context="Interactive examples and visual models.",
                visual_recommendation=session.latest_teaching.visual_instruction,
                expected_understanding="Student demonstrates foundational grasp.",
            )

        plan = self.visual_planner.create_scene_plan(
            section=section,
            teaching=session.latest_teaching,
            profile=session.learner_profile,
            grounded_context=session.grounded_context,
        )

        # Localize scene narration and onscreen text if language != "en"
        if session.teaching_language and session.teaching_language != "en":
            for scn in plan.scenes:
                loc = self.language_controller.localize_scene_narration(
                    scene=scn,
                    target_lang=session.teaching_language,
                    mode=session.language_mode,
                    learner_name=session.learner_profile.name or "Learner",
                )
                scn.narration = loc["narration"]
                scn.onscreen_text = loc["onscreen_text"]
                scn.language = loc["language"]

        self.scene_plans_cache[cache_key] = plan
        return plan

    async def create_adaptive_remediation_scene(
        self, session: TeachingSessionStateSchema
    ) -> TeachingScene:
        """
        Synthesize and insert an adaptive remediation scene when student encounters a misconception.
        """
        sec_id = session.current_section_id or "sec-1"
        concept = session.current_concept or session.current_topic

        misconception = None
        if session.history and session.history[-1].misconception_report:
            misconception = session.history[-1].misconception_report

        scene = self.visual_planner.create_remediation_scene(
            concept=concept,
            section_id=sec_id,
            misconception=misconception,
            adaptation=session.latest_adaptation,
        )

        # Localize remediation scene if language != "en"
        if session.teaching_language and session.teaching_language != "en":
            loc = self.language_controller.localize_scene_narration(
                scene=scene,
                target_lang=session.teaching_language,
                mode=session.language_mode,
                learner_name=session.learner_profile.name or "Learner",
            )
            scene.narration = loc["narration"]
            scene.onscreen_text = loc["onscreen_text"]
            scene.language = loc["language"]

        # Insert into active scene plan if present
        cache_key = f"{session.session_id}_{sec_id}"
        if cache_key in self.scene_plans_cache:
            plan = self.scene_plans_cache[cache_key]
            # Replace or insert before checkpoint scene
            plan.scenes.insert(len(plan.scenes) - 1, scene)
            plan.is_adaptive_branch = True

        return scene

    async def switch_session_language(
        self,
        session: TeachingSessionStateSchema,
        new_language: str,
        mode: Optional[str] = None,
        voice_id: Optional[str] = None,
    ) -> TeachingSessionStateSchema:
        """
        Step 10: Switch the active presentation language for an ongoing teaching session.
        CRITICAL: Preserves current section index, concept mastery, learning history,
        RAG grounding context, and lesson plan.
        """
        fallback = session.learner_profile.fallback_language or "en"
        decision = self.language_controller.resolve_language(
            new_language, fallback_code=fallback, mode=mode or session.language_mode
        )

        session.teaching_language = decision.resolved_language.value
        session.language_mode = decision.mode.value
        session.active_voice_id = voice_id or decision.voice_id
        session.learner_profile.preferred_language = decision.resolved_language.value
        session.learner_profile.language_mode = decision.mode.value
        if voice_id:
            session.learner_profile.preferred_voice_id = voice_id

        # Re-localize cached scene plan for current section if it exists
        sec_id = session.current_section_id or "sec-1"
        cache_key = f"{session.session_id}_{sec_id}"
        if cache_key in self.scene_plans_cache:
            plan = self.scene_plans_cache[cache_key]
            for scn in plan.scenes:
                loc = self.language_controller.localize_scene_narration(
                    scene=scn,
                    target_lang=session.teaching_language,
                    mode=session.language_mode,
                    learner_name=session.learner_profile.name or "Learner",
                )
                scn.narration = loc["narration"]
                scn.onscreen_text = loc["onscreen_text"]
                scn.language = loc["language"]

        # If latest question exists, localize it as well
        if session.latest_question:
            session.latest_question = self.language_controller.localize_question(
                session.latest_question, target_lang=session.teaching_language
            )

        return session

    async def generate_final_assessment(
        self, session: TeachingSessionStateSchema
    ) -> FinalAssessmentSchema:
        """Generate a short final assessment tailored to concepts taught in the lesson."""
        if session.session_id in self.assessments_cache:
            return self.assessments_cache[session.session_id]

        assessment = await self.provider.generate_structured(
            prompt=f"Generate final assessment for topic '{session.current_topic}'.",
            response_schema=FinalAssessmentSchema,
            topic=session.current_topic,
            profile=session.learner_profile,
            session_id=session.session_id,
        )

        self.assessments_cache[session.session_id] = assessment
        return assessment

    async def evaluate_final_assessment(
        self,
        session: TeachingSessionStateSchema,
        submitted_answers: list[AssessmentAnswerItem],
    ) -> LearningReportSchema:
        """
        Grade the student's final assessment submissions and produce a comprehensive,
        traceable LearningReportSchema with personalized revision and next-topic recommendations.
        """
        assessment = await self.generate_final_assessment(session)
        q_map: Dict[str, AssessmentQuestion] = {q.question_id: q for q in assessment.questions}

        results: list[QuestionGradingResult] = []
        correct_count = 0

        for item in submitted_answers:
            q = q_map.get(item.question_id)
            if not q:
                continue
            student_ans = item.student_answer.strip().upper()
            expected_ans = q.expected_answer.strip().upper()
            is_corr = (student_ans == expected_ans) or (student_ans in expected_ans) or (expected_ans in student_ans)
            score = 1.0 if is_corr else 0.0
            if is_corr:
                correct_count += 1

            feedback = q.explanation if is_corr else f"Incorrect. Correct answer is {q.expected_answer}. {q.explanation}"
            results.append(
                QuestionGradingResult(
                    question_id=q.question_id,
                    concept=q.concept,
                    is_correct=is_corr,
                    score=score,
                    student_answer=item.student_answer,
                    expected_answer=q.expected_answer,
                    feedback=feedback,
                )
            )

        # Calculate final composite score
        total_q = max(1, len(assessment.questions))
        asmt_pct = int((correct_count / total_q) * 100)

        # Checkpoint average from history
        checkpoint_scores = [h.evaluation.score for h in session.history if h.evaluation]
        if checkpoint_scores:
            chk_avg_pct = int((sum(checkpoint_scores) / len(checkpoint_scores)) * 100)
            overall_score = int(0.4 * chk_avg_pct + 0.6 * asmt_pct)
        else:
            overall_score = asmt_pct

        # Concepts understood vs needing improvement
        understood = list(session.concepts_mastered)
        needing_work = list(session.concepts_needing_improvement)

        for r in results:
            if r.is_correct and r.concept not in understood:
                understood.append(r.concept)
            elif not r.is_correct and r.concept not in needing_work:
                needing_work.append(r.concept)

        # Misconceptions identified and resolved
        misc_identified = []
        misc_resolved = []
        for h in session.history:
            if h.misconception_report and h.misconception_report.is_misconception:
                m_model = h.misconception_report.flawed_mental_model
                if m_model not in misc_identified:
                    misc_identified.append(m_model)
                    # If subsequently answered correctly or final assessment was passed
                    if overall_score >= 70 or h.concept in understood:
                        if m_model not in misc_resolved:
                            misc_resolved.append(m_model)

        # Traceable Revision Recommendation
        topic_lower = session.current_topic.lower()
        topic_domain = classify_topic(topic=session.current_topic)
        if needing_work:
            rec_concept = needing_work[0]
            rec_revision = f"{rec_concept} Practice & Visual Review"
            rec_reason = f"You showed partial understanding or misconceptions during '{rec_concept}'. Reviewing the visual mental model will solidify your grasp."
        else:
            if topic_domain == TopicDomain.MACHINE_LEARNING:
                rec_revision = "Neural Network Forward Pass & Activation Dynamics"
                rec_reason = "You demonstrated strong mastery of foundational neuron computation; practicing multi-layer forward propagation and activation mechanics will solidify your intuition."
            elif topic_domain == TopicDomain.RECURSION:
                rec_revision = "Recursive Call Stack Tracing & Base Case Deep-Dive"
                rec_reason = "You demonstrated strong mastery of foundational recursion principles; practicing multi-branch call stack tracing will solidify your intuition."
            elif topic_domain == TopicDomain.DATA_STRUCTURES:
                rec_revision = f"{session.current_topic} Traversal & Algorithmic Mechanics"
                rec_reason = "You demonstrated strong mastery of foundational principles; advancing to traversal mechanics will deepen your intuition."
            else:
                rec_revision = f"{session.current_topic} Core Principles & Practical Application"
                rec_reason = "You demonstrated strong mastery of foundational principles; advancing to applied scenarios will deepen your intuition."

        # Traceable Next Topic Recommendation
        if topic_domain == TopicDomain.MACHINE_LEARNING:
            next_topic = "Backpropagation & Gradient Descent Optimization"
            next_reason = "With the forward pass and activation dynamics mastered, backpropagation explains how errors flow backward to iteratively update weights and minimize loss."
        elif topic_domain == TopicDomain.RECURSION:
            next_topic = "Divide and Conquer Algorithms & Dynamic Programming"
            next_reason = "With recursion and call stacks mastered, divide-and-conquer (Merge Sort) and memoization (Dynamic Programming) naturally optimize redundant recursive calls."
        elif topic_domain == TopicDomain.DATA_STRUCTURES:
            next_topic = "Binary Search Trees (BST) & Self-Balancing Trees"
            next_reason = "Now that you understand 2-way hierarchical branching and leaf nodes, Binary Search Trees introduce key ordering rules for O(log n) search operations."
        elif topic_domain == TopicDomain.PHYSICS_ELECTRONICS or "ohm" in topic_lower or "circuit" in topic_lower:
            next_topic = "Kirchhoff's Laws & Multi-Loop Circuit Analysis"
            next_reason = "With single-resistor Ohm's Law mastered, Kirchhoff's Laws allow you to calculate voltages and currents across complex multi-branch networks."
        else:
            next_topic = f"Advanced System Architectures & Scaling in {session.current_topic}"
            next_reason = f"Builds directly on {session.current_topic} principles to design production-grade resilient systems."

        status_str = "mastered" if overall_score >= 85 else ("completed" if overall_score >= 60 else "needs_revision")

        report = LearningReportSchema(
            report_id=f"rep-{uuid.uuid4().hex[:8]}",
            session_id=session.session_id,
            topic=session.current_topic,
            learner_name=session.learner_profile.name or "Learner",
            overall_score_percent=overall_score,
            status=status_str,
            concepts_understood=understood,
            concepts_needing_improvement=needing_work,
            misconceptions_identified=misc_identified,
            misconceptions_resolved=misc_resolved,
            progress_percent=100,
            recommended_revision=rec_revision,
            revision_reason=rec_reason,
            next_topic_recommendation=next_topic,
            next_topic_reason=next_reason,
            total_questions_answered=len(session.history) + len(results),
            question_results=results,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        session.status = SessionStatus.COMPLETED
        self.reports_cache[session.session_id] = report
        return report

    def get_learning_report(self, session: TeachingSessionStateSchema) -> Optional[LearningReportSchema]:
        """Retrieve cached LearningReportSchema for a session if completed."""
        return self.reports_cache.get(session.session_id)

    def get_learner_progress_dashboard(self, session: TeachingSessionStateSchema) -> Dict[str, Any]:
        """Assemble structured learner progress dashboard data."""
        report = self.get_learning_report(session)
        total_secs = len(session.lesson_plan.sections) if session.lesson_plan and session.lesson_plan.sections else 1
        progress_pct = 100 if session.status == SessionStatus.COMPLETED else int((session.current_section_index / max(1, total_secs)) * 100)

        # Average mastery score
        if session.concept_mastery_map:
            avg_mastery = round(sum(m.mastery_score for m in session.concept_mastery_map.values()) / len(session.concept_mastery_map) * 100)
        else:
            avg_mastery = 80 if session.status == SessionStatus.COMPLETED else 50

        # Mastered vs struggling
        mastered = list(session.concepts_mastered)
        struggling = list(session.concepts_needing_improvement)
        if not mastered and session.status == SessionStatus.COMPLETED:
            mastered = [s.concept for s in session.lesson_plan.sections] if session.lesson_plan else [session.current_topic]

        return {
            "learner_id": session.learner_profile.learner_id,
            "learner_name": session.learner_profile.name,
            "current_topic": session.current_topic,
            "level": session.learner_profile.educational_level.value,
            "status": session.status.value,
            "progress_percent": progress_pct,
            "overall_mastery_percent": avg_mastery,
            "concepts_mastered": mastered,
            "concepts_needing_improvement": struggling,
            "concept_mastery_details": [m.model_dump() for m in session.concept_mastery_map.values()],
            "recommended_revision": report.recommended_revision if report else f"{session.current_topic} Core Invariants",
            "revision_reason": report.revision_reason if report else "Foundational reinforcement for rapid problem-solving.",
            "next_topic": report.next_topic_recommendation if report else f"Advanced {session.current_topic}",
            "next_topic_reason": report.next_topic_reason if report else f"Next progressive step in mastering {session.current_topic}.",
            "total_interactions": len(session.history),
            "recent_sessions": [
                {
                    "session_id": session.session_id,
                    "topic": session.current_topic,
                    "score_percent": report.overall_score_percent if report else avg_mastery,
                    "status": session.status.value,
                    "date": datetime.now(timezone.utc).strftime("%b %d, %Y"),
                }
            ],
        }

