PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS consent (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    version TEXT NOT NULL,
    accepted_at TEXT NOT NULL,
    user_name TEXT,
    organization TEXT,
    purpose TEXT,
    text_hash TEXT
);

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    client TEXT DEFAULT '',
    description TEXT DEFAULT '',
    path TEXT DEFAULT '',
    base_url TEXT DEFAULT '',
    environment TEXT DEFAULT 'laboratory',
    authorization_ref TEXT DEFAULT '',
    authorized_by TEXT DEFAULT '',
    authorized_at TEXT,
    authorization_confirmed INTEGER NOT NULL DEFAULT 0,
    scope_domains TEXT NOT NULL DEFAULT '[]',
    scope_paths TEXT NOT NULL DEFAULT '[]',
    activity_level TEXT NOT NULL DEFAULT 'B',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scans (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    mode TEXT NOT NULL DEFAULT 'passive',
    target TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'queued',
    progress INTEGER NOT NULL DEFAULT 0,
    message TEXT DEFAULT '',
    config_json TEXT NOT NULL DEFAULT '{}',
    summary_json TEXT NOT NULL DEFAULT '{}',
    error TEXT,
    started_at TEXT,
    finished_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_scans_project ON scans(project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_scans_status ON scans(status);

CREATE TABLE IF NOT EXISTS findings (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    scan_id TEXT,
    engine TEXT NOT NULL,
    rule_id TEXT NOT NULL,
    category TEXT DEFAULT '',
    title TEXT NOT NULL,
    severity TEXT NOT NULL,
    confidence TEXT NOT NULL DEFAULT 'medium',
    description TEXT DEFAULT '',
    evidence TEXT DEFAULT '',
    file_path TEXT DEFAULT '',
    line_start INTEGER,
    line_end INTEGER,
    url TEXT DEFAULT '',
    cwe TEXT DEFAULT '',
    owasp TEXT DEFAULT '',
    remediation TEXT DEFAULT '',
    references_json TEXT DEFAULT '[]',
    fingerprint TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    risk_score REAL NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY(scan_id) REFERENCES scans(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_findings_project ON findings(project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_findings_scan ON findings(scan_id);
CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity, status);
CREATE INDEX IF NOT EXISTS idx_findings_created ON findings(created_at);
CREATE INDEX IF NOT EXISTS idx_findings_dashboard ON findings(project_id, severity, status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_findings_fingerprint ON findings(scan_id, fingerprint);

CREATE TABLE IF NOT EXISTS dependencies (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    scan_id TEXT,
    ecosystem TEXT NOT NULL,
    package TEXT NOT NULL,
    version TEXT DEFAULT '',
    vulnerable INTEGER NOT NULL DEFAULT 0,
    vuln_id TEXT DEFAULT '',
    severity TEXT DEFAULT '',
    summary TEXT DEFAULT '',
    fixed_version TEXT DEFAULT '',
    source TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY(scan_id) REFERENCES scans(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_dependencies_scan ON dependencies(scan_id);

CREATE TABLE IF NOT EXISTS threat_sources (
    name TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    url TEXT NOT NULL,
    kind TEXT NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1,
    last_sync_at TEXT,
    status TEXT NOT NULL DEFAULT 'never',
    items_count INTEGER NOT NULL DEFAULT 0,
    error TEXT
);

CREATE TABLE IF NOT EXISTS threat_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    external_id TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT DEFAULT '',
    severity TEXT DEFAULT 'unknown',
    cvss REAL,
    published_at TEXT,
    modified_at TEXT,
    product TEXT DEFAULT '',
    cve TEXT DEFAULT '',
    exploited INTEGER NOT NULL DEFAULT 0,
    url TEXT DEFAULT '',
    tags_json TEXT NOT NULL DEFAULT '[]',
    raw_json TEXT NOT NULL DEFAULT '{}',
    fetched_at TEXT NOT NULL,
    UNIQUE(source, external_id)
);
CREATE INDEX IF NOT EXISTS idx_threat_cve ON threat_items(cve);
CREATE INDEX IF NOT EXISTS idx_threat_published ON threat_items(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_threat_severity ON threat_items(severity);
CREATE VIRTUAL TABLE IF NOT EXISTS threat_fts USING fts5(
    title, summary, product, cve,
    content='threat_items', content_rowid='id'
);
CREATE TRIGGER IF NOT EXISTS threat_ai AFTER INSERT ON threat_items BEGIN
    INSERT INTO threat_fts(rowid, title, summary, product, cve)
    VALUES (new.id, new.title, new.summary, new.product, new.cve);
END;
CREATE TRIGGER IF NOT EXISTS threat_ad AFTER DELETE ON threat_items BEGIN
    INSERT INTO threat_fts(threat_fts, rowid, title, summary, product, cve)
    VALUES ('delete', old.id, old.title, old.summary, old.product, old.cve);
END;
CREATE TRIGGER IF NOT EXISTS threat_au AFTER UPDATE ON threat_items BEGIN
    INSERT INTO threat_fts(threat_fts, rowid, title, summary, product, cve)
    VALUES ('delete', old.id, old.title, old.summary, old.product, old.cve);
    INSERT INTO threat_fts(rowid, title, summary, product, cve)
    VALUES (new.id, new.title, new.summary, new.product, new.cve);
END;

CREATE TABLE IF NOT EXISTS alerts (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    source TEXT DEFAULT '',
    severity TEXT NOT NULL DEFAULT 'info',
    title TEXT NOT NULL,
    message TEXT DEFAULT '',
    link TEXT DEFAULT '',
    read INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at DESC);

CREATE TABLE IF NOT EXISTS knowledge_docs (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'Général',
    content TEXT NOT NULL,
    source TEXT DEFAULT '',
    tags TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
    title, category, content, tags,
    content='knowledge_docs', content_rowid='rowid'
);
CREATE TRIGGER IF NOT EXISTS knowledge_ai AFTER INSERT ON knowledge_docs BEGIN
    INSERT INTO knowledge_fts(rowid, title, category, content, tags)
    VALUES (new.rowid, new.title, new.category, new.content, new.tags);
END;
CREATE TRIGGER IF NOT EXISTS knowledge_ad AFTER DELETE ON knowledge_docs BEGIN
    INSERT INTO knowledge_fts(knowledge_fts, rowid, title, category, content, tags)
    VALUES ('delete', old.rowid, old.title, old.category, old.content, old.tags);
END;
CREATE TRIGGER IF NOT EXISTS knowledge_au AFTER UPDATE ON knowledge_docs BEGIN
    INSERT INTO knowledge_fts(knowledge_fts, rowid, title, category, content, tags)
    VALUES ('delete', old.rowid, old.title, old.category, old.content, old.tags);
    INSERT INTO knowledge_fts(rowid, title, category, content, tags)
    VALUES (new.rowid, new.title, new.category, new.content, new.tags);
END;

CREATE TABLE IF NOT EXISTS lab_scenarios (
    id TEXT PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    level TEXT NOT NULL DEFAULT 'B',
    description TEXT NOT NULL,
    objective TEXT NOT NULL,
    vulnerable_code TEXT NOT NULL,
    secure_code TEXT NOT NULL,
    test_steps TEXT NOT NULL,
    detection TEXT NOT NULL DEFAULT '',
    references_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS automations (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,
    interval_minutes INTEGER NOT NULL DEFAULT 1440,
    config_json TEXT NOT NULL DEFAULT '{}',
    enabled INTEGER NOT NULL DEFAULT 1,
    last_run_at TEXT,
    next_run_at TEXT,
    last_status TEXT DEFAULT 'never',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS automation_runs (
    id TEXT PRIMARY KEY,
    automation_id TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL DEFAULT 'running',
    log TEXT DEFAULT '',
    FOREIGN KEY(automation_id) REFERENCES automations(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_automation_runs ON automation_runs(automation_id, started_at DESC);

-- Opportunités rémunérées repérées par les recherches publiques planifiées.
CREATE TABLE IF NOT EXISTS income_opportunities (
    id TEXT PRIMARY KEY,
    method TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT '',
    snippet TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'new',
    note TEXT NOT NULL DEFAULT '',
    proposal_draft TEXT NOT NULL DEFAULT '',
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(url, method)
);
CREATE INDEX IF NOT EXISTS idx_income_opportunities_status ON income_opportunities(status, last_seen_at DESC);

CREATE TABLE IF NOT EXISTS reports (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    scan_id TEXT,
    kind TEXT NOT NULL,
    title TEXT NOT NULL,
    path TEXT NOT NULL,
    meta_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_reports_project ON reports(project_id, created_at DESC);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor TEXT NOT NULL DEFAULT 'local',
    action TEXT NOT NULL,
    details TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at DESC);

CREATE TABLE IF NOT EXISTS assistant_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    context_json TEXT NOT NULL DEFAULT '{}',
    model TEXT DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS terminal_guardrails (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    command TEXT NOT NULL,
    working_dir TEXT NOT NULL DEFAULT 'root',
    description TEXT NOT NULL DEFAULT '',
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS terminal_runs (
    id TEXT PRIMARY KEY,
    guardrail_id TEXT,
    command TEXT NOT NULL,
    working_dir TEXT NOT NULL DEFAULT 'root',
    started_at TEXT NOT NULL,
    finished_at TEXT,
    exit_code INTEGER,
    stdout TEXT NOT NULL DEFAULT '',
    stderr TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Confidentialité : proxies gérés par l'utilisateur (gestionnaire type ProxySwitcher).
CREATE TABLE IF NOT EXISTS proxies (
    id TEXT PRIMARY KEY,
    label TEXT NOT NULL DEFAULT '',
    scheme TEXT NOT NULL DEFAULT 'http',
    host TEXT NOT NULL,
    port INTEGER NOT NULL,
    username TEXT DEFAULT '',
    password TEXT DEFAULT '',
    enabled INTEGER NOT NULL DEFAULT 1,
    note TEXT DEFAULT '',
    last_test_at TEXT,
    last_test_ok INTEGER,
    last_test_ip TEXT DEFAULT '',
    last_test_ms INTEGER,
    created_at TEXT NOT NULL
);

-- Confidentialité : profils VPN = pointeurs vers les fichiers de configuration
-- fournis par l'utilisateur (WireGuard .conf / OpenVPN .ovpn de Proton, Hide.me, etc.).
-- Aucun identifiant VPN n'est stocké par Cybbig.
CREATE TABLE IF NOT EXISTS vpn_profiles (
    id TEXT PRIMARY KEY,
    label TEXT NOT NULL DEFAULT '',
    provider TEXT NOT NULL DEFAULT '',
    kind TEXT NOT NULL DEFAULT 'wireguard',
    config_path TEXT NOT NULL,
    created_at TEXT NOT NULL
);


-- Résultats produits par le moteur IA de fond (synthèses, digest, plan de la semaine).
CREATE TABLE IF NOT EXISTS ai_cache (
    key TEXT PRIMARY KEY,
    task TEXT NOT NULL,
    params_json TEXT NOT NULL DEFAULT '{}',
    content TEXT NOT NULL DEFAULT '',
    model TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

-- Propositions d'amélioration produites par les agents IA de chaque module.
CREATE TABLE IF NOT EXISTS ai_suggestions (
    id TEXT PRIMARY KEY,
    module TEXT NOT NULL,
    title TEXT NOT NULL,
    detail TEXT NOT NULL DEFAULT '',
    kind TEXT NOT NULL DEFAULT 'process',
    impact TEXT NOT NULL DEFAULT 'moyen',
    setting_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'new',
    model TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    decided_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_ai_suggestions_module ON ai_suggestions(module, status, created_at DESC);

-- Visites de sites web (exploration de plusieurs pages d'un même site vers la base de connaissances).
CREATE TABLE IF NOT EXISTS web_jobs (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL DEFAULT 'crawl',
    url TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    progress_json TEXT NOT NULL DEFAULT '{}',
    result_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    finished_at TEXT
);

-- Entraînement : exemples question/réponse produits par le modèle « professeur » (en ligne) à partir de la bibliothèque.
CREATE TABLE IF NOT EXISTS training_examples (
    id TEXT PRIMARY KEY,
    doc_id TEXT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    teacher TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    UNIQUE(doc_id, question)
);
CREATE INDEX IF NOT EXISTS idx_training_status ON training_examples(status, created_at DESC);

-- Tâches d'entraînement (enrichissement de la bibliothèque, génération de Q/R, création du modèle local).
CREATE TABLE IF NOT EXISTS training_jobs (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    progress_json TEXT NOT NULL DEFAULT '{}',
    result_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    finished_at TEXT
);
