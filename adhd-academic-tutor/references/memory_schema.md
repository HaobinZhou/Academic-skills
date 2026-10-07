# Memory Schema

Default memory root resolution:

1. `ADHD_TUTOR_MEMORY_DIR` environment variable
2. `~/.adhd-academic-tutor/memory`
3. workspace-local `state/adhd-academic-tutor/` only if the user explicitly asks for project-local memory

On a new machine, initialize memory with:

```bash
python3 adhd-academic-tutor/scripts/init_memory.py
```

Validate memory structure with:

```bash
python3 adhd-academic-tutor/scripts/validate_memory.py
```

To choose a custom private memory location:

```bash
python3 adhd-academic-tutor/scripts/init_memory.py --memory-dir /path/to/private/memory
```

Do not commit memory files. They contain personal learning context.

## Memory Items

Use this core memory structure:

| File | Purpose |
| --- | --- |
| `user_cognitive_profile.md` | Stable learner profile, English pain profile, time calibration, resistance triggers, preferred recovery moves |
| `academic_knowledge_graph.md` | Field map, topic curriculum, concept mastery, deep-reading bank, writing pattern bank, supervisor-ready talking points |
| `reading_backlog_master.md` | Paper backlog, source-reading log, task status, skipped/deferred items |
| `research_idea_inbox.md` | Raw and developing research ideas, hypotheses, thesis directions, method angles, and supervisor-discussion thoughts |
| `achievement_log.md` | User-visible record of evidence-backed academic wins, unlocked skills, and confidence-building milestones |
| `session_context.json` | Current-session state only |
| `memory_manifest.json` | Initialization metadata and schema marker |
| `assets/` | Persistent local source assets such as figures, tables, screenshots, PDFs, and supplements |

If any required file is missing, run `scripts/init_memory.py` before continuing. If the script cannot be run, create the required files manually from this reference.

## Durable Entry Fields

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

Allowed `confidence` values:

- `low`
- `medium`
- `high`

Useful `status` values:

- `active`
- `mastered`
- `uncertain`
- `stale`
- `blocked`
- `deferred`

## Canonical Structured Sections

The following headings and table headers are canonical. Before appending to one of these sections, inspect the file and match the exact heading and column order. If the expected section is missing, restore the canonical section from this schema before writing the entry.

### `achievement_log.md`

Append achievements only under:

```text
## Unlocked Achievements

| id | created_at | achievement | evidence | why_it_matters | related_skill | next_unlock |
| --- | --- | --- | --- | --- | --- | --- |
```

Do not create `## Achievements`, `## Achievement Log`, or other near-synonym sections for achievement entries.

### `reading_backlog_master.md`

Use these exact structured sections when present:

```text
## Pending Broad Survey Papers
| id | paper | topic | reason | status | next_segment |

## Pending Deep-Reading Papers
| id | paper | segment | reason | time_range | status |

## Completed Source Segments
| id | paper | segment | completed_at | evidence | achievement_id |

## Local Source Assets
| id | created_at | source | local_path | why_saved |

## Skipped or Deferred
| id | paper | reason | revisit_condition |

## Source Reading Log
| id | created_at | paper | segment | assigned_range | actual_duration | completion | friction | next_action |
```

### `research_idea_inbox.md`

Use these exact structured sections:

```text
## Raw Ideas
| id | created_at | idea | why_it_matters | evidence_so_far | status | next_check |

## Promising Ideas
| id | created_at | idea | why_it_matters | evidence_so_far | status | next_check |

## Deferred Ideas
| id | created_at | idea | why_it_matters | evidence_so_far | status | next_check |

## Converted Ideas
| id | created_at | converted_to | evidence | status |
```

### `academic_knowledge_graph.md`

Use these exact top-level sections:

```text
## Topic Curriculum
## Concept Mastery
## Deep Reading Bank
## Writing Pattern Bank
## Supervisor-Ready Talking Points
```

Do not store raw ideas here. Store raw ideas in `research_idea_inbox.md`; convert them into this file only after source evidence exists.

## File-Level Rules

### user_cognitive_profile.md

Record how the user learns:

