from pathlib import Path
import secrets
import json
import time

import pytest


def wait_scan(client, scan_id, timeout=180):
    deadline = time.time() + timeout
    while time.time() < deadline:
        response = client.get(f"/api/scans/{scan_id}")
        assert response.status_code == 200
        data = response.json()
        if data["status"] in {"completed", "failed", "blocked", "cancelled"}:
            return data
        time.sleep(0.5)
    raise AssertionError(f"timeout while waiting for scan {scan_id}")


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"]["ok"] is True
    assert data["database"]["fts5"] is True


def test_consent_flow(consented):
    status = consented.get("/api/consent").json()
    assert status["accepted"] is True
    health = consented.get("/api/health").json()
    assert health["consent"] is True


def test_demo_project(project):
    assert project["id"] == "proj-demo-cybbig"
    assert project["path_exists"] is True
    assert project["base_url"]


def test_php_scan(consented, project):
    response = consented.post("/api/scans", json={
        "project_id": project["id"],
        "kind": "php",
        "config": {"max_files": 1000},
    })
    assert response.status_code == 200
    scan = wait_scan(consented, response.json()["id"])
    assert scan["status"] == "completed"
    assert (scan.get("summary") or {}).get("findings", 0) > 0
    assert len(scan.get("findings") or []) > 0


def test_web_scan(consented, project):
    response = consented.post("/api/scans", json={
        "project_id": project["id"],
        "kind": "web",
    })
    assert response.status_code == 200
    scan = wait_scan(consented, response.json()["id"])
    assert scan["status"] == "completed"
    assert scan.get("findings")


def test_api_scan(consented, project):
    response = consented.post("/api/scans", json={
        "project_id": project["id"],
        "kind": "api",
    })
    assert response.status_code == 200
    scan = wait_scan(consented, response.json()["id"])
    assert scan["status"] == "completed"
    assert scan.get("findings")


def test_checkout_scan(consented, project):
    response = consented.post("/api/scans", json={
        "project_id": project["id"],
        "kind": "checkout",
    })
    assert response.status_code == 200
    scan = wait_scan(consented, response.json()["id"])
    assert scan["status"] == "completed"
    assert scan.get("findings")


