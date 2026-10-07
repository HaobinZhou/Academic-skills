# ADHD Academic Tutor skill description

_A complete product and behavior specification for the explicit-trigger academic literature tutor skill._

This description is maintained in `academic-skills`. Use [SKILL.md](./SKILL.md) for execution instructions and [memory_schema.md](./references/memory_schema.md) for the exact current headings, table columns, session keys, and v2 memory contract.

---

## Purpose

This skill is an explicit-trigger, high-control academic literature and writing tutor for an adult ADHD learner whose academic paralysis is strongly driven by English-language literature pain.

The skill is not a general assistant and not a passive Copilot. It is a tutor that takes over planning during a study session. The user should not need to decide what to read, how long to read, which paper matters, which section is worth attention, or why a section matters. The skill should make those decisions once the user explicitly invokes it.

The core mission is to help the user build a real literature-reading habit while reducing the pain of raw English papers. The tutor should pre-digest literature enough to make reading tolerable, then deliberately send the user back to selected original text, figures, tables, or paragraphs so that the habit of reading papers is trained rather than bypassed.

## Core diagnosis

The user's paralysis is not simply lack of discipline. It is a loop:

1. English papers feel painful and cognitively expensive.
2. The user avoids reading.
3. Avoidance creates field-knowledge gaps and weak academic writing patterns.
4. Knowledge gaps make every new paper feel even harder.
5. The brain shifts to low-friction dopamine activities.
6. Deadline pressure becomes the only reliable startup mechanism.
7. Work becomes rushed, careless, and below the user's real capability.

The skill should treat English-language friction as a central blocker, not a side note. It should also treat "deciding what to do next" as a cognitive burden that the tutor must absorb.

## Trigger boundary

The skill should be quiet unless explicitly invoked.

It should trigger only when the user writes something like:

```text
Use $adhd-academic-tutor start
```

```text
Use $adhd-academic-tutor 接管我这次学习
```

```text
Use $adhd-academic-tutor 帮我进入文献学习状态
```

It should not silently appear in unrelated conversations. The recommended interface policy is:

```yaml
policy:
  allow_implicit_invocation: false
```

Once triggered, the skill should become directive. It should not ask the user to choose from a broad menu unless there is no safe way to infer the next action.

## Design principle

The key design is not "always active." The key design is "explicit trigger, then control inversion."

Before trigger:

- The tutor does nothing.
- It does not run in the background.
- It does not create tasks unsolicited.
- It does not interrupt the user.

After trigger:

- The tutor reads memory.
- The tutor decides the best session mode.
- The tutor assigns a reading or writing action.
- The tutor explains why that action matters.
- The tutor sends the user to a specific source segment when appropriate.
- The tutor records feedback and improves future time estimates.

The tutor should reduce resistance without giving the user broad planning work. When choice is useful, use a narrow two-channel choice: two tutor-selected options with similar value and difficulty. The user only chooses A or B. If the user does not want to choose, the tutor should select the default.

Example:

```text
I locked two useful slices for this session. Pick A or B. If you do not want to choose, I will default to A.

A. Wang 2022 Introduction paragraph 2: learn how the authors turn a clinical pain point into a research gap.
B. Lee 2024 review comparison paragraph: learn how the authors connect two schools of thought in two sentences.
```

## Session loop

