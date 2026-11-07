# Cybbig

**Cybbig** est un poste de travail de cybersécurité défensive pour Windows. Il regroupe la veille sur les menaces, l'audit statique d'applications PHP, l'analyse passive d'applications Web/API, la surveillance de l'intégrité d'une page de paiement, un laboratoire de formation, un assistant IA local et un moteur de rapports.

> Version 0.4.0 — local-first, passif par défaut ; IA en ligne optionnelle.

## Téléchargements

- **[⬇ Télécharger tous les fichiers du dépôt (.zip)](../../archive/refs/heads/main.zip)** : code source complet.
- **[⬇ Installateurs Windows (dernière version)](../../releases/latest)** : application prête à installer.

Le dépôt ne contient aucune clé API, aucun mot de passe et aucun accès administrateur :
uniquement l'accès utilisateur standard (voir [Vos clés API](#vos-clés-api) et [Administration](#administration)).

## Installer sur Windows

Sur la page **[Releases](../../releases/latest)**, choisissez :

| Fichier | Pour qui |
|---|---|
| `Cybbig-Setup-<version>.zip` | **Recommandé.** Décompressez puis double-cliquez sur `Installer Cybbig.cmd`. Compatible Smart App Control (aucun exécutable recompilé). |
| `Cybbig-Setup-<version>.exe` | Installateur classique. Non signé : Windows SmartScreen / Smart App Control peut l'avertir ou le bloquer (« Informations complémentaires › Exécuter quand même »). |

Aucune installation de Python ou de Node.js n'est nécessaire. Windows 10/11 64 bits.
Pour l'assistant IA local, installez [Ollama](https://ollama.com) puis un modèle (`ollama pull qwen2.5-coder:7b`).

## Vos clés API

Cybbig fonctionne sans aucune clé. Pour activer les options en ligne (Ollama Cloud, Brave Search, NVD),
**chaque utilisateur crée ses propres clés** : voir **[docs/CLES-API.md](docs/CLES-API.md)**.
Aucune clé n'est incluse dans le code ni dans l'installateur.

## Administration

L'espace Administration n'a **aucun identifiant par défaut** et n'est pas nécessaire pour utiliser Cybbig.
Il est réservé au propriétaire du projet, qui l'active par une signature cryptographique : voir [docs/ADMIN.md](docs/ADMIN.md).

## Démarrage rapide (depuis les sources)

Prérequis : Windows 10/11, Python 3.11+, Node.js 20+.

```powershell
cd cybbig
.\scripts\setup.ps1
.\scripts\start.ps1
```

`start.ps1` lance le backend Python puis l'application de bureau Electron depuis les sources. En cas d'échec de la fenêtre Electron, l'interface reste accessible sur `http://127.0.0.1:8765`.

## Installation comme logiciel Windows

```powershell
.\scripts\install.ps1
```

Installe Cybbig pour l'utilisateur courant dans `%LOCALAPPDATA%\Programs\Cybbig`, avec des raccourcis Bureau et menu Démarrer et une entrée dans « Applications installées » (désinstallation possible depuis Windows). Les données sont dans `%APPDATA%\Cybbig\data`. À la première installation, la base de `backend\data` est reprise.

Relancez le même script après chaque modification du code pour mettre l'installation à jour : les données ne sont jamais écrasées.

Aucun exécutable n'est recompilé : `Cybbig.exe` est une copie à l'identique de `electron.exe` et le backend utilise le Python signé du poste. C'est ce qui permet de rester compatible avec Smart App Control, qui bloquerait un installateur ou un `.exe` PyInstaller non signé.

Développement de l'interface :

```powershell
cd frontend
npm run dev
# UI sur http://127.0.0.1:5173 (proxy /api vers 8765)
```

Tests :

```powershell
.\scripts\test.ps1
```

## Ce qui fonctionne dans cette version

