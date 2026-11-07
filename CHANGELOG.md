# Journal des modifications

## 0.4.0 — Cybbig Tunnel, modèles en ligne de l'Ollama local, génération de configurations

- **IA en ligne via l'Ollama local** : les modèles « -cloud » listés par votre serveur Ollama (ex. `deepseek-v4-pro:0813-cloud`) servent le mode en ligne **sans clé API**, tant que le serveur est connecté à ollama.com (`ollama signin`). Ils sont retirés du mode « Local uniquement » (leur calcul se fait en ligne), reçoivent le masquage des secrets et le budget de contexte du mode en ligne, sans réglages matériels ni `keep_alive`. Un refus 401 affiche un message explicite ; en mode *Automatique*, l'assistant, l'atelier et le générateur retombent sur le modèle local.
- **Rôles de modèles** : `ai_model_code` (Paramètres > IA en ligne) fixe le modèle du rôle « code » ; sans réglage, un modèle « coder » du serveur actif est choisi (atelier IA compris).
- **Générateur Ollama** (page Confidentialité) : configuration de proxy (Squid, nginx, tunnel SSH, mitmproxy), configuration WireGuard ou code, par le modèle « code » du serveur actif. Le résultat est à relire : rien n'est appliqué. API : `POST /api/assistant/generate`.
- **Cybbig Tunnel** (page Confidentialité) : VPN personnel WireGuard. Génération des clés (X25519 en Python pur, vecteurs RFC 7748 testés), configuration serveur + profil client, analyse des fuites (tunnel partiel, DNS non imposé, clé pré-partagée, keepalive), copie durcie d'un profil (tunnel IPv4 + IPv6 et DNS imposés : active le coupe-circuit natif de WireGuard pour Windows), classement des profils par latence et connexion rapide. Aucune règle de pare-feu n'est modifiée.
- **Modèles de proxy** : Tor, Tor Browser, tunnel SSH, mitmproxy, ZAP, Squid en un clic ; détection (information seulement) des applications Proton VPN et NordVPN installées.
- Étude d'architecture de Proton VPN avec REA : voir ADR-012.

## 0.3.2 — Interrupteur du mode en ligne et entraînement automatique

- **Interrupteur « Cloud »** dans la barre du haut, trois modes : *Coupé* (rien ne quitte le PC), *Entraînement seulement* (le chat reste local, seule la bibliothèque de connaissances part chez le modèle en ligne, jamais les projets) et *Actif* (chat et tâches IA utilisent aussi le modèle en ligne). Le mode se règle aussi dans Paramètres > IA en ligne.
- **Pilote automatique d'entraînement** (page Entraînement IA) : un cycle périodique (6 h à 7 jours) rédige les fiches manquantes, génère les questions/réponses, les approuve automatiquement (option, avec contrôles de longueur et de CVE inventées) et met à jour le modèle local `cybbig-analyst`, qui n'est activé automatiquement qu'à sa première création. Le cycle n'utilise jamais un professeur local et ne se lance pas en mode *Coupé*. Bouton « Lancer un cycle maintenant ».
- Paramètres > IA en ligne : **Enregistrer et tester** conserve tout de suite la clé et les réglages en ligne, sans dépendre du bouton Enregistrer de la page.

## 0.3.1 — Atelier IA, accès propriétaire et personnalisation

- **Atelier IA** (Administration > Atelier IA) : un modèle Ollama (en ligne ou local, de préférence un modèle « coder ») propose des modifications du code sous forme de blocs SEARCH/REPLACE. Chaque bloc est vérifié contre le fichier réel (le texte doit exister une seule fois), les différences s'affichent, **rien n'est écrit sans validation**, l'application est tout-ou-rien, avec sauvegarde de l'ancienne version, contrôle de syntaxe Python et journal d'audit. Les fichiers `.env`, clés, bases de données, `.venv` et `backend/data` ne sont jamais envoyés au modèle ni modifiables par l'atelier.
- **Bouton Paramètres** dans la barre du haut, carte **Accès propriétaire** (liens vers l'Atelier IA, l'éditeur de code, la base de données et le terminal) et carte **Personnalisation** : couleur d'accent, taille du texte, arrondis, pages du menu, CSS libre (`?safe=1` dans l'adresse démarre sans CSS personnalisé). Paramètres et Administration ne peuvent pas être masqués.
- Les réglages d'apparence sont validés côté serveur.

## 0.3.0 — IA en ligne, ressources du PC, visite de sites, bibliothèque et entraînement

