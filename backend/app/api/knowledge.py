from __future__ import annotations

import csv
import io
import json
import re
import sqlite3
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from .. import db
from ..services.ai import _fts_query
from ..utils import new_id, now_iso, truncate

router = APIRouter(prefix="/knowledge", tags=["base de connaissances"])


class DocCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    category: str = Field(default="Général", max_length=100)
    content: str = Field(min_length=1, max_length=200_000)
    source: str = Field(default="", max_length=500)
    tags: str = Field(default="", max_length=500)


class DocUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=300)
    category: str | None = Field(default=None, max_length=100)
    content: str | None = Field(default=None, max_length=200_000)
    source: str | None = Field(default=None, max_length=500)
    tags: str | None = Field(default=None, max_length=500)


def _search(q: str, category: str, limit: int) -> list[dict[str, Any]]:
    # « Groupe · * » filtre tout un groupe de catégories (préfixe) ; sans « * », la catégorie doit correspondre exactement.
    like_cat = category[:-1] + "%" if category.endswith("*") else category
    if q:
        fts = _fts_query(q)
        try:
            if fts:
                rows = db.fetch_all(
                    """SELECT d.id,d.title,d.category,d.source,d.tags,d.updated_at,
                              snippet(knowledge_fts,2,'« ',' »',' … ',28) AS excerpt
                       FROM knowledge_fts JOIN knowledge_docs d ON d.rowid=knowledge_fts.rowid
                       WHERE knowledge_fts MATCH ? AND (?='' OR d.category=? OR d.category LIKE ?) ORDER BY bm25(knowledge_fts) LIMIT ?""",
                    (fts, category, category, like_cat, limit),
                )
                if rows:
                    return rows
        except sqlite3.OperationalError:
            pass
        like = f"%{q[:120]}%"
        return db.fetch_all(
            "SELECT id,title,category,source,tags,updated_at,substr(content,1,320) AS excerpt "
            "FROM knowledge_docs WHERE (title LIKE ? OR content LIKE ? OR tags LIKE ?) "
            "AND (?='' OR category=? OR category LIKE ?) ORDER BY updated_at DESC LIMIT ?",
            (like, like, like, category, category, like_cat, limit),
        )
    return db.fetch_all(
        "SELECT id,title,category,source,tags,updated_at,substr(content,1,320) AS excerpt "
        "FROM knowledge_docs WHERE (?='' OR category=? OR category LIKE ?) ORDER BY updated_at DESC LIMIT ?",
        (category, category, like_cat, limit),
    )


@router.get("")
def list_docs(q: str = "", category: str = "", limit: int = 100) -> dict[str, Any]:
    rows = _search(q, category, min(300, max(1, limit)))
    for row in rows:
        row["excerpt"] = re.sub(r"\s+", " ", row.get("excerpt") or "").strip()
    categories = db.fetch_all("SELECT category, COUNT(*) AS count FROM knowledge_docs GROUP BY category ORDER BY category")
    return {"items": rows, "categories": categories, "total": len(rows)}


@router.get("/categories")
def categories() -> dict[str, Any]:
    return {"items": db.fetch_all("SELECT category, COUNT(*) AS count FROM knowledge_docs GROUP BY category ORDER BY category")}


@router.post("")
def create_doc(payload: DocCreate) -> dict[str, Any]:
    doc_id = new_id("kb")
    now = now_iso()
    db.execute(
        "INSERT INTO knowledge_docs(id,title,category,content,source,tags,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)",
        (doc_id, payload.title.strip(), payload.category.strip(), payload.content, payload.source.strip(), payload.tags.strip(), now, now),
    )
    db.audit("knowledge_created", {"id": doc_id, "title": payload.title})
    return db.fetch_one("SELECT * FROM knowledge_docs WHERE id=?", (doc_id,)) or {}


class BulkPayload(BaseModel):
    text: str = Field(min_length=2, max_length=5_000_000)
    format: str = Field(default="auto", max_length=8)  # auto | json | jsonl | csv
    category: str = Field(default="Import", max_length=100)


