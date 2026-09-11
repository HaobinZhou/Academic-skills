---
name: oppen-project-steward
description: Maintain durable, non-scientific AI-assisted projects with canonical ownership, Git-owned history, current Deliverables, recoverable machine Audit evidence, Human Attention escalation, consequential Decision Memory, deterministic registries, and path-scoped dirty-work protection. Use when initializing or adopting an existing project, upgrading a legacy Steward layout, governing, recovering Audit staging, indexing, escalating material unresolved concerns, recording non-reconstructable decision context, or validating long-lived software, AI application, quantitative engineering, infrastructure, or mixed code/document projects. Also use when asked to check for or install updates to this skill from its GitHub source.
---

# Oppen Project Steward

Keep one understandable current project truth. Keep artifact history in Git. Use AI judgment for meaning and the bundled helper for mechanics.

## Skill Updates

When the user invokes this skill and says “check the update”, “check for updates”, “检查更新”, or “更新技能”, check its GitHub source and install an available update in the same task. This request authorizes the available skill update; do not ask again merely because a newer commit exists. If the user explicitly says “check only”, “只检查，不更新”, or equivalent, only report availability.

Run the bundled updater with the active Python 3 interpreter and the **absolute path of this installed skill**:

```text
python ABSOLUTE_SKILL_PATH/scripts/update_skill.py --apply
python ABSOLUTE_SKILL_PATH/scripts/update_skill.py --check
```

