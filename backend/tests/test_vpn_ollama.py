"""VPN interne (X25519, profils WireGuard, durcissement) et routage Ollama (modèles « -cloud » du serveur local)."""
from __future__ import annotations

import base64

import pytest

from app.services import ai, codegen, proxy, vpn_engine


def test_x25519_rfc7748_vectors():
    scalar = bytes.fromhex("a546e36bf0527c9d3b16154b82465edd62144c0ac1fc5a18506a2244ba449ac4")
    point = bytes.fromhex("e6db6867583030db3594c1a424b15f7c726624ec26b3353b10a903a6d0ab1c4c")
    assert vpn_engine.x25519(scalar, point).hex() == "c3da55379de9c6908e94ea4df28d084f32eccf03491c71f754b4075577a28552"
    alice = bytes.fromhex("77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a")
    assert vpn_engine.x25519(alice, b"\x09" + b"\x00" * 31).hex() == "8520f0098930a754748b7ddcb43ef75a0dbf3a0d26381af4eba4a98eaa9b4e6a"


def test_keypair_is_consistent():
    pair = vpn_engine.generate_keypair()
    assert len(base64.b64decode(pair["private"])) == 32
    assert vpn_engine.public_key(pair["private"]) == pair["public"]
    assert vpn_engine.generate_keypair()["private"] != pair["private"]
    with pytest.raises(vpn_engine.VpnEngineError):
        vpn_engine.public_key("pas-une-cle")


PARTIAL = """[Interface]
PrivateKey = AAAA
Address = 10.2.0.2/32

[Peer]
PublicKey = BBBB
AllowedIPs = 0.0.0.0/0
Endpoint = 203.0.113.7:51820
"""


def test_analyze_flags_leaks():
    info = vpn_engine.analyze_config(PARTIAL)
    messages = " ".join(i["message"] for i in info["issues"])
    assert info["valid"] and info["endpoint_host"] == "203.0.113.7" and info["endpoint_port"] == 51820
    assert not info["full_tunnel"] and "fuite DNS" in messages and "l'autre peut fuir" in messages
    assert not vpn_engine.analyze_config("n'importe quoi")["valid"]


def test_harden_forces_full_tunnel_and_dns():
    hardened = vpn_engine.harden_config(PARTIAL)
    info = vpn_engine.analyze_config(hardened)
    assert info["full_tunnel"] and info["dns"] == list(vpn_engine.DEFAULT_DNS) and info["keepalive"] == "25"
    assert not [i for i in info["issues"] if i["level"] == "warning"]
    assert "PrivateKey = AAAA" in hardened and hardened.count("[Peer]") == 1
    assert vpn_engine.harden_config(hardened) == hardened  # idempotent
    with pytest.raises(vpn_engine.VpnEngineError):
        vpn_engine.harden_config(PARTIAL, dns=("pas une ip",))


def test_bundle_and_api(consented, tmp_path, monkeypatch):
    monkeypatch.setattr(vpn_engine, "VPN_DIR", tmp_path / "vpn")
    response = consented.post("/api/privacy/vpn/bundle", json={"name": "Maison", "endpoint_host": "vpn.example.org", "endpoint_port": 51999})
    assert response.status_code == 200, response.text
    data = response.json()
    server = vpn_engine.parse_config(data["server_config"])
    client_text = open(data["client_path"], encoding="utf-8").read()
    client = vpn_engine.parse_config(client_text)
    server_if, server_peer = server[0][1], server[1][1]
    client_if, client_peer = client[0][1], client[1][1]
    assert vpn_engine.public_key(server_if["privatekey"]) == client_peer["publickey"]
    assert vpn_engine.public_key(client_if["privatekey"]) == server_peer["publickey"]
    assert server_peer["presharedkey"] == client_peer["presharedkey"]
    assert client_peer["endpoint"] == "vpn.example.org:51999" and client_peer["allowedips"] == vpn_engine.FULL_TUNNEL
    assert server_if["address"] == "10.66.0.1/24" and client_if["address"] == "10.66.0.2/24"
    assert "PrivateKey" not in str(data["profile"]) and data["profile"]["provider"] == "Cybbig Tunnel"

    analysis = consented.get(f"/api/privacy/vpn/profiles/{data['profile']['id']}/analysis").json()
    assert analysis["full_tunnel"] and analysis["has_preshared_key"]
    hardened = consented.post(f"/api/privacy/vpn/profiles/{data['profile']['id']}/harden").json()
    assert hardened["profile"]["label"].endswith("(durci)")
    consented.delete(f"/api/privacy/vpn/profiles/{hardened['profile']['id']}")
    consented.delete(f"/api/privacy/vpn/profiles/{data['profile']['id']}")


