from __future__ import annotations

import html
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import db
from .api import admin as admin_api, ai_api, automations, dashboard, demo, findings, income, intel_api, knowledge, lab, privacy, projects, reports, resources_api, scans, system, assistant, terminal, training_api, web_api
from .config import APP_NAME, APP_VERSION, FRONTEND_DIST, ensure_dirs
from .services import admin, ai_worker, jobs, scheduler, training, webfetch

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
logger = logging.getLogger("cybbig")


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_dirs()
    db.init_db()
    admin.ensure_credentials()
    jobs.recover_stale_scans()
    webfetch.recover_stale_jobs()
    training.recover_stale_jobs()
    scheduler.recover_stale_runs()
    scheduler.ensure_improvement_cycle()
    scheduler.ensure_income_watch()
    scheduler.start()
    ai_worker.start()
    logger.info("Cybbig %s prêt sur http://127.0.0.1", APP_VERSION)
    yield
    scheduler.stop()
    ai_worker.stop()


app = FastAPI(
    title=f"{APP_NAME} API",
    version=APP_VERSION,
    description="Poste de travail de cybersécurité défensive. API locale uniquement.",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173", "http://127.0.0.1:8765", "http://localhost:8765"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path.startswith("/demo"):
        return response
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("X-Frame-Options", "DENY")
    if "/api/reports/" in path and path.endswith("/download"):
        response.headers["Content-Security-Policy"] = "default-src 'none'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; frame-ancestors 'none'"
    else:
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
            "connect-src 'self'; font-src 'self' data:; frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
        )
    return response


app.include_router(system.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(scans.router, prefix="/api")
app.include_router(findings.router, prefix="/api")
app.include_router(intel_api.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(dashboard.alerts_router, prefix="/api")
app.include_router(knowledge.router, prefix="/api")
app.include_router(assistant.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(automations.router, prefix="/api")
app.include_router(income.router, prefix="/api")
app.include_router(lab.router, prefix="/api")
app.include_router(privacy.router, prefix="/api")
app.include_router(terminal.router, prefix="/api")
app.include_router(admin_api.router, prefix="/api")
app.include_router(ai_api.router, prefix="/api")
app.include_router(web_api.router, prefix="/api")
app.include_router(training_api.router, prefix="/api")
app.include_router(resources_api.router, prefix="/api")
app.include_router(demo.router)

if FRONTEND_DIST.exists():
    assets = FRONTEND_DIST / "assets"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")


PLACEHOLDER = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><title>Cybbig</title>
<style>body{font-family:Segoe UI,sans-serif;background:#0b1220;color:#e2e8f0;display:grid;place-items:center;height:100vh;margin:0}
main{max-width:640px;padding:32px;border:1px solid #1e293b;border-radius:16px;background:#111a2e}
code{background:#0b1220;padding:2px 6px;border-radius:4px}a{color:#38bdf8}</style></head>
<body><main><h1>Cybbig</h1><p>Le backend est démarré. L'interface n'est pas encore compilée.</p>
<p>Exécutez <code>cd frontend &amp;&amp; npm.cmd install &amp;&amp; npm.cmd run build</code>, puis rechargez cette page.</p>
<p><a href="/api/health">Santé de l'API</a> · <a href="/api/docs">Documentation API</a></p></main></body></html>"""


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index() -> HTMLResponse:
    if FRONTEND_DIST.exists():
        return HTMLResponse((FRONTEND_DIST / "index.html").read_text(encoding="utf-8"))
    return HTMLResponse(PLACEHOLDER)


@app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
def spa(full_path: str) -> HTMLResponse:
    if full_path.startswith(("api/", "demo")):
        return JSONResponse(status_code=404, content={"detail": "Route inconnue."})  # type: ignore[return-value]
    if full_path.startswith("assets/"):
        return JSONResponse(status_code=404, content={"detail": "Ressource inconnue."})  # type: ignore[return-value]
    if FRONTEND_DIST.exists():
        return HTMLResponse((FRONTEND_DIST / "index.html").read_text(encoding="utf-8"))
    return HTMLResponse(PLACEHOLDER)
