---
name: stepwise-r-project
description: Maintain strict, human-readable scientific R analysis projects with canonical ownership, Results, Audit, Human Attention and Decision Memory. Use for scientific freeze rounds and the temporary Freeze web workbench, or when initializing, migrating, modifying, indexing, validating or reviewing an R analysis workspace. Also use for skill update checks.
---

# Stepwise R Project

Keep one current truth for humans. Keep artifact history in Git. Use AI discretion for scientific meaning, not project mechanics. If a decision does not require project-specific scientific or semantic context, let the helper make it deterministically.

## Skill Updates

When the user invokes this skill and says “check the update”, “check for updates”, “检查更新”, or “更新技能”, check its GitHub source and install an available update in the same task. This request authorizes the available skill update; do not ask again merely because a newer commit exists. If the user explicitly says “check only”, “只检查，不更新”, or equivalent, only report availability.

Run the bundled updater with the active Python 3 interpreter and the **absolute path of this installed skill**:

```text
python ABSOLUTE_SKILL_PATH/scripts/update_skill.py --apply
python ABSOLUTE_SKILL_PATH/scripts/update_skill.py --check
```

- Use `--apply` for the default check-and-update request and `--check` for an explicit read-only check. On Windows, `py -3` is also suitable. Python and Git must be available.
- The source is [HaobinZhou/academic-skills](https://github.com/HaobinZhou/academic-skills), directory `stepwise-r-project`. The updater resolves GitHub's current default branch and pins its commit; it never guesses a version from governance markers such as v3 or 3.1.
- This supports the repository's documented Git clone installation, including symlinked skills. It resolves this skill's location independently of the working project. A shared checkout updates **all upstream changed paths in academic-skills**, including other skills; report that scope. If the user restricts changes to only one skill, do not use the shared-checkout updater.
- Checks may fetch Git objects and metadata but do not change installed files or the local branch. Apply uses only a fast-forward, preserves unrelated dirty work, and blocks overlapping tracked, staged, untracked, or ignored files. Never reset, force, stash, rebase, or discard local changes to obtain an update. For a copied installation, source mismatch, divergence, detached HEAD, network failure, or conflict, report the concrete blocker and preserve the installation; do not claim it is current.
- Report `UP_TO_DATE`, `UPDATE_AVAILABLE`, `UPDATED`, `LOCAL_AHEAD`, or `UPDATE_BLOCKED`, the before/upstream/after commits when available, and changed paths or conflicts. `LOCAL_AHEAD` means local commits are ahead of upstream and no downgrade was performed. After `UPDATED`, reread the installed `SKILL.md` before using its new instructions.
- Skill maintenance uses this workflow directly. It does not require initializing, indexing, or migrating the working R project, and does not rerun analyses. Scientific definitions, R/Data/Results/Audit, and governance migrations remain separate authorized work under the normal workflow below.
- After `UPDATED`, if OppenSteward-MCP is available, follow the skill-guide refresh check in [MCP publication and refresh](references/mcp-publication.md).

## Core Workflow

1. Resolve the target before writing. Inspect `project.md`, relevant canonical sources, R code, Results, Audit, tests, relevant active Attention, and only relevant Decision Memory identified through `Memory/index.md`. Read relevant MCP discussion documents as needed, using `Discussion/index.md` when available.
2. Treat the default budget for new Markdown documents as zero. Search the canonical registry and existing documents first.
3. Classify the project as v3, migration required, migration blocked but recoverable, unmanaged, or damaged. Run `init` only for a new unmanaged project; never use it as migration.
4. Resolve one current authority for every scientific definition and cross-script contract. Stop on conflicting owners or ambiguous directory aliases.
5. Perform the authorized work. For every semantic change, update the canonical definition, R implementation, and contract test together.
6. Route current human deliverables to Results and machine verification to Audit. Publish only after staging validation and atomic promotion.
7. Apply the Decision Memory counterfactual test and Human Attention trigger. Do not create either merely because a task ended.
8. Run relevant R, unit, and registered contract tests; run `index`; then require `validate` to exit zero.
9. After successful `init`, check OppenSteward-MCP availability and whether this exact project root is published. If available and unpublished, ask whether the user wants to publish it; register it only after consent. After changes to an already-published project, refresh and verify its MCP view. Follow [MCP publication and refresh](references/mcp-publication.md); local validation alone does not prove publication.

## Existing v2 Projects

If the target has a recognized v2 marker, do not run `init` or edit v3 managed state directly. A healthy v2 project is `MIGRATION_REQUIRED`, not an invalid v3 project.

1. Run `migrate TARGET --check` read-only. Read project status, recoverable and structural blockers, migration write-set, dirty paths and overlaps, legacy Memory, and Audit staging separately.
2. Treat mechanically clear failed/incomplete Audit staging as `MIGRATION_BLOCKED_RECOVERABLE`, not project damage. Run `audit-recover TARGET --stage STAGE`, confirm the recovery manifest is outside the project, and rerun preflight. Never recover an ambiguous entry automatically.
3. Require only migration write-set paths (`project.md`, Memory, Attention, and reported helper metadata) to be free of conflicting changes. Unrelated dirty R, Results, or document paths may remain and must stay byte-for-byte and Git-state unchanged; never stash the whole project automatically.
4. Review every inventoried legacy Memory as an input container, not a migration unit. Extract each qualifying consequential decision independently and apply the Human Attention test separately; never convert a whole file merely because it exists. Ask the human only when genuine scientific ambiguity prevents classification.
5. Read [managed-systems.md](references/managed-systems.md) and create the complete semantic JSON payload outside the project. Explicitly account for every old file, including files producing no v3 entry.
6. Run `migrate TARGET --apply --input TEMP_JSON`. Let the helper stage, validate, promote, protect unrelated dirty paths, and roll back; never create migration backups or staging inside the project.
7. Require the promoted project to pass v3 `index` and `validate` before continuing normal work. Treat rollback failure as a hard blocker.

Preserve adopted R/Data/Results/Audit aliases, canonical topics and owners, verification paths, statuses, Result IDs and files, Function Audits, Audit `current/`, R code, data, and scientific content. Migration upgrades governance state only; it does not rerun analyses or redesign the research project.

Migration transactions stage only the managed migration write set. Never clone, copy, hardlink, symlink, or otherwise materialize the full scientific project; unchanged R, Data, Results, Audit current evidence, and other content remain in place and are read only as needed for candidate validation. Candidate validation must not require filesystem symlink privileges and must work on Windows, macOS, and Linux. Cross-filesystem migration is supported, and `EXDEV` must never trigger recursive full-project copying.

For already-v3 projects, `migrate --check` and repeated `--apply` perform no migration. For unmanaged, ambiguous, or damaged projects, do not guess; report the required repair.

## Current-State Ownership

- Canonical answers what the current scientific truth or project contract is.
- Git answers what files and code changed.
- Audit holds verification, provenance, diagnostics, and current run state.
- Attention holds unresolved material issues requiring human awareness or decision.
- Decision Memory explains why a consequential design decision happened.

Never route verification to Memory, unresolved risk to Memory, decision rationale to Audit, or current definitions to history records.

## MCP Discussion Documents

`Discussion/` at the project root holds freely written discussion documents from any AI through MCP. MCP owns file creation, naming, updates, organization, and compliance. The skill and helper accept the directory and let local Codex read relevant documents; they do not manage its files or index.

- Use a flat directory with `index.md` and names such as `D-000001__项目部署方式的讨论.md` or `D-000002__缺失值处理与敏感性分析.md`.
- MCP assigns six-digit sequence numbers in creation order, starting at `000001`. Keep numbers stable; never renumber or reuse deleted numbers.
- Choose a short, specific topic in the discussion's language. Keep dates, AI names, and processing status out of filenames; place them in the index or document when useful.
- Continue updating the same document at the same path. Create another document for an independent discussion, without `_new`, `_final`, or version suffixes for revisions. If a rename is needed, MCP preserves the ID and updates index links.
- MCP maintains `index.md` with document links, brief descriptions, and last-updated times. Its presentation and document bodies have no helper-enforced schema, required headings, or lifecycle fields.
- Accept any discussion content, including ideas, drafts, code, quotations, unresolved questions, and competing approaches. Exempt these materials from the new-Markdown budget, Canonical registration, frozen-content, parallel-copy, and Result requirements.
- Read as needed. Reading does not require a reply, implementation, closure, archiving, Attention, or Memory. Subsequent authorized project work follows the normal governance rules.
- An absent or empty directory, missing or stale index, or MCP naming issue does not block project validation. MCP may create the directory on first use. Helper initialization, indexing, validation, and migration leave existing discussion files untouched; do not repair or rename them as routine governance work.

## Freeze Workbench

When the user asks to identify or resolve scientific definitions through the web workbench, read [Freeze workbench](references/freeze-workbench.md). Inspect the actual project before writing a question batch; enumerate **all questions currently identifiable** in one round, with project-specific reasons and source summaries. A round is not a fixed template. After the user responds, read the saved project records, keep unresolved discussion visible, reopen affected questions and add newly discovered questions in another batch. The user invokes Codex manually to continue; saving the page does not start an AI turn.

`Freeze/` contains structured collaboration drafts, not current Canonical authority. User answers, AI positions, messages, and explanatory HTML examples have distinct fields and per-question revisions. Neither a user answer nor an MCP edit declares a definition frozen. Once the relevant scientific choices are confirmed, update the registered Canonical owner, R implementation and contract test together, then run the normal completion gate. The workbench must not write Canonical, Audit, Attention, or Decision Memory on behalf of a webpage or remote AI.

Preserve the author source: local commands record Codex; when Codex uses the MCP Freeze write tools, explicitly pass `actor: "codex"` (ChatGPT uses `"chatgpt"`). Show author names on questions, opinions, discussion messages and examples; leave ambiguous historical authors unassigned.

The web process is temporary. Start it on request with `scripts/freeze_workbench.py start TARGET`; return its port and URL. Its default `127.0.0.1` listener can be forwarded by a proxy on the same host; use `--public-origin https://...` for a remote link. The default mode uses a random login link. When the user explicitly wants a directly shareable page without a login key, use `--no-auth`; anyone who reaches the forwarded address can read and edit the draft Freeze records. Use `--host 0.0.0.0` only for explicit direct network access. `stop TARGET` ends the web process while the project's records remain. Remote ChatGPT participates through the separately configured OppenSteward-MCP Freeze tools, not the temporary web port.

## Canonical Ownership

- Register one stable topic key and exactly one Markdown, QMD, or Rmd owner for each scientific definition, variable meaning, or cross-script/output contract.
- Use only `Status: draft`, `Status: partially-frozen`, or `Status: frozen`. Treat frozen as current authority, not immutable history.
- Keep frozen content free of unresolved scope, stale counts, execution status, and run history.
- Before changing frozen semantics, lower the status; revise definition, implementation, and contract test; run the test; then restore the justified status.
- Treat the registered verification path as a contract to execute, not proof of execution.
- Use `canonical --replace` only for an explicit ownership migration and resolve the former owner in the same task.
- Never create `_old`, `_new`, `_updated`, backup, dated, or versioned copies. Revise the current owner and rely on Git.
- Treat rendered HTML/PDF as a view or registered Result, never a second editable source.

## R Writing Rules

- Keep scripts runnable line by line in RStudio with visible packages, paths, seeds, inputs, outputs, and important intermediate objects.
- Use RStudio section headers for import, cleaning, analysis, validation, and export blocks.
- Keep scientifically important transformations in short pipelines or named steps.
- Use concise Chinese comments to explain why control points and transformations exist.
- Avoid hidden global state, deeply nested expressions, and whole-analysis wrapper functions.
- Preserve stable object names when they carry the same meaning across scripts.

## Results And Audit

- Retain only publication or formal-review tables, figures, cohort flows, codebooks, and reports in Results. Register each with a stable ID, kind, audience, and producing R script.
- Rebuild the same registered path when a deliverable changes. Use `result --replace` only for an intentional contract move.
- Put reusable machine data in Data. Put QA, provenance, manifests, diagnostics, traces, and session state in Audit.
- Build run output in a stage-specific system temporary directory. Validate schema, provenance, acceptance, and read-back there.
- Atomically replace the whole `Audit/Runs/<stage>/current/` tree only after checks pass. Publish Results afterward.
- Leave the prior `current/` untouched on failure. Keep no persistent staging, dated, historical, or backup sibling.

## Human Attention

Raise Attention only when a concern is material, unresolved, outside ordinary authorized work, requires added authorization/scientific judgment/substantial scope, has concrete evidence, and has no equivalent active entry. Raising an issue never grants authority to resolve it.

Noteworthy does not mean Attention. Known pending work is not Attention when no new human decision is required, current Canonical/Audit state already represents it, and an authorized workflow already contains its resolution.

Use `blocking: true` when the issue could materially undermine analysis correctness or interpretation, including eligibility, time zero, exposure, outcomes, joins, missingness, censoring, weighting, models, inference, denominators, provenance, or reported numbers. Do not claim the affected analysis complete while such an issue remains unresolved.

Do not use Attention for formatting, naming, package upgrades, routine refactoring, generic debt, or speculative improvements. Read [managed-systems.md](references/managed-systems.md) before raising or resolving an entry.

## Decision Memory

Create Decision Memory only when a consequential scientific or technical decision passes this test:

> Without an explicit record, could a future AI with the current project and Git history plausibly fail to explain why the decision was made, or unknowingly reintroduce a rejected approach?

Valid events preserve non-obvious causal history such as failed prior designs, diagnostic-driven strategy changes, collaborator/reviewer requirements, data-imposed compromises, or deliberately rejected credible methods. Prefer the pattern: previously X; observed Y; therefore decided Z.

Consequential technical or execution architecture also qualifies when its causal rationale is durable and cannot be reconstructed from current code, Canonical, and Git. For example: the project previously used one execution architecture; real resource behavior made it unsafe at project scale; the project therefore changed storage, concurrency, worker memory, or spill policy; future maintainers should not restore the former design without new evidence.

Do not record routine bugs, package compatibility fixes, ordinary normalization, local optimization, refactors, tests, reruns, commands, file lists, benchmarks, progress/status summaries, unchanged results, information already in Canonical or Git, Audit evidence, or unresolved concerns unless they caused a durable consequential design decision whose rationale would otherwise be lost. A task ending is never a trigger. `related_topics: []` is valid. Read [managed-systems.md](references/managed-systems.md) before adding an entry or declaring relationships.

## Function Policy

- Create functions only for genuine reuse or meaningfully error-prone repeated logic. Give every function Roxygen documentation and executable tests.
- Create a Function Audit when an error could alter eligibility, time windows, joins/deduplication, exposure, outcomes, missingness, censoring, weighting/modeling, aggregation/denominators, or a cross-script/output contract.
- Keep one `Audit/Functions/audit_<function>.Rmd` per high-risk function. Update it in place with its source hash, purpose/risk, contract, edge cases/tests, and known limits.
- Do not retain rendered Function Audit HTML. Treat `UPDATE_REQUIRED` as an instruction to update the returned Rmd.

## Helper Commands

Run `scripts/stepwise_r_project.py` using its absolute skill path:

```text
init TARGET
migrate TARGET --check
migrate TARGET --apply --input TEMP_JSON
audit-recover TARGET --stage STAGE
canonical TARGET --topic KEY --path PATH [--section HEADING] --verification TEST_PATH [--replace]
result TARGET --id KEY --path PATH --kind KIND --audience AUDIENCE --producer PATH [--replace]
attention raise TARGET --input TEMP_JSON
attention resolve TARGET --id A-XXXX
memory add TARGET --input TEMP_JSON
function-audit TARGET --function NAME --source PATH --risk-reason TEXT
index TARGET
validate TARGET
```

Let the helper own IDs, paths, fixed schemas, indices, relationships, lifecycle mechanics, and atomic writes. Never hand-edit managed indices or relationship reverse links.

## Completion Gate

1. Run relevant R/unit tests and every contract test linked to changed canonical topics.
2. Confirm no second current definition, stale frozen content, parallel old/versioned document, unregistered Result, or invalid Audit run tree remains.
3. Complete any triggered Function Audit. Evaluate Decision Memory and Attention explicitly; "none required" is normal.
4. Do not claim an affected analysis complete while a relevant blocking Attention undermines correctness.
5. Require Memory and Attention indices to match entries and no legacy/alternative managed topology to remain.
6. Run `index`, then require `validate` to exit zero.
7. Report current deliverables, verification, migration behavior when applicable, and unresolved blockers.
