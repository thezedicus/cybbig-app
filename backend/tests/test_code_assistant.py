"""Atelier IA : analyse des blocs SEARCH/REPLACE, vérification contre les fichiers réels, application atomique."""
from __future__ import annotations

import json

import pytest

from app.services import ai, code_assistant, code_editor


@pytest.fixture()
def project(consented, tmp_path, monkeypatch):
    root = tmp_path / "soft"
    (root / "backend").mkdir(parents=True)
    (root / "backend" / "data").mkdir()
    (root / "backend" / "calc.py").write_text("def add(a, b):\n    return a + b\n\n\ndef sub(a, b):\n    return a - b\n", encoding="utf-8")
    (root / "backend" / "dup.py").write_text("x = 1\nx = 1\n", encoding="utf-8")
    (root / "backend" / "crlf.txt").write_bytes(b"un\r\ndeux\r\ntrois\r\n")
    (root / "backend" / ".env").write_text("SECRET=1\n", encoding="utf-8")
    (root / "backend" / "data" / "cybbig.db").write_bytes(b"\x00")
    monkeypatch.setattr(code_editor, "ROOT", root.resolve())
    monkeypatch.setattr(code_editor, "BACKUPS", tmp_path / "backups")
    return root


def block(path, search, replace):
    return f"<<<<<<< SEARCH {path}\n{search}\n=======\n{replace}\n>>>>>>> REPLACE"


def test_parse_edits_ignores_prose_and_fences():
    text = "Voici le correctif :\n```\n" + block("backend/calc.py", "return a + b", "return a + b  # somme") + "\n```\nEt un fichier neuf :\n" + \
        "<<<<<<< SEARCH backend/new.py\n=======\nprint('x')\n>>>>>>> REPLACE\n"
    edits = code_assistant.parse_edits(text)
    assert [e["path"] for e in edits] == ["backend/calc.py", "backend/new.py"]
    assert edits[0]["search"] == "return a + b" and edits[1]["search"] == "" and edits[1]["replace"] == "print('x')"
    assert code_assistant.parse_edits("<<<<<<< SEARCH a.py\nincomplet") == []  # bloc jamais refermé : ignoré


def test_preview_statuses(project):
    edits = [
        {"path": "backend/calc.py", "search": "return a + b", "replace": "return int(a) + int(b)"},
        {"path": "backend/calc.py", "search": "texte absent", "replace": "x"},
        {"path": "backend/dup.py", "search": "x = 1", "replace": "x = 2"},
        {"path": "backend/nouveau.py", "search": "", "replace": "print('ok')\n"},
        {"path": "backend/calc.py", "search": "", "replace": "ecrase"},
        {"path": "../dehors.py", "search": "a", "replace": "b"},
        {"path": "backend/.env", "search": "SECRET=1", "replace": "SECRET=2"},
        {"path": "backend/data/cybbig.db", "search": "a", "replace": "b"},
    ]
    result = code_assistant.preview(edits)
    assert [r["status"] for r in result] == ["ok", "error", "error", "ok", "error", "error", "error", "error"]
    assert "ambigu" in result[2]["message"] and result[3]["new_file"] is True
    assert "-    return a + b" in result[0]["diff"] and "+    return int(a) + int(b)" in result[0]["diff"]
    assert "existe déjà" in result[4]["message"]
    assert "non accessible" in result[6]["message"] and "non accessible" in result[7]["message"]


def test_sequential_blocks_on_same_file(project):
    edits = [{"path": "backend/calc.py", "search": "return a + b", "replace": "return a + b + 0"},
             {"path": "backend/calc.py", "search": "return a + b + 0", "replace": "return sum((a, b))"}]
    assert [r["status"] for r in code_assistant.preview(edits)] == ["ok", "ok"]
    code_assistant.apply(edits)
    assert "return sum((a, b))" in (project / "backend" / "calc.py").read_text(encoding="utf-8")


