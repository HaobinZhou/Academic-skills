# Freeze Workbench

Use this reference when a researcher asks Codex to run a batch-based, revisitable freeze discussion. The editable draft workspace is `Freeze/` at a Stepwise R v3 project root. It is separate from the registered Canonical owner and the optional free-form `Discussion/` documents.

## Workflow

1. Read `project.md`, registered Canonical owners, relevant R contracts, Results/Audit evidence, active Attention and relevant Decision Memory. State what is already frozen, pending and suggested. Identify all presently knowable questions in one batch, rather than serializing the first few or copying a generic checklist.
2. Write a UTF-8 JSON input containing `questions` with `group`, `title`, `why`, `source_summary`, `ai_position` and optional `suggestions`. Import the batch using the bundled CLI. Existing question IDs remain stable; a new import advances the round and only adds genuinely new questions.
3. Start the temporary server and give the user its URL and port. Explicit saves persist answers and comments in project files; `保存本轮` saves the pending answers and comments across questions. Saving gives visible confirmation. Marking a question as disputed keeps it `discussing` through later answer edits; only the user can explicitly confirm the dispute is resolved, after saving any pending inputs for that question. The user may pause, resume, or forward the local listener to access it elsewhere. When the user explicitly requests a keyless, directly shareable page, start with `--no-auth`.
4. When the user manually says the round is filled, run `snapshot`, read the individual question JSON records and relevant source evidence, then address disputes, update AI positions and reopen affected questions using `ai-change`. Import all newly identified questions as one next-round batch. Preserve earlier messages and answers. Repeat until no material question remains unresolved.
5. For agreed scientific definitions, follow the normal Stepwise Canonical, R implementation, test, index, validate, Attention and Decision Memory rules. The workbench records are the review trail and do not replace them.

## Commands

Run the script from the installed skill's absolute path with the active Python 3 interpreter:

```text
python SKILL/scripts/freeze_workbench.py import PROJECT --input batch.json
python SKILL/scripts/freeze_workbench.py start PROJECT
python SKILL/scripts/freeze_workbench.py start PROJECT --port 65080 --no-auth
python SKILL/scripts/freeze_workbench.py start PROJECT --public-origin https://freeze.example.org
python SKILL/scripts/freeze_workbench.py start PROJECT --host 0.0.0.0
python SKILL/scripts/freeze_workbench.py status PROJECT
python SKILL/scripts/freeze_workbench.py snapshot PROJECT
python SKILL/scripts/freeze_workbench.py ai-change PROJECT --input update.json
python SKILL/scripts/freeze_workbench.py stop PROJECT
```

`start` chooses an available port by default and prints `local_url`, `forward_target`, and `remote_url` when `--public-origin` was supplied. Default loopback binding is sufficient for a reverse proxy running on the same computer. A reverse proxy should forward an HTTPS origin to `forward_target`. In the default mode, the login secret is in the URL fragment, so it is not sent in the HTTP request; anyone with the complete link can open the workbench. `--no-auth` removes that login requirement and returns a plain URL: anyone who can reach it can view and edit the project draft records. Same-origin checks and a CSRF token still protect browser writes from unrelated sites. `--host 0.0.0.0` allows direct network connections; use it only when that network exposure is intended. Switching login modes requires stopping the running workbench first.

An import file has this shape:

```json
{
  "request_id": "round-1-research-design",
  "questions": [
    {
      "group": "时间与策略",
      "title": "时间零点如何定义？",
      "why": "不同起点会改变纳入及风险时间。",
      "source_summary": "project.md 中的设计草案；尚未形成 Canonical 定义",
      "ai_position": "建议给出可从原始记录计算的日期规则。",
      "suggestions": ["首次处方日", "首次满足纳入条件日"]
    }
  ]
}
```

