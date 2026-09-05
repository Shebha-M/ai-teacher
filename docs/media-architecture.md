# AI Teacher — Media Architecture & Subject-Aware Visuals

This document details the multimedia video and visual explanation architecture implemented in the AI Teacher platform.

---

## 1. Architectural Philosophy

Traditional educational chatbots place a static avatar next to a wall of text. The AI Teacher platform treats teaching as a **dynamic multimedia presentation**:
- **Atomic Scene Planning**: Lessons are segmented into synchronized visual and narrative moments.
- **Subject-Aware Visual Selection**: Visual formats are deterministically chosen based on academic discipline (SVG binary trees, recursion stack frames, neural network graphs, circuit schematics, code viewers).
- **Interactive Checkpoints**: Video playback pauses automatically at pedagogical checkpoints, requiring student input before proceeding.
- **Adaptive Remediation Branching**: If a student demonstrates a misconception at a checkpoint, the player dynamically branches to an inserted **Remediation Scene (Scene 3-R)** before resuming the lesson.
- **Offline First**: All visuals and animations render deterministically in the client using SVG, Canvas, and CSS, requiring no external paid video APIs.

---

## 2. The 4-Scene Teaching Plan Structure

For each section in the lesson plan, the `VisualPlanner` (`ai_engine/modules/visual_planner.py`) constructs a `TeachingScenePlan` comprising 4 atomic scenes:

```text
+-------------------------------------------------------------------------------+
|                             TEACHING SCENE PLAN                               |
+-------------------------------------------------------------------------------+
| Scene 1: INTRO (Welcoming)                                                   |
|   -> Teacher greets student by name and frames the core learning objective.   |
+-------------------------------------------------------------------------------+
| Scene 2: VISUAL EXPLANATION (Explaining)                                      |
|   -> Displays domain-specific visual (Tree/Circuit/Code/Equation/Network).    |
|   -> Teacher points to specific visual elements.                              |
+-------------------------------------------------------------------------------+
| Scene 3: ANALOGY WALKTHROUGH (Explaining)                                     |
|   -> Traces elements while narrating a memorable real-world analogy.          |
+-------------------------------------------------------------------------------+
| Scene 4: CHECKPOINT PROMPT (Thoughtful)                                       |
|   -> Video pauses automatically; teacher prompts for student understanding.   |
+-------------------------------------------------------------------------------+
                                     |
                              [Misconception?]
                                     |
                                    YES
                                     v
+-------------------------------------------------------------------------------+
| Scene 3-R: ADAPTIVE REMEDIATION (Encouraging)                                 |
|   -> Injects counter-analogy and alternative visual representation.           |
+-------------------------------------------------------------------------------+
```

---

## 3. Subject-Aware Visual Planner

The `VisualPlanner` inspects the topic and domain to select the optimal visual schema:

| Domain | Inferred Visual Type | Deterministic Data Payload | Interactive Renderer |
| :--- | :--- | :--- | :--- |
| **Data Structures** | `tree_diagram` | Hierarchical tree nodes, left/right pointers, traversal list | Interactive SVG with glowing nodes and hover tooltips |
| **Recursion** | `stack_diagram` | Call stack frames, activation records, return values | Dynamic frame stack with base case badges |
| **Neural Networks / ML** | `neural_diagram` | Layers (Input $\to$ Hidden $\to$ Output), weighted edges, activations | Interactive multi-layer node graph with edge weights |
| **Electronics / Physics** | `circuit_diagram` | Power supply, resistor value, formula ($I = V / R$) | Vector schematic with animated current flow |
| **Programming** | `code` | Code snippet, language, highlighted lines | Monospaced syntax viewer with line indicators |
| **Mathematics** | `equation` | LaTeX equation, step-by-step derivation cards | Card breakdown of mathematical variables |
| **General / Document** | `flowchart` | Steps, sequence arrows, key takeaways, citations | Sequential card flowchart with source badges |

---

## 4. AI Teacher Avatar & Voice Engine

### Avatar Animation System
- **Keyframe Mouth Animation**: Driven by sub-second word timestamps, modulating between visemes (`OPEN`, `HALF_OPEN`, `NARROW`, `REST`).
- **Keyframe Blinking**: Periodic natural blinking (150ms every 3.5 seconds).
- **Emotion States**:
  - `WELCOMING`: Open smile, friendly greeting pose.
  - `EXPLAINING`: Focused eyes, dynamic gestures pointing to the visual stage.
  - `ENCOURAGING`: Warm nod, validating reassurance.
  - `THOUGHTFUL`: Inquisitive expression during checkpoints.
  - `CELEBRATING`: Enthusiastic confirmation of mastery.

### Spoken Narration Engine
- **Microsoft Edge Neural TTS**: Generates `.mp3` audio files with sub-second word-boundary and sentence-boundary timestamp cues.
- **Deterministic Audio Fallback**: Backend mock provider generates standard RIFF/WAV headers with duration metadata for headless or offline environments.
- **Web Speech API**: In-browser speech synthesis (`SpeechSynthesisUtterance`) with accurate BCP-47 tags (`hi-IN`, `ta-IN`, etc.) for zero-latency client synthesis.
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

When teaching from uploaded documents (PDF, DOCX, PPTX, TXT):
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
| `/api/v1/teaching/sessions/{id}/scenes/{scene_id}/speech` | `POST` | Synthesizes neural audio asset and word-level timestamp cues for a scene. |
| `/api/v1/teaching/sessions/{id}/scenes/{scene_id}/avatar-state` | `GET` | Retrieves instantaneous avatar posture, emotion, mouth state, and gestures. |
| `/api/v1/teaching/sessions/{id}/language` | `POST` | Switches teaching language mid-lesson without resetting progress. |
| `/api/v1/teaching/sessions/{id}/branch` | `POST` | Generates an adaptive remediation scene on detected misconception. |
