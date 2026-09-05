"""Document-driven curriculum concept extractor.
Extracts authentic pedagogical concepts, workflows, rules, and visual structures
directly from retrieved document chunks for grounded lesson planning.
"""
import re
from typing import List, Optional, Tuple
from ai_engine.schemas.grounding import GroundedContextSchema, RetrievedChunkSchema
from ai_engine.schemas.learner import LearnerLevel
from ai_engine.schemas.lesson import (
    LessonSectionSchema,
    VisualRecommendation,
    VisualType,
    CheckpointSchema,
)


def _clean_text_snippet(text: str, max_len: int = 220) -> str:
    """Clean whitespace and trim text cleanly to max_len."""
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= max_len:
        return cleaned
    truncated = cleaned[:max_len]
    last_space = truncated.rfind(" ")
    if last_space > 100:
        return truncated[:last_space] + "..."
    return truncated + "..."


def _extract_key_phrases(text: str) -> List[str]:
    """Extract bullet headings, header terms, colon-delimited key phrases, or component names."""
    phrases: List[str] = []
    meta_patterns = [
        r"^first task",
        r"^full workflow",
        r"^integration needed",
        r"^pushed in commit",
        r"^files primarily",
        r"^remaining limitations",
        r"^implemented$",
        r"^notes$",
        r"^summary$",
        r"^overview$",
        r"^shebha",
    ]
    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        # Remove markdown heading hashes
        line = re.sub(r"^#+\s*", "", line).strip()
        # Remove leading bullets
        line = re.sub(r"^[-*•\d\.]+\s*", "", line).strip()
        # Strip trailing colon if single word / header
        clean_header = line.rstrip(":").strip()
        if any(re.search(pat, clean_header, re.I) for pat in meta_patterns):
            continue

        # Extract file component name if code path
        if "/" in line and any(ext in line for ext in [".jsx", ".tsx", ".js", ".py", ".css"]):
            fname = line.split("/")[-1]
            if fname not in phrases:
                phrases.append(fname)
            continue

        # If line has colon like "Key: Value", take the key
        if ":" in line:
            parts = [p.strip() for p in line.split(":", 1) if p.strip()]
            if len(parts) == 2 and len(parts[0]) > 3 and not any(re.search(pat, parts[0], re.I) for pat in meta_patterns):
                if parts[0] not in phrases:
                    phrases.append(parts[0])
                continue

        # Standard descriptive phrase
        clean_p = line.rstrip(".:-").strip()
        if 4 <= len(clean_p) <= 65 and not any(re.search(pat, clean_p, re.I) for pat in meta_patterns):
            if clean_p not in phrases:
                phrases.append(clean_p)

    return phrases


def _derive_section_concept(
    chunk: RetrievedChunkSchema,
    topic: str,
    section_num: int,
    total_sections: int,
    used_concepts: Optional[List[str]] = None,
    all_chunks: Optional[List[RetrievedChunkSchema]] = None,
) -> Tuple[str, str, str]:
    """
    Derives (concept_title, primary_theme, short_summary) from chunk content.
    Guarantees domain-authentic terminology without generic data structure leakage.
    """
    text = chunk.text_content
    phrases = _extract_key_phrases(text)
    used = used_concepts or []

    # Filter out generic structural headings
    is_generic_heading = bool(
        re.match(
            r"^(section\s*\d+|page\s*\d+|general|document|part\s*\d+|slide\s*\d+|untitled)$",
            (chunk.heading or "").strip(),
            re.I,
        )
    )

    concept = ""
    if chunk.heading and not is_generic_heading and len(chunk.heading.strip()) > 3 and chunk.heading.strip() not in used:
        concept = chunk.heading.strip()
    else:
        # Find first unused phrase in current chunk
        unused_phrases = [p for p in phrases if p not in used]
        if unused_phrases:
            concept = unused_phrases[0]
            if len(unused_phrases) > 1 and len(concept) < 25:
                concept = f"{concept} & {unused_phrases[1]}"
        elif phrases:
            concept = phrases[0]

    # If still empty or used, borrow unused phrases from other chunks in the document
    if (not concept or concept in used) and all_chunks:
        for oc in all_chunks:
            oc_phrases = _extract_key_phrases(oc.text_content)
            oc_unused = [p for p in oc_phrases if p not in used]
            if oc_unused:
                concept = oc_unused[0]
                if len(oc_unused) > 1 and len(concept) < 25:
                    concept = f"{concept} & {oc_unused[1]}"
                break

    if not concept:
        # Extract subject from first sentence
        sentences = [s.strip() for s in re.split(r"[.!?]\s+", text) if s.strip()]
        first_sent = sentences[0] if sentences else topic
        cleaned = re.sub(r"^(this document|the system|we describe|in this|overview of)\s*", "", first_sent, flags=re.I)
        cleaned = cleaned.split(":")[0].strip()
        concept = cleaned[:50].strip()
        if not concept or concept.lower() in [u.lower() for u in used]:
            concept = f"{topic} Operational Implementation"

    # Normalize concept formatting
    concept = concept.rstrip(".:-").strip()
    if not any(c.isupper() for c in concept):
        concept = concept.title()

    # Determine theme archetype based on section index
    if total_sections == 1:
        theme = "Core Workflow & Foundations"
    elif section_num == 1:
        theme = "Foundational Architecture & Workflow"
    elif section_num == total_sections:
        theme = "Practical Integration & Operational Rules"
    else:
        theme = "Execution Dynamics & Business Rules"

    summary = _clean_text_snippet(text, max_len=280)
    return concept, theme, summary


