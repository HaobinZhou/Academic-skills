# ADHD Academic Tutor

ADHD Academic Tutor is a skill package for guided academic literature reading and writing practice. It is designed for learners who get stuck on English-language papers, lack field structure, and need a tutor-like workflow that plans sessions, assigns selected original-source reading, calibrates reading time, and maintains local memory for continuity.

## What It Does

- Runs guided thematic literature surveys.
- Assigns targeted deep-reading segments instead of whole papers by default.
- Adds a short Read-First Base before source reading.
- Uses generous early time ranges and calibrates from real feedback.
- Validates completion with low-pressure checks.
- Records evidence-backed achievements for confidence rebuilding.
- Maintains local Markdown/JSON memory outside the skill folder.
- Captures research ideas without interrupting the active reading task.
- Saves persistent source materials under `assets/` and indexes their source and purpose.
- Validates memory files, structured tables, session state, and saved asset paths.

The full [product and behavior description](./adhd-academic-tutor-full-description.md) explains the tutor's learning workflow. [SKILL.md](./SKILL.md) and the [memory schema](./references/memory_schema.md) define its current execution and memory contracts.

## First-Time Memory Setup

On each new machine, create the private local memory directory before first use:

```bash
python3 scripts/init_memory.py
```

By default this creates:

```text
~/.adhd-academic-tutor/memory/
```

To use a custom private memory location:

```bash
python3 scripts/init_memory.py --memory-dir /path/to/private/memory
```

Validate the same memory directory after initialization:

```bash
python3 scripts/validate_memory.py --memory-dir /path/to/private/memory
```

For the default directory, omit `--memory-dir`. Both scripts also accept `ADHD_TUTOR_MEMORY_DIR`. The initializer preserves existing files by default. For an existing v1 memory directory, retain the learner's entries and bring its manifest, session keys, and structured sections into line with the current memory schema before validating; initialization alone does not migrate existing files. `--force` overwrites existing memory and is not a migration command.

The skill will run first-time onboarding if `user_cognitive_profile.md` says `Status: not onboarded`.

## Repository Layout

```text
adhd-academic-tutor/
├── SKILL.md
├── README.md
├── adhd-academic-tutor-full-description.md
├── agents/openai.yaml
├── scripts/
│   ├── init_memory.py
│   └── validate_memory.py
└── references/
    ├── memory_schema.md
    ├── report_templates.md
    └── session_protocols.md
```

## Notes

The skill is designed to preserve source-facing learning. It can reduce friction around English academic papers, but it should not permanently replace reading original paper sections.