- Use `--apply` for the default check-and-update request and `--check` for an explicit read-only check. On Windows, `py -3` is also suitable. Python and Git must be available.
- The source is [HaobinZhou/academic-skills](https://github.com/HaobinZhou/academic-skills), directory `oppen-project-steward`. The updater resolves GitHub's current default branch and pins its commit; it never guesses a version from governance markers such as v3 or 4.3.
- This supports the repository's documented Git clone installation, including symlinked skills. It resolves this skill's location independently of the working project. A shared checkout updates **all upstream changed paths in academic-skills**, including other skills; report that scope. If the user restricts changes to only one skill, do not use the shared-checkout updater.
- Checks may fetch Git objects and metadata but do not change installed files or the local branch. Apply uses only a fast-forward, preserves unrelated dirty work, and blocks overlapping tracked, staged, untracked, or ignored files. Never reset, force, stash, rebase, or discard local changes to obtain an update. For a copied installation, source mismatch, divergence, detached HEAD, network failure, or conflict, report the concrete blocker and preserve the installation; do not claim it is current.
- Report `UP_TO_DATE`, `UPDATE_AVAILABLE`, `UPDATED`, `LOCAL_AHEAD`, or `UPDATE_BLOCKED`, the before/upstream/after commits when available, and changed paths or conflicts. `LOCAL_AHEAD` means local commits are ahead of upstream and no downgrade was performed. After `UPDATED`, reread the installed `SKILL.md` before using its new instructions.
- Skill maintenance uses this workflow directly. It does not require adopting, indexing, migrating, or modifying the user's working project. Project layout upgrades remain separate authorized work under the normal workflow below.
- After `UPDATED`, if OppenSteward-MCP is available, follow the skill-guide refresh check in [MCP publication and refresh](references/mcp-publication.md).

## Core Workflow

1. Resolve and classify the target with `validate` before managed work. For `MANAGED_READY`, read `.oppen-project-steward/registry.md`, relevant Canonical sources, implementation, tests, current Audit, and relevant Deliverables. Navigate active Attention and Decision Memory through their generated indices; do not load every Memory entry. Read relevant MCP discussion documents as needed, using `Discussion/index.md` within the namespace when available.
2. Treat an ordinary unmanaged project as `ADOPTION_REQUIRED`, not damaged. Use `adopt --check`, make only the necessary semantic mappings, then use `adopt --apply`. Stop on `ADOPTION_BLOCKED`; do not invent another namespace.
3. Confirm the project is Git-backed when applicable; the helper never initializes, commits, or rewrites Git history. Use `init` only for a genuinely new project. Use `upgrade-layout` only for a proven `LEGACY_STEWARD_LAYOUT`.
4. Search the canonical registry before adding documentation. Update the registered owner in place instead of creating a parallel version.
5. For a semantic change, update the canonical definition, implementation, and linked verification together, then execute the verification.
6. Retain direct human outputs in Deliverables. Route machine evidence, traces, provenance, diagnostics, and acceptance checks to Audit.
7. Create a High-Risk Contract Audit only when a hidden error could materially alter core behavior, results, safety-relevant contracts, or downstream interpretation.
8. Evaluate Attention only for a material unresolved concern outside current authorization. Raising it does not grant authority to resolve it.
9. Evaluate Memory only at a consequential decision boundary. Never create it merely because a task, session, code change, or test run ended.
10. Do not widen scope when inspection reveals an adjacent issue. Complete the authorized work, then use Attention only if the separate trigger passes.
11. Run relevant tests and registered verification, then run `index` and `validate`. Do not claim completion while validation fails.
12. After successful `init`, check OppenSteward-MCP availability and whether this exact project root is published. If available and unpublished, ask whether the user wants to publish it; register it only after consent. After changes to an already-published project, refresh and verify its MCP view. Follow [MCP publication and refresh](references/mcp-publication.md); local validation alone does not prove publication.

## Five Information Systems

- Canonical states what is true now.
- Git preserves historical artifact changes.
- Audit holds machine verification for the current implementation.
- Human Attention exposes material unresolved concerns needing awareness or decision.
- Decision Memory records why a consequential decision happened.

Keep each fact in its owning system. Deliverables are registered current outputs for direct human use, not another history or verification system.

## Runtime State And Managed Writes

- Treat valid current Steward state as `MANAGED_READY`.
- Treat an ordinary existing project with no Steward state as `ADOPTION_REQUIRED`; use `ADOPTION_BLOCKED` only for a concrete adoption conflict.
- Treat deterministic operational blockers as `BLOCKED_RECOVERABLE`; report the blocker, affected paths, and recovery action. Recoverable residue is not governance damage.
- Reserve `DAMAGED` for authority or metadata that cannot be interpreted without semantic or manual repair.
- Use `audit recover` only for clearly failed or incomplete staging. Let the helper verify the external recovery copy and manifest before removing the source; never move `current/` or create an in-project archive.
- Let every mutation use its Managed Operation Write Set. Permit unrelated tracked or untracked Git work and leave it byte-for-byte untouched.
- Stage transaction content and rollback only for the declared Managed Operation Write Set. Never clone, recursively copy, hardlink, reflink, or otherwise materialize the full project. Read unchanged project content in place through a read-only candidate overlay when candidate validation needs it.
- Support cross-filesystem transactions without widening their scope. Treat `EXDEV` as permission to copy only an individual managed file, never the project tree.
- Stop with `MANAGED_WRITESET_CONFLICT` when dirty user-owned paths overlap operation-owned paths. Reconcile only those paths; never stash the whole repository automatically.

## Steward-Owned State

`.oppen-project-steward/**` is Steward-owned managed state except for MCP-owned `Discussion/**`. Steward continuity is determined by the helper-managed `.oppen-project-steward/.managed-state.json` baseline, not by comparison with Git HEAD.

- Continue normal Steward operations when managed files match the last successful baseline, whether Git sees them as committed, staged, modified, or untracked. A Git commit is never required merely to continue governance.
- Stop with `MANAGED_STATE_CONFLICT` when `registry.md`, `Memory/**`, `Attention/**`, or `Audit/Contracts/**` differs from the baseline. Inspect and reconcile only the reported paths; never reset them from Git or overwrite unexplained drift.
- Keep user-owned project paths under Managed Operation Write Set Git conflict protection. Referencing a dirty user-owned Canonical owner is allowed; writing a dirty user-owned path is not.
- Exclude `.managed-state.json`, `Audit/Runs/**`, `Discussion/**` (including its MCP-maintained index), and user project content from the baseline. Let Audit retain its own evidence-integrity checks.
- For a valid pre-4.3 managed project missing only the baseline, run `managed-state TARGET --check`, then `managed-state TARGET --bootstrap`. Bootstrap creates generation 1 without re-adoption, Git mutation, or a required commit. Never bootstrap a damaged or otherwise blocked namespace.

## Project Roles

- Steward owns `registry.md`, `Memory/`, `Attention/`, and `Audit/` with fixed topology inside `.oppen-project-steward/`. The namespace also permits optional MCP-owned `Discussion/`.
- Source, Data, and Deliverables are optional logical roles mapped only to useful existing directories.
- Do not create standard role directories or reject a project because a role is absent.
- Treat root `project.md`, `Memory/`, `Attention/`, and `Audit/` as user-owned unless the legacy upgrade preflight proves old Steward ownership.

Never create a standard directory beside an existing path already serving the same role. Stop on ambiguous supplied mappings.

## MCP Discussion Documents

`.oppen-project-steward/Discussion/` holds freely written discussion documents from any AI through MCP. MCP owns file creation, naming, updates, organization, and compliance. The skill and helper accept the directory and let local Codex read relevant documents; they do not manage its files or index.

- Use a flat directory with `index.md` and names such as `D-000001__项目部署方式的讨论.md` or `D-000002__缺失值处理与敏感性分析.md`.
- MCP assigns six-digit sequence numbers in creation order, starting at `000001`. Keep numbers stable; never renumber or reuse deleted numbers.
- Choose a short, specific topic in the discussion's language. Keep dates, AI names, and processing status out of filenames; place them in the index or document when useful.
- Continue updating the same document at the same path. Create another document for an independent discussion, without `_new`, `_final`, or version suffixes for revisions. If a rename is needed, MCP preserves the ID and updates index links.
- MCP maintains `index.md` with document links, brief descriptions, and last-updated times. Its presentation and document bodies have no helper-enforced schema, required headings, or lifecycle fields.
- Accept any discussion content, including ideas, drafts, code, quotations, unresolved questions, and competing approaches. Do not apply Canonical registration, frozen-content, parallel-copy, or Deliverable requirements to these materials.
- Read as needed. Reading does not require a reply, implementation, closure, archiving, Attention, or Memory. Subsequent authorized project work follows the normal governance rules.
- An absent or empty directory, missing or stale index, or MCP naming issue does not block project validation. MCP may create the directory on first use. Helper initialization, indexing, validation, and migration leave existing discussion files untouched; do not repair or rename them as routine governance work.

## Existing Projects

An existing project without Steward metadata is not damaged. If `.oppen-project-steward/` is absent and the target is ordinary, classify it as `ADOPTION_REQUIRED`.

Run `adopt TARGET --check` read-only, then `adopt TARGET --apply --input TEMP_JSON`. Leave root `project.md`, directories, documentation, dirty work, and naming conventions unchanged. Register useful existing roles and authoritative documents by reference; all payload sections may be empty. Adoption stages only `.oppen-project-steward/**`, never materializes the full project, and creates no Attention or Memory merely for adoption.

If validation reports `LEGACY_STEWARD_LAYOUT`, run `upgrade-layout TARGET --check` and then `upgrade-layout TARGET --apply`. Move only mechanically proven old Steward state; never infer ownership from root filenames alone.

## Canonical Ownership

- Register each important semantic definition or cross-component contract under one stable topic key.
- Use one stable file or one stable Markdown section per topic.
- Store one `draft`, `partially-frozen`, or `frozen` status in the registry. Existing files may be registered non-invasively with `--status`; otherwise infer exactly one valid `Status:` field from the owned scope.
- Treat `frozen` as current authority, not immutable history. Revise the same owner when the authority changes.
- Use `canonical --replace` only for an explicit ownership move after resolving the former owner.
- Stop on conflicting owners. Never create `_old`, `_new`, `_updated`, `_final`, `_backup`, dated, or version-number copies. Git stores history.

## Deliverables And Audit

- Register every retained Deliverable with a stable ID, path, kind, audience, and producer.
- Replace the same current output path when it changes. Use `deliverable --replace` only for an intentional path move.
- Keep logs, caches, traces, manifests, staging, backups, historical versions, temporary diagnostics, and serialized machine state out of Deliverables.
- Build run evidence in a system temporary directory, validate it, and atomically promote it to `.oppen-project-steward/Audit/Runs/<stage>/current/`.
- On failure, leave the prior `current/` untouched and keep failed staging outside the project.
- Do not retain siblings such as `previous/`, `run_001/`, dated runs, or `staging/` beside `current/`.
- Promote validated external staging with `audit promote`; let the helper perform internal SHA-256/size read-back verification and replace the whole current tree. No user-authored manifest is required.
- If failed staging already blocks a stage, run `audit recover`, inspect the reported external manifest, then rerun the blocked operation or validation.

## High-Risk Contract Audit

Ask: could a hidden error materially alter core behavior, results, a safety-relevant contract, or downstream interpretation?

If yes, use `contract-audit` to create or locate one stable audit. Complete its four required sections through a temporary JSON payload and `contract-audit --input`; the helper refreshes the reviewed source hash and advances the managed-state baseline transactionally. Reuse the same audit for later changes. If no, normal executable tests are sufficient.

## Human Attention

- Raise Attention only when a concrete, material issue remains unresolved, ordinary task work does not cover it, and resolution needs human judgment, additional authorization, or substantial scope expansion.
- Do not use Attention for upgrades, cleanup, routine debt, naming preferences, speculative ideas, or generic improvement suggestions.
- Keep an item normally non-blocking. If it undermines the requested deliverable's correctness or trustworthiness, do not claim the task complete merely because an item was raised.
- Check `.oppen-project-steward/Attention/index.md` for an equivalent active issue before raising another.
- Resolve an item only after the underlying human decision or authorized work is complete. Resolution deletes the active file; Git preserves history.
- Yes: a critical downstream component violates an intended contract, but correcting its architecture is outside current authorization. No: a package is outdated or naming is slightly inconsistent.
- Noteworthy does not mean Attention. Known pending work is not Attention when the current authorized workflow already defines and permits its resolution.
- Attention is not a TODO system. Exclude planned stages, expected temporary staleness, roadmap work, normal debt, and generic improvements unless the full material, unresolved, out-of-scope, evidence-backed trigger requires a new human decision.

## Decision Memory

- Apply the counterfactual test: without an explicit record, could a future agent with the current project and complete Git history fail to explain a consequential decision or repeat a rejected direction?
- Create one Memory entry only when the answer is yes and the decision is consequential. Do not create one per task, conversation, change, commit, rerun, verification, or unresolved concern.
- Use `supersedes` when a later decision changes direction. Use `invalidates` when later evidence shows a key fact or assumption was wrong. Let the helper update prior status and reverse links.
- Allow zero related canonical topics. Memory records causal history; Canonical records current belief, Audit records verification, and Attention records unresolved significance.
- Never store chain of thought, scratchpads, deliberation transcripts, unresolved-risk fields, or verification logs in Attention or Memory.
- Yes: a real failure or user experience causes an important architectural direction to be abandoned and replaced. No: a routine bug fix passes tests and Git fully explains the change.
- Technical difficulty alone does not justify Decision Memory. Exclude subtle compatibility, parser, optimization, refactor, and isolated defect work when code, tests, and Git explain it.
- Allow consequential architecture, execution, storage, concurrency, reliability, performance policy, operational safety, dependency, deployment, or state-management decisions when the counterfactual test passes.
- An incident alone is Audit, logs, or Git as appropriate. Create Memory only when the incident causes a durable consequential decision whose causal context would otherwise be lost.

## Helper Commands

Run `scripts/oppen_project_steward.py` with its absolute skill path:

```text
init TARGET
adopt TARGET --check
adopt TARGET --apply --input TEMP_JSON
upgrade-layout TARGET --check
upgrade-layout TARGET --apply
managed-state TARGET --check
managed-state TARGET --bootstrap
canonical TARGET --topic KEY --path PATH [--section HEADING] [--status STATUS] --verification TEST_PATH [--replace]
deliverable TARGET --id KEY --path PATH --kind KIND --audience AUDIENCE --producer PATH [--replace]
contract-audit TARGET --topic KEY --source PATH --risk-reason TEXT
contract-audit TARGET --topic KEY --input TEMP_JSON
audit promote TARGET --stage KEY --input STAGING_DIR
audit recover TARGET --stage KEY
attention raise TARGET --input TEMP_JSON
attention resolve TARGET --id A-XXXX
memory add TARGET --input TEMP_JSON
index TARGET
validate TARGET
```

Invoke the helper through the active Python 3 interpreter. On Windows, use `py -3 ABSOLUTE_SKILL_PATH\scripts\oppen_project_steward.py ...` or `python ...`; do not rely on the POSIX shebang. The helper preserves deterministic LF-managed text and uses the platform file-lock backend automatically.

Before using `adopt`, `contract-audit --input`, `attention`, or `memory`, read [references/payload-schemas.md](references/payload-schemas.md). Create the JSON outside the project; the helper validates and removes it after a successful write.

Expect unchanged indexing commands to be idempotent. Do not use `init` as a migration command. Do not edit generated registries, indices, IDs, paths, statuses, or relationship reverse links manually.

## Completion Gate

1. Run relevant implementation tests and every verification linked to changed canonical topics.
2. Confirm one current owner per topic and no parallel old/versioned copies.
3. If a Deliverables role is registered, confirm it contains only registered current human outputs.
4. Confirm every `.oppen-project-steward/Audit/Runs/` stage contains only one `current/` tree.
5. Complete any High-Risk Contract Audit that was actually triggered.
6. Raise any qualifying non-blocking Attention without expanding scope. Treat blocking Attention as a completion blocker.
7. Add Decision Memory only for qualifying consequential decisions; never automate it from task completion.
8. Recover deterministic operational residue, run `index`, then require `validate` to report `MANAGED_READY` and exit zero.
9. Report current deliverables, verification performed, active Attention, and unresolved blockers.
