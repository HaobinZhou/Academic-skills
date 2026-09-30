"""Contracts shared by the temporary web UI and remote MCP adapter."""

import importlib.util
import json
import importlib
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest


SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "freeze_store.py"
SPEC = importlib.util.spec_from_file_location("freeze_store_test", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FreezeStore, FreezeError = MODULE.FreezeStore, MODULE.FreezeError


@pytest.fixture
def store(tmp_path):
    (tmp_path / "project.md").write_text("<!-- stepwise-r-project:v3 -->\n", encoding="utf-8")
    return FreezeStore(tmp_path)


def question(title):
    return {
        "group": "时间与策略", "title": title, "why": "这会改变人群与风险时间。",
        "source_summary": "方案草案", "ai_position": "需要明确日期规则。",
        "suggestions": ["首次处方日", "首次配药日"],
    }


def test_rounds_idempotency_and_question_level_conflict(store):
    first = store.add_questions([question("时间零点？"), question("随访结束？")], request_id="round-1")
    assert first["ids"] == ["F-000001", "F-000002"]
    assert store.add_questions([question("时间零点？"), question("随访结束？")],
                               request_id="round-1")["replayed"]
    with pytest.raises(FreezeError, match="different questions"):
        store.add_questions([question("换药？")], request_id="round-1")
    q = store.read_question("F-000001")
    answered = store.change(q["id"], "answer", "首次处方日", expected_revision=q["revision"],
                            request_id="answer-1", actor="user")
    assert answered["status"] == "answered"
    with pytest.raises(FreezeError, match="changed since read"):
        store.change(q["id"], "comment", "旧页面上的评论", expected_revision=q["revision"],
                     request_id="stale-1", actor="web_ai")
    q = store.read_question("F-000001")
    reopened = store.change(q["id"], "reopen", "新数据提示另一个起点", expected_revision=q["revision"],
                            request_id="reopen-1", actor="web_ai")
    assert reopened["user_answer"] == "首次处方日"
    assert reopened["status"] == "discussing"
    assert reopened["messages"][-1]["actor"] == "web_ai"
    revised = store.change(q["id"], "answer", "首次配药日", expected_revision=reopened["revision"],
                           request_id="answer-2", actor="user")
    assert revised["user_answer"] == "首次配药日" and revised["status"] == "discussing"
    with pytest.raises(FreezeError, match="unavailable"):
        store.change(q["id"], "resolve", None, expected_revision=revised["revision"],
                     request_id="ai-resolve", actor="web_ai")
    resolved = store.change(q["id"], "resolve", None, expected_revision=revised["revision"],
                            request_id="user-resolve", actor="user")
    assert resolved["status"] == "answered"
    assert store.add_questions([question("新增依赖问题？")], request_id="round-2")["ids"] == ["F-000003"]
    assert store.snapshot()["round"] == 2


def test_ai_cannot_answer_and_example_is_separate_sandbox_source(store):
    qid = store.add_questions([question("死亡如何处理？")], request_id="initial")["ids"][0]
    q = store.read_question(qid)
    with pytest.raises(FreezeError, match="unavailable"):
        store.change(qid, "answer", "竞争事件", expected_revision=q["revision"],
                     request_id="ai-answer", actor="web_ai")
    example = {"title": "竞争事件示意", "summary": "同一批人的两种归属。",
               "html": "<h3>100 人示例</h3><p>20 人死亡</p>"}
    store.change(qid, "example", example, expected_revision=q["revision"],
                 request_id="example-1", actor="codex")
    compact = store.read_question(qid)
    full = store.read_question(qid, include_example=True)
    assert "html" not in compact["example"]
    assert full["example"]["html"] == example["html"]
    assert (store.examples / f"{qid}.html").read_text(encoding="utf-8") == example["html"]
    assert store.snapshot()["questions"][0]["canonical_ref"] is None


def test_linked_workspace_is_rejected(store):
    store.root.symlink_to(store.project / "elsewhere", target_is_directory=True)
    with pytest.raises(FreezeError, match="Unsafe freeze directory"):
        store.add_questions([question("不能写到链接目标")], request_id="unsafe")


def test_author_sources_persist_across_ai_edits_and_retries(store):
    qid = store.add_questions([question("时间零点？")], request_id="codex-round", actor="codex")["ids"][0]
    with pytest.raises(FreezeError, match="different questions"):
        store.add_questions([question("时间零点？")], request_id="codex-round", actor="chatgpt")
    q = store.read_question(qid)
    assert q["created_by"] == q["ai_position_by"] == "codex"
    q = store.change(qid, "answer", "首次处方日", expected_revision=q["revision"],
                     request_id="human-answer", actor="user")
    q = store.change(qid, "ai_position", "建议核对配药日期", expected_revision=q["revision"],
                     request_id="chatgpt-opinion", actor="chatgpt")
    assert q["ai_position_by"] == "chatgpt" and q["ai_position_at"]
    assert q["messages"][-1]["actor"] == "chatgpt"
    assert store.change(qid, "ai_position", "建议核对配药日期", expected_revision=1,
                        request_id="chatgpt-opinion", actor="chatgpt")["replayed"]
    with pytest.raises(FreezeError, match="different content"):
        store.change(qid, "ai_position", "建议核对配药日期", expected_revision=1,
                     request_id="chatgpt-opinion", actor="codex")
    q = store.change(qid, "comment", "Codex 已核对实现", expected_revision=q["revision"],
                     request_id="codex-comment", actor="codex")
    q = store.change(qid, "example", {"title": "日期示例", "summary": "两种起点", "html": "<p>时间线</p>"},
                     expected_revision=q["revision"], request_id="chatgpt-example", actor="chatgpt")
    saved = FreezeStore(store.project).read_question(qid)
    assert saved["created_by"] == "codex" and saved["ai_position_by"] == "chatgpt"
    assert [m["actor"] for m in saved["messages"]] == ["chatgpt", "codex"]
    assert saved["example"]["updated_by"] == "chatgpt"
    assert saved["user_answer"] == "首次处方日"
    for operation in ("answer", "resolve"):
        with pytest.raises(FreezeError, match="unavailable"):
            store.change(qid, operation, "不能代答", expected_revision=saved["revision"],
                         request_id="chatgpt-" + operation, actor="chatgpt")
    with pytest.raises(FreezeError, match="recognized AI"):
        store.add_questions([question("无效来源")], request_id="human-round", actor="user")


def test_legacy_records_remain_readable_without_inventing_opinion_author(store):
    qid = store.add_questions([question("历史问题")], request_id="legacy-round", actor="web_ai")["ids"][0]
    q = store.read_question(qid)
    del q["ai_position_by"], q["ai_position_at"]
    MODULE.atomic_json(store.questions / f"{qid}.json", q)
    original = (store.questions / f"{qid}.json").read_bytes()
    assert store.snapshot()["questions"][0]["created_by"] == "web_ai"
    assert "ai_position_by" not in store.read_question(qid)
    assert (store.questions / f"{qid}.json").read_bytes() == original


def test_keyless_workbench_serves_and_saves_without_login(store, monkeypatch):
    monkeypatch.syspath_prepend(str(SOURCE.parent))
    workbench = importlib.import_module("freeze_workbench")
    qid = store.add_questions([question("时间零点？")], request_id="keyless-round")["ids"][0]
    server = ThreadingHTTPServer(("127.0.0.1", 0), workbench.WorkbenchHandler)
    server.store = store
    server.public_origin = ""
    server.no_auth = True
    server.login_token = ""
    server.cookie_token = "unused"
    server.csrf_token = "csrf-test"
    server.admin_token = "admin-test"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        assert workbench.urls({"port": server.server_address[1], "pid": 1, "host": "127.0.0.1",
                               "public_origin": "", "no_auth": True})["local_url"] == base + "/"
        with urllib.request.urlopen(base + "/") as response:
            assert b"sw-freeze-v2" in response.read()
        with urllib.request.urlopen(base + "/api/snapshot") as response:
            snapshot = json.load(response)
        assert snapshot["csrf"] == "csrf-test"
        payload = json.dumps({"operation": "answer", "value": "首次处方日",
                              "expected_revision": snapshot["snapshot"]["questions"][0]["revision"],
                              "request_id": "keyless-answer"}).encode()
        request = urllib.request.Request(base + f"/api/questions/{qid}/change", data=payload,
            headers={"Content-Type": "application/json", "X-Freeze-CSRF": "csrf-test",
                     "Origin": base})
        with urllib.request.urlopen(request) as response:
            assert json.load(response)["question"]["status"] == "answered"
        assert store.read_question(qid)["user_answer"] == "首次处方日"
        server.no_auth = False
        with pytest.raises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(base + "/api/snapshot")
        assert error.value.code == 401
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
