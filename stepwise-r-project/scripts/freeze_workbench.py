"""On-demand Stepwise R freeze workbench and local Codex import commands."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import secrets
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from freeze_store import FreezeError, FreezeStore, atomic_json

ASSETS = Path(__file__).resolve().parent.parent / "assets"
MAX_BODY = 128 * 1024


def runtime_for(project: Path) -> Path:
    identity = hashlib.sha256(str(project.resolve()).encode()).hexdigest()[:20]
    owner = str(os.getuid()) if hasattr(os, "getuid") else os.environ.get("USERNAME", "user")
    return Path(tempfile.gettempdir()) / f"stepwise-freeze-{owner}" / identity


def private_runtime(path: Path) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    path.mkdir(mode=0o700, exist_ok=True)
    for directory in (path.parent, path):
        if directory.is_symlink():
            raise FreezeError("Runtime directory must not be a link")
        os.chmod(directory, 0o700)


def connection_info(runtime: Path) -> dict | None:
    path = runtime / "server.json"
    try:
        info = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return None
    port = info.get("port")
    if not isinstance(port, int) or not 1 <= port <= 65535:
        return None
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/healthz", headers={"X-Freeze-Admin": info.get("admin_token", "")}
    )
    try:
        with urllib.request.urlopen(request, timeout=0.7) as response:
            return info if response.status == 200 else None
    except (OSError, urllib.error.URLError):
        return None


def urls(info: dict) -> dict:
    no_auth = bool(info.get("no_auth"))
    suffix = "" if no_auth else "/#key=" + info["login_token"]
    return {
        "port": info["port"], "pid": info["pid"],
        "local_url": f"http://127.0.0.1:{info['port']}/{suffix.lstrip('/')}",
        "forward_target": f"127.0.0.1:{info['port']}",
        "remote_url": info["public_origin"] + (suffix or "/") if info.get("public_origin") else None,
        "host": info["host"],
        "auth_required": not no_auth,
    }


class WorkbenchHandler(BaseHTTPRequestHandler):
    server_version = "StepwiseFreeze/1"

    def log_message(self, format, *args):
        # Never log login tokens, cookies, project answers, or forwarded URLs.
        return

    @property
    def app(self):
        return self.server

    def headers_common(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; frame-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")

    def send_data(self, data: bytes, content_type: str, status: int = 200, cookie: str | None = None):
        self.send_response(status)
        self.headers_common()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, value: object, status: int = 200, cookie: str | None = None):
        self.send_data(json.dumps(value, ensure_ascii=False).encode("utf-8"),
                       "application/json; charset=utf-8", status, cookie)

    def same_origin(self) -> bool:
        origin = self.headers.get("Origin")
        if not origin:
            return True
        host = self.headers.get("Host", "")
        allowed = {f"http://{host}", f"https://{host}"}
        if self.app.public_origin:
            allowed.add(self.app.public_origin)
        return origin in allowed

    def authenticated(self) -> bool:
        if self.app.no_auth:
            return True
        values = [part.strip() for part in self.headers.get("Cookie", "").split(";")]
        return any(hmac.compare_digest(item, "swfreeze=" + self.app.cookie_token) for item in values)

    def admin(self) -> bool:
        return hmac.compare_digest(self.headers.get("X-Freeze-Admin", ""), self.app.admin_token)

    def require_auth(self) -> bool:
        if not self.authenticated():
            self.send_json({"error": "Login required"}, HTTPStatus.UNAUTHORIZED)
            return False
        return True

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/healthz":
            return self.send_json({"ok": True} if self.admin() else {"error": "Forbidden"},
                                  200 if self.admin() else HTTPStatus.FORBIDDEN)
        if path == "/login.js":
            return self.send_data((ASSETS / "freeze_login.js").read_bytes(),
                                  "application/javascript; charset=utf-8")
        if path == "/" and not self.authenticated():
            page = b'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>Stepwise R \xe7\x99\xbb\xe5\xbd\x95</title><body><p id="message">\xe6\xad\xa3\xe5\x9c\xa8\xe6\x89\x93\xe5\xbc\x80\xe5\x86\xbb\xe7\xbb\x93\xe5\x8f\xa3\xe5\xbe\x84\xe5\xb7\xa5\xe4\xbd\x9c\xe5\x8f\xb0...</p><script src="/login.js" defer></script></body></html>'
            return self.send_data(page, "text/html; charset=utf-8")
        if not self.require_auth():
            return
        if path == "/":
            return self.send_data((ASSETS / "freeze_workbench.html").read_bytes(), "text/html; charset=utf-8")
        if path == "/workbench.js":
            return self.send_data((ASSETS / "freeze_workbench.js").read_bytes(), "application/javascript; charset=utf-8")
        if path == "/api/snapshot":
            return self.send_json({"snapshot": self.app.store.snapshot(), "csrf": self.app.csrf_token})
        parts = path.split("/")
        if len(parts) == 5 and parts[:3] == ["", "api", "questions"] and parts[4] == "example":
            try:
                question = self.app.store.read_question(parts[3], include_example=True)
                return self.send_json({"html": (question.get("example") or {}).get("html", "")})
            except FreezeError as error:
                return self.send_json({"error": str(error)}, HTTPStatus.NOT_FOUND)
        return self.send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if not self.same_origin():
            return self.send_json({"error": "Untrusted Origin"}, HTTPStatus.FORBIDDEN)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_BODY:
                return self.send_json({"error": "Invalid request size"}, HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise FreezeError("JSON object required")
        except (ValueError, UnicodeDecodeError, FreezeError) as error:
            return self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
        if path == "/api/login":
            if self.app.no_auth:
                return self.send_json({"error": "Login is disabled"}, HTTPStatus.NOT_FOUND)
            if not hmac.compare_digest(str(body.get("key", "")), self.app.login_token):
                return self.send_json({"error": "Invalid login link"}, HTTPStatus.FORBIDDEN)
            secure = "; Secure" if self.headers.get("X-Forwarded-Proto") == "https" else ""
            cookie = f"swfreeze={self.app.cookie_token}; HttpOnly; SameSite=Strict; Path=/{secure}"
            return self.send_json({"ok": True}, cookie=cookie)
        if path == "/api/stop":
            if not self.admin():
                return self.send_json({"error": "Forbidden"}, HTTPStatus.FORBIDDEN)
            self.send_json({"stopping": True})
            threading.Thread(target=self.app.shutdown, daemon=True).start()
            return
        if not self.require_auth():
            return
        if not hmac.compare_digest(self.headers.get("X-Freeze-CSRF", ""), self.app.csrf_token):
            return self.send_json({"error": "CSRF check failed"}, HTTPStatus.FORBIDDEN)
        parts = path.split("/")
        if len(parts) != 5 or parts[:3] != ["", "api", "questions"] or parts[4] != "change":
            return self.send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
        try:
            question = self.app.store.change(
                parts[3], body.get("operation"), body.get("value"),
                expected_revision=body.get("expected_revision"),
                request_id=body.get("request_id"), actor="user",
            )
            return self.send_json({"question": question})
        except FreezeError as error:
            status = HTTPStatus.CONFLICT if "changed since read" in str(error) else HTTPStatus.BAD_REQUEST
            return self.send_json({"error": str(error)}, status)


def serve(project: Path, host: str, port: int, public_origin: str, runtime: Path,
          no_auth: bool = False) -> None:
    store = FreezeStore(project)
    if public_origin:
        url = urlsplit(public_origin)
        if (url.scheme != "https" or not url.hostname or url.path or url.query or url.fragment
                or url.username or url.password):
            raise FreezeError("--public-origin must be an HTTPS origin without a path")
    private_runtime(runtime)
    server = ThreadingHTTPServer((host, port), WorkbenchHandler)
    server.store = store
    server.public_origin = public_origin.rstrip("/")
    server.no_auth = no_auth
    server.login_token = "" if no_auth else secrets.token_urlsafe(32)
    server.cookie_token = secrets.token_urlsafe(32)
    server.csrf_token = secrets.token_urlsafe(32)
    server.admin_token = secrets.token_urlsafe(32)
    info = {"pid": os.getpid(), "port": server.server_address[1], "host": host,
            "public_origin": server.public_origin, "login_token": server.login_token,
            "admin_token": server.admin_token, "no_auth": no_auth}
    state_path = runtime / "server.json"
    atomic_json(state_path, info)
    try:
        server.serve_forever(poll_interval=0.2)
    finally:
        server.server_close()
        try:
            if json.loads(state_path.read_text(encoding="utf-8")).get("pid") == os.getpid():
                state_path.unlink()
        except (FileNotFoundError, ValueError):
            pass


def start(args) -> dict:
    project = Path(args.project).expanduser().resolve(strict=True)
    FreezeStore(project)
    runtime = runtime_for(project)
    private_runtime(runtime)
    running = connection_info(runtime)
    if running:
        if bool(running.get("no_auth")) != args.no_auth:
            raise FreezeError("Workbench is running with a different login mode; stop it before restarting")
        return {**urls(running), "already_running": True}
    state_path = runtime / "server.json"
    state_path.unlink(missing_ok=True)
    command = [sys.executable, str(Path(__file__).resolve()), "_serve", str(project),
               "--host", args.host, "--port", str(args.port), "--runtime", str(runtime)]
    if args.public_origin:
        command += ["--public-origin", args.public_origin]
    if args.no_auth:
        command += ["--no-auth"]
    with (runtime / "server.log").open("ab") as output:
        process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=output, stderr=output,
                                   start_new_session=True)
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        running = connection_info(runtime)
        if running:
            return {**urls(running), "already_running": False}
        if process.poll() is not None:
            break
        time.sleep(0.1)
    raise FreezeError(f"Workbench failed to start; inspect {runtime / 'server.log'}")


def stop(project: Path) -> dict:
    runtime = runtime_for(project)
    info = connection_info(runtime)
    if not info:
        return {"stopped": False, "reason": "No running workbench"}
    data = b"{}"
    request = urllib.request.Request(f"http://127.0.0.1:{info['port']}/api/stop", data=data,
        headers={"X-Freeze-Admin": info["admin_token"], "Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=2) as response:
        response.read()
    return {"stopped": True, "port": info["port"]}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Temporary web UI for Stepwise R freeze drafts")
    commands = root.add_subparsers(dest="command", required=True)
    start_parser = commands.add_parser("start")
    start_parser.add_argument("project", type=Path)
    start_parser.add_argument("--host", choices=["127.0.0.1", "0.0.0.0"], default="127.0.0.1")
    start_parser.add_argument("--port", type=int, default=0)
    start_parser.add_argument("--public-origin", default="")
    start_parser.add_argument("--no-auth", action="store_true")
    for name in ("status", "stop", "snapshot"):
        commands.add_parser(name).add_argument("project", type=Path)
    import_parser = commands.add_parser("import")
    import_parser.add_argument("project", type=Path)
    import_parser.add_argument("--input", type=Path, required=True)
    ai_parser = commands.add_parser("ai-change")
    ai_parser.add_argument("project", type=Path)
    ai_parser.add_argument("--input", type=Path, required=True)
    serve_parser = commands.add_parser("_serve")
    serve_parser.add_argument("project", type=Path)
    serve_parser.add_argument("--host", required=True)
    serve_parser.add_argument("--port", required=True, type=int)
    serve_parser.add_argument("--public-origin", default="")
    serve_parser.add_argument("--no-auth", action="store_true")
    serve_parser.add_argument("--runtime", type=Path, required=True)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "start":
            result = start(args)
        elif args.command == "_serve":
            serve(args.project, args.host, args.port, args.public_origin, args.runtime, args.no_auth)
            return 0
        elif args.command == "status":
            info = connection_info(runtime_for(args.project))
            result = urls(info) if info else {"running": False}
        elif args.command == "stop":
            result = stop(args.project)
        elif args.command == "snapshot":
            result = FreezeStore(args.project).snapshot()
        elif args.command == "import":
            payload = json.loads(args.input.read_text(encoding="utf-8"))
            result = FreezeStore(args.project).add_questions(payload["questions"],
                request_id=payload.get("request_id") or secrets.token_urlsafe(18), actor="codex")
        elif args.command == "ai-change":
            payload = json.loads(args.input.read_text(encoding="utf-8"))
            result = FreezeStore(args.project).change(payload["question_id"], payload["operation"],
                payload["value"], expected_revision=payload["expected_revision"],
                request_id=payload.get("request_id") or secrets.token_urlsafe(18), actor="codex")
        else:
            raise FreezeError("Unknown command")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (FreezeError, KeyError, OSError, json.JSONDecodeError) as error:
        print(f"Freeze workbench: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
