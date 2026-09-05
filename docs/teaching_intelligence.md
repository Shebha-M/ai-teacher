# AI Teacher — Core Teaching Intelligence & Cognitive Mechanics

## 1. The Pedagogical Teaching Cycle

The AI Teacher is engineered around an explicit **8-step cycle** that models the cognitive workflow of an expert human tutor:

```
[1. Understand]  Learner background, level (Beginner/Intermediate/Advanced), available time, and style
       ↓
[2. Plan]        Curriculum synthesis adapting section count and depth to time (5m sprint vs 15m vs 60m)
       ↓
[3. Explain]     Pedagogical narrative grounded in an intuitive analogy, concrete example, and key takeaway
       ↓
[4. Demonstrate] Visual direction specifying diagrammatic, code, or graph representations
       ↓
[5. Question]    Targeted checkpoint question (conceptual, multiple choice, or problem solving)
       ↓
[6. Evaluate]    Multi-dimensional scoring: strengths, errors, missing concepts, and rubric feedback
       ↓
[7. Diagnose]    Misconception detector isolates whether an error is lack of knowledge vs. a flawed mental model
       ↓
[8. Adapt]       Pedagogical action: change analogy, simplify, give another example, or advance to next section
```

---

## 2. Dynamic Time Adaptation (Curriculum Planning)

The `LessonPlanner` (`ai_engine/modules/lesson_planner.py`) does not merely shorten a text prompt; it alters the **underlying curriculum architecture**:

### A. 5–10 Minutes: Rapid Essential Sprint
- **Sections**: Exactly 1 core section.
- **Pedagogical Goal**: Rapid mental model grounding with minimal cognitive overhead.
- **Visual**: High-contrast labeled schematic isolating the single governing principle.
- **Checkpoint**: 1 essential validation question.

### B. 15–30 Minutes: Balanced Mastery Curriculum
- **Sections**: Exactly 3 sequential sections:
  1. *Foundations & Intuition*: Physical model, everyday metaphor, core invariant rules.
  2. *Mechanics & Operations*: Traversal, comparisons, execution steps, decision branching.
  3. *Practical Applications & Trade-offs*: Real-world context, edge cases, and complexity analysis.
- **Checkpoints**: Incremental diagnostic checkpoints after each section.

### C. 45–60+ Minutes: Comprehensive Masterclass
- **Sections**: 5 deep dive sections:
  1. *Mathematical Anatomy*: Invariants, formal definitions, inductive proofs.
  2. *Operational Deep Dive*: Step-by-step state changes, memory representation, call stacks.
  3. *Pathological Edge Cases*: Degenerate states, performance collapse, rebalancing invariants.
  4. *Memory Layout & Pointers*: Pointer overhead, cache locality, and low-level trade-offs.
  5. *Architectural System Design*: Real-world database indexing, distributed storage, and production trade-offs.

---

## 3. Subject-Aware Domain Classification

To prevent domain leaks (such as applying Binary Tree terms to Recursion or Attendance policies), the `TopicClassifier` categorizes learning topics into distinct domains:

| Domain | Example Topics | Default Visual Schema | Default Pedagogical Metaphor |
| :--- | :--- | :--- | :--- |
| **Data Structures** | Binary Trees, Heaps, AVL, BST | SVG Hierarchical Tree Diagram | Tournament bracket or family hierarchy |
| **Recursion** | Call Stacks, Base Cases, Fibonacci | Stack Frame Activation Visualizer | Russian nesting dolls or recursive mirror |
| **Neural Networks** | Forward Pass, Backprop, Perceptrons | Multi-Layer Node Network Diagram | Assembly line with weight dial calibrators |
| **Electronics / Physics** | Ohm's Law, Circuits, Kirchhoff | DC Circuit Schematic with Formula | Water pipe pressure and constriction valve |
| **Mathematics** | Calculus, Linear Algebra, Equations | Step-by-Step LaTeX Derivation Card | Balancing scales and geometric balance |
| **Programming** | Python Loops, Async/Await, Memory | Syntax-Highlighted Code Viewer | Recipe checklist with conditional execution |
| **General / Document** | Workplace Policy, History, Biology | Sequential Step-by-Step Workflow | Multi-stage project roadmap |

---

## 4. Cognitive Misconception Diagnosis

Traditional auto-graders evaluate student responses as binary `correct/incorrect`. The AI Teacher's `MisconceptionDetector` (`ai_engine/modules/misconception_detector.py`) categorizes responses into 4 distinct cognitive states:

1. **Accurate Understanding**: Full rubric fulfillment with sound reasoning.
2. **Partial Understanding**: Directional intuition is correct, but formal formula or boundary condition is missing.
3. **Lack of Knowledge**: Student did not recall or does not know the concept.
4. **Active Misconception**: Student possesses a flawed internal mental model that consistently generates systematic errors.

### Misconception Taxonomy & Interventions:
- **Overgeneralization (Binary Trees)**:
  - *Student Response*: "Every node in a binary tree must always have exactly 2 children."
  - *Diagnosed Flaw*: Student equates the word 'binary' with mandatory equality, forgetting leaf nodes.
  - *Intervention*: Bicycle rack counter-analogy (rack designed for at most 2 bikes; holding 0, 1, or 2).
- **Inverse Proportionality Confusion (Ohm's Law)**:
  - *Student Response*: "Current increases when resistance goes up."
  - *Diagnosed Flaw*: Student confuses resistance with driving force rather than friction.
  - *Intervention*: Water hose valve constriction analogy.
- **Call Stack Ignorance (Recursion)**:
  - *Student Response*: "Recursive functions execute all calls at the exact same moment."
  - *Diagnosed Flaw*: Student lacks mental model of the call stack push and pop mechanics.
  - *Intervention*: Stack of dinner plates analogy.

---

## 5. Adaptation Decision Engine

The `AdaptationEngine` (`ai_engine/modules/adaptation_engine.py`) operates under strict pedagogical rules:

```
                  ┌───────────────────────────────┐
                  │ Diagnostic Checkpoint Result  │
                  └───────────────┬───────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
  [Correct Score >= 0.8]   [Score 0.5 - 0.79]     [Misconception Detected]
         │                        │                        │
         ▼                        ▼                        ▼
┌──────────────────┐     ┌──────────────────┐    ┌──────────────────┐
│ ADVANCE_SECTION  │     │ GIVE_EXAMPLE /   │    │ CHANGE_ANALOGY / │
│ (Mastery Score ↑)│     │ SIMPLIFY         │    │ RE_EXPLAIN       │
└──────────────────┘     └──────────────────┘    │ (Branch Scene 3R)│
                                                 └──────────────────┘
```

- **Invariant**: A student is **never allowed to advance** past a curriculum section with an unresolved active misconception.
- When an active misconception is diagnosed, the orchestrator triggers an **Adaptive Remediation Branch** (Scene 3-R), replacing the original abstract explanation with a grounded counter-analogy and alternative visual before re-prompting.

---

## 6. Cumulative Assessment & Learning Analytics

At the conclusion of the teaching sections, the AI Teacher conducts a multi-concept cumulative assessment:
1. **Assessment Generation**: Generates 3 multi-choice and problem-solving questions spanning all taught sections.
2. **Automated Rubric Grading**: Evaluates submitted answers, calculating an overall percentage score.
3. **Mastery Vector Update**: Updates persistent `ConceptMastery` scores in SQLite.
4. **Learning Report & Dashboard**:
   - Lists explicitly understood concepts vs. concepts requiring further practice.
   - Generates concrete **Revision Recommendations** with pedagogical explanations.
   - Prescribes the **Next Recommended Topic** to maintain learner momentum.
