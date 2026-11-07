# Modules Cybbig

## Moteurs

- **PHP** (`services/engines/php_scanner.py`) : analyse statique de code PHP, règles, taint heuristique, secrets, configuration, dépendances Composer avec OSV.
- **Web** (`services/engines/web_scanner.py`) : analyse passive HTTP/HTTPS, en-têtes, TLS, cookies, formulaires, scripts, chemins exposés.
- **API** (`services/engines/api_scanner.py`) : audit de spécification OpenAPI, authentification, BOLA (revue), idempotence.
- **Checkout** (`services/engines/checkout_scanner.py`) : intégrité d'une page de paiement, SRI, SVG, WebSocket, indicateurs de skimming.
- **Intel** (`services/intel.py`) : collecte CISA KEV, NVD, CERT-FR, versions PHP.
- **Lab** (`services/lab.py`) : scénarios pédagogiques et validation par motifs.
- **Assistant** (`services/ai.py`) : Ollama optionnel + RAG FTS5 + analyste déterministe hors ligne.

## Interfaces

- **Desktop** : Electron 45 charge l'interface React/Vite servie par le backend local.
- **Frontend** : React 19 + React Router 7 + Vite 8, CSS maison.
- **Backend** : FastAPI + Uvicorn sur `127.0.0.1:8765`.
- **Stockage** : SQLite WAL + FTS5.
- **Rapports** : HTML et JSON, impression PDF via le navigateur.

## Sécurité par conception

- Écoute réseau uniquement sur `127.0.0.1`.
- Analyses passives ou statiques, aucun exploit.
- Consentement et périmètre obligatoires.
- Secrets masqués dans les preuves.
- Aucune télémétrie.
- IA en ligne uniquement sur configuration explicite (clé API), secrets masqués avant envoi.
- Pages web lues = données non fiables, adresses internes refusées.
- Electron : `contextIsolation`, `sandbox`, navigation externe contrôlée, téléchargements locaux.