def _as_tags(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        value = ",".join(str(v).strip() for v in value if str(v).strip())
    return str(value or "").strip()[:500]


def _guess_format(text: str) -> str:
    if text.startswith("["):
        return "json"
    if text.startswith("{"):
        # Plusieurs objets, un par ligne : JSONL ; un seul objet (éventuellement sur plusieurs lignes) : JSON.
        return "jsonl" if len([l for l in text.splitlines() if l.strip().startswith("{")]) > 1 and text.splitlines()[0].rstrip().endswith("}") else "json"
    return "csv"


def parse_bulk(text: str, fmt: str, default_category: str) -> list[dict[str, str]]:
    """Accepte un tableau JSON, du JSONL ou un CSV (colonnes title, content, category, source, tags).

    Les noms de champs d'autres bases sont reconnus : summary + content, category_slug, technologies.
    """
    text = text.strip()
    fmt = fmt if fmt in {"json", "jsonl", "csv"} else _guess_format(text)
    rows: list[Any]
    if fmt == "json":
        data = json.loads(text)
        rows = data if isinstance(data, list) else data.get("items") or data.get("documents") or [data]
    elif fmt == "jsonl":
        rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    else:
        rows = list(csv.DictReader(io.StringIO(text)))
    docs = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        title = str(row.get("title") or row.get("name") or row.get("titre") or "").strip()
        body = str(row.get("content") or row.get("text") or row.get("contenu") or "").strip()
        summary = str(row.get("summary") or row.get("resume") or "").strip()
        if summary and body and summary not in body:
            body = f"{summary}\n\n{body}"
        body = body or summary
        if not title or not body:
            continue
        docs.append({
            "title": title[:300], "content": body[:200_000],
            "category": str(row.get("category") or row.get("category_slug") or row.get("categorie") or default_category).strip()[:100] or default_category,
            "source": str(row.get("source") or row.get("url") or row.get("source_url") or "import en lot").strip()[:500],
            "tags": _as_tags(row.get("tags") or row.get("technologies") or "import"),
        })
    return docs


@router.post("/bulk")
def bulk_import(payload: BulkPayload) -> dict[str, Any]:
    """Ajoute plusieurs fiches d'un coup. Une fiche de même titre et même catégorie n'est pas dupliquée."""
    try:
        docs = parse_bulk(payload.text, payload.format, payload.category.strip() or "Import")
    except (ValueError, TypeError, AttributeError, csv.Error) as exc:
        raise HTTPException(status_code=400, detail=f"Format illisible : {exc}") from exc
    if not docs:
        raise HTTPException(status_code=400, detail="Aucune fiche valide (champs title et content requis).")
    if len(docs) > 500:
        raise HTTPException(status_code=400, detail="Maximum 500 fiches par import.")
    added = skipped = 0
    now = now_iso()
    with db.db_cursor() as conn:
        for doc in docs:
            if conn.execute("SELECT 1 FROM knowledge_docs WHERE title=? AND category=?", (doc["title"], doc["category"])).fetchone():
                skipped += 1
                continue
            conn.execute("INSERT INTO knowledge_docs(id,title,category,content,source,tags,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)",
                         (new_id("kb"), doc["title"], doc["category"], doc["content"], doc["source"], doc["tags"], now, now))
            added += 1
    db.audit("knowledge_bulk_imported", {"added": added, "skipped": skipped})
    return {"added": added, "skipped": skipped, "total": len(docs)}


@router.get("/{doc_id}")
def get_doc(doc_id: str) -> dict[str, Any]:
    row = db.fetch_one("SELECT * FROM knowledge_docs WHERE id=?", (doc_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Document introuvable.")
    return row


@router.put("/{doc_id}")
def update_doc(doc_id: str, payload: DocUpdate) -> dict[str, Any]:
    if not db.fetch_one("SELECT id FROM knowledge_docs WHERE id=?", (doc_id,)):
        raise HTTPException(status_code=404, detail="Document introuvable.")
    data = payload.dict(exclude_unset=True)
    if not data:
        return db.fetch_one("SELECT * FROM knowledge_docs WHERE id=?", (doc_id,)) or {}
    fields = []
    params: list[Any] = []
    for key in ("title", "category", "content", "source", "tags"):
        if key in data:
            fields.append(f"{key}=?")
            params.append(data[key])
    fields.append("updated_at=?")
    params.append(now_iso())
    params.append(doc_id)
    db.execute(f"UPDATE knowledge_docs SET {', '.join(fields)} WHERE id=?", params)
    db.audit("knowledge_updated", {"id": doc_id, "fields": list(data.keys())})
    return db.fetch_one("SELECT * FROM knowledge_docs WHERE id=?", (doc_id,)) or {}


@router.delete("/{doc_id}")
def delete_doc(doc_id: str) -> dict[str, Any]:
    if not db.fetch_one("SELECT id FROM knowledge_docs WHERE id=?", (doc_id,)):
        raise HTTPException(status_code=404, detail="Document introuvable.")
    db.execute("DELETE FROM knowledge_docs WHERE id=?", (doc_id,))
    db.audit("knowledge_deleted", {"id": doc_id})
    return {"ok": True}


@router.post("/import")
async def import_doc(file: UploadFile = File(...), category: str = Form("Import")) -> dict[str, Any]:
    data = await file.read(2_000_001)
    if len(data) > 2_000_000:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 2 Mo).")
    try:
        content = data.decode("utf-8")
    except UnicodeDecodeError:
        content = data.decode("latin-1")
    title = (file.filename or "Document importé").rsplit(".", 1)[0][:300]
    if (file.filename or "").lower().endswith((".html", ".htm")):
        try:
            import trafilatura
            content = trafilatura.extract(content, include_tables=True, favor_recall=True) or content
        except Exception:  # noqa: BLE001 — HTML illisible : on conserve le texte brut
            pass
    doc_id = new_id("kb")
    now = now_iso()
    db.execute(
        "INSERT INTO knowledge_docs(id,title,category,content,source,tags,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)",
        (doc_id, title, category[:100], content[:200_000], file.filename or "import", "import", now, now),
    )
    db.audit("knowledge_imported", {"id": doc_id, "filename": file.filename})
    return {"id": doc_id, "title": title, "size": len(data)}