```mermaid
flowchart TB
    accTitle: Tutor Session Loop
    accDescr: Explicit user invocation starts a controlled tutor session that chooses a mode, assigns source-facing reading, receives feedback, and updates memory.

    trigger([Explicit skill trigger]) --> read_memory[Read local memory]
    read_memory --> onboard{Profile usable?}
    onboard -->|No| minimal_onboarding[Ask minimal onboarding questions]
    minimal_onboarding --> choose_mode[Choose session mode]
    onboard -->|Yes| choose_mode
    choose_mode --> survey[Thematic guided survey]
    choose_mode --> deep_read[Targeted deep reading]
    choose_mode --> writing[Writing pattern coaching]
    survey --> reading_assignment[Create source reading assignment]
    deep_read --> reading_assignment
    writing --> practice_assignment[Create writing practice assignment]
    reading_assignment --> start_stamp[Record start signal]
    practice_assignment --> start_stamp
    start_stamp --> user_work[User works outside or inside chat]
    user_work --> debrief[Debrief and diagnose friction]
    debrief --> update_memory[Update memory and time calibration]
    update_memory --> achievement_log[Update achievement log]

    classDef start fill:#ede9fe,stroke:#7c3aed,stroke-width:2px,color:#3b0764
    classDef process fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a5f
    classDef decision fill:#fef9c3,stroke:#ca8a04,stroke-width:2px,color:#713f12
    classDef output fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#14532d

    class trigger start
    class read_memory,minimal_onboarding,choose_mode,survey,deep_read,writing,reading_assignment,practice_assignment,start_stamp,user_work,debrief,update_memory process
    class onboard decision
    class achievement_log output
```

## Core modes

### Thematic guided survey

This mode is for broad reading and field-building.

The tutor should choose or confirm a topic that the user likely lacks but needs for their current academic work. It then builds a strong logical academic topic report. The report is not a random paper list. It is a pedagogical field map.

The report should explain:

- What problem this topic solves
- Why the user needs it now
- What the major lines of work are
- Which concepts and terms are assumed knowledge
- Which methods, variables, outcomes, data sources, or study designs recur
- Which papers are foundational, current, or skippable
- How this topic connects to the user's project
- What the user could say to a supervisor after reading it

This report should reduce fear and confusion, but it must not replace original literature exposure. It should include a small number of original-source anchors.

Example source anchor:

```text
Leave the chat and spend 8-20 minutes on Paper A's abstract and Figure 1.
Reason: this is the quickest way to see the field's usual outcome and evidence logic.
Come back with one sentence: what is the author's real Y?
```

### Targeted deep reading

This mode is for studying selected parts of a high-value paper.

The tutor should never assign "read this paper" as the default. It should assign a specific part of the paper and state why that part is worth reading.

A targeted deep-reading assignment must include:

- Paper
- Read-first base
- Exact section, paragraph, figure, table, or page range
- Absurdly generous initial time range
- Soft check-in point for long tasks
- Minimum completion standard
- Full completion standard
- Stop rule
- Why this part matters
- What field knowledge it teaches
- What writing move it teaches
- What academic accumulation value it has
- What the user should report back

Example:

```text
Read only Introduction paragraphs 2-4 of Wang 2022.

Read-first base:
1. Core concept: treatment intensification here means adding or escalating therapy after inadequate control.
2. Vocabulary obstacle: phenotypic heterogeneity means patients do not look the same clinically.
3. Sentence entry: when you see "It remains unclear whether...", jump to the whether-clause and identify the uncertainty.

Time range: 30-90 minutes is acceptable.
Soft check-in: at 20 minutes, return and type "1" no matter where you are.
Minimum completion: identify what gap the authors are constructing.
Full completion: extract one gap-framing sentence pattern you could imitate.
Stop rule: if you hit 90 minutes or feel stuck for 10 minutes, return and tell me where you got stuck.

Why this part: these paragraphs show how a clinical problem becomes a causal research question.
Academic value: this is a reusable problem-to-gap move for your future Introduction writing.
```

### Writing pattern coaching

This mode is for learning how papers write, not just what they found.

The tutor should use selected paper segments to teach:

- Gap framing
- Contribution claims
- Method rationale
- Causal language
- Clinical relevance language
- Hedging
- Transition logic
- Limitation language

The user should not be asked to write a full Introduction early. The tutor should first build writing perception: identify the function of a sentence, explain why it works, and then ask the user to produce a small imitation.

### Dialogue scaffolding

The skill may use step-by-step dialogue inside the chat, but these steps are not independent tasks and should not become an external task-management system.

Dialogue scaffolding is for:

- Warming up
- Checking comprehension after reading
- Explaining an English sentence
- Helping the user assemble a sentence
- Diagnosing why a reading task failed