- **IA en ligne (Ollama Cloud)** réactivée, **à la demande** : Paramètres > IA en ligne (clé API Ollama distincte de celle d'un serveur local). Trois modes : *Automatique* (en ligne si disponible, sinon local, avec bascule en cas de panne), *Local uniquement* (aucun appel vers l'extérieur) et *En ligne uniquement*. Les clés, jetons, Bearer, JWT et clés privées sont masqués avant tout envoi. Le champ « URL Ollama » reste limité aux serveurs locaux.
- **Plus rapide** : état des serveurs mis en cache quelques secondes (au lieu d'un appel réseau par requête), budget de contexte élargi en ligne, jusqu'à 3 tâches IA de fond en parallèle avec le modèle en ligne, préchargement du modèle local au démarrage, options Ollama stables (un `num_ctx` qui change force Ollama à recharger le modèle).
- **Ressources du PC** : détection du processeur, de la mémoire et des cartes graphiques, charge en direct, part du modèle placée sur le GPU (`/api/ps`), profils de performance (Auto, Économe, Équilibré, Maximum) qui règlent `num_thread`, `num_ctx` et `num_batch`, nombre d'analyses simultanées selon le processeur, recommandations. Cybbig ne pilote pas le GPU : Ollama l'utilise seul s'il est compatible (NVIDIA CUDA, AMD ROCm).
- **Visite de sites web** : lecture de pages publiques (aperçu ou ajout à la base), exploration d'un site (25 pages, profondeur 2, même domaine), URL collée dans l'assistant lue automatiquement. Garde-fous anti-SSRF (adresses publiques seulement, redirections revalidées), robots.txt respecté, contenu importé étiqueté `web-import` et non vérifié.
- **Scrapling** (D4Vinci/Scrapling) intégré comme moteur d'extraction (sélecteurs CSS, liens, métadonnées) avec trafilatura pour le texte principal.
- **Base de connaissances** : bouton **Ajouter des données** (fichiers multiples, site web, JSON/JSONL/CSV, texte), import en lot, catégories regroupées. Quatre paquets installés au démarrage : *Cyber* (66 fiches défensives PHP/Python/Web), *Référentiel* (fiches, 11 incidents 2026 « à vérifier », 29 outils open source, sources de veille), *Génie logiciel* (34 fiches), *Cybbig* (7 fiches d'exploitation). Une fiche modifiée par l'utilisateur n'est jamais écrasée.
- **Entraînement** (page *Entraînement IA*) : le modèle en ligne (professeur) rédige les fiches manquantes d'un programme de 46 sujets et des paires question/réponse ; relecture et approbation ; création d'un modèle Ollama local personnalisé (`cybbig-analyst`) ; export JSONL pour un fine-tuning externe. Il ne s'agit pas d'un réentraînement des poids.

## 0.2.0 — Reverse engineering & confidentialité

- **Moteur de reverse engineering** : nouveau type d'analyse `reverse` qui pilote Ghidra en mode headless (`analyzeHeadless`) via l'orchestrateur de scans. Le binaire reste dans le périmètre du projet et n'est jamais exécuté ; les imports sensibles et indicateurs réseau sont remontés en findings de triage.
- **Confidentialité & Accessibilité** (nouvelle page) :
  - *Synthèse vocale* locale (SAPI Windows) pour lire rapports et findings, ou exporter un WAV — 100 % hors ligne.
  - *Gestionnaire de proxies* (ajout, test via écho d'IP, activation) avec option explicite de router les analyses passives via le proxy actif.
  - *Client VPN* : gestion de profils pointant vers vos propres configurations WireGuard/OpenVPN (Proton VPN, Hide.me…), état de connexion, IP de sortie, (dé)connexion via les clients officiels. Aucun identifiant VPN n'est stocké.
- Cybbig ne fournit aucun service d'anonymat, de VPN hébergé ni de numéro de téléphone : seuls des clients pilotant vos propres ressources sont intégrés.

## 0.1.0 — MVP

- Application de bureau Windows (Electron 45 + React 19 + TypeScript) avec backend FastAPI local.
- Base SQLite WAL + FTS5, veille CISA KEV/NVD/CERT-FR/PHP.
- Scanner PHP statique, analyse Web/API passive, intégrité checkout.
- Laboratoire de formation avec validation par motifs.
- Assistant IA local (Ollama optionnel, repli déterministe) et base de connaissances.
- Automatisations planifiées et rapports HTML/JSON.
- Consentement, périmètre, niveaux d'activité, journal d'audit.
- Tests pytest et parcours `smoke.py`.
- Documentation initiale et scripts d'installation/démarrage/test.
