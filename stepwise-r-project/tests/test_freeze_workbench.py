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