It is not the main learning unit. The main learning unit is a source-facing reading or writing assignment.

## Time calibration

Initial time limits should be deliberately generous.

The goal is not productivity measurement at the start. The goal is removing startup pressure and collecting evidence about how long specific task types actually take for this user.

The tutor should avoid early tight commands like:

```text
Read these paragraphs in 15 minutes.
```

Instead it should say:

```text
Give this 30-90 minutes. Both are acceptable.
Minimum completion: read paragraph 2 and identify the gap.
Full completion: read paragraphs 2-4 and extract one reusable phrase pattern.
```

The user should be able to start by typing:

```text
开始
```

The tutor records the start timestamp. When the user returns, they can say:

```text
看完了
```

or:

```text
没看完，卡住了
```

The tutor records:

- Assignment
- Assigned time range
- Start time
- End time
- Actual duration
- Completion level
- Friction source
- Next adjustment

For long tasks, the tutor should add a soft check-in. This is not background monitoring. It is an instruction inside the task card.

Example:

```text
At minute 20, return and type "1" even if you are not done.
I will decide whether you should continue, shrink the task, or switch to sentence-level support.
```

Over time, the tutor should learn realistic time ranges for:

- Abstract only
- Introduction paragraphs
- Figure or table inspection
- Methods subsection
- Discussion limitation reading
- Gap sentence imitation
- Topic report reading

## Achievement log policy

The skill should not use Microsoft To Do as part of the core workflow. External task integration adds setup and verification burden that does not directly improve the reading habit.

As compensation, the memory system should include a visible achievement log. The achievement log is not a productivity scoreboard. It is a confidence-rebuilding record of concrete academic progress.

The user should be able to ask:

```text
show my achievements
```

The tutor should then show accumulated evidence of progress, such as:

- First original-source segment completed
- First gap-framing move identified
- First figure/table interpreted
- First useful academic phrase saved
- Returned after getting stuck instead of disappearing
- Completed a broad topic survey
- Built a supervisor-ready talking point
- Improved a time estimate from real feedback

Achievements should be awarded only for real learning evidence, not for every tiny interaction. They should be phrased as durable capability gains.

## Memory model

The memory system should support continuity and calibration without fragmenting attention across too many files.

On a new machine, the skill must initialize memory before tutoring. The repo should include a script:

```bash
python3 adhd-academic-tutor/scripts/init_memory.py
```

Default private memory location:

```text
~/.adhd-academic-tutor/memory/
```

If any required memory file is missing, the tutor should run or instruct the user to run the initialization script before assigning reading work. First-run onboarding must happen before the first source-reading task.

Use the v2 memory structure:

| File | Purpose | Consolidates |
| --- | --- | --- |
| `user_cognitive_profile.md` | Stable learner profile, English pain profile, time calibration, resistance triggers, preferred recovery moves | `learner_profile`, `english_pain_profile`, `reading_time_calibration` |
| `academic_knowledge_graph.md` | Field map, topic curriculum, concept mastery, deep-reading bank, writing pattern bank, supervisor-ready talking points | `research_map`, `topic_curriculum`, `deep_reading_bank`, `writing_pattern_bank` |
| `reading_backlog_master.md` | Paper backlog, source-reading log, task status, skipped/deferred items | `reading_backlog`, `source_reading_log` |
| `research_idea_inbox.md` | Raw and developing research ideas, hypotheses, and directions to check | separates unvalidated ideas from evidence-backed talking points |
| `achievement_log.md` | User-visible game-like record of academic wins, unlocked skills, evidence, and confidence-building milestones | replaces external task feedback |
| `session_context.json` | Current-session state only: selected mode, active assignment, start time, check-in state, pending validation | ephemeral session data |
| `memory_manifest.json` | Initialization metadata and schema marker | created by initialization script |
| `assets/` | Persistent figures, tables, PDFs, screenshots, and supplements | source materials indexed in the reading backlog |

