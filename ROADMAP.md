# Roadmap Cybbig

## Phase 0 — Audit de l'environnement ✅
Windows 11, Python 3.11.9, Node 24.19, npm 11.17, Git 2.55. Rust absent, PHP absent, sqlite3 CLI absent (module stdlib présent). WebView2/Edge présent. Internet opérationnel.

## Phase 1 — Socle ✅
Architecture, SQLite, consentement, périmètre, journal d'audit, API locale, coquille Electron, UI React.

## Phase 2 — Threat Intelligence ✅ (MVP)
CISA KEV, NVD, CERT-FR, versions PHP, stockage, recherche, synchronisation manuelle/planifiée.

## Phase 3 — Scanner PHP ✅ (MVP)
Règles statiques, taint heuristique, secrets, configuration, dépendances Composer→OSV, rapport.

## Phase 4 — Web & API ✅ (MVP)
Analyse passive, TLS, en-têtes, cookies, formulaires, scripts, chemins exposés, OpenAPI.

## Phase 5 — Checkout ✅ (MVP)
Inventaire des scripts, indicateurs de skimming, CSP, SVG, WebSocket, formulaires de carte.

## Phase 6 — Laboratoire ✅ (MVP)
Scénarios pédagogiques, code vulnérable/corrigé, tests défensifs, données fictives.

## Phase 7 — Assistant IA ✅ (MVP)
Ollama optionnel, RAG FTS5, fallback local, historique de conversation.

## Phase 8 — Automatisations ✅ (MVP)
Planification, exécution, historique, reprise simple.

## Phase 9 — Rapports ✅ (MVP)
HTML, JSON, impression PDF.

## Phase 10 — Durcissement et distribution ⏳
- Intégration Semgrep/Psalm/PHPStan/ZAP passif.
- Signature de code, installateur MSI/NSIS.
- Chiffrement au repos optionnel.
- i18n FR/EN.
- Tests E2E Playwright.
- Migration Tauri 2 si chaîne Rust disponible.
- Règles YAML versionnées.
