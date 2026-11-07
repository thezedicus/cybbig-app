# API Cybbig

L'API est locale uniquement (`127.0.0.1:8765`), servie par FastAPI. La documentation interactive est disponible sur `/api/docs`.

## Système

- `GET /api/health` — état du service, base, planificateur, moteurs
- `GET /api/consent` — statut et texte du cadre d'utilisation
- `POST /api/consent` — accepter le cadre
- `GET /api/settings` — paramètres locaux (clé NVD masquée)
- `PUT /api/settings` — mise à jour des paramètres autorisés
- `GET /api/audit` — journal d'audit
- `GET /api/engines` — capacités et limites des moteurs

## Projets et périmètre

- `GET /api/projects` — liste des projets
- `POST /api/projects` — créer un projet
- `GET /api/projects/{id}` — détail d'un projet
- `PUT /api/projects/{id}` — mettre à jour
- `DELETE /api/projects/{id}` — supprimer

## Analyses

- `GET /api/scans` — liste (filtres `project_id`, `kind`, `status`)
- `POST /api/scans` — démarrer une analyse
- `GET /api/scans/{id}` — détail et résultats
- `POST /api/scans/{id}/cancel` — annuler
- `POST /api/scans/{id}/rerun` — relancer

Kinds : `php`, `web`, `api`, `checkout`.

## Résultats

- `GET /api/findings` — liste paginée et filtrée
- `GET /api/findings/{id}` — détail
- `PATCH /api/findings/{id}` — statut (`open`, `acknowledged`, `fixed`, `accepted_risk`, `false_positive`)
- `GET /api/findings/{id}/export` — export JSON

## Threat Intelligence

- `GET /api/intel/sources` — sources configurées
- `POST /api/intel/sync` — synchroniser (`{"sources": [...]}` optionnel)
- `POST /api/intel/archive/start` — lancer l'import reprenable des flux annuels CVE NVD 2.0 (2002 à l'année courante)
- `GET /api/intel/archive/status` — progression, année en cours, empreintes et erreurs éventuelles de l'import
- `GET /api/intel/items` — recherche (`q`, `source`, `severity`, `exploited`, `limit`, `offset`)
- `GET /api/intel/items/{id}` — détail
- `GET /api/intel/stats` — statistiques

## Connaissances

- `GET /api/knowledge` — liste/recherche (`q`, `category`, `limit`, `offset`)
- `POST /api/knowledge` — créer
- `GET /api/knowledge/{id}` — détail
- `PUT /api/knowledge/{id}` — mettre à jour
- `DELETE /api/knowledge/{id}` — supprimer
- `POST /api/knowledge/import` — importer un fichier texte

## Assistant IA

- `GET /api/assistant/status` — état Ollama
- `POST /api/assistant/chat` — question (`message`, `project_id`, `model`)
- `GET /api/assistant/history` — historique
- `DELETE /api/assistant/history` — effacer
- `GET /api/assistant/search` — recherche documentaire

## Rapports

- `GET /api/reports` — liste
- `POST /api/reports` — générer (`project_id`, `scan_id`, `title`)
- `GET /api/reports/{id}` — métadonnées
- `GET /api/reports/{id}/download` — rapport HTML
- `GET /api/reports/{id}/json` — données JSON
- `DELETE /api/reports/{id}` — supprimer

## Automatisations

- `GET /api/automations` — liste et état du planificateur
- `POST /api/automations` — créer
- `PATCH /api/automations/{id}` — activer/désactiver
- `POST /api/automations/{id}/run` — exécuter
- `DELETE /api/automations/{id}` — supprimer

## Laboratoire

- `GET /api/lab/scenarios` — liste (`category`)
- `GET /api/lab/scenarios/{id|slug}` — détail
- `POST /api/lab/validate` — validation par motifs (`code`, `language`)

## Alertes