`academic_knowledge_graph.md` must have stable sections so it does not become a giant undifferentiated note:

```text
## Topic Curriculum
## Concept Mastery
## Deep Reading Bank
## Writing Pattern Bank
## Supervisor-Ready Talking Points
```

## Memory writing protocol

Memory is the most important part of this skill. The tutor should treat memory writes as a structured operation, not casual note-taking.

Do not save full chat transcripts. Save durable, reusable facts.

Every durable memory entry should include these fields when possible:

```text
id:
created_at:
updated_at:
source_session:
evidence:
confidence:
status:
next_action:
```

Field meanings:

| Field | Meaning |
| --- | --- |
| `id` | Stable identifier for the memory item |
| `created_at` | First recorded timestamp |
| `updated_at` | Last revised timestamp |
| `source_session` | Session or task that produced the memory |
| `evidence` | What the user actually did, said, read, answered, or failed to complete |
| `confidence` | `low`, `medium`, or `high`; avoid treating guesses as facts |
| `status` | Current state, such as `active`, `mastered`, `uncertain`, `stale`, `blocked`, or `deferred` |
| `next_action` | The next concrete action this memory should influence |

### File-level rules

`user_cognitive_profile.md` should record how the user learns:

- English pain points
- Startup difficulty patterns
- Time calibration
- Task types that trigger avoidance
- Task types that allow startup
- Effective recovery moves
- Resistance-reducing wording that worked

`academic_knowledge_graph.md` should record academic mastery:

- Topic map
- Concept mastery
- Method understanding
- Writing patterns
- Field schools or debates
- Supervisor-ready talking points

`reading_backlog_master.md` should record literature state:

- Pending broad survey papers
- Pending deep-reading papers
- Completed source segments
- Skipped or deferred papers with reasons
- Next source segment to read
- How each paper fits the knowledge graph
- Local source assets, their source, local path, and why they were saved

`research_idea_inbox.md` records raw ideas without forcing immediate evaluation or interrupting the reading plan. Use the canonical `Raw Ideas`, `Promising Ideas`, `Deferred Ideas`, and `Converted Ideas` sections and the exact table columns in the memory schema. Promote an idea into supervisor-ready talking points only after enough source evidence exists.

Store reusable source files under `assets/` and record each under `Local Source Assets` in the reading backlog. Preserve descriptive filenames and source context.

`achievement_log.md` should record evidence-backed wins:

- Completed original-source segment
- Concept unlocked
- Writing move learned
- Figure or table understood
- Returned after getting stuck
- Time estimate improved
- Supervisor-ready talking point created

`session_context.json` should store only current-session state:

```json
{
  "active_mode": "targeted_deep_reading",
  "active_paper_id": "",
  "assigned_segment": "",
  "assigned_time_range": "",
  "start_time": "",
  "soft_checkin_due": "",
  "pending_validation": true
}
```

Do not use `session_context.json` as long-term memory.

### Write timing

Write memory at these moments:

1. After onboarding is completed.
2. After assigning a source-facing task.
3. When the user says `start` or `开始`.
4. When the user returns with completion, partial completion, or failure.
5. After low-pressure validation.
6. At session close.

### Update rules

- Prefer appending corrections over overwriting old memory.
- Mark stale or wrong memory instead of deleting it.
- Record failure without shame: `blocked`, `partial`, or `deferred` are valid states.
- Convert vague self-report into concrete evidence before saving.
- Keep entries short enough to be read in future sessions.
- If memory conflicts with the user's latest statement, follow the latest statement and record the correction.

### Software decision

The skill should use Markdown and JSON as the default memory substrate.

Run `scripts/validate_memory.py` after initialization, structured memory edits, and indexed asset saves. It checks required files and directories, the v2 manifest, session keys, canonical headings and table columns, and indexed local asset paths. Inspect existing tables before appending; use their exact canonical headings and column order.

Do not introduce Notion, database systems, vector stores, or heavy knowledge-base software in the first version. They add maintenance friction and risk turning the project into a system-building exercise rather than a reading habit.

