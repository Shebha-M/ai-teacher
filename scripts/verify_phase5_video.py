"""End-to-end verification script for Phase 5: AI Teaching Video and Subject-Aware Visuals."""
import asyncio
import sys
from pathlib import Path

# Ensure root directory is on PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from httpx import AsyncClient, ASGITransport
from backend.main import app
from ai_engine.schemas.scene import VisualType, TeacherEmotion


async def main():
    print("================================================================================")
    print("   AI TEACHER -- PHASE 5 END-TO-END VERIFICATION: VIDEO & SUBJECT-AWARE VISUALS   ")
    print("================================================================================\n")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # STEP 1: Create teaching session on Binary Trees
        print("[Step 1] Initializing teaching session for 'Jordan' on 'Binary Trees'...")
        create_resp = await client.post(
            "/api/v1/teaching/sessions",
            json={
                "topic": "Binary Trees",
                "learner_name": "Jordan Lee",
                "educational_level": "beginner",
                "available_learning_time": 15,
                "preferred_teaching_style": "analogy_driven",
                "knowledge_mode": "topic",
            },
        )
        assert create_resp.status_code == 201, f"Failed: {create_resp.text}"
        sess = create_resp.json()
        session_id = sess["session_id"]
        print(f"  [OK] Session initialized: {session_id}")

        # STEP 2: Plan Curriculum
        print("\n[Step 2] Generating structured lesson plan...")
        plan_resp = await client.post(f"/api/v1/teaching/sessions/{session_id}/plan")
        assert plan_resp.status_code == 200, f"Failed: {plan_resp.text}"
        plan = plan_resp.json()
        sections = plan.get("lesson_plan", {}).get("sections", [])
        print(f"  [OK] Plan synthesized with {len(sections)} sections:")
        for s in sections:
            print(f"    - Section {s['section_number']}: {s['title']} ({s['estimated_time_minutes']} min)")

        # STEP 3: Teach Section 1
        print("\n[Step 3] Explaining Section 1 (Foundations & Intuition)...")
        teach_resp = await client.post(f"/api/v1/teaching/sessions/{session_id}/explain")
        assert teach_resp.status_code == 200, f"Failed: {teach_resp.text}"
        teach_data = teach_resp.json()
        print(f"  [OK] Core Concept: {teach_data['concept']}")
        print(f"  [OK] Key Takeaway: {teach_data['key_takeaway']}")

        # STEP 4: Generate Teaching Scene Plan (Phase 5 Core)
        print("\n[Step 4] Synthesizing 4-Scene Teaching Video Plan...")
        scenes_resp = await client.post(f"/api/v1/teaching/sessions/{session_id}/scenes")
        assert scenes_resp.status_code == 200, f"Failed: {scenes_resp.text}"
        scene_plan = scenes_resp.json()
        print(f"  [OK] Scene Plan ID: {scene_plan['plan_id']}")
        print(f"  [OK] Total Video Duration: {scene_plan['total_duration_estimate']}s")
        print(f"  [OK] Total Scenes: {len(scene_plan['scenes'])}")

        for scn in scene_plan["scenes"]:
            print(f"\n    [Scene {scn['scene_index']}: {scn['scene_type'].upper()}]")
            print(f"      - Emotion: {scn['teacher_emotion']}")
            print(f"      - Teacher Action: {scn['teacher_action']}")
            print(f"      - Visual Type: {scn['visual_specification']['visual_type']}")
            print(f"      - Visual Title: {scn['visual_specification']['title']}")
            print(f"      - Narration: \"{scn['narration'][:90]}...\"")
            if scn["is_checkpoint"]:
                print("      - [?] INTERACTIVE CHECKPOINT: Video pauses for assessment question!")

        # STEP 5: Verify Subject-Aware Deterministic Visual Specification
        print("\n[Step 5] Validating Deterministic SVG Binary Tree Specification...")
        scene_2 = scene_plan["scenes"][1]
        v_data = scene_2["visual_specification"]["data"]
        assert scene_2["visual_specification"]["visual_type"] == "tree_diagram"
        assert "root" in v_data
        assert v_data["root"]["val"] == 50
        assert v_data["root"]["left"]["val"] == 25
        assert v_data["root"]["right"]["val"] == 75
        print(f"  [OK] Root Node: {v_data['root']['val']} ({v_data['root']['label']})")
        print(f"  [OK] Left Child: {v_data['root']['left']['val']}")
        print(f"  [OK] Right Child: {v_data['root']['right']['val']}")
        print(f"  [OK] In-Order Traversal Sequence: {v_data['in_order_sequence']}")
        print(f"  [OK] Highlight Elements: {scene_2['visual_specification']['highlight_elements']}")

        # STEP 6: Render Scene Assets (Audio, Avatar Visemes, Visual Spec)
        print("\n[Step 6] Rendering Scene Media Assets...")
        scene_1_id = scene_plan["scenes"][0]["scene_id"]
        render_resp = await client.post(f"/api/v1/teaching/sessions/{session_id}/scenes/{scene_1_id}/render")
        assert render_resp.status_code == 200, f"Failed: {render_resp.text}"
        render_data = render_resp.json()
        print(f"  [OK] Mock Audio Stream: {render_data['audio_stream_mock'][:45]}...")
        print(f"  [OK] Avatar Visemes: {render_data['avatar_animation']['lip_sync_visemes']}")
        print(f"  [OK] Avatar Head Nods: {render_data['avatar_animation']['expressions']['head_nod_points']}")

        # STEP 7: Checkpoint Interruption & Student Misconception
        print("\n[Step 7] Reaching Scene 4 Checkpoint: Posing Assessment Question...")
        q_resp = await client.post(f"/api/v1/teaching/sessions/{session_id}/question")
        assert q_resp.status_code == 200, f"Failed: {q_resp.text}"
        q_data = q_resp.json()
        print(f"  [OK] Question: {q_data['prompt']}")

        print("\n[Step 8] Student submits misconception response...")
        student_wrong = "A node can have 4 children as long as the tree is balanced."
        print(f"  -> Student Answer: \"{student_wrong}\"")
        eval_resp = await client.post(
            f"/api/v1/teaching/sessions/{session_id}/evaluate",
            json={"student_answer": student_wrong, "question_id": q_data["question_id"]},
        )
        assert eval_resp.status_code == 200, f"Failed: {eval_resp.text}"
        eval_data = eval_resp.json()
        print(f"  [OK] Evaluator Score: {eval_data['evaluation']['score']}")
        print(f"  [OK] Misconception Detected: {eval_data['misconception']['is_misconception']}")
        print(f"  [OK] Flawed Mental Model: {eval_data['misconception']['flawed_mental_model']}")

        # STEP 9: Adaptive Branching: Insert Scene 3-R
        print("\n[Step 9] Executing Adaptive Branching (Inserting Remediation Scene 3-R)...")
        branch_resp = await client.post(f"/api/v1/teaching/sessions/{session_id}/branch")
        assert branch_resp.status_code == 200, f"Failed: {branch_resp.text}"
        rem_scene = branch_resp.json()
        print(f"  [OK] Remediation Scene ID: {rem_scene['scene_id']}")
        print(f"  [OK] Teacher Emotion: {rem_scene['teacher_emotion']}")
        print(f"  [OK] Narration: \"{rem_scene['narration'][:95]}...\"")
        print(f"  [OK] Counter-Analogy Deployed: {rem_scene['visual_specification']['data'].get('counter_analogy')}")

        # STEP 10: Multi-Subject Awareness Verification
        print("\n[Step 10] Testing Subject Awareness across multiple domains...")
        from ai_engine.modules.visual_planner import VisualPlanner

        phys = VisualPlanner.determine_visual_specification("Ohm's Law", "Electronics")
        assert phys.visual_type == VisualType.CIRCUIT_DIAGRAM
        print(f"  [OK] Physics ('Ohm\\'s Law') -> {phys.visual_type.value.upper()} (Formula: {phys.data['formula']})")

        prog = VisualPlanner.determine_visual_specification("Recursion Stack", "Python Programming")
        assert prog.visual_type == VisualType.CODE
        print(f"  [OK] Programming ('Recursion') -> {prog.visual_type.value.upper()} (Lang: {prog.data['language']})")

        math_spec = VisualPlanner.determine_visual_specification("Balance Factor Derivation", "Calculus")
        assert math_spec.visual_type == VisualType.EQUATION
        print(f"  [OK] Math ('Balance Factor') -> {math_spec.visual_type.value.upper()} (Formula: {math_spec.data['latex_equation'][:35]}...)")

    print("\n================================================================================")
    print("   [OK] PHASE 5 VERIFICATION COMPLETE: ALL CHECKS PASSED SUCCESSFULLY!          ")
    print("================================================================================")


if __name__ == "__main__":
    asyncio.run(main())