def test_apply_writes_backup_and_preserves_crlf(project):
    result = code_assistant.apply([
        {"path": "backend/calc.py", "search": "return a - b", "replace": "return a - b  # différence"},
        {"path": "backend/crlf.txt", "search": "deux", "replace": "2"},
        {"path": "backend/neuf.py", "search": "", "replace": "VALEUR = 1\n"},
    ])
    assert (project / "backend" / "crlf.txt").read_bytes() == b"un\r\n2\r\ntrois\r\n"
    assert (project / "backend" / "neuf.py").read_text(encoding="utf-8") == "VALEUR = 1\n"
    assert result["needs"] == "restart" and len(result["files"]) == 3
    saved = [b for b in code_editor.backups() if b["path"] == "backend/calc.py"]
    assert saved  # l'ancienne version est sauvegardée avant l'écriture


def test_apply_is_all_or_nothing(project):
    before = (project / "backend" / "calc.py").read_text(encoding="utf-8")
    with pytest.raises(code_assistant.AssistantError, match="Bloc 2"):
        code_assistant.apply([{"path": "backend/calc.py", "search": "return a + b", "replace": "return 0"},
                              {"path": "backend/calc.py", "search": "introuvable", "replace": "x"}])
    with pytest.raises(code_assistant.AssistantError, match="syntaxe"):
        code_assistant.apply([{"path": "backend/dup.py", "search": "x = 1\nx = 1", "replace": "def (:"},
                              {"path": "backend/calc.py", "search": "return a + b", "replace": "return 0"}])
    assert (project / "backend" / "calc.py").read_text(encoding="utf-8") == before  # rien n'a été écrit
    assert (project / "backend" / "dup.py").read_text(encoding="utf-8") == "x = 1\nx = 1\n"


def test_pick_model_prefers_coder():
    assert code_assistant.pick_model({"models": ["qwen2.5:7b", "qwen2.5-coder:7b"], "selected_model": "qwen2.5:7b"}) == "qwen2.5-coder:7b"
    assert code_assistant.pick_model({"models": ["qwen2.5:7b"], "selected_model": "qwen2.5:7b"}) == "qwen2.5:7b"


def test_search_files_hides_private_files(project):
    found = code_assistant.search_files("")
    assert "backend/calc.py" in found and not any(".env" in f or f.endswith(".db") for f in found)
    assert code_assistant.search_files("calc") == ["backend/calc.py"]  # la copie sous release/ est ignorée


def test_stream_proposes_validated_edits(consented, project, monkeypatch):
    status = {"available": True, "provider": "cloud", "url": "https://ollama.com", "models": ["gpt-oss:120b"], "selected_model": "gpt-oss:120b", "error": ""}
    monkeypatch.setattr(ai, "ollama_status", lambda full=False: dict(status))
    sent = {}

    class Reply:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def raise_for_status(self): pass
        def iter_lines(self):
            text = "Je corrige la soustraction.\n" + block("backend/calc.py", "return a - b", "return a - b  # ok")
            yield json.dumps({"message": {"content": text[:30]}}).encode()
            yield json.dumps({"message": {"content": text[30:]}, "done": True}).encode()

    def fake_post(url, json=None, **kw):
        sent["payload"] = json
        return Reply()

    monkeypatch.setattr(ai.requests, "post", fake_post)
    events = [json.loads(line) for line in "".join(code_assistant.stream("Commente la soustraction", ["backend/calc.py"])).splitlines()]
    assert events[0]["type"] == "meta" and events[0]["files"][0]["path"] == "backend/calc.py"
    done = events[-1]
    assert done["type"] == "done" and len(done["edits"]) == 1 and done["edits"][0]["status"] == "ok"
    prompt = " ".join(m["content"] for m in sent["payload"]["messages"])
    assert "def sub(a, b)" in prompt and "Commente la soustraction" in prompt
    with pytest.raises(code_assistant.AssistantError):
        list(code_assistant.stream("x", ["backend/.env"]))  # un fichier d'environnement n'est jamais envoyé au modèle


def test_assistant_routes_need_admin_session(consented):
    assert consented.post("/api/admin/code/assist", json={"instruction": "x"}).status_code == 401
    assert consented.post("/api/admin/code/assist/apply", json={"edits": [{"path": "a", "search": "", "replace": "b"}]}).status_code == 401
    assert consented.get("/api/admin/code/search?q=main").status_code == 401
