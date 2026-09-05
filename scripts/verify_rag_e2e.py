import asyncio
import sys
import httpx

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000/api/v1"


async def main():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        print("\n--- 1. Upload Educational Document ---")
        with open("sample_docs/Binary_Trees_Lecture.md", "rb") as f:
            files = {"file": ("Binary_Trees_Lecture.md", f, "text/markdown")}
            upload_res = await client.post("/documents/upload", files=files)
        assert upload_res.status_code == 201, f"Upload failed: {upload_res.text}"
        doc_data = upload_res.json()
        doc_id = doc_data["document_id"]
        print(f"Document Uploaded: {doc_data['filename']}")
        print(f"Document ID: {doc_id}")
        print(f"Status: {doc_data['status']}")
        print(f"Chunks Indexed: {doc_data['chunk_count']}")

        print("\n--- 2. Create Document-Grounded Teaching Session ---")
        session_res = await client.post(
            "/teaching/sessions",
            json={
                "topic": "Binary Trees",
                "learner_name": "Taylor",
                "educational_level": "beginner",
                "available_learning_time": 15,
                "preferred_teaching_style": "analogy_driven",
                "preferred_language": "en",
                "learning_objective": "Master Binary Tree invariants and traversal algorithms from class notes",
                "knowledge_mode": "document",
                "document_id": doc_id,
            },
        )
        assert session_res.status_code == 201, f"Session create failed: {session_res.text}"
        session = session_res.json()
        session_id = session["session_id"]
        print(f"Session Created: {session_id}")
        print(f"Knowledge Mode: {session['knowledge_mode']}")
        print(f"Document Attached: {session['document_id']}")

        print("\n--- 3. Plan Grounded Curriculum ---")
        plan_res = await client.post(f"/teaching/sessions/{session_id}/plan")
        assert plan_res.status_code == 200, f"Planning failed: {plan_res.text}"
        plan_data = plan_res.json()
        lesson_plan = plan_data["lesson_plan"]
        grounded_context = plan_data.get("grounded_context")
        print(f"Lesson Title: {lesson_plan['lesson_title']}")
        print(f"Sections Count: {len(lesson_plan['sections'])}")
        assert "Binary_Trees_Lecture.md" in lesson_plan["lesson_title"], "Source document missing from title!"
        if grounded_context and grounded_context.get("citations"):
            print(f"Citations Verified ({len(grounded_context['citations'])}):")
            for cit in grounded_context["citations"]:
                print(f"  - [{cit['location']}] {cit['filename']}: \"{cit['excerpt'][:60]}...\"")

        print("\n--- 4. Teach Current Section with Citation Ingestion ---")
        explain_res = await client.post(f"/teaching/sessions/{session_id}/explain")
        assert explain_res.status_code == 200, f"Explain failed: {explain_res.text}"
        teach_data = explain_res.json()
        print(f"Concept: {teach_data['concept']}")
        print(f"Teaching Action: {teach_data['teaching_action']}")
        print(f"Explanation (Sample): {teach_data['explanation'][:160]}...")
        assert "Binary_Trees_Lecture.md" in teach_data["explanation"], "Citation missing from explanation!"

        print("\n--- 5. Generate Grounded Diagnostic Question ---")
        q_res = await client.post(f"/teaching/sessions/{session_id}/question")
        assert q_res.status_code == 200, f"Question failed: {q_res.text}"
        q_data = q_res.json()
        print(f"Question Type: {q_data['question_type']}")
        print(f"Prompt: {q_data['prompt']}")
        print(f"Hints: {q_data['hints']}")
        assert any("Binary_Trees_Lecture.md" in h for h in q_data["hints"]), "Source missing from hints!"

        print("\n=== LIVE E2E VERIFICATION SUCCEEDED 100%! ===")


if __name__ == "__main__":
    asyncio.run(main())