| Module | État | Détail |
|---|---|---|
| Tableau de bord | Fonctionnel | Risque, résultats, scans récents, état des moteurs |
| Projets & périmètre | Fonctionnel | Autorisation, domaines, chemins, journal d'audit |
| Threat Intelligence | Fonctionnel | CISA KEV, NVD, CERT-FR, versions PHP (synchronisation Internet) |
| Scanner PHP | Fonctionnel | Règles statiques, flux taint heuristiques, secrets, config, Composer/OSV |
| Web & API | Fonctionnel | En-têtes, TLS, cookies, formulaires, scripts, chemins exposés, OpenAPI |
| Intégrité checkout | Fonctionnel | Inventaire de scripts, indicateurs de skimming, CSP, SVG, WebSocket |
| Reverse engineering | Fonctionnel si Ghidra | Type d'analyse `reverse` via Ghidra headless (`analyzeHeadless`), triage imports/indicateurs, binaire jamais exécuté |
| Confidentialité & Accessibilité | Fonctionnel | Synthèse vocale locale (SAPI), gestionnaire de proxies, pilotage de vos clients VPN WireGuard/OpenVPN |
| Laboratoire | Fonctionnel | Scénarios pédagogiques, code vulnérable/corrigé, tests de validation |
| Assistant IA | Fonctionnel si Ollama | RAG local ; modèle en ligne (Ollama Cloud) sur option avec bascule automatique ; sinon analyste déterministe hors ligne |
| Entraînement IA | Fonctionnel | Le modèle en ligne enrichit la bibliothèque et prépare des exemples ; profil local `cybbig-analyst` ; export JSONL |
| Ressources du PC | Fonctionnel | Détection CPU/RAM/GPU, charge en direct, profils de performance pour Ollama |
| Visite de sites web | Fonctionnel | Lecture et exploration de pages publiques (Scrapling), garde-fous anti-SSRF, robots.txt |
| Recherche web | Fonctionnel | Recherche DuckDuckGo sans clé, Brave Search en option, requêtes parallèles, résultats cités et intégration facultative à l'assistant |
| Base de connaissances | Fonctionnel | FTS5, 200+ fiches livrées (cybersécurité, génie logiciel), catalogue de sources vérifiables et veille locale injectée dans le RAG ; bouton « Ajouter des données » (fichiers, site web, JSON/JSONL/CSV) |
| Automatisations | Fonctionnel | Planification, exécution, historique |
| Rapports | Fonctionnel | HTML, JSON, impression PDF via le navigateur |
| Conformité | Fonctionnel | Consentement, périmètre, niveaux A–E, avertissements |

## IA en ligne, vitesse et entraînement

1. **Activer l'IA en ligne** : Paramètres > *IA en ligne* : créez une clé API sur ollama.com, collez-la, enregistrez, puis *Tester la connexion en ligne*. Mode *Automatique* : le modèle en ligne répond s'il est joignable, sinon le modèle local prend le relais. *Local uniquement* ne fait aucun appel externe. Voir SECURITY.md pour ce qui est envoyé.
2. **Recherche web** : ouvrez *Recherche web* pour chercher des sources publiques avec DuckDuckGo. Une clé Brave Search facultative dans Paramètres permet d'interroger Brave en parallèle. Les résultats incluent leur URL, un extrait et une action pour ajouter une page à la base locale. L'option *Recherche web de l'assistant* envoie le sujet de la question au moteur ; le bouton propriétaire *Recherche étendue* augmente les résultats jusqu'à 20 et les pages consultées par l'assistant jusqu'à 3.
3. **Vitesse** : sans GPU compatible (NVIDIA/AMD), l'IA locale reste limitée par le processeur ; Paramètres > *Ressources du PC* montre le matériel détecté, la charge, le modèle chargé et permet de choisir un profil de performance.
4. **Ajouter des données** : Connaissances > *Ajouter des données* (fichiers, site web avec exploration optionnelle, JSON/JSONL/CSV, texte). Les pages web sont étiquetées `web-import` et non vérifiées.
5. **Entraîner** : page *Entraînement IA* : rédaction de fiches par le modèle en ligne, génération de questions/réponses, relecture, création du modèle local `cybbig-analyst`, export JSONL. Ce n'est pas un réentraînement des poids (ADR-011).