def test_lab_scenarios(consented):
    response = consented.get("/api/lab/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 9
    validation = consented.post("/api/lab/validate", json={
        "code": "$sql = \"SELECT * FROM users WHERE id=\" . $_GET['id'];",
        "language": "php",
    })
    assert validation.status_code == 200
    assert validation.json()["count"] > 0


def test_knowledge_search(consented):
    response = consented.get("/api/knowledge", params={"q": "paiement", "limit": 20})
    assert response.status_code == 200
    data = response.json()
    assert data["items"]
    assert any("paiement" in (item.get("title") or "").lower() or "paiement" in (item.get("content") or "").lower()
               for item in data["items"])


def test_assistant_chat(consented, monkeypatch):
    from app.services import ai
    # Indépendant d'un Ollama éventuellement installé sur le poste.
    monkeypatch.setattr(ai, "ollama_status", lambda: {"available": False, "url": "", "models": [], "selected_model": "", "error": "off"})
    response = consented.post("/api/assistant/chat", json={"message": "Qu'est-ce qu'un XSS ?"})
    assert response.status_code == 200
    data = response.json()
    assert data["answer"]
    assert data["offline"] is True


def test_settings_roundtrip(consented):
    original = consented.get("/api/settings").json()["values"]
    response = consented.put("/api/settings", json={"values": {"max_pages": "4"}})
    assert response.status_code == 200
    assert consented.get("/api/settings").json()["values"]["max_pages"] == "4"
    consented.put("/api/settings", json={"values": {"max_pages": original.get("max_pages", "3")}})


def test_report_generation(consented, project):
    response = consented.post("/api/reports", json={"project_id": project["id"], "title": "Rapport test"})
    assert response.status_code == 200
    report = response.json()
    download = consented.get(report["download_url"])
    assert download.status_code == 200
    assert "html" in download.headers.get("content-type", "").lower() or download.text


def test_engines_and_audit(consented):
    engines = consented.get("/api/engines").json()
    assert len(engines["engines"]) >= 5
    audit = consented.get("/api/audit", params={"limit": 5}).json()
    assert "items" in audit


# Clé propriétaire de TEST, générée à chaque session : la vraie clé privée n'est jamais dans le dépôt.
_TEST_OWNER_SECRET = secrets.token_bytes(32)
_TEST_ADMIN = {"identifier": "test-owner", "password": "test-password-" + secrets.token_hex(4)}


def _activate_owner(client):
    from app.services import ed25519, owner

    owner.OWNER_PUBLIC_KEY = ed25519.public_key(_TEST_OWNER_SECRET).hex()
    challenge = client.post("/api/admin/owner/challenge").json()["challenge"]
    signature = ed25519.sign(_TEST_OWNER_SECRET, challenge.encode()).hex()
    return client.post("/api/admin/owner/activate", json={"challenge": challenge, "signature": signature, **_TEST_ADMIN})


def _admin_token(client):
    response = client.post("/api/admin/login", json=_TEST_ADMIN)
    if response.status_code != 200:
        assert _activate_owner(client).status_code == 200
        response = client.post("/api/admin/login", json=_TEST_ADMIN)
    assert response.status_code == 200
    return response.json()["token"]


def test_no_default_admin_credentials(client):
    from app.services import admin

    source = Path(admin.__file__).read_text(encoding="utf-8")
    assert "DEFAULT_PASSWORD" not in source and "DEFAULT_IDENTIFIER" not in source
    assert not hasattr(admin, "DEFAULT_PASSWORD")
    assert client.post("/api/admin/login", json={"identifier": "admin", "password": "admin-password"}).status_code == 401


def test_owner_activation_rejects_bad_signature(client):
    from app.services import ed25519, owner

    owner.OWNER_PUBLIC_KEY = ed25519.public_key(_TEST_OWNER_SECRET).hex()
    challenge = client.post("/api/admin/owner/challenge").json()["challenge"]
    forged = ed25519.sign(secrets.token_bytes(32), challenge.encode()).hex()
    response = client.post("/api/admin/owner/activate", json={"challenge": challenge, "signature": forged, **_TEST_ADMIN})
    assert response.status_code == 403
    # Le défi est à usage unique, même après un échec.
    good = ed25519.sign(_TEST_OWNER_SECRET, challenge.encode()).hex()
    assert client.post("/api/admin/owner/activate", json={"challenge": challenge, "signature": good, **_TEST_ADMIN}).status_code == 403


def test_admin_requires_session(consented):
    assert consented.get("/api/admin/overview").status_code == 401
    assert consented.post("/api/admin/exec", json={"code": "echo hi"}).status_code == 401
    assert consented.post("/api/admin/login", json={"identifier": "x", "password": "y"}).status_code == 401


def test_admin_hashes_not_exposed(consented):
    values = consented.get("/api/settings").json()["values"]
    assert not any(key.startswith("admin_") for key in values)
    consented.put("/api/settings", json={"values": {"admin_password_hash": "pwned", "owner_mode": "true"}})
    token = _admin_token(consented)
    assert token


def test_admin_features(consented):
    headers = {"X-Admin-Token": _admin_token(consented)}
    overview = consented.get("/api/admin/overview", headers=headers).json()
    assert "settings" in overview["tables"]
    result = consented.post("/api/admin/exec", headers=headers, json={"code": "print(6*7)", "shell": "python"}).json()
    assert result["exit_code"] == 0 and "42" in result["stdout"]
    sql = consented.post("/api/admin/sql", headers=headers, json={"sql": "SELECT COUNT(*) AS n FROM projects"}).json()
    assert sql["columns"] == ["n"]
    assert consented.put("/api/admin/settings", headers=headers, json={"values": {"custom_key": "1"}}).status_code == 200
    assert consented.get("/api/admin/settings", headers=headers).json()["values"]["custom_key"] == "1"
    backup = consented.post("/api/admin/backups", headers=headers).json()
    assert backup["bytes"] > 0
    assert consented.delete(f"/api/admin/backups/{backup['name']}", headers=headers).status_code == 200
    assert consented.post("/api/admin/logout", headers=headers).status_code == 200
    assert consented.get("/api/admin/session", headers=headers).status_code == 401


def test_assistant_stream_fallback(consented, monkeypatch):
    from app.services import ai
    monkeypatch.setattr(ai, "ollama_status", lambda: {"available": False, "url": "", "models": [], "selected_model": "", "error": "off"})
    finding = consented.get("/api/findings?limit=1").json()["items"][0]
    response = consented.post("/api/assistant/chat/stream", json={"message": "Explique ce résultat", "finding_id": finding["id"]})
    assert response.status_code == 200
    events = [json.loads(line) for line in response.text.splitlines() if line.strip()]
    assert events[0]["type"] == "meta" and events[-1]["type"] == "done"
    text = "".join(e["content"] for e in events if e["type"] == "token")
    assert finding["title"] in text


def test_assistant_stream_with_model_and_memory(consented, monkeypatch):
    from app.services import ai
    monkeypatch.setattr(ai, "ollama_status", lambda: {"available": True, "url": "http://ollama.test", "models": ["fake:1b"], "selected_model": "fake:1b", "error": ""})
    sent = {}

    class FakeResponse:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def raise_for_status(self): pass
        def iter_lines(self):
            yield json.dumps({"message": {"content": "Bon"}}).encode()
            yield json.dumps({"message": {"content": "jour"}, "done": True}).encode()

    def fake_post(url, json=None, **kwargs):
        sent.update(json)
        return FakeResponse()

    monkeypatch.setattr(ai.requests, "post", fake_post)
    consented.delete("/api/assistant/history")
    consented.post("/api/assistant/chat/stream", json={"message": "Première question"})
    response = consented.post("/api/assistant/chat/stream", json={"message": "Et ensuite ?"})
    events = [json.loads(line) for line in response.text.splitlines() if line.strip()]
    assert "".join(e["content"] for e in events if e["type"] == "token") == "Bonjour"
    assert events[-1]["model"] == "fake:1b" and events[-1]["offline"] is False
    contents = [m["content"] for m in sent["messages"]]
    assert "Première question" in contents and "Bonjour" in contents and contents[-1] == "Et ensuite ?"
    assert contents.count("Et ensuite ?") == 1


def test_assistant_pull_rejects_bad_name(consented):
    assert consented.post("/api/assistant/models/pull", json={"model": "bad name; rm"}).status_code == 400


OFFLINE = {"available": False, "url": "", "models": [], "selected_model": "", "error": "off"}


def test_ai_tasks_fallback_stream(consented, monkeypatch):
    from app.services import ai
    monkeypatch.setattr(ai, "ollama_status", lambda: dict(OFFLINE))
    scan = consented.get("/api/scans").json()["items"][0]
    for task, params in [("scan_summary", {"scan_id": scan["id"]}), ("dashboard_priorities", {}), ("intel_digest", {})]:
        response = consented.post("/api/ai/run", json={"task": task, "params": params})
        assert response.status_code == 200, task
        events = [json.loads(line) for line in response.text.splitlines() if line.strip()]
        assert events[-1]["type"] == "done" and events[-1]["offline"] is True
    assert consented.post("/api/ai/run", json={"task": "terminal_explain", "params": {}}).status_code == 400
    status = consented.get("/api/ai/status").json()
    assert status["enabled"] is False and "ai_agents" in status["sections"]


def test_ai_agents_parse_and_decide(consented):
    from app.services import ai_agents
    from app import db
    parsed = ai_agents._parse('Voici : [{"title": "Limiter les pages", "detail": "x", "kind": "config", "setting": {"key": "max_pages", "value": "5"}}, {"title": "Nouvelle règle", "kind": "rule"}]')
    assert len(parsed) == 2 and parsed[0]["setting"]["key"] == "max_pages" and parsed[1]["setting"] is None
    db.execute("INSERT INTO ai_suggestions(id,module,title,detail,kind,impact,setting_json,status,model,created_at) VALUES('sugg-t','scans','t','d','config','moyen','{\"key\":\"max_pages\",\"value\":\"5\"}','new','m','2026-01-01')")
    assert len(consented.get("/api/ai/agents").json()["items"]) == len(ai_agents.AGENTS)
    headers = {"X-Admin-Token": _admin_token(consented)}
    assert consented.post("/api/admin/ai/suggestions/sugg-t/apply", headers=headers).json()["status"] == "applied"
    assert consented.get("/api/settings").json()["values"]["max_pages"] == "5"
    consented.put("/api/settings", json={"values": {"max_pages": "3"}})


def test_code_editor_backup_and_restore(consented):
    headers = {"X-Admin-Token": _admin_token(consented)}
    tree = consented.get("/api/admin/code/tree", headers=headers).json()
    assert any(e["name"] == "backend" for e in tree["entries"])
    assert not any(e["name"] == ".venv" for e in consented.get("/api/admin/code/tree?path=backend", headers=headers).json()["entries"])
    assert consented.get("/api/admin/code/file?path=../../secret", headers=headers).status_code == 400
    path = "backend/samples/zz_code_editor_test.py"
    consented.delete(f"/api/admin/code/file?path={path}", headers=headers)  # reste d'un passage interrompu
    assert consented.put("/api/admin/code/file", headers=headers, json={"path": path, "content": "x = 1\n", "create": True}).status_code == 200
    bad = consented.put("/api/admin/code/file", headers=headers, json={"path": path, "content": "def (:\n"})
    assert bad.status_code == 400 and "syntaxe" in bad.json()["detail"]
    saved = consented.put("/api/admin/code/file", headers=headers, json={"path": path, "content": "x = 2\n"}).json()
    assert saved["needs"] == "restart" and saved["backup"]
    assert consented.post("/api/admin/code/restore", headers=headers, json={"backup": saved["backup"], "path": path}).status_code == 200
    assert consented.get(f"/api/admin/code/file?path={path}", headers=headers).json()["content"] == "x = 1\n"
    assert consented.delete(f"/api/admin/code/file?path={path}", headers=headers).status_code == 200


def test_active_mode_toggle_and_exec_cwd(consented):
    headers = {"X-Admin-Token": _admin_token(consented)}
    assert consented.get("/api/mode").json()["active"] is False
    assert consented.put("/api/admin/active-mode", headers=headers, json={"enabled": True}).json()["active"] is True
    assert consented.get("/api/mode").json()["active"] is True
    consented.put("/api/admin/active-mode", headers=headers, json={"enabled": False})
    run = consented.post("/api/admin/exec", headers=headers, json={"code": "Set-Location backend", "shell": "powershell"}).json()
    assert run["exit_code"] == 0 and run["cwd_after"].endswith("backend") and "__CYBBIG_CWD__" not in run["stdout"]
    failing = consented.post("/api/admin/exec", headers=headers, json={"code": "cmd /c exit 3", "shell": "powershell"}).json()
    assert failing["exit_code"] == 3


def test_php_new_rules():
    from app.services.engines.php_scanner import RULES
    samples = {
        "php-open-redirect": 'header("Location: " . $_GET["next"]);',
        "php-session-fixation": "session_id($_GET['sid']);",
        "php-loose-compare-secret": "if ($token == $expected) {",
        "php-phpinfo": "phpinfo();",
        "php-cors-wildcard": "header('Access-Control-Allow-Origin: *');",
    }
    by_id = {r.rule_id: r for r in RULES}
    for rule_id, line in samples.items():
        assert by_id[rule_id].pattern.search(line), rule_id
    assert not by_id["php-insecure-cookie"].pattern.search("setcookie('a', $v, ['secure' => true, 'httponly' => true]);")


def test_automation_backup_kind(consented):
    created = consented.post("/api/automations", json={"name": "Sauvegarde", "kind": "backup", "interval_minutes": 1440}).json()
    run = consented.post(f"/api/automations/{created['id']}/run").json()
    assert run["status"] == "completed", run
    consented.delete(f"/api/automations/{created['id']}")


def test_local_only_ai(consented):
    from app.services import ai
    assert ai.is_local_url("http://127.0.0.1:11434") and ai.is_local_url("http://192.168.1.10:11434") and ai.is_local_url("http://localhost:11434")
    assert not ai.is_local_url("https://ollama.com") and not ai.is_local_url("http://8.8.8.8:11434")
    from app import db
    previous = db.get_setting("ollama_url", "http://127.0.0.1:11434")
    db.set_setting("ollama_url", "https://ollama.com")
    try:
        status = ai.ollama_status()
        assert status["available"] is False and "locaux" in status["error"]
    finally:
        db.set_setting("ollama_url", previous)


def test_strip_thinking():
    from app.services.ai import strip_thinking
    assert strip_thinking("<think>[réflexion]</think>\nVERDICT: faux positif") == "VERDICT: faux positif"
    assert strip_thinking("Réponse <think>coupée") == "Réponse"
