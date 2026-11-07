# Décisions d'architecture (ADR)

## ADR-001 — Electron plutôt que Tauri 2 (v0.1)
**Contexte** : la spécification privilégie Tauri 2. La machine ne possède ni `rustc` ni `cargo`. Installer Rust + compiler Tauri aurait retardé un MVP testable.
**Décision** : Electron 45 + React 19 pour la coquille Windows, backend Python inchangé.
**Conséquences** : empreinte plus lourde ; chemin de migration Tauri conservé (l'UI et l'API sont découplées). À réévaluer en phase 10.

## ADR-002 — Backend FastAPI local
**Décision** : API HTTP sur 127.0.0.1, servie par Uvicorn, démarrée par Electron.
**Raisons** : séparation UI/moteurs, testabilité, réutilisation dans une future version web/desktop.
**Sécurité** : bind localhost uniquement, CORS restreint, pas d'authentification multi-utilisateur en v0.1 (menace locale assumée).

## ADR-003 — SQLite WAL + FTS5
**Décision** : SQLite avec accès par connexion courte, WAL, migrations par `PRAGMA user_version`.
**Raisons** : zéro administration, requêtes FTS, portable.
**Limites** : accès concurrent modéré ; suffisant pour un poste local.

## ADR-004 — Passif par défaut, aucun exploit
**Décision** : les scans Web n'envoient pas de charges d'attaque. Les tests de chemins exposés sont des GET tronqués, sans conservation du corps. Aucun contournement d'authentification.
**Raisons** : sécurité juridique et technique ; conformité avec la vocation défensive.
**Évolution** : un mode laboratoire isolé pourra exécuter des scénarios sur des applications locales dédiées.

## ADR-005 — Périmètre obligatoire
**Décision** : refus des scans publics sans référence d'autorisation et sans domaine autorisé. Le consentement n'est pas une autorisation légale.
**Conséquences** : les démonstrations utilisent localhost et le projet d'exemple.

## ADR-006 — Ollama optionnel
**Décision** : aucune dépendance obligatoire à un service IA. Détection d'Ollama, sinon analyste déterministe basé sur les résultats et la base de connaissances.
**Raisons** : fonctionnement hors ligne, coût nul, maîtrise des données.

## ADR-007 — Preuves expurgées
**Décision** : les secrets détectés sont masqués dans les preuves ; seuls le type, le fichier et la ligne sont conservés.
**Raisons** : éviter que Cybbig devienne une base de secrets en clair.

## ADR-008 — Rapports HTML/JSON d'abord
**Décision** : HTML autonome + JSON ; PDF via impression navigateur.
**Raisons** : zéro dépendance native. Export PDF natif prévu.

## ADR-009 — IA en ligne optionnelle et explicite (assouplit la restriction « local seulement » de l'ADR-006)
**Contexte** : sur un poste sans GPU, un modèle de 7 milliards de paramètres met de 15 à 60 s par réponse. L'utilisateur demande la réactivation d'un modèle Ollama en ligne.
**Décision** : un second serveur « en ligne » (HTTPS, clé API dédiée) s'ajoute au serveur local ; le champ `ollama_url` reste limité au réseau local. Mode par défaut *Automatique* : le modèle en ligne n'est utilisé que si une clé est saisie ; *Local uniquement* coupe tout appel externe. Masquage des secrets avant envoi, bascule automatique vers le local en cas de panne.
**Conséquences** : les données de projet peuvent quitter le poste dès qu'une clé est configurée ; c'est dit dans l'interface et dans SECURITY.md. Le masquage est heuristique.

## ADR-010 — Visites de sites : lecture publique, contrôlée, non fiable
**Décision** : un module `webfetch` lit des pages publiques avec contrôle d'adresse à chaque redirection, robots.txt, limites de taille/durée et délai entre pages. Scrapling fournit l'analyse HTML (CSS), trafilatura le texte principal. Les fetchers navigateur/anti-bot de Scrapling ne sont pas activés.
**Raisons** : une page peut contenir des consignes destinées à l'IA ou viser le réseau interne (SSRF) ; le contenu importé est étiqueté `web-import` et exclu de l'entraînement.

## ADR-011 — « Entraîner » = bibliothèque (RAG) + profil Ollama, pas de réentraînement des poids
**Décision** : le professeur (modèle en ligne) enrichit la bibliothèque et produit des exemples relus par l'utilisateur ; le modèle local reçoit un profil personnalisé (`/api/create` : instruction système + exemples). Un export JSONL permet un vrai fine-tuning (LoRA) hors de Cybbig.
**Raisons** : un fine-tuning réel demande un GPU et des heures ; la recherche documentaire apporte l'essentiel du gain, et chaque contenu généré reste vérifiable.

## ADR-012 — « VPN interne » : fonctions de client, protocole public, aucune copie
**Contexte** : demande d'un VPN intégré inspiré de Proton VPN et NordVPN, avec étude de leur ingénierie.
**Constat (REA, application Proton VPN 5.1.8 installée sur ce poste, lecture des en-têtes, imports et exports, rien d'exécuté)** : application .NET (BouncyCastle, ARSoft.Tools.Net pour le DNS, DeviceId) ; tunnel WireGuard par `wireguard.dll` + `wintun.dll` pilotés par un service dédié (`ProtonVPN.WireGuardService`) ; une DLL Go `wireguard-tunnel-tcp.dll` (exports `WireGuardGenerateKeypair`, `WireGuardTunnelService`) indique un transport WireGuard sur TCP. Ghidra GUI n'était pas démarré : seul REA a servi. Les applications de Proton sont publiées en open source, et NordLynx est WireGuard : l'architecture est documentée publiquement.
**Décision** : Cybbig reprend les *fonctions* de ces clients (génération de clés, profils, durcissement, coupe-circuit, classement par latence, connexion rapide) sur WireGuard (protocole public) et pilote le client WireGuard officiel. On ne décompile pas le code propriétaire pour le reproduire, on ne contourne ni leur authentification ni leurs API, on ne réutilise pas leurs serveurs ni leurs identifiants. NordVPN n'est pas installé ici : aucune analyse de ses binaires (ses conditions interdisent la rétro-ingénierie, et la documentation publique suffit).
**Coupe-circuit** : un profil WireGuard avec `AllowedIPs = 0.0.0.0/0, ::/0` active le coupe-circuit natif de WireGuard pour Windows ; Cybbig n'écrit donc aucune règle de pare-feu (une règle erronée coupe Internet du poste).
**Limites** : Cybbig n'est pas un service VPN (aucun serveur fourni) ; l'établissement du tunnel exige les droits administrateur ; le transport TCP/furtif de Proton n'est pas reproduit ; pas de reconnexion automatique en fond. Les clés X25519 sont générées en Python (opérations non constantes en temps) : acceptable pour une clé créée localement, pas pour un service exposé.

## ADR-013 — Modèles « -cloud » de l'Ollama local = IA en ligne sans clé
**Contexte** : le serveur Ollama du poste liste `deepseek-v4-pro:0813-cloud` (champ `remote_host`). Ces modèles sont servis par ollama.com à travers le serveur local, avec le compte connecté (`ollama signin`).
**Décision** : ils alimentent le fournisseur « en ligne » (route `daemon`) quand aucune clé directe ne fonctionne, soumis à `ai_allow_cloud` et au masquage des secrets ; ils n'apparaissent jamais dans le mode « Local uniquement ». L'état affiché indique la route (`direct` ou `daemon`).
**Conséquence** : sur un serveur non connecté, le modèle est listé mais répond 401 ; l'erreur le dit et le mode *Automatique* bascule sur le modèle local.