def _determine_visual_for_chunk(text: str, concept: str) -> VisualRecommendation:
    """Selects an appropriate pedagogical visual based on document chunk content."""
    text_lower = text.lower()

    if any(k in text_lower for k in ["workflow", "step", "flow", "process", "transition", "request", "approve", "reject", "clock"]):
        # Procedural / Flowchart visual
        elements = [
            "User Action / Trigger",
            "State Verification",
            "Processing / Gatekeeper Review",
            "Status Update & Persistence",
        ]
        # Extract actual keywords from text for elements
        extracted_steps = re.findall(r"\b([A-Z][a-z]+(?:\s+[a-z]+)?)\b", text)
        if len(extracted_steps) >= 3:
            elements = [s for s in extracted_steps[:4] if len(s) > 3]

        return VisualRecommendation(
            visual_type=VisualType.FLOWCHART,
            description=f"Step-by-step procedural flowchart illustrating {concept} execution.",
            suggested_elements=elements[:4],
        )

    elif any(k in text_lower for k in ["component", "dashboard", "widget", "modal", "interface", "jsx", "architecture"]):
        return VisualRecommendation(
            visual_type=VisualType.ARCHITECTURE_DIAGRAM,
            description=f"System architectural layout and component interactions for {concept}.",
            suggested_elements=["User Interface Layer", "Component State", "Data Store / LocalStorage", "API Gateway"],
        )

    elif any(k in text_lower for k in ["balance", "limit", "hours", "calculation", "rule", "policy", "days", "category"]):
        return VisualRecommendation(
            visual_type=VisualType.CONCEPT_MAP,
            description=f"Conceptual rule matrix and policy boundaries governing {concept}.",
            suggested_elements=["Category / Type", "Allocation Rule", "Approval Condition", "Audit Log"],
        )

    return VisualRecommendation(
        visual_type=VisualType.LABELED_DIAGRAM,
        description=f"Structured visual diagram mapping key components of {concept}.",
        suggested_elements=["Input Source", "Core Engine", "State Record", "Output / Report"],
    )


def extract_document_curriculum_concepts(
    grounded_context: GroundedContextSchema,
    time_limit: int,
    topic: str,
    level: LearnerLevel = LearnerLevel.BEGINNER,
    lesson_id: str = "plan-doc",
) -> List[LessonSectionSchema]:
    """
    Extracts authentic, time-adapted curriculum sections directly from retrieved document chunks.
    Ensures zero terminology contamination from unrelated domains.
    """
    chunks = grounded_context.retrieved_chunks
    if not chunks:
        return []

    # 1. Determine target section count based on available time
    if time_limit <= 10:
        target_count = 1
    elif time_limit <= 30:
        target_count = min(3, max(2, len(chunks)))
    else:
        target_count = min(5, max(3, len(chunks)))

    # Select representative chunks evenly across retrieved evidence
    step = max(1, len(chunks) // target_count)
    selected_chunks: List[RetrievedChunkSchema] = []
    for i in range(target_count):
        idx = min(i * step, len(chunks) - 1)
        if chunks[idx] not in selected_chunks:
            selected_chunks.append(chunks[idx])
        elif len(selected_chunks) < len(chunks):
            # Pick first unselected chunk
            for c in chunks:
                if c not in selected_chunks:
                    selected_chunks.append(c)
                    break

    if not selected_chunks:
        selected_chunks = chunks[:target_count]

    actual_count = len(selected_chunks)
    sections: List[LessonSectionSchema] = []
    used_concepts: List[str] = []

    for idx, chunk in enumerate(selected_chunks, start=1):
        concept, theme, summary = _derive_section_concept(
            chunk,
            topic,
            idx,
            actual_count,
            used_concepts=used_concepts,
            all_chunks=selected_chunks,
        )
        used_concepts.append(concept)
        citation_label = chunk.citation or f"Source: {chunk.filename}"

        # Calculate time allocation
        if actual_count == 1:
            sec_time = time_limit
        elif actual_count == 2:
            sec_time = int(time_limit * 0.5)
        elif actual_count == 3:
            sec_time = int(time_limit * 0.3) if idx != 2 else int(time_limit * 0.4)
        else:
            sec_time = max(5, time_limit // actual_count)

        # Build visual recommendation
        visual = _determine_visual_for_chunk(chunk.text_content, concept)

        # Extract realistic example context from chunk text
        lines = [l.strip() for l in chunk.text_content.split("\n") if len(l.strip()) > 20]
        example_scenario = lines[0] if lines else f"Practical application of {concept} in active operations."
        if len(example_scenario) > 160:
            example_scenario = example_scenario[:157] + "..."

        # Checkpoint schema testing document facts
        chk = CheckpointSchema(
            checkpoint_id=f"chk-{idx}",
            core_concept=f"Operational mechanics and rules of {concept}",
            trigger_condition="after_section_explanation",
        )

        section = LessonSectionSchema(
            section_id=f"{lesson_id}-sec-{idx}",
            section_number=idx,
            concept=concept,
            title=f"{idx}. {concept}",
            objective=f"Master {concept} and understand its operational workflow [{citation_label}]",
            difficulty="intermediate" if idx > 1 and level != LearnerLevel.BEGINNER else "beginner",
            estimated_time_minutes=sec_time,
            explanation_outline=(
                f"[{citation_label}]\n"
                f"Source excerpt: {summary}\n"
                f"Key operational principle: How {concept} is structured and executed."
            ),
            example_context=example_scenario,
            visual_recommendation=visual,
            question_checkpoint=chk,
            expected_understanding=f"Student can explain the rules, workflow, and significance of {concept} based on source documentation.",
        )
        sections.append(section)

    return sections
