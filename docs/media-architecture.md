# AI Teacher -- Media Architecture & Subject-Aware Visuals

This document details the multimedia video and visual explanation architecture implemented in **Phase 5** of the AI Teacher platform.

---

## 1. Architectural Philosophy

Traditional educational chatbots place a static avatar next to a wall of text. The AI Teacher platform treats teaching as a **dynamic multimedia presentation**:
- **Atomic Scene Planning**: Lessons are broken down into synchronized visual and narrative moments.
- **Subject-Aware Visual Selection**: Visual formats are deterministically chosen based on academic discipline (e.g. SVG binary trees for data structures, circuit schematics for electronics, code blocks for programming).
- **Interactive Checkpoints**: Video playback pauses automatically at pedagogical checkpoints, requiring student input before proceeding.
- **Adaptive Remediation Branching**: If a student demonstrates a misconception at a checkpoint, the player dynamically branches to an inserted **Remediation Scene (Scene 3-R)** before resuming the lesson.
- **Offline First**: All visuals and animations render deterministically in the client using SVG, Canvas, and CSS, requiring no external paid video APIs.

---

## 2. The 4-Scene Teaching Plan Structure

For each section in the lesson plan, the `VisualPlanner` constructs a `TeachingScenePlan` comprising 4 atomic scenes:

```text
+-------------------------------------------------------------------------------+
|                             TEACHING SCENE PLAN                               |
+-------------------------------------------------------------------------------+
| Scene 1: INTRO (Welcoming)                                                   |
|   -> Teacher greets student by name and frames the core learning objective.   |
+-------------------------------------------------------------------------------+
| Scene 2: VISUAL EXPLANATION (Explaining)                                      |
|   -> Displays domain-specific visual (Tree/Circuit/Code/Equation).            |
|   -> Teacher points to specific visual elements.                              |
+-------------------------------------------------------------------------------+
| Scene 3: ANALOGY WALKTHROUGH (Explaining)                                     |
|   -> Traces elements while narrating a memorable real-world analogy.           |
+-------------------------------------------------------------------------------+
| Scene 4: CHECKPOINT PROMPT (Thoughtful)                                       |
|   -> Video pauses automatically; teacher prompts for student understanding.    |
+-------------------------------------------------------------------------------+
                                     |
                              [Misconception?]
                                     |
                                    YES
                                     v
+-------------------------------------------------------------------------------+
| Scene 3-R: ADAPTIVE REMEDIATION (Encouraging)                                 |
|   -> Injects counter-analogy and alternative visual representation.            |
+-------------------------------------------------------------------------------+
```

---

## 3. Subject-Aware Visual Planner

The `VisualPlanner` (`ai_engine/modules/visual_planner.py`) inspects the topic and domain to select the optimal visual schema:

| Domain | Inferred Visual Type | Deterministic Data Payload | Interactive Renderer |
| :--- | :--- | :--- | :--- |
| **Data Structures** | `tree_diagram` | Hierarchical tree nodes, left/right pointers, traversal list | Interactive SVG with glowing nodes and hover tooltips |
| **Electronics / Physics** | `circuit_diagram` | Power supply, resistor value, formula ($I = V / R$) | Vector schematic with animated current flow |
| **Programming** | `code` | Code snippet, language, highlighted lines | Monospaced syntax viewer with line indicators |
| **Mathematics** | `equation` | LaTeX equation, step-by-step derivation cards | Card breakdown of mathematical variables |
| **General / Conceptual** | `flowchart` | Steps, sequence arrows, key takeaways | Sequential card flowchart |

---

## 4. AI Teacher Avatar & Voice Engine

### Avatar Animation System
- **Keyframe Mouth Animation**: CSS `@keyframes mouthTalk` modulates mouth opening height and width during active speech.
- **Keyframe Blinking**: CSS `@keyframes eyeBlink` creates periodic natural blinking.
- **Emotion States**:
  - `WELCOMING`: Open smile, friendly greeting pose.
  - `EXPLAINING`: Focused eyes, dynamic gestures pointing to the visual stage.
  - `ENCOURAGING`: Warm nod, validating reassurance.
  - `THOUGHTFUL`: Inquisitive expression during checkpoints.
  - `CELEBRATING`: Enthusiastic confirmation of mastery.

### Spoken Narration Engine
- **Web Speech API**: In-browser speech synthesis (`SpeechSynthesisUtterance`) with customized pitch (1.05), rate (0.95), and accent selection.
- **Deterministic Audio Fallback**: Backend mock provider generates standard RIFF/WAV headers with duration metadata for headless or offline environments.
- **Synchronized Subtitles**: Narration is highlighted synchronously in the player's subtitle bar.

---

## 5. Non-Linear Checkpoint Interruption & Adaptive Branching

1. When playback reaches **Scene 4**, the player automatically halts:
   - `isPlaying` is set to `false`.
   - The diagnostic checkpoint question is presented in the interactive console.
2. If the student answers correctly:
   - The student gains mastery points.
   - The player advances to the next section.
3. If the student exhibits a misconception:
   - The backend `/branch` endpoint synthesizes **Scene 3-R**.
   - Scene 3-R is injected into the player timeline.
   - The avatar delivers an encouraging counter-analogy and simplified visual.
   - The student is re-prompted to reinforce correct understanding.

---

## 6. RAG Grounding Continuity

When teaching from uploaded documents (PDF, DOCX, TXT):
- Each scene carries `CitationSchema` metadata pointing to the exact source document, page, and excerpt.
- The visual studio renders a persistent **Source Attribution Badge** (e.g. `[Document Grounded: Binary_Trees_Lecture.md, Page 3]`).
- Hovering or clicking the badge reveals the verbatim excerpt used to formulate the visual explanation.

---

## 7. Media REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/teaching/sessions/{id}/scenes` | `POST` | Generates or retrieves the 4-scene video plan for the current section. |
| `/api/v1/teaching/sessions/{id}/scenes` | `GET` | Retrieves the active scene plan and current scene index. |
| `/api/v1/teaching/sessions/{id}/scenes/{scene_id}/render` | `POST` | Renders audio stream, avatar visemes, and visual specifications. |
| `/api/v1/teaching/sessions/{id}/branch` | `POST` | Generates an adaptive remediation scene on detected misconception. |