def test_bundle_rejects_bad_input(consented):
    for body in (
        {"name": "x", "endpoint_host": "a b; rm -rf"},
        {"name": "x", "endpoint_host": "vpn.example.org", "subnet": "8.8.8.0/24"},
        {"name": "x", "endpoint_host": "vpn.example.org", "dns": ["1.1.1.1\nPostUp = x"]},
    ):
        assert consented.post("/api/privacy/vpn/bundle", json=body).status_code == 400


def test_proxy_presets(consented):
    presets = consented.get("/api/privacy/proxies/presets").json()["items"]
    assert {"tor", "ssh-dynamic", "mitmproxy"} <= {p["id"] for p in presets}
    created = consented.post("/api/privacy/proxies/presets/tor").json()
    assert created["scheme"] == "socks5h" and created["port"] == 9050
    consented.delete(f"/api/privacy/proxies/{created['id']}")
    assert consented.post("/api/privacy/proxies/presets/inconnu").status_code == 404


# --- Ollama : modèles « -cloud » du serveur local -------------------------------------------------

class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


TAGS = {"models": [
    {"name": "deepseek-v4-pro:0813-cloud", "remote_host": "https://ollama.com"},
    {"name": "qwen2.5:7b"}, {"name": "qwen2.5-coder:7b"},
]}


@pytest.fixture()
def daemon(monkeypatch, consented):
    from app import db
    for key, value in (("ollama_url", "http://127.0.0.1:11434"), ("ai_provider", "auto"), ("ai_allow_cloud", "true"),
                       ("ollama_cloud_key", ""), ("ollama_cloud_model", ""), ("ollama_model", ""), ("ai_model_code", "")):
        db.set_setting(key, value)
    monkeypatch.setattr(ai.requests, "get", lambda url, **kw: FakeResponse(TAGS))
    ai.reset_cloud_block()
    yield db
    ai.reset_cloud_block()


def test_cloud_models_of_local_server_serve_online_mode(daemon):
    status = ai.ollama_status(full=True)
    assert status["provider"] == "cloud" and status["route"] == "daemon"
    assert status["selected_model"] == "deepseek-v4-pro:0813-cloud" and status["url"] == "http://127.0.0.1:11434"
    assert status["local"]["models"] == ["qwen2.5:7b", "qwen2.5-coder:7b"]  # le mode local ne contient aucun modèle en ligne
    assert status["cloud"]["models"] == ["deepseek-v4-pro:0813-cloud"] and status["cloud"]["configured"]


def test_local_only_never_selects_cloud_model(daemon):
    daemon.set_setting("ai_provider", "local")
    ai.invalidate_status()
    status = ai.ollama_status()
    assert status["provider"] == "local" and status["selected_model"] == "qwen2.5:7b"
    daemon.set_setting("ai_provider", "auto")
    daemon.set_setting("ai_allow_cloud", "false")
    ai.invalidate_status()
    status = ai.ollama_status()
    assert status["provider"] == "local" and "cloud" not in status["selected_model"]


def test_online_payload_is_redacted_without_local_tuning(daemon):
    status = ai.ollama_status()
    payload = ai.build_payload(status, [{"role": "user", "content": "clé sk-abcdefghijklmnopqrstuvwx"}])
    assert "sk-abcdef" not in payload["messages"][0]["content"] and "keep_alive" not in payload
    assert "num_thread" not in payload["options"]


def test_model_roles(daemon):
    both = {"models": ["qwen2.5:7b", "qwen2.5-coder:7b", "deepseek-r1:7b"], "selected_model": "qwen2.5:7b"}
    assert ai.model_for("code", both) == "qwen2.5-coder:7b"
    assert ai.model_for("reason", both) == "deepseek-r1:7b"
    assert ai.model_for("chat", both) == "qwen2.5:7b"
    daemon.set_setting("ai_model_code", "deepseek-r1:7b")
    assert ai.model_for("code", both) == "deepseek-r1:7b"
    daemon.set_setting("ai_model_code", "absent")
    assert ai.model_for("code", both) == "qwen2.5-coder:7b"