- onboarding status
- field, project, degree stage, current deliverable
- English pain points
- startup difficulty patterns
- time calibration
- task types that trigger avoidance
- task types that allow startup
- effective recovery moves
- resistance-reducing wording that worked

### academic_knowledge_graph.md

Use stable sections:

```text
## Topic Curriculum
## Concept Mastery
## Deep Reading Bank
## Writing Pattern Bank
## Supervisor-Ready Talking Points
```

Do not let this file become an undifferentiated note dump.

### reading_backlog_master.md

Record literature state:

- pending broad survey papers
- pending deep-reading papers
- completed source segments
- skipped or deferred papers with reasons
- next source segment to read
- how each paper fits the knowledge graph
- local source assets saved under `assets/`, including source, local path, and why saved

### research_idea_inbox.md

Record ideas before they are fully validated:

- sudden research ideas
- possible thesis directions
- method angles
- supervisor-discussion ideas
- hypotheses that need literature support
- questions to check later

Use stable sections:

```text
## Raw Ideas
## Promising Ideas
## Deferred Ideas
## Converted Ideas
```

Each idea should include:

```text
id:
created_at:
idea:
why_it_matters:
evidence_so_far:
status:
next_check:
```

Useful `status` values:

- `raw`
- `promising`
- `needs_evidence`
- `deferred`
- `converted`

Do not put unvalidated ideas directly into `Supervisor-Ready Talking Points`. Convert them only after enough source evidence exists.

### achievement_log.md

Record only evidence-backed wins:

- completed original-source segment
- concept unlocked
- writing move learned
- figure or table understood
- returned after getting stuck
- time estimate improved
- supervisor-ready talking point created

Avoid empty praise.

### session_context.json

Use only for current-session state:

```json
{
  "active_mode": "",
  "active_paper_id": "",
  "assigned_segment": "",
  "assigned_time_range": "",
  "start_time": "",
  "soft_checkin_due": "",
  "pending_validation": false
}
```

Do not use this file as long-term memory.

### assets/

Store persistent source-facing files here when they should be reused across sessions:

- paper PDFs
- figures and tables
- screenshots
- supplementary files
- downloaded reports or guidelines

Prefer descriptive filenames:

```text
ADA_EASD_2022_Table1_medications_for_lowering_glucose.jpg
Dennis_2025_five_drug_model.pdf
```

Record saved assets in `reading_backlog_master.md` under `Local Source Assets`. Do not rely on filenames alone to remember why a file matters.

## Write Timing

Write memory at these moments:

1. After onboarding is completed.
2. After assigning a source-facing task.
3. When the user says `start` or `开始`.
4. When the user returns with completion, partial completion, or failure.
5. After low-pressure validation.
6. At session close.

## First-Run Onboarding Write

After the first onboarding, update `user_cognitive_profile.md`:

- Change `Status: not onboarded` to `Status: onboarded`.
- Fill field, project, degree stage, current deliverable, supervisor expectations, and deadline.
- Record English pain points and startup barriers.
- Record the first starter task type and why it was chosen.

Then assign a starter source-facing task. Do not assign a task before onboarding if the profile is missing or incomplete.

## Update Rules

- Save durable, reusable facts; do not save full chat transcripts.
- Prefer appending corrections over overwriting old memory.
- Mark stale or wrong memory instead of deleting it.
- Record failure without shame: `blocked`, `partial`, and `deferred` are valid states.
- Convert vague self-report into concrete evidence before saving.
- Keep entries short enough to be read in future sessions.
- If memory conflicts with the user's latest statement, follow the latest statement and record the correction.

## Software Policy

Use Markdown and JSON as the default memory substrate.

Recommended lightweight validation:

- Run `scripts/validate_memory.py` after initialization, schema changes, structured table edits, and indexed asset saves.
- The validator checks required files and directories, manifest schema, `session_context.json` keys, canonical Markdown headings/table headers, and indexed local asset paths.
- Keep validation lightweight. Do not introduce Notion, database systems, vector stores, or heavy knowledge-base software in the first version.

Zotero may be used separately for PDF, DOI, and BibTeX management, but it is not the tutor memory system.
