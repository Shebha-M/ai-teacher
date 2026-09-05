"""End-to-end 22-step verification script for Phase 8: Final AI Teacher Integration & Golden Demo Journey."""
import asyncio
import sys
from pathlib import Path

# Ensure root directory is on PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from httpx import AsyncClient, ASGITransport
from backend.main import app
from ai_engine.schemas.avatar import MouthState
from ai_engine.schemas.grounding import KnowledgeMode


async def main():
    print("================================================================================")
    print("   AI TEACHER -- PHASE 8 VERIFICATION: GOLDEN DEMO & FULL E2E JOURNEY            ")
    print("================================================================================\n")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:

        # ----------------------------------------------------------------------
        # STEP 1: Create learner profile & initialize session
        # ----------------------------------------------------------------------
        print("[Step 1] Creating learner profile & initializing teaching session...")
        create_resp = await client.post(
            "/api/v1/teaching/sessions",
            json={
                "topic": "Binary Trees",
                "learner_name": "Alex Chen",
                "educational_level": "beginner",
                "available_learning_time": 15,
                "preferred_teaching_style": "analogy_driven",
                "preferred_language": "en",
                "knowledge_mode": "document",
            },
        )
        assert create_resp.status_code == 201, f"Step 1 Failed: {create_resp.text}"
        sess_data = create_resp.json()
        session_id = sess_data["session_id"]
        print(f"  [OK] Session initialized: {session_id}")
        print(f"  [OK] Learner: {sess_data['learner_profile']['name']} ({sess_data['learner_profile']['educational_level']})")

        # ----------------------------------------------------------------------
        # STEP 2: Upload / Attach educational material (RAG Document Ingestion)
        # ----------------------------------------------------------------------
        print("\n[Step 2] Uploading and indexing educational material ('Binary_Trees_Lecture.md')...")
        sample_doc_content = (
            b"# Binary Trees Lecture\n\n"
            b"## Definition\n"
            b"A binary tree is a hierarchical non-linear data structure where each node has at most two children, "
            b"customarily designated as the left child and right child. A node with no children is termed a leaf node.\n\n"
            b"## Properties\n"
            b"A node does NOT need to have exactly two children; it can have 0, 1, or 2 children.\n"
        )
        upload_resp = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("Binary_Trees_Lecture.md", sample_doc_content, "text/markdown")},
        )
        assert upload_resp.status_code == 201, f"Step 2 Failed: {upload_resp.text}"
        doc_meta = upload_resp.json()
        print(f"  [OK] Document Ingested: {doc_meta['filename']} (ID: {doc_meta['document_id']})")
        print(f"  [OK] Chunks Indexed: {doc_meta['chunk_count']}")

        # ----------------------------------------------------------------------
        # STEP 3: Create personalized lesson plan
        # ----------------------------------------------------------------------
        print("\n[Step 3] Creating personalized lesson plan preview...")
        plan_resp = await client.post(f"/api/v1/teaching/sessions/{session_id}/plan")
        assert plan_resp.status_code == 200, f"Step 3 Failed: {plan_resp.text}"
        session_state = plan_resp.json()
        lesson_plan = session_state["lesson_plan"]
        assert lesson_plan is not None, "Lesson plan was not generated"
        print(f"  [OK] Lesson Title: {lesson_plan.get('lesson_title', lesson_plan.get('topic'))}")
        print(f"  [OK] Target Duration: {lesson_plan.get('estimated_duration', 15)} min")
        print(f"  [OK] Curriculum Sections: {len(lesson_plan['sections'])}")
        for idx, sec in enumerate(lesson_plan["sections"]):
            print(f"       Section {idx+1}: {sec['title']} ({sec['concept']})")

        # ----------------------------------------------------------------------
        # STEP 4: Generate structured scene plan
        # ----------------------------------------------------------------------
        print("\n[Step 4] Generating 4-scene teaching sequence for current section...")
        scene_plan_resp = await client.post(f"/api/v1/teaching/sessions/{session_id}/scenes")
        assert scene_plan_resp.status_code == 200, f"Step 4 Failed: {scene_plan_resp.text}"
        scene_plan = scene_plan_resp.json()
        scenes = scene_plan["scenes"]
        assert len(scenes) >= 3, f"Expected at least 3 scenes, got {len(scenes)}"
        print(f"  [OK] Generated {len(scenes)} scenes:")
        for sc in scenes:
            print(f"       - Scene {sc['scene_index']}: {sc['scene_type']} | {sc['teacher_action']} | {sc['teacher_emotion']}")

        # ----------------------------------------------------------------------
        # STEP 5: Generate & validate visual specification
        # ----------------------------------------------------------------------
        print("\n[Step 5] Validating visual specification (diagram / data structure)...")
        scene_2 = scenes[1]
        vis_spec = scene_2.get("visual_specification", {})
        assert vis_spec is not None, "Visual specification is missing"
        v_type = vis_spec.get("visual_type")
        v_data = vis_spec.get("data", {})
        print(f"  [OK] Visual Spec Title: {vis_spec.get('title')}")
        print(f"  [OK] Visual Type: {v_type}")
        assert v_type in ["tree_diagram", "labeled_diagram", "concept_map"], f"Unexpected visual type: {v_type}"
        if "root" in v_data:
            print(f"  [OK] Root Node: {v_data['root'].get('val')} ({v_data['root'].get('label')})")
            print(f"  [OK] Left Child: {v_data['root'].get('left', {}).get('val')}")
            print(f"  [OK] Right Child: {v_data['root'].get('right', {}).get('val')}")
        print(f"  [OK] Highlight Elements: {vis_spec.get('highlight_elements', [])}")

        # ----------------------------------------------------------------------
        # STEP 6: Generate spoken audio (Edge TTS / Fallback)
        # ----------------------------------------------------------------------
        print("\n[Step 6] Synthesizing real natural voice audio with word timestamps...")
        scene_1_id = scenes[0]["scene_id"]
        speech_resp = await client.post(
            f"/api/v1/teaching/sessions/{session_id}/scenes/{scene_1_id}/speech",
            json={"voice_id": "en-US-AriaNeural"},
        )
        assert speech_resp.status_code == 200, f"Step 6 Failed: {speech_resp.text}"
        audio_asset = speech_resp.json()
        print(f"  [OK] Spoken Audio Created: {audio_asset['asset_id']}")
        print(f"  [OK] Duration: {audio_asset['duration_seconds']}s")
        print(f"  [OK] Provider: {audio_asset['provider_type']}")
        print(f"  [OK] Subtitle Cues: {len(audio_asset.get('subtitles', []))}")

        # ----------------------------------------------------------------------
        # STEP 7: Start teaching (Pedagogical section explanation)
        # ----------------------------------------------------------------------
        print("\n[Step 7] Explaining section concept with pedagogical analogy & example...")
        explain_resp = await client.post(f"/api/v1/teaching/sessions/{session_id}/explain")
        assert explain_resp.status_code == 200, f"Step 7 Failed: {explain_resp.text}"
        teaching_content = explain_resp.json()
        print(f"  [OK] Spoken Explanation: {teaching_content['explanation'][:70]}...")
        print(f"  [OK] Pedagogical Analogy: {teaching_content['analogy'][:70]}...")

        # ----------------------------------------------------------------------
        # STEP 8: Reach checkpoint question
        # ----------------------------------------------------------------------
        print("\n[Step 8] Reaching diagnostic checkpoint question...")
        q_resp = await client.post(f"/api/v1/teaching/sessions/{session_id}/question")
        assert q_resp.status_code == 200, f"Step 8 Failed: {q_resp.text}"
        question_data = q_resp.json()
        q_id = question_data["question_id"]
        print(f"  [OK] Question Prompt: {question_data.get('prompt', '')}")
        opts_summary = [f"{o.get('key')}: {o.get('text')}" if isinstance(o, dict) else str(o) for o in question_data.get('options', [])]
        print(f"  [OK] Options: {opts_summary}")

        # ----------------------------------------------------------------------
        # STEP 9: Submit intentionally incorrect answer (Fail case for demo)
        # ----------------------------------------------------------------------
        print("\n[Step 9] Submitting intentional misconception answer (Option C: 'Must always have exactly 2 children')...")
        eval_resp = await client.post(
            f"/api/v1/teaching/sessions/{session_id}/evaluate",
            json={
                "question_id": q_id,
                "student_answer": "Option C: Must always have exactly 2 children",
            },
        )
        assert eval_resp.status_code == 200, f"Step 9 Failed: {eval_resp.text}"
        eval_data = eval_resp.json()

        # ----------------------------------------------------------------------
        # STEP 10: Evaluate answer
        # ----------------------------------------------------------------------
        print("\n[Step 10] Validating evaluation result...")
        evaluation = eval_data["evaluation"]
        assert evaluation["score"] < 0.85, "Expected incorrect answer score < 0.85"
        print(f"  [OK] Evaluator Result: correctness={evaluation.get('correctness')}, score={evaluation.get('score')}")
        print(f"  [OK] Feedback: {evaluation.get('rubric_feedback', '')[:80]}...")

        # ----------------------------------------------------------------------
        # STEP 11: Detect misconception / learning gap
        # ----------------------------------------------------------------------
        print("\n[Step 11] Detecting pedagogical misconception & root cause...")
        misconception = eval_data["misconception"]
        assert misconception["is_misconception"] is True, "Expected misconception to be detected"
        print(f"  [OK] Misconception Category: {misconception.get('category')}")
        print(f"  [OK] Flawed Mental Model: {misconception.get('flawed_mental_model')}")
        print(f"  [OK] Correct Mental Model: {misconception.get('correct_mental_model')}")

        # ----------------------------------------------------------------------
        # STEP 12: Trigger adaptive remediation
        # ----------------------------------------------------------------------
        print("\n[Step 12] Triggering adaptive remediation decision...")
        adaptation = eval_data["adaptation"]
        print(f"  [OK] Pedagogical Action: {adaptation.get('action')}")
        print(f"  [OK] Target Concept: {adaptation.get('target_concept')}")
        print(f"  [OK] Adaptation Strategy: {str(adaptation.get('strategy', ''))[:80]}...")

        # ----------------------------------------------------------------------
        # STEP 13: Generate alternative scene / remediation
        # ----------------------------------------------------------------------
        print("\n[Step 13] Synthesizing adapted remediation explanation scene...")
        remediation_resp = await client.post(f"/api/v1/teaching/sessions/{session_id}/advance")
        assert remediation_resp.status_code == 200, f"Step 13 Failed: {remediation_resp.text}"
        rem_data = remediation_resp.json()
        print(f"  [OK] Remediation Action Dispatched: status={rem_data['status']}")
        print(f"  [OK] Remediation Details: {str(rem_data['result'])[:80]}...")

        # ----------------------------------------------------------------------
        # STEP 14: Re-evaluate with correct understanding
        # ----------------------------------------------------------------------
        print("\n[Step 14] Student re-evaluates with corrected answer (Option B: 'At most 2 children')...")
        re_eval_resp = await client.post(
            f"/api/v1/teaching/sessions/{session_id}/evaluate",
            json={
                "question_id": q_id,
                "student_answer": "Option B: At most 2 children (0, 1, or 2)",
            },
        )
        assert re_eval_resp.status_code == 200, f"Step 14 Failed: {re_eval_resp.text}"
        re_eval_data = re_eval_resp.json()
        assert re_eval_data["evaluation"]["score"] >= 0.85, "Re-evaluation should now pass"
        print(f"  [OK] Re-evaluation Result: correctness={re_eval_data['evaluation'].get('correctness')}, score={re_eval_data['evaluation'].get('score')}")
        print(f"  [OK] Feedback: {re_eval_data['evaluation'].get('rubric_feedback', '')[:80]}...")

        # ----------------------------------------------------------------------
        # STEP 15: Update concept mastery
        # ----------------------------------------------------------------------
        print("\n[Step 15] Verifying concept mastery update in session state...")
        sess_check = await client.get(f"/api/v1/teaching/sessions/{session_id}")
        assert sess_check.status_code == 200, f"Step 15 Failed: {sess_check.text}"
        curr_sess = sess_check.json()
        profile = curr_sess["learner_profile"]
        mastery_map = profile.get("concept_mastery", {})
        print(f"  [OK] Mastered Concepts: {curr_sess.get('concepts_mastered')}")
        print(f"  [OK] Current Mastery Map: {mastery_map}")
        assert len(curr_sess.get("concepts_mastered", [])) >= 1 or len(mastery_map) >= 1

        # ----------------------------------------------------------------------
        # STEP 16: Continue lesson
        # ----------------------------------------------------------------------
        print("\n[Step 16] Advancing lesson to subsequent curriculum section...")
        adv_resp = await client.post(f"/api/v1/teaching/sessions/{session_id}/advance")
        assert adv_resp.status_code == 200, f"Step 16 Failed: {adv_resp.text}"
        adv_data = adv_resp.json()
        print(f"  [OK] Advanced to Section Index: {adv_data['current_section_index']}")
        print(f"  [OK] Current Concept: {adv_data['current_concept']}")

        # ----------------------------------------------------------------------
        # STEP 17: Complete final assessment
        # ----------------------------------------------------------------------
        print("\n[Step 17] Generating and completing cumulative final assessment...")
        assess_resp = await client.post(f"/api/v1/teaching/sessions/{session_id}/assessment")
        assert assess_resp.status_code == 200, f"Step 17 Failed: {assess_resp.text}"
        assessment = assess_resp.json()
        print(f"  [OK] Assessment ID: {assessment['assessment_id']}")
        print(f"  [OK] Questions: {len(assessment['questions'])}")
        
        # Submit answers
        answers_payload = []
        for q in assessment["questions"]:
            opts = q.get("options", [])
            first_ans = opts[0]["key"] if (opts and isinstance(opts[0], dict) and "key" in opts[0]) else (opts[0] if opts else "Option A")
            answers_payload.append({"question_id": q["question_id"], "student_answer": first_ans})

        submit_resp = await client.post(
            f"/api/v1/teaching/sessions/{session_id}/assessment/submit",
            json={"answers": answers_payload},
        )
        assert submit_resp.status_code == 200, f"Step 17 Submit Failed: {submit_resp.text}"
        learning_report = submit_resp.json()
        print(f"  [OK] Assessment Submitted & Graded: Score = {learning_report['overall_score_percent']}%")

        # ----------------------------------------------------------------------
        # STEP 18: Generate learning report
        # ----------------------------------------------------------------------
        print("\n[Step 18] Inspecting comprehensive learning report...")
        report_get_resp = await client.get(f"/api/v1/teaching/sessions/{session_id}/report")
        assert report_get_resp.status_code == 200, f"Step 18 Failed: {report_get_resp.text}"
        report_data = report_get_resp.json()
        print(f"  [OK] Report ID: {report_data['report_id']}")
        print(f"  [OK] Status: {report_data['status']}")
        print(f"  [OK] Concepts Understood: {report_data['concepts_understood']}")
        print(f"  [OK] Concepts Needing Work: {report_data['concepts_needing_improvement']}")

        # ----------------------------------------------------------------------
        # STEP 19: Generate traceable revision recommendations
        # ----------------------------------------------------------------------
        print("\n[Step 19] Verifying pedagogical revision recommendations...")
        recommended_revision = report_data.get("recommended_revision", "")
        revision_reason = report_data.get("revision_reason", "")
        assert len(recommended_revision) > 0, "Expected recommended revision to be populated"
        print(f"  [OK] Recommended Revision: {recommended_revision}")
        print(f"  [OK] Revision Reason: {revision_reason[:80]}...")

        # ----------------------------------------------------------------------
        # STEP 20: Generate next-topic recommendation
        # ----------------------------------------------------------------------
        print("\n[Step 20] Verifying next-topic progression recommendation...")
        next_topic = report_data.get("next_topic_recommendation")
        next_reason = report_data.get("next_topic_reason", "")
        assert next_topic is not None and len(next_topic) > 0, "Missing next topic recommendation"
        print(f"  [OK] Next Recommended Topic: '{next_topic}'")
        print(f"  [OK] Next Topic Reason: {next_reason[:80]}...")

        # ----------------------------------------------------------------------
        # STEP 21: Switch language mid-session (Tamil 'ta')
        # ----------------------------------------------------------------------
        print("\n[Step 21] Switching language mid-session to Tamil ('ta')...")
        lang_resp = await client.post(
            f"/api/v1/teaching/sessions/{session_id}/language",
            json={"language": "ta", "mode": "bilingual"},
        )
        assert lang_resp.status_code == 200, f"Step 21 Failed: {lang_resp.text}"
        lang_data = lang_resp.json()
        print(f"  [OK] Active Teaching Language: {lang_data['teaching_language']}")
        print(f"  [OK] Active Neural Voice: {lang_data['active_voice_id']}")
        assert lang_data["teaching_language"] == "ta"

        # ----------------------------------------------------------------------
        # STEP 22: Verify session continuity across language switch & dashboard
        # ----------------------------------------------------------------------
        print("\n[Step 22] Verifying session continuity, mastery retention & dashboard...")
        # Check session state
        continuity_resp = await client.get(f"/api/v1/teaching/sessions/{session_id}")
        assert continuity_resp.status_code == 200, f"Step 22 Failed: {continuity_resp.text}"
        cont_sess = continuity_resp.json()
        assert cont_sess["session_id"] == session_id
        assert cont_sess["teaching_language"] == "ta"
        assert cont_sess["current_section_index"] == adv_data["current_section_index"]
        print(f"  [OK] Session Continuity Verified: Section Index = {cont_sess['current_section_index']}")
        print(f"  [OK] Preserved Learner Profile: {cont_sess['learner_profile']['name']}")

        # Check Learner Dashboard endpoint
        dash_resp = await client.get(f"/api/v1/teaching/sessions/{session_id}/dashboard")
        assert dash_resp.status_code == 200, f"Dashboard check failed: {dash_resp.text}"
        dash = dash_resp.json()
        print(f"  [OK] Dashboard Concept Mastery Count: {len(dash.get('concept_mastery', {}))}")
        print(f"  [OK] Dashboard Recommendations Count: {len(dash.get('recent_recommendations', []))}")

        # Check Readiness Endpoint
        readiness_resp = await client.get("/api/v1/readiness")
        assert readiness_resp.status_code == 200, f"Readiness check failed: {readiness_resp.text}"
        readiness = readiness_resp.json()
        assert readiness.get("system_ready") is True, "Expected system_ready to be True"
        print(f"  [OK] Readiness Overall Status: {readiness.get('overall_status')}")
        print(f"  [OK] System Ready: {readiness.get('system_ready')}")
        for comp, info in readiness.get("services", {}).items():
            print(f"       - {comp.capitalize()}: {info.get('status')} ({info.get('label')})")

    print("\n================================================================================")
    print("   ALL 22 STEPS OF THE GOLDEN DEMO JOURNEY PASSED SUCCESSFULLY!                ")
    print("================================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