For `ai-change`, supply `question_id`, `operation`, `value`, `expected_revision`, and an optional stable `request_id`. Operations are `comment`, `ai_position`, `example` or `reopen`. `example` takes `{"title":"...","summary":"...","html":"..."}`. The HTML is shown in an iframe without script or same-origin permission; use CSS and native controls for interactive explanations. A `reopen` reason preserves the user's earlier answer and marks the question for discussion. The user-only `resolve` operation closes a dispute after an answer has been saved; remote AI cannot invoke it. Read the latest snapshot before writing so revision conflicts do not overwrite human changes.

## Review layout

The review UI contains the workbench name, round, counts and operations in one compact upper band. It is for experienced reviewers: omit introductory slogans, onboarding paragraphs and repeated descriptions of the workflow. Retain question-specific scientific context, sources, operation feedback and unsaved-state indicators. On desktop, the three work areas fill the remaining viewport height and scroll independently; do not cap them at a fixed pixel height. Group the complete question list by domain. Switching questions resets the detail scroll position so the new question's title is visible. Search with no matches displays a filter-specific empty state and a clear-filter action.

Use readable, responsive type, prominent question titles and distinct evidence cards. The example area uses 42% of the desktop width without a maximum-width cap. Its display scale defaults to 150%. Scale the existing iframe through its viewport container, preserving native control selections rather than rebuilding its document. Saving unrelated answers and refreshing an unchanged example also preserve the iframe. Reload only when the question or example source changes. Author new examples with responsive layouts and legible text.

## Drafts, saves and handoff

Pending browser inputs are separate from saved project records. Persist drafts synchronously in project-keyed `sessionStorage`, independently for each browser tab, so a browser refresh restores its answers, comments and last selected question. Show unsaved counts and per-question markers. Request the browser's normal leave warning when unsaved drafts exist; its presentation depends on the browser. Closing a tab or clearing browser storage is not durable project storage. If browser storage is unavailable, visibly report that local draft caching failed and require explicit saving. AI and MCP readers only see project records written by explicit saves.

Keep a draft's original project answer for conflict comparison. Revision conflicts must retain the local draft; after project refresh, show the changed project answer alongside the draft, requiring an explicit choice before saving over a different answer. A round save handles each question sequentially under revision checks. Partial failure reports which questions remain unsaved; successful changes stay saved and failed drafts remain available. Reuse pending mutation request IDs on retries to avoid duplicate comments after uncertain network responses.

Before handoff, list every question with a pending answer or comment. Offer `保存全部并生成摘要` and `仅交接已保存内容`; the latter explicitly lists the excluded draft question IDs in the resulting summary. Do not claim that the whole round was filled merely because the handoff was opened. The summary includes all questions, their saved answers, AI positions and messages, including discussions on unanswered questions. The modal manages focus, traps Tab, closes with Escape and returns focus to its entry control. Copy success or fallback selection has visible feedback. Handoff does not invoke Codex.

Network and expired-session errors tell the reviewer to restore the service or forwarded connection and use `刷新项目记录` before retrying. This operation refreshes the snapshot and session while preserving drafts. Explicitly identify this page control rather than ambiguously recommending a browser refresh.

## Storage and MCP

`Freeze/manifest.json` lists stable `F-000001` IDs and the current round. `Freeze/questions/F-000001.json` contains one question, its user answer, AI position, append-only messages, status, timestamps, revision and optional canonical reference. `Freeze/examples/F-000001.html` contains the explanatory example. The manifest publishes each newly imported batch after question files have been written. Readers use only its ID list. Files are UTF-8 JSON/HTML; writes are locked and atomically replaced. They can be versioned with the project in Git.

OppenSteward-MCP loads the installed skill's storage helper. A Stepwise R v3 project must be both explicitly registered and included in `OPPEN_FREEZE_PROJECTS=["/absolute/project/root"]`. With that allowlist, `OPPEN_FREEZE_MODE=read` gives `freeze_snapshot` and `freeze_read_question`; `write` also gives `freeze_add_questions` and `freeze_change_question`. An empty allowlist denies all Freeze access. Remote AI may add questions, opinions, comments, examples and reopen draft questions. It cannot edit human answers or write Canonical. This is a separate authenticated MCP service that stays available independently of the temporary web page. The MCP tool inventory and OAuth consent must be refreshed after enabling new scopes.
