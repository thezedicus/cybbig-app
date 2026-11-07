# Architecture Cybbig

## 1. Vue d'ensemble

```
┌──────────────────────────────────────────────────────────────┐
│ Electron (fenêtre Windows)                                    │
│  └─ React + TypeScript + Vite (UI, thème sombre/clair)        │
│        ↕ HTTP localhost 127.0.0.1:8765                        │
│ FastAPI (backend Python, API locale, fichiers statiques)      │
│  ├─ Orchestrateur de scans (ThreadPoolExecutor)               │
│  ├─ Moteurs : PHP · Web · API · Checkout · Threat Intel       │
│  ├─ Service de connaissances commun (SQLite FTS5 + RAG)       │
│  ├─ Assistant IA et agents d'amélioration (Ollama local)      │
│  ├─ Planificateur (thread, intervalle, reprise)               │
│  └─ SQLite (WAL) + rapports HTML/JSON sur disque              │
└──────────────────────────────────────────────────────────────┘
```

## 2. Choix techniques

| Couche | Choix | Justification |
|---|---|---|
| Desktop | Electron 45 | Rust/Tauri absent de la machine au moment de l'audit ; Electron fournit une vraie fenêtre Windows sans chaîne Rust. Une migration Tauri est prévue. |
| UI | React 19 + TypeScript + Vite | Écosystème mature, build statique simple. |
| Backend | Python 3.11 + FastAPI + Uvicorn | Productivité, accès aux bibliothèques réseau/SSL, orchestration. |
| DB | SQLite 3.45 (stdlib) | Local, zéro serveur, WAL, FTS5. |
| IA | Ollama (local, et en ligne sur option) | Local par défaut ; Ollama Cloud si une clé est saisie ; fallback déterministe sans modèle. |
| Rapports | HTML autonome + JSON | Portable, imprimable en PDF. |
| Tests | pytest + httpx/requests | Vérification des moteurs et du périmètre. |

Le poste ne dispose pas de `rustc`/`cargo`, et `npm.ps1` est bloqué par la stratégie PowerShell (contournement : `npm.cmd`). Ces contraintes sont documentées dans [DECISIONS.md](DECISIONS.md).

## 3. Modules

1. **Dashboard** : agrégats, tendance de risque, état des moteurs.
2. **Projets** : périmètre, autorisation, domaines/chemins, audit.
3. **Threat Intelligence** : CISA KEV, NVD 2.0, CERT-FR RSS, versions PHP.
4. **Scanner PHP** : règles, taint heuristique, secrets, configuration, dépendances Composer via OSV.
5. **Web & API** : analyse passive HTTP/TLS/en-têtes/HTML/formulaires/scripts ; audit OpenAPI.
6. **Checkout** : intégrité de la page de paiement, indicateurs de skimming, inventaire des scripts.
7. **Laboratoire** : scénarios, code vulnérable/corrigé, validation défensive.
8. **Service de connaissances** : base FTS5 interrogée par l'assistant, les tâches IA, l'atelier de code, les générateurs et les agents ; les nouveaux documents sont disponibles au prochain appel RAG.
9. **Agents d'amélioration** : rapprochement périodique des connaissances, analyses, erreurs et décisions du propriétaire ; les agents proposent des réglages et changements, sans modifier le code automatiquement.
10. **Assistant IA** : contexte projet/résultats + service de connaissances, Ollama local.
11. **Connaissances** : FTS5, paquets versionnés et fiches importées.
12. **Automatisations** : sync intel, scans planifiés, historique.
13. **Rapports** : synthèse, preuves, remédiation, disclaimers.
14. **Paramètres/Conformité** : consentement, Ollama (local et en ligne), rétention, export.
15. **Ressources** (`services/resources.py`) : matériel, charge, profils de performance appliqués à Ollama.
16. **Visite de sites** (`services/webfetch.py`) : lecture publique contrôlée, Scrapling, exploration.
17. **Bibliothèque** (`knowledge_packs/`) : paquets de fiches versionnés installés au démarrage ; importations manuelles restent conservées.
18. **Entraînement** (`services/training.py`) : professeur en ligne, exemples relus, modèle local personnalisé, export JSONL.

## 4. Flux d'un scan

1. L'UI crée un projet (périmètre + autorisation) et demande un scan.
2. Le backend vérifie le consentement et le périmètre (`services/scope.py`).
3. Un job est créé en base et exécuté par `services/jobs.py`.
4. Le moteur écrit sa progression et ses résultats normalisés (`findings`).
5. L'UI interroge `/api/scans/{id}` jusqu'à `completed`.
6. Le rapport est généré à la demande (`services/reports.py`).

## 5. Modèle de sécurité

- Écoute uniquement sur `127.0.0.1`.
- CORS limité aux origines locales de développement.
- Aucune exécution de code scanné.
- Aucune requête active d'exploitation. Les tests de chemins exposés utilisent des requêtes GET tronquées et ne conservent pas le contenu.
- Périmètre obligatoire : localhost ou domaine autorisé + référence d'autorisation.
- Limites : temps, taille, nombres de fichiers/pages, débit.
- Journal d'audit de chaque action sensible.
- Preuves expurgées (secrets masqués).
- Les niveaux A–E contextualisent le risque, sans bloquer la recherche documentaire.

## 6. Arborescence

```
cybbig/
├─ backend/
│  ├─ app/
│  │  ├─ api/            # routeurs FastAPI
│  │  ├─ services/       # moteurs et orchestration
│  │  ├─ db.py           # schéma, migrations, accès SQLite
│  │  ├─ main.py         # application FastAPI + static SPA
│  │  └─ seed.py         # données initiales
│  ├─ samples/           # projet PHP de démonstration (non exécuté)
│  ├─ data/              # SQLite, rapports (généré)
│  └─ tests/
├─ frontend/             # React/TS/Vite
├─ desktop/              # processus principal Electron
└─ scripts/              # setup, start, test, build
```

## 7. Évolutions prévues

- Intégration d'outils externes : Semgrep, Psalm, PHPStan, Composer Audit, OWASP ZAP (mode passif).
- Packaging Tauri (si Rust installé) ou Electron Builder signé.
- Moteur de règles YAML versionnées et importables.
- Embeddings locaux pour un RAG plus riche.
- Connecteurs Wazuh/osquery en lecture seule.
- i18n FR/EN complète.