class Unauthorized(ai.requests.HTTPError):
    def __init__(self):
        super().__init__("401 Client Error: Unauthorized")
        self.response = type("R", (), {"status_code": 401})()


def test_unsigned_daemon_explains_401_and_falls_back_to_local(daemon, monkeypatch):
    calls = []

    def fake_post(status, payload, stream=False, timeout=0):
        calls.append((status["provider"], payload["model"]))
        if status["provider"] == "cloud":
            class Denied:
                def raise_for_status(self):
                    raise Unauthorized()
            return Denied()
        return FakeResponse({"message": {"content": "reponse locale"}})

    monkeypatch.setattr(ai, "post_chat", fake_post)
    result = ai.complete("bonjour", "systeme", role="code")
    assert result["provider"] == "local" and result["model"] == "qwen2.5-coder:7b" and result["text"] == "reponse locale"
    assert calls == [("cloud", "deepseek-v4-pro:0813-cloud"), ("local", "qwen2.5-coder:7b")]

    daemon.set_setting("ai_provider", "cloud")  # « en ligne uniquement » : pas de repli, l'erreur doit dire quoi faire
    ai.invalidate_status()
    with pytest.raises(RuntimeError, match="ollama signin"):
        ai.complete("bonjour", "systeme")


def test_payment_required_pauses_online_mode(daemon):
    class PaymentRequired(ai.requests.HTTPError):
        def __init__(self):
            super().__init__("402")
            self.response = type("R", (), {"status_code": 402})()

    status = ai.ollama_status()
    assert status["provider"] == "cloud"
    message = ai.explain_error(status, PaymentRequired())
    assert "402" in message and "gratuit" in message
    after = ai.ollama_status(full=True)
    assert after["provider"] == "local" and "402" in after["cloud"]["error"]  # pause : plus d'aller-retour inutile vers le service en ligne
    ai.reset_cloud_block()
    assert ai.ollama_status()["provider"] == "cloud"


def test_codegen_uses_active_server(daemon, monkeypatch):
    sent = {}

    def fake_post(status, payload, stream=False, timeout=0):
        sent["model"], sent["messages"] = payload["model"], payload["messages"]
        return FakeResponse({"message": {"content": "```conf\nhttp_port 3128\n```"}})

    monkeypatch.setattr(ai, "post_chat", fake_post)
    result = codegen.generate("proxy", "Squid avec liste blanche 192.168.1.0/24")
    assert result["provider"] == "cloud" and result["route"] == "daemon" and result["model"] == "deepseek-v4-pro:0813-cloud"
    assert "http_port 3128" in result["text"] and "Squid" in sent["messages"][1]["content"]
    with pytest.raises(ValueError):
        codegen.generate("inconnu", "x")
    with pytest.raises(ValueError):
        codegen.generate("code", "   ")
    with pytest.raises(ValueError):
        codegen.generate("code", "x", language="cobol")


def test_roles_are_wired_into_chat_and_tasks(daemon, monkeypatch):
    from app.services import ai_tasks
    daemon.set_setting("ai_provider", "local")
    daemon.set_setting("ai_auto_route", "true")
    ai.reset_cloud_block()
    status = ai.ollama_status()
    assert status["selected_model"] == "qwen2.5:7b"
    assert ai.role_for_message("Corrige cette fonction PHP") == "code" and ai.role_for_message("Resume les risques du projet") == "chat"
    assert ai._prepare("Corrige cette fonction PHP", None, None, "qwen2.5:7b")["selected"] == "qwen2.5-coder:7b"
    assert ai._prepare("Resume les risques du projet", None, None, "qwen2.5:7b")["selected"] == "qwen2.5:7b"
    assert ai._prepare("Corrige cette fonction PHP", None, None, "qwen2.5-coder:7b")["selected"] == "qwen2.5-coder:7b"
    daemon.set_setting("ai_auto_route", "false")
    assert ai._prepare("Corrige cette fonction PHP", None, None, "qwen2.5:7b")["selected"] == "qwen2.5:7b"
    daemon.set_setting("ai_auto_route", "true")
    task, context, _ = ai_tasks._terminal_explain({"code": "ls", "stderr": "erreur"})
    assert ai_tasks._payload(status, task, context, name="terminal_explain")["model"] == "qwen2.5-coder:7b"
    assert ai_tasks._payload(status, task, context, name="dashboard_priorities")["model"] == "qwen2.5:7b"