Les tâches IA, l'assistant de code, les générateurs et les agents d'amélioration interrogent la même base de connaissances au moment de répondre. Les agents rapprochent les fiches pertinentes des analyses, échecs et décisions du propriétaire puis proposent des améliorations dans Administration > Agents IA. L'application peut fonctionner en cycle continu lorsque le moteur IA de fond et les agents sont activés ; les changements de code restent soumis à validation du propriétaire. Les prochaines fiches ajoutées à la base deviennent automatiquement candidates au RAG.

Les paquets livrés comprennent les sources OWASP, CISA, NVD, CERT-FR, EPSS, GitHub Advisories, OSV, les documentations PHP/Python/Java, des travaux de recherche et Reddit comme source communautaire à vérifier. Dix fiches pratiques supplémentaires couvrent Java sécurisé et des commandes locales défensives. Quand une question correspond à un avis synchronisé, l'assistant ajoute un résultat de veille locale au contexte RAG avec sa date, sa gravité et son lien. La page Threat Intelligence permet aussi d'importer les flux annuels NVD CVE 2.0 depuis 2002 : chaque JSON est conservé dans `%APPDATA%\Cybbig\data\knowledge_sources\nvd\cve`, vérifié avec le SHA-256 publié par NVD, puis indexé dans la base locale. L'import est reprenable et les avis indexés sont disponibles dans la recherche de veille et le contexte de l'assistant.

Les imports manuels restent plafonnés à 2 Mo par fichier et 200 000 caractères par fiche. L'archive NVD historique est un import structuré distinct, issue des flux officiels annuels et accompagnée de leur provenance. Les descriptions NVD restent des données externes non fiables : l'assistant ne doit pas traiter leur contenu comme des instructions.

Scrapling : `pip install scrapling` (déjà dans `requirements.txt`) fournit l'analyseur HTML. Ses fetchers navigateur (`scrapling[fetchers]`) ne sont pas utilisés.

## Limites assumées

- **Aucun scan actif intrusif** n'est inclus : pas d'exploitation, pas de fuzzing, pas de contournement d'authentification. Les analyses Web sont passives et limitées au périmètre déclaré.
- L'analyse PHP est une analyse statique heuristique. Elle ne remplace pas Semgrep/Psalm/PHPStan, dont l'intégration est prévue en phase 2.
- Le PDF est produit via l'impression du rapport HTML (Ctrl+P) ; un export PDF natif est prévu.
- L'interface est en français ; l'i18n FR/EN est planifiée.
- Les fiches « incidents 2026 » du paquet Référentiel sont des synthèses importées, marquées « à vérifier » : contrôlez CVE, dates et chiffres à la source.
- Les fiches générées par IA sont étiquetées « non vérifiées » : relisez-les avant de vous y fier.
- Le packaging installateur signé n'est pas encore réalisé.

## Sécurité et usage responsable

Cybbig est destiné à l'audit de systèmes que vous possédez ou pour lesquels vous disposez d'une **autorisation écrite**. Le consentement intégré n'est pas une autorisation juridique. Voir [SECURITY.md](SECURITY.md).

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [ROADMAP.md](ROADMAP.md)
- [TASKS.md](TASKS.md)
- [DECISIONS.md](DECISIONS.md)
- [docs/DATABASE.md](docs/DATABASE.md)
- [docs/API.md](docs/API.md)
- [docs/MODULES.md](docs/MODULES.md)
- [docs/TESTING.md](docs/TESTING.md)
- [CHANGELOG.md](CHANGELOG.md)
