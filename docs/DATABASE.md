# Base de données Cybbig

Cybbig utilise **SQLite** en mode WAL, avec une base unique par poste (`backend/data/cybbig.db` par défaut, configurable via `CYBBIG_DB_PATH` / `CYBBIG_DATA_DIR`). La recherche plein texte utilise **FTS5** (`knowledge_fts`).

## Tables principales

| Table | Rôle |
|---|---|
| `meta` | métadonnées et version du schéma |
| `consent` | consentement et cadre d'utilisation |
| `projects` | périmètres autorisés, niveaux d'activité, références d'autorisation |
| `scans` | analyses et leur état d'avancement |
| `findings` | résultats normalisés par moteur |
| `dependencies` | dépendances Composer et vulnérabilités OSV |
| `threat_sources` | sources de veille et leur état de synchronisation |
| `threat_items` | fiches CVE/KEV/alertes |
| `alerts` | alertes applicatives |
| `knowledge_docs` | base documentaire |
| `knowledge_fts` | index FTS5 de recherche |
| `lab_scenarios` | scénarios pédagogiques |
| `automations` | tâches planifiées |
| `automation_runs` | historique d'exécution |
| `reports` | rapports générés |
| `audit_log` | journal d'audit local |
| `assistant_messages` | historique de l'assistant IA |
| `settings` | configuration locale |
| `web_jobs` | explorations de sites web (progression, résultat) |
| `training_examples` | paires question/réponse du professeur (`pending`, `approved`, `rejected`) |
| `training_jobs` | tâches d'entraînement (enrichissement, Q/R, création du modèle) |

## Conventions

- Les secrets détectés sont masqués avant stockage dans `findings.evidence`.
- Les résultats sont liés à un projet et, le plus souvent, à un scan.
- Les données ne quittent le poste que si l'IA en ligne est configurée (voir SECURITY.md) ; il n'y a aucune télémétrie.
- Les paquets de connaissances livrés (`backend/app/knowledge_packs/`) sont installés au démarrage, versionnés par le réglage `kb_pack_<id>`.
- L'archive historique NVD CVE 2.0 est conservée sous `knowledge_sources/nvd/cve/` dans `DATA_DIR`; les flux annuels sont contrôlés via les métadonnées SHA-256 NVD et importés par lots dans `threat_items`. La progression et les empreintes indexées sont suivies dans `settings` pour permettre la reprise.
- La base peut être réinitialisée en supprimant `backend/data/cybbig.db` puis en relançant le backend.
- `PRAGMA user_version` vaut `1` dans cette version.

## Sauvegarde

Copier le dossier `backend/data/` (base + rapports) est suffisant pour sauvegarder l'état complet d'un poste Cybbig.
