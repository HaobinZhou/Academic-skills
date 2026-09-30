"""Project-owned, structured draft discussion for Stepwise R freeze rounds.

Freeze/ is a collaboration workspace. It never changes Canonical or declares a
scientific definition frozen. Both the temporary web UI and MCP use this module.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

MARKER = "<!-- stepwise-r-project:v3 -->"
QUESTION_ID = re.compile(r"F-[0-9]{6}\Z")
MAX_JSON = 1024 * 1024
MAX_HTML = 128 * 1024
STATUSES = {"open", "answered", "discussing"}


class FreezeError(ValueError):
    """The requested draft operation would violate the storage contract."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def require_text(value, name: str, limit: int = 20000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit or "\x00" in value:
        raise FreezeError(f"{name} must be nonempty text of at most {limit} characters")
    return value.strip()


def request_fingerprint(operation: str, payload: object) -> str:
    raw = json.dumps([operation, payload], ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def ordinary_file(path: Path, limit: int) -> bytes | None:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > limit:
        raise FreezeError(f"Unsafe or oversized freeze file: {path.name}")
    with path.open("rb") as source:
        if os.fstat(source.fileno()).st_ino != info.st_ino:
            raise FreezeError("Freeze file changed during read")
        data = source.read(limit + 1)
    if len(data) > limit:
        raise FreezeError(f"Oversized freeze file: {path.name}")
    return data


def atomic_write(path: Path, data: bytes) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=".freeze-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temporary, 0o600)
        current = ordinary_file(path, max(MAX_JSON, MAX_HTML))
        if current is not None and path.is_symlink():
            raise FreezeError("Refusing to replace a linked freeze file")
        os.replace(temporary, path)
        if os.name != "nt":
            directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def atomic_json(path: Path, value: dict) -> None:
    data = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if len(data) > MAX_JSON:
        raise FreezeError("Freeze record exceeds 1 MiB")
    atomic_write(path, data)


class FreezeStore:
    def __init__(self, project: str | Path):
        self.project = Path(project).expanduser().resolve(strict=True)
        marker = ordinary_file(self.project / "project.md", MAX_JSON)
        if marker is None or marker.decode("utf-8").splitlines().count(MARKER) != 1:
            raise FreezeError("A Stepwise R v3 project root is required")
        self.root = self.project / "Freeze"
        self.questions = self.root / "questions"
        self.examples = self.root / "examples"
        self.manifest = self.root / "manifest.json"

    def _directory(self, path: Path, create: bool) -> bool:
        if create:
            try:
                path.mkdir(mode=0o700)
            except FileExistsError:
                pass
        try:
            info = path.lstat()
        except FileNotFoundError:
            return False
        if not stat.S_ISDIR(info.st_mode) or path.is_symlink():
            raise FreezeError(f"Unsafe freeze directory: {path.name}")
        return True

    @contextmanager
    def locked(self, create: bool = False):
        if not self._directory(self.root, create):
            yield False
            return
        self._directory(self.questions, create)
        self._directory(self.examples, create)
        lock_path = self.root / ".lock"
        if ordinary_file(lock_path, 128) is None and not create:
            yield True
            return
        flags = os.O_RDWR | os.O_CREAT
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(lock_path, flags, 0o600)
        try:
            if os.name == "nt":
                import msvcrt

                os.write(descriptor, b"\0") if os.fstat(descriptor).st_size == 0 else None
                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_LOCK, 1)
            else:
                import fcntl

                fcntl.flock(descriptor, fcntl.LOCK_EX)
            yield True
        finally:
            if os.name == "nt":
                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)

    def _manifest(self) -> dict:
        raw = ordinary_file(self.manifest, MAX_JSON)
        if raw is None:
            return {"schema_version": 1, "round": 0, "question_ids": [], "revision": 0, "requests": {}}
        value = json.loads(raw)
        if value.get("schema_version") != 1 or not isinstance(value.get("question_ids"), list):
            raise FreezeError("Unsupported Freeze manifest")
        if len(set(value["question_ids"])) != len(value["question_ids"]) or not all(
            isinstance(item, str) and QUESTION_ID.fullmatch(item) for item in value["question_ids"]
        ):
            raise FreezeError("Invalid Freeze question index")
        return value

    def _question(self, question_id: str) -> dict:
        if not QUESTION_ID.fullmatch(question_id):
            raise FreezeError("Invalid question ID")
        raw = ordinary_file(self.questions / f"{question_id}.json", MAX_JSON)
        if raw is None:
            raise FreezeError("Question not found")
        value = json.loads(raw)
        if value.get("id") != question_id or value.get("schema_version") != 1:
            raise FreezeError("Question file does not match its ID")
        return value

    def snapshot(self) -> dict:
        with self.locked() as exists:
            manifest = self._manifest()
            questions = [self._question(item) for item in manifest["question_ids"]] if exists else []
            return {"project": str(self.project), "round": manifest["round"],
                    "revision": manifest["revision"], "questions": questions}

    def read_question(self, question_id: str, include_example: bool = False) -> dict:
        with self.locked() as exists:
            if not exists or question_id not in self._manifest()["question_ids"]:
                raise FreezeError("Question not found")
            question = self._question(question_id)
            if include_example and question.get("example"):
                raw = ordinary_file(self.examples / f"{question_id}.html", MAX_HTML)
                question["example"] = {**question["example"], "html": raw.decode("utf-8") if raw else ""}
            return question

    def add_questions(self, items: list[dict], *, request_id: str, actor: str = "codex") -> dict:
        require_text(request_id, "request_id", 100)
        if not isinstance(items, list) or not 1 <= len(items) <= 200:
            raise FreezeError("Submit 1–200 questions in one round")
        clean = []
        for item in items:
            if not isinstance(item, dict):
                raise FreezeError("Each question must be an object")
            suggestions = item.get("suggestions", [])
            if not isinstance(suggestions, list) or len(suggestions) > 8:
                raise FreezeError("suggestions must contain at most eight choices")
            clean.append({
                "group": require_text(item.get("group", "其他"), "group", 80),
                "title": require_text(item.get("title"), "title", 300),
                "why": require_text(item.get("why"), "why", 5000),
                "source_summary": require_text(item.get("source_summary", "尚待核对来源"), "source_summary", 5000),
                "ai_position": str(item.get("ai_position", "")).strip()[:10000],
                "suggestions": [require_text(value, "suggestion", 300) for value in suggestions],
            })
        fingerprint = request_fingerprint("add_questions", clean)
        with self.locked(create=True):
            manifest = self._manifest()
            previous = manifest["requests"].get(request_id)
            if previous:
                if previous["fingerprint"] != fingerprint:
                    raise FreezeError("request_id was used with different questions")
                return {"round": previous["round"], "ids": previous["ids"], "replayed": True}
            existing_numbers = [int(value[2:]) for value in manifest["question_ids"]]
            existing_numbers += [int(path.stem[2:]) for path in self.questions.glob("F-*.json")
                                 if QUESTION_ID.fullmatch(path.stem)]
            first = max(existing_numbers, default=0) + 1
            round_number = manifest["round"] + 1
            ids = [f"F-{first + number:06d}" for number in range(len(clean))]
            for question_id, item in zip(ids, clean):
                atomic_json(self.questions / f"{question_id}.json", {
                    "schema_version": 1, "id": question_id, "round": round_number,
                    **item, "created_by": actor, "created_at": now(),
                    "status": "open", "user_answer": None, "messages": [],
                    "example": None, "canonical_ref": None, "revision": 1, "requests": {},
                })
            manifest["round"] = round_number
            manifest["revision"] += 1
            manifest["question_ids"].extend(ids)
            manifest["requests"][request_id] = {"fingerprint": fingerprint, "round": round_number, "ids": ids}
            atomic_json(self.manifest, manifest)
            return {"round": round_number, "ids": ids, "replayed": False}

    def change(self, question_id: str, operation: str, value: object, *,
               expected_revision: int, request_id: str, actor: str) -> dict:
        require_text(request_id, "request_id", 100)
        fingerprint = request_fingerprint(operation, value)
        with self.locked(create=True):
            if question_id not in self._manifest()["question_ids"]:
                raise FreezeError("Question not found")
            question = self._question(question_id)
            previous = question["requests"].get(request_id)
            if previous:
                if previous != fingerprint:
                    raise FreezeError("request_id was used with different content")
                return {**question, "replayed": True}
            if question["revision"] != expected_revision:
                raise FreezeError("Question changed since read; reload before editing")
            if operation == "answer" and actor == "user":
                question["user_answer"] = require_text(value, "answer")
                if question["status"] != "discussing":
                    question["status"] = "answered"
            elif operation == "discuss" and actor == "user":
                question["status"] = "discussing"
            elif operation == "resolve" and actor == "user":
                if not question["user_answer"]:
                    raise FreezeError("Save an answer before resolving the discussion")
                question["status"] = "answered"
            elif operation == "comment" and actor in {"user", "codex", "web_ai"}:
                text = require_text(value, "message")
                question["messages"].append({"id": request_id, "actor": actor,
                                             "text": text, "round": self._manifest()["round"], "at": now()})
                if actor == "user":
                    question["status"] = "discussing"
            elif operation == "ai_position" and actor in {"codex", "web_ai"}:
                text = require_text(value, "ai_position", 10000)
                question["ai_position"] = text
                question["messages"].append({"id": request_id, "actor": actor,
                                             "text": text, "round": self._manifest()["round"], "at": now()})
            elif operation == "reopen" and actor in {"codex", "web_ai"}:
                text = require_text(value, "reason", 10000)
                question["status"] = "discussing"
                question["messages"].append({"id": request_id, "actor": actor,
                                             "text": "重新讨论：" + text,
                                             "round": self._manifest()["round"], "at": now()})
            elif operation == "example" and actor in {"codex", "web_ai"}:
                if not isinstance(value, dict):
                    raise FreezeError("example must be an object")
                title = require_text(value.get("title"), "example.title", 300)
                summary = require_text(value.get("summary"), "example.summary", 2000)
                html = require_text(value.get("html"), "example.html", MAX_HTML)
                if len(html.encode("utf-8")) > MAX_HTML:
                    raise FreezeError("example.html exceeds 128 KiB")
                atomic_write(self.examples / f"{question_id}.html", html.encode("utf-8"))
                question["example"] = {"title": title, "summary": summary,
                                       "updated_by": actor, "updated_at": now()}
            else:
                raise FreezeError("Operation is unavailable to this actor")
            if question["status"] not in STATUSES:
                raise FreezeError("Invalid question status")
            question["revision"] += 1
            question["requests"][request_id] = fingerprint
            atomic_json(self.questions / f"{question_id}.json", question)
            return question
