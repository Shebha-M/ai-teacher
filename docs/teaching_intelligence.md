# AI Teacher — Core Teaching Intelligence & Cognitive Mechanics

## 1. The Pedagogical Teaching Cycle

The AI Teacher is engineered around an explicit 8-step cycle that mimics an elite human tutor:

```
[1. Understand]  Learner background, level (Beginner/Intermediate/Advanced), available time, and style
       ↓
[2. Plan]        Curriculum synthesis adapting section count and depth to time (5m sprint vs 20m vs 60m)
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

The `LessonPlanner` does not merely alter text prompts; it alters the **underlying structure**:

### A. 5–10 Minutes: Rapid Essential Sprint
- **Sections**: Exactly 1 core section.
- **Goal**: Rapid mental model grounding with minimal cognitive overhead.
- **Visual**: High-contrast labeled schematic isolating the single governing principle.
- **Checkpoint**: 1 essential validation question.

### B. 15–30 Minutes: Balanced Curriculum
- **Sections**: Exactly 3 sequential sections:
  1. *Foundations & Intuition*: Physical model, everyday metaphor, node rules.
  2. *Mechanics & Operations*: Traversal, comparisons, decision branching.
  3. *Practical Applications & Trade-offs*: Real-world context and complexity analysis.
- **Checkpoints**: Incremental checkpoints after each section.

### C. 45–60+ Minutes: Comprehensive Masterclass
- **Sections**: 5 deep dive sections:
  1. *Mathematical Anatomy*: Invariants, inductive definitions, height/depth bounds.
  2. *Traversal Deep Dive*: Call stack mechanics during DFS vs. Queue-based BFS.
  3. *Pathological Edge Cases*: Degenerate trees, sorting vulnerabilities, AVL/Red-Black rotation intuition.
  4. *Memory Layout & Pointers*: Pointer overhead, cache locality, and contiguous array heaps.
  5. *Architectural System Design*: B-Trees and disk-based indexing engines in modern databases.

---

## 3. Cognitive Misconception Diagnosis

Traditional auto-graders categorize answers as binary `true/false`. The AI Teacher's `MisconceptionDetector` distinguishes:
1. **Accurate Understanding**: Full rubric fulfillment.
2. **Partial Understanding**: Direction is correct, but formal reasoning or formula is omitted.
3. **Lack of Knowledge**: Student did not recall or does not know the concept.
4. **Active Misconception**: Student possesses a flawed internal mental model that produces predictable errors.

### Example Misconception Taxonomy:
- **Inverse Proportionality Confusion (Ohm's Law)**:
  - *Student Response*: "Current increases when resistance goes up."
  - *Diagnosed Flaw*: Student equates resistance with energy or flow rather than friction.
  - *Prescribed Intervention*: Deploy the garden hose / water valve constriction analogy.
- **Overgeneralization (Binary Trees)**:
  - *Student Response*: "Every node must always have exactly two children."
  - *Diagnosed Flaw*: Student confuses upper bound constraint with strict equality, forgetting leaf nodes.
  - *Prescribed Intervention*: Bicycle rack counter-analogy (capacity for at most 2 bikes).

---

## 4. Adaptation Decision Engine

The `AdaptationEngine` operates under pedagogical safeguards:
- If an active misconception is diagnosed $\to$ **`CHANGE_ANALOGY`** or **`RE_EXPLAIN`** with counter-analogy. Never advance until resolved.
- If incorrect due to lack of knowledge $\to$ **`SIMPLIFY`** with decreased difficulty and step-by-step scaffolding.
- If partially correct $\to$ **`GIVE_ANOTHER_EXAMPLE`** to bridge missing nuances.
- If fully mastered $\to$ **`MOVE_TO_NEXT_CONCEPT`** or **`INCREASE_DIFFICULTY`**.