- `GET /api/alerts` — liste (`unread_only`, `limit`)
- `PATCH /api/alerts/{id}/read` — marquer lu
- `POST /api/alerts/read-all` — tout marquer lu
- `DELETE /api/alerts/{id}` — supprimer

## Tableau de bord

- `GET /api/dashboard` — agrégats, tendance, résultats prioritaires

## Assistant IA — serveurs local et en ligne

- `GET /api/assistant/status?refresh=` — état des deux serveurs (`local`, `cloud`), serveur actif (`provider`), mode (`preferred`)
- `PUT /api/assistant/model` — `{model, provider: local|cloud}` : modèle actif de chaque serveur
- `POST /api/assistant/chat/stream` — événements `meta`, `token`, `notice` (bascule vers le local), `done` (`provider`)
- Réglages : `ai_provider` (`auto|local|cloud`), `ai_allow_cloud`, `ollama_cloud_url`, `ollama_cloud_key` (masquée), `ollama_cloud_model`, `ai_warmup`, `ai_browse`

## Ressources du PC

- `GET /api/resources` — matériel, charge en direct, modèles chargés dans Ollama, options appliquées, recommandations
- `PUT /api/resources/profile` — `{profile: auto|eco|balanced|max, num_thread?}`
- `POST /api/resources/warmup` — précharge le modèle local

## Visite de sites web

- `GET /api/web/search?q=...&lang=fr&limit=1..20` — recherche DuckDuckGo sans clé et Brave facultatif ; résultats dédupliqués avec titre, URL, extrait et moteur source. Sans `limit`, 10 résultats standard ou jusqu'à 20 en mode propriétaire étendu.
- `POST /api/web/visit` — `{url, selector?, save?, category?, tags?}` : lit une page publique ; `save` l'ajoute à la base
- `POST /api/web/crawl` — `{url, max_pages≤25, depth≤2, selector?, category?, tags?}` : exploration du même site en tâche de fond
- `GET /api/web/jobs`, `GET /api/web/jobs/{id}`, `POST /api/web/jobs/{id}/cancel`
- Session propriétaire : `GET/PUT /api/admin/web-research-mode` — lecture/activation du mode de recherche étendue (le `PUT` reçoit `{enabled: boolean}`).

## Base de connaissances (ajouts)

- `POST /api/knowledge/bulk` — `{text, format?: json|jsonl|csv, category?}` : jusqu'à 500 fiches, sans doublon (titre + catégorie)
- `GET /api/knowledge?category=Groupe · *` — un `*` final filtre un groupe de catégories

## Atelier IA (session administrateur requise)

- `GET /api/admin/code/search?q=` — fichiers du logiciel dont le nom correspond
- `POST /api/admin/code/assist` — `{instruction, paths≤4, history?, model?}` : flux NDJSON `meta`, `token`, `error`, `done` (blocs proposés et vérifiés, avec différences)
- `POST /api/admin/code/assist/preview` — vérifie des blocs `{path, search, replace}`
- `POST /api/admin/code/assist/apply` — applique les blocs sélectionnés (tout ou rien, sauvegarde préalable)

## Entraînement

- `POST /api/training/auto-run` — lance un cycle automatique (fiches, Q/R, approbation, modèle local) ; réglages `training_auto`, `training_auto_hours`, `training_auto_approve`, `ai_provider = auto|local|cloud|training`

- `GET /api/training` — état (professeur, bibliothèque, exemples, modèle personnalisé, tâches)
- `GET /api/training/curriculum` — sujets du programme et état de rédaction
- `POST /api/training/enrich` — `{limit, teacher?}` ; `POST /api/training/qa` — `{limit, per_doc, teacher?}` ; `POST /api/training/model` — `{name, base?, max_examples, activate}` ; `DELETE /api/training/model`
- `GET /api/training/jobs/{id}`, `POST /api/training/jobs/{id}/cancel`
- `GET /api/training/examples?status=`, `PATCH /api/training/examples/{id}`, `POST /api/training/examples/bulk`
- `GET /api/training/export?include_pending=` — JSONL conversationnel
