from __future__ import annotations

import json
import sys
import time

import requests

BASE = "http://127.0.0.1:8765"
s = requests.Session()
s.headers["User-Agent"] = "Cybbig-Smoke/1.0"


def call(method: str, path: str, **kwargs):
    r = s.request(method, BASE + path, timeout=60, **kwargs)
    try:
        data = r.json()
    except ValueError:
        data = r.text[:500]
    print(f"{method:6} {path:45} -> {r.status_code}")
    if r.status_code >= 400:
        print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
        raise SystemExit(1)
    return data


def wait_scan(scan_id: str, timeout: int = 120) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        data = call("GET", f"/api/scans/{scan_id}")
        status = data.get("status")
        if status in {"completed", "failed", "blocked", "cancelled"}:
            print("   status:", status, "findings:", len(data.get("findings", [])), "message:", data.get("message"))
            if status == "failed":
                print("   error:", data.get("error"))
                raise SystemExit(2)
            return data
        time.sleep(0.4)
    raise SystemExit(f"timeout on {scan_id}")


print("== système ==")
health = call("GET", "/api/health")
print("   db:", health["database"]["ok"], "fts5:", health["database"]["fts5"], "consent:", health["consent"])

consent = call("GET", "/api/consent")
if not consent.get("accepted"):
    call("POST", "/api/consent", json={
        "accepted": True, "user_name": "Test local", "organization": "Cybbig Lab",
        "purpose": "Vérification automatisée du MVP",
    })
print("   consent accepted:", call("GET", "/api/health")["consent"])

print("== projets ==")
projects = call("GET", "/api/projects")
project = projects["items"][0]
print("   projet:", project["id"], project["name"], "risk:", project["risk_score"])

print("== scans locaux ==")
scan_ids = []
for kind in ("php", "api", "checkout"):
    scan = call("POST", "/api/scans", json={"project_id": project["id"], "kind": kind})
    print("   créé:", scan["id"], kind, "->", scan["status"])
    scan_ids.append(scan["id"])
for sid in scan_ids:
    wait_scan(sid)

print("== scan web local ==")
web = call("POST", "/api/scans", json={"project_id": project["id"], "kind": "web"})
web_done = wait_scan(web["id"], timeout=180)
print("   url finale:", web_done.get("summary", {}).get("extra", {}).get("final_url"))

print("== résultats ==")
findings = call("GET", f"/api/findings?project_id={project['id']}&limit=500")
print("   total:", findings["total"], findings["severity"])
for f in findings["items"][:8]:
    print(f"   [{f['severity']:8}] {f['engine']:8} {f['title'][:80]}")

print("== document ==")
finding = findings["items"][0]
call("PATCH", f"/api/findings/{finding['id']}", json={"status": "acknowledged"})
print("   statut mis à jour:", call("GET", f"/api/findings/{finding['id']}")["status"])

print("== knowledge ==")
kb = call("GET", "/api/knowledge?q=checkout")
print("   docs:", len(kb["items"]), "catégories:", len(kb["categories"]))
kb2 = call("GET", "/api/knowledge?q=BOLA")
print("   BOLA docs:", len(kb2["items"]))

print("== assistant hors ligne ==")
answer = call("POST", "/api/assistant/chat", json={"message": "Comment prioriser les résultats du checkout ?", "project_id": project["id"]})
print("   modèle:", answer["model"], "offline:", answer["offline"], "sources:", len(answer["sources"]))
print("   extrait:", answer["answer"][:180].replace("\n", " "))

print("== rapport ==")
report = call("POST", "/api/reports", json={"project_id": project["id"], "scan_id": web["id"]})
print("   rapport:", report["id"], report["download_url"])
html = s.get(BASE + report["download_url"], timeout=30)
print("   HTML:", html.status_code, len(html.content), "octets")
j = s.get(BASE + report["json_url"], timeout=30)
print("   JSON:", j.status_code, len(j.content), "octets")

print("== labo ==")
labs = call("GET", "/api/lab/scenarios")
print("   scénarios:", len(labs["items"]))
lab = call("GET", f"/api/lab/scenarios/{labs['items'][0]['slug']}")
print("   détail:", lab["title"])

print("== automatisations ==")
autos = call("GET", "/api/automations")
print("   total:", autos["status"]["total"], "actives:", autos["status"]["enabled"])

print("== threat intel local ==")
items = call("GET", "/api/intel/items?limit=5")
print("   éléments:", items["total"])

print("== audit ==")
audit = call("GET", "/api/audit?limit=5")
print("   entrées:", len(audit["items"]))

print("\nSMOKE OK")