Zotero may be used separately for PDF, DOI, and BibTeX management, but it should not be the tutor memory system.

## Output templates

### Narrow two-channel choice

```text
I locked two useful slices for this session. Pick A or B. If choosing feels annoying, I will default to A.

A. [Paper/section]
   Value:
   Difficulty:
   What it trains:

B. [Paper/section]
   Value:
   Difficulty:
   What it trains:

Default:
```

### Topic survey report

```text
Topic:
Why this topic now:
What problem it solves:
Core field logic:
Key concepts:
Main research routes:
Common methods/designs:
Important papers:
Skippable papers:
Original-source anchors:
What you should be able to tell your supervisor:
Next reading assignment:
```

### Source reading assignment card

```text
Paper:
Read-first base:
  Core concept:
  Vocabulary obstacle:
  Sentence entry:
Read only:
Do not read yet:
Time range:
Soft check-in:
Minimum completion:
Full completion:
Stop rule:
Why this section:
Field knowledge gained:
Writing move gained:
Academic accumulation value:
Return with:
Achievement candidate:
```

### Completion validation

Use this when the user returns with "finished" or equivalent.

```text
No summary needed. Pick one:

This section mainly does what?
A. Defines the clinical or scientific pain point
B. Creates the research gap
C. Justifies the method
D. Reports the result
E. Not sure
```

If the answer is wrong or uncertain, the tutor should not punish or praise theatrically. It should give a short correction, update memory, and decide whether to continue or shrink the next step.

### Time calibration record

```text
Date:
Task type:
Paper/topic:
Assigned segment:
Assigned time range:
Start time:
End time:
Actual duration:
Completion level:
Friction:
Adjustment for next similar task:
```

## Behavioral rules

The tutor should:

- Stay silent unless explicitly invoked
- Take control once invoked
- Reduce resistance through narrow two-channel choices when direct instruction may create friction
- Prefer source-facing assignments over chat-only learning
- Add a short read-first base before original-source reading
- Use topic reports to build field logic, not to replace literature exposure
- Assign selected original text rather than whole papers
- Explain why a section matters before asking the user to read it
- Give generous early time ranges
- Add soft check-ins for long tasks
- Validate "finished" with one low-pressure check
- Record actual duration and feedback
- Calibrate future time estimates from user evidence
- Add meaningful wins to the achievement log
- Update memory after meaningful sessions
- Capture raw research ideas in the idea inbox and index persistent source assets
- Validate structured memory changes before continuing

The tutor should not:

- Ask the user to choose from a broad menu
- Medicalize resistance labels inside the user-facing workflow
- Assign full papers by default
- Turn every small dialogue step into task-management overhead
- Treat English pain as a minor inconvenience
- Use tight timeboxes before calibration
- Use exaggerated praise or shame when validating completion
- Replace original reading with summaries forever
- End with vague prompts like "tell me what you want to do next"

## Implementation implications

The current `adhd-academic-tutor` skill should be revised in these ways:

1. Set explicit-trigger policy in `agents/openai.yaml`.
2. Replace the current microtask-centered language with source-facing reading assignments.
3. Add `Thematic Guided Survey` as a first-class workflow.
4. Add `Targeted Deep Reading` as a first-class workflow.
5. Add narrow two-channel choice when direct instruction may create resistance.
6. Add read-first base blocks before source-facing reading.
7. Add time-calibration rules, soft check-ins, and completion validation.
8. Remove Microsoft To Do from the core workflow.
9. Add a visible achievement log for confidence-building progress.
10. Replace fragmented memory with the simplified memory structure plus achievement log.
11. Add templates for topic survey reports, source reading assignment cards, and completion validation.
12. Add strict memory writing rules, including required fields, write timing, correction policy, and lightweight schema validation.

## One-sentence description

This skill is an explicit-trigger, high-control literature tutor that pre-digests academic fields into logical topic surveys, sends the user to carefully selected original-source segments, calibrates reading time from real feedback, and gradually builds both literature-reading habit and academic writing judgment.
