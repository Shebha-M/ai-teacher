"""Tests for FastAPI backend routes and database integration."""
import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.database.connection import init_db


@pytest.mark.asyncio
async def test_health_endpoints():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

        res_ai = await client.get("/api/v1/ai/health")
        assert res_ai.status_code == 200
        data = res_ai.json()
        assert data["status"] == "operational"
        assert "TeachingSessionOrchestrator" in data["registered_modules"]


@pytest.mark.asyncio
async def test_full_api_teaching_lifecycle():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create Session
        create_payload = {
            "topic": "Binary Trees",
            "learner_name": "API Tester",
            "educational_level": "beginner",
            "available_learning_time": 20,
            "preferred_teaching_style": "analogy_driven",
            "preferred_language": "en",
            "learning_objective": "Test full API cycle",
        }
        res_create = await client.post("/api/v1/teaching/sessions", json=create_payload)
        assert res_create.status_code == 201
        session_data = res_create.json()
        session_id = session_data["session_id"]
        assert session_id is not None

        # 2. Generate Plan
        res_plan = await client.post(f"/api/v1/teaching/sessions/{session_id}/plan")
        assert res_plan.status_code == 200
        plan_data = res_plan.json()
        assert plan_data["lesson_plan"] is not None
        assert len(plan_data["lesson_plan"]["sections"]) == 3

        # 3. Teach Current Section
        res_teach = await client.post(f"/api/v1/teaching/sessions/{session_id}/explain")
        assert res_teach.status_code == 200
        teach_data = res_teach.json()
        assert teach_data["concept"] is not None
        assert teach_data["analogy"] is not None
        assert teach_data["visual_instruction"] is not None

        # 4. Fetch Checkpoint Question
        res_q = await client.post(f"/api/v1/teaching/sessions/{session_id}/question")
        assert res_q.status_code == 200
        q_data = res_q.json()
        assert q_data["prompt"] is not None
        assert q_data["expected_answer"] is not None

        # 5. Submit Answer and Evaluate
        eval_payload = {
            "student_answer": "B",
            "question_id": q_data["question_id"],
        }
        res_eval = await client.post(f"/api/v1/teaching/sessions/{session_id}/evaluate", json=eval_payload)
        assert res_eval.status_code == 200
        eval_data = res_eval.json()
        assert eval_data["evaluation"]["correctness"] == "correct"
        assert eval_data["evaluation"]["score"] == 1.0
        assert eval_data["adaptation"]["action"] in ["move_to_next_concept", "continue"]

        # 6. Advance Session
        res_adv = await client.post(f"/api/v1/teaching/sessions/{session_id}/advance")
        assert res_adv.status_code == 200
        adv_data = res_adv.json()
        assert adv_data["result"]["action_taken"] == "advanced_to_next_section"
        assert adv_data["current_section_index"] == 1
