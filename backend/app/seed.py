from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from .config import CONSENT_VERSION, SAMPLES_DIR
from . import db

DEMO_PROJECT_ID = "proj-demo-cybbig"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def seed_settings() -> None:
    defaults = {
        "language": "fr",
        "theme": "dark",
        "intel_nvd_days": "14",
        "intel_max_items": "150",
        "ollama_url": "http://127.0.0.1:11434",
        "ollama_model": "",
        "ollama_api_key": "",
        "max_files": "2500",
        "max_pages": "3",
        "allow_private_targets": "true",
        "data_retention_days": "365",
        "user_agent": "Cybbig-PassiveAudit/0.1",
        "enable_external_tools": "true",
        "owner_mode": "false",
        "nvd_api_key": "",
        "consent_version": CONSENT_VERSION,
        # L'amélioration continue s'appuie uniquement sur l'IA locale et produit des propositions à valider.
        "ai_auto": "true",
        "ai_agents": "true",
        "ai_auto_scans": "false",
        "ai_auto_triage": "false",
        "ai_auto_intel": "false",
        "ai_auto_dashboard": "false",
    }
    with db.db_cursor() as conn:
        for key, value in defaults.items():
            conn.execute("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)", (key, value))
    # Garde-fous de terminal préenregistrés (aucune exécution arbitraire)
    existing = db.fetch_one("SELECT COUNT(*) AS c FROM terminal_guardrails")
    if not existing or existing["c"] == 0:
        terminal_defaults = [
            ("Vérification Python (compileall)", ["python", "-m", "compileall", "app"], "backend", "Compile les fichiers Python pour détecter les erreurs de syntaxe."),
            ("Tests pytest", ["python", "-m", "pytest", "-q", "tests"], "backend", "Lance la suite de tests backend."),
            ("Build frontend", ["npm", "run", "build"], "frontend", "Compile l'interface React/Vite."),
        ]
        for name, command, working_dir, description in terminal_defaults:
            db.execute(
                """INSERT OR IGNORE INTO terminal_guardrails(id,name,command,working_dir,description,enabled,created_at)
                   VALUES(?,?,?,?,?,?,?)""",
                (str(__import__("uuid").uuid4()), name, db.json_dumps(command), working_dir, description, 1, db.utcnow()),
            )


def seed_sources() -> None:
    sources = [
        ("cisa_kev", "CISA — Known Exploited Vulnerabilities", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog", "json", 1),
        ("nvd", "NVD / NIST — CVE récentes", "https://nvd.nist.gov/", "api", 1),
        ("cert_fr", "CERT-FR — alertes et avis", "https://www.cert.ssi.gouv.fr/", "rss", 1),
        ("php_releases", "PHP — versions et correctifs", "https://www.php.net/releases/", "json", 1),
        ("osv", "OSV — dépendances open source", "https://osv.dev/", "api", 0),
    ]
    with db.db_cursor() as conn:
        for name, label, url, kind, enabled in sources:
            conn.execute(
                "INSERT OR IGNORE INTO threat_sources(name,label,url,kind,enabled) VALUES(?,?,?,?,?)",
                (name, label, url, kind, enabled),
            )


def seed_project() -> None:
    if db.fetch_one("SELECT id FROM projects WHERE id=?", (DEMO_PROJECT_ID,)):
        return
    now = _now()
    sample_path = str((SAMPLES_DIR / "php-demo").resolve())
    db.execute(
        """INSERT INTO projects(
            id,name,client,description,path,base_url,environment,
            authorization_ref,authorized_by,authorized_at,authorization_confirmed,
            scope_domains,scope_paths,activity_level,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            DEMO_PROJECT_ID,
            "Boutique de démonstration",
            "Cybbig Lab",
            "Projet local fourni pour découvrir les moteurs PHP, Web, API et checkout. "
            "Les cibles sont locales et le code PHP n'est jamais exécuté.",
            sample_path,
            "http://127.0.0.1:8765/demo/shop",
            "laboratory",
            "LAB-CYBBIG-DEMO",
            "Cybbig",
            now,
            1,
            db.json_dumps(["127.0.0.1", "localhost"]),
            db.json_dumps([sample_path]),
            "B",
            now,
            now,
        ),
    )


KNOWLEDGE = [
    {
        "id": "kb-php-hardening",
        "title": "Durcir PHP en production",
        "category": "PHP",
        "tags": "php, configuration, sessions, uploads, durcissement",
        "source": "OWASP / PHP Manual",
        "content": """# Durcir PHP en production

## Configuration critique
- `display_errors = Off` et `log_errors = On` : ne jamais exposer les traces au visiteur.
- `expose_php = Off` : limite la divulgation de version.
- `allow_url_include = Off` et `allow_url_fopen = Off` sauf besoin explicite.
- `session.use_strict_mode = 1`, `session.use_only_cookies = 1`.
- `session.cookie_httponly = 1`, `session.cookie_secure = 1` sous HTTPS.
- `session.cookie_samesite = Lax` ou `Strict` selon le parcours.
- Limiter `upload_max_filesize`, `post_max_size` et `memory_limit`.

## Sessions
Renouveler l'identifiant avec `session_regenerate_id(true)` après authentification et après une élévation de privilège. Détruire la session à la déconnexion. Ne pas stocker de secrets dans le cookie.

## Entrées et sorties
- Utiliser PDO avec requêtes préparées et `ATTR_EMULATE_PREPARES=false`.
- Encoder toute sortie HTML avec `htmlspecialchars($v, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')`.
- Valider les chemins avec `realpath()` et vérifier le préfixe autorisé.
- Pour les commandes, préférer les API natives et `escapeshellarg()` si unavoidable.

## Fichiers téléversés
Vérifier taille, extension autorisée, type MIME réel (`finfo`), signature, nom généré côté serveur. Stocker hors racine publique et retirer les droits d'exécution.

## Dépendances
Générer un SBOM, exécuter `composer audit` en CI, comparer à OSV et suivre les versions corrigées. Une dépendance vulnérable non utilisée reste à qualifier, pas à ignorer.

## Vérification Cybbig
Le scanner PHP détecte des motifs et des flux heuristiques. Il ne prouve pas l'absence de vulnérabilité. Croiser avec Psalm taint analysis, revue manuelle et tests dynamiques autorisés.""",
    },
    {
        "id": "kb-owasp-top10",
        "title": "OWASP Top 10 — lecture défensive",
        "category": "Web",
        "tags": "owasp, contrôle accès, injection, configuration, supply chain",
        "source": "OWASP",
        "content": """# OWASP Top 10 — grille de lecture

| Risque | Question d'audit |
|---|---|
| Broken Access Control | Chaque objet est-il rattaché à un propriétaire vérifié côté serveur ? |
| Security Misconfiguration | En-têtes, TLS, comptes par défaut, debug et répertoires sont-ils maîtrisés ? |
| Software Supply Chain | Les dépendances sont-elles inventoriées, signées et à jour ? |
| Cryptographic Failures | Les données sensibles sont-elles chiffrées en transit et au repos ? |
| Injection | Les entrées atteignent-elles des sinks sans validation contextuelle ? |
| Insecure Design | Les limites métier (montants, quotas, états) sont-elles définies ? |
| Authentication Failures | MFA, rotation de session, anti-bruteforce, récupération de compte ? |
| Integrity Failures | Les artefacts et scripts sont-ils vérifiés par hash/signature ? |
| Logging Failures | Les événements sensibles sont-ils tracés sans secrets ? |
| Exception Mishandling | Les erreurs révèlent-elles des détails internes ? |

## Méthode
1. Cartographier les actifs et les flux.
2. Définir des invariants de sécurité (propriété, montant, état).
3. Tester les invariants avec des comptes fictifs.
4. Corriger, puis rejouer les tests.
5. Conserver les preuves et la date de validation.

L'analyse statique et l'analyse passive ne remplacent pas un test d'autorisation contrôlé sur un environnement de préproduction.""",
    },
    {
        "id": "kb-pci-checkout",
        "title": "Intégrité de la page de paiement — PCI DSS 4.0",
        "category": "E-commerce",
        "tags": "pci dss, checkout, scripts, intégrité, 6.4.3, 11.6.1",
        "source": "PCI SSC",
        "content": """# Intégrité de la page de paiement

## Exigences clés
- **6.4.3** : inventaire, justification et autorisation de chaque script chargé sur les pages de paiement ; détection des modifications non autorisées.
- **11.6.1** : détection des altérations non autorisées du contenu et des en-têtes HTTP de la page de paiement, avec une fréquence définie (la surveillance continue est recommandée).
- **6.4.3.1** : procédure de réponse aux modifications non autorisées.

## Inventaire des scripts
Pour chaque script : domaine, propriétaire, finalité, version, hash, méthode de mise à jour, date de revue. Les scripts tiers (GTM, chat, A/B testing) augmentent la surface d'attaque.

## Signaux de skimming
- SVG inline avec `onload` + `atob()`/`setTimeout`.
- `new Function()` alimenté par un contenu distant.
- WebSocket/WebRTC inattendus depuis le checkout.
- Lecture des champs carte par un script non autorisé.
- Stockage de blobs dans `localStorage` avec des clés inconnues.
- Faux conteneur GTM ou domaine lookalike.
- Formulaire de carte dont l'action sort du périmètre du PSP.

## Réponse
1. Ne pas collecter les données de carte.
2. Isoler la page compromise et préserver les journaux.
3. Révoquer les scripts et secrets concernés.
4. Comparer au dernier hash autorisé.
5. Corriger, tester, puis surveiller.

Cybbig inventorie et signale ; il ne remplace ni un WAF ni une surveillance d'intégrité de production.""",
    },
    {
        "id": "kb-skimming-indicators",
        "title": "Indicateurs de skimming côté client",
        "category": "Détection",
        "tags": "skimmer, magecart, svg, gtm, websocket, csp",
        "source": "Cybbig Research",
        "content": """# Indicateurs de skimming côté client

## Analyse statique de la page
Rechercher les motifs suivants, sans les exécuter :
- `<svg ... onload=...>` de petite taille, surtout avec `atob(`, `eval(`, `setTimeout(`.
- `new Function(` avec une source réseau.
- Concaténation de morceaux de charge utile (`meta0`, `meta1`, ...).
- `localStorage` / `sessionStorage` avec clés inattendues.
- `wss://` ou `RTCPeerConnection` sur une page de paiement.
- Formulaires de carte pointant vers un domaine hors PSP.
- Scripts sans `integrity` ni version épinglée.
- Conteneurs GTM inconnus ou récemment modifiés.

## Limites
Un motif isolé n'est pas une preuve. Il faut le contexte, l'inventaire des scripts autorisés et l'historique des hashs. Les skimmers modernes chiffrent et fragmentent leurs données ; l'analyse statique doit être combinée à la surveillance d'intégrité et aux journaux réseau.

## Bonnes pratiques
- CSP stricte avec nonces, `object-src 'none'`, `base-uri 'none'`.
- SRI pour les scripts statiques compatibles.
- Revue de chaque script tiers et de ses mises à jour.
- Surveillance continue du DOM et des requêtes sortantes, avec alertes.""",
    },
    {
        "id": "kb-bola",
        "title": "BOLA/IDOR — vérifier la propriété des objets",
        "category": "API",
        "tags": "api, bola, idor, autorisation, owasp api",
        "source": "OWASP API Security Top 10",
        "content": """# BOLA/IDOR

## Définition
L'API accepte un identifiant d'objet fourni par le client et retourne ou modifie l'objet sans vérifier que l'utilisateur authentifié en est propriétaire.

## Test défensif
1. Créer deux comptes fictifs A et B en préproduction.
2. Créer une ressource avec A (commande, compte, bénéficiaire).
3. Tenter d'y accéder avec la session de B.
4. Attendre un refus (403/404) et une journalisation.
5. Répéter sur les méthodes GET, PATCH, DELETE et sur les champs imbriqués.

## Correction
- Extraire l'identité du token signé, jamais d'un champ du corps.
- Vérifier la propriété côté serveur pour chaque objet et chaque action.
- Utiliser des identifiants non énumérables ne remplace pas l'autorisation.
- Ajouter des tests d'autorisation automatisés en CI.
- Journaliser les tentatives refusées sans données sensibles.

## Piège
Un identifiant imprévisible (UUID) réduit l'énumération mais ne corrige pas une absence de contrôle d'accès.""",
    },
    {
        "id": "kb-sessions",
        "title": "Sessions et authentification PHP",
        "category": "PHP",
        "tags": "session, authentification, csrf, cookie, php",
        "source": "OWASP",
        "content": """# Sessions et authentification PHP

## Cycle de vie
- Démarrer la session avec une configuration stricte.
- Régénérer l'identifiant après connexion et changement de rôle.
- Détruire la session et le cookie à la déconnexion.
- Fixer une durée d'inactivité et une durée absolue.
- Protéger les formulaires par un jeton CSRF à usage unique.

## Stockage des mots de passe
Utiliser `password_hash($password, PASSWORD_ARGON2ID)` et `password_verify()`. Ne jamais utiliser MD5/SHA1 seuls. Prévoir une migration progressive des anciens hachages.

## Réinitialisation
Jeton aléatoire à haute entropie, usage unique, expiration courte, invalidation après usage, réponse neutre pour ne pas révéler l'existence du compte.

## Cookies
`HttpOnly`, `Secure`, `SameSite`. Éviter de stocker des données sensibles dans le cookie ; préférer un identifiant opaque.

## Vérification
Contrôler la configuration `php.ini`, le code de connexion, la rotation, le CSRF et les journaux d'échec. Un test avec deux comptes fictifs permet de vérifier l'isolation.""",
    },
    {
        "id": "kb-intel-sources",
        "title": "Threat Intelligence — sources et niveau de confiance",
        "category": "Threat Intel",
        "tags": "cve, cisa, nvd, cert-fr, osv, confiance",
        "source": "Cybbig",
        "content": """# Sources de renseignement

## Sources primaires
- **CISA KEV** : vulnérabilités exploitées dans la nature ; priorisation forte.
- **NVD** : référentiel CVE, scores CVSS, produits concernés.
- **CERT-FR** : avis et alertes contextualisés pour la France.
- **Éditeurs** (PHP, Microsoft, Adobe, etc.) : source de vérité pour les versions corrigées.
- **OSV** : vulnérabilités des dépendances open source.
- **MITRE ATT&CK** : techniques adverses, utile pour la détection.

## Règle de confiance
Chaque fiche conserve sa source, sa date de publication, sa date de récupération et son statut de vérification. Une information non confirmée ne doit pas devenir une règle de blocage.

## Corrélation
Comparer la fiche aux actifs inventoriés : produit, version, exposition réseau, configuration, exploitation connue. Une CVE critique sur un composant non utilisé n'a pas la même priorité qu'une CVE moyenne exploitée sur un service exposé.

## Cycle
Collecter → normaliser → dédupliquer → qualifier → corréler → alerter → corriger → vérifier.""",
    },
    {
        "id": "kb-legal-scope",
        "title": "Cadre d'utilisation, périmètre et preuves",
        "category": "Conformité",
        "tags": "légal, autorisation, périmètre, preuve, éthique",
        "source": "Cybbig",
        "content": """# Cadre d'utilisation

## Principes
- N'auditer que des systèmes possédés ou explicitement autorisés.
- Conserver la référence de l'autorisation, son auteur, sa date et son périmètre.
- Le consentement logiciel n'est pas une autorisation légale.
- En France, les atteintes aux systèmes sont encadrées par les articles 323-1 et suivants du Code pénal.
- En cas de doute, suspendre et consulter un juriste.

## Preuves
- Horodater les scans.
- Conserver la configuration, les versions d'outils et les résultats.
- Expurger les secrets et données personnelles.
- Ne pas télécharger de données privées pour « prouver » une exposition.
- Documenter les limites et les faux positifs.

## Niveaux
A documentation, B simulation locale, C infrastructure contrôlée, D tiers autorisé, E impact potentiel. Cybbig n'implémente pas le niveau E.""",
    },
    {
        "id": "kb-payments",
        "title": "Paiements : idempotence, concurrence et invariants",
        "category": "Finance",
        "tags": "paiement, idempotence, race condition, webhook, remboursement",
        "source": "Cybbig",
        "content": """# Invariants de paiement

## À vérifier
- Une commande ne peut être payée qu'une fois.
- Une clé d'idempotence est exigée pour les opérations de création.
- Les montants sont exprimés en unités minimales (entiers) ou en décimal, jamais en flottants binaires.
- La devise est validée et ne peut changer après création.
- Un remboursement ne dépasse pas le montant capturé.
- Une annulation ne peut pas être rejouée pour recréditer.
- Les transitions d'état sont explicites et journalisées.
- Les webhooks sont vérifiés par signature, horodatage et anti-rejeu.
- Les opérations concurrentes utilisent verrous/transactions et contraintes uniques.

## Test défensif
Avec des données fictives en préproduction, soumettre deux fois la même requête et vérifier qu'un seul débit existe. Simuler deux workers concurrents et vérifier la contrainte d'unicité côté base.

## Anti-pattern
Vérifier le solde puis débiter dans deux transactions séparées sans verrou. La vérification applicative seule ne suffit pas ; la base doit garantir l'invariant.""",
    },
    {
        "id": "kb-incident-legacy",
        "title": "Leçons des incidents : systèmes hérités et tiers",
        "category": "Incidents",
        "tags": "incident, legacy, fournisseur, segmentation, cve",
        "source": "Cybbig Research",
        "content": """# Leçons des incidents

## Systèmes hérités
Un ancien système de livraison ou une plateforme « oubliée » peut rester connectée et exposée. L'inventaire doit inclure les systèmes hors service, les sauvegardes, les sous-domaines et les intégrations oubliées.

## Fournisseurs
Un compte fournisseur compromis peut ouvrir la voie à un réseau interne. MFA, moindre privilège, expiration des accès, segmentation et surveillance des connexions sont indispensables.

## Correctifs
Une CVE connue non corrigée reste un risque majeur. Il faut un inventaire des composants, un SBOM, une politique de délai et une vérification que le correctif est réellement déployé sur tous les nœuds.

## Détection
Surveiller les processus PHP anormaux, les téléchargements, les nouveaux comptes, les tâches planifiées, les modifications de fichiers et les connexions sortantes.

## Communication
Préserver les preuves, ne pas perturber le service sans procédure, informer les autorités et les personnes concernées selon les obligations applicables.""",
    },
    {
        "id": "kb-headers-csp",
        "title": "En-têtes HTTP et CSP : vérifications concrètes",
        "category": "Web",
        "tags": "headers, csp, hsts, cookies, cors",
        "source": "OWASP",
        "content": """# En-têtes HTTP

## Minimum attendu
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (si HTTPS).
- `Content-Security-Policy` restrictive, sans `unsafe-inline` ni `unsafe-eval` pour les scripts.
- `X-Content-Type-Options: nosniff`.
- `Referrer-Policy: strict-origin-when-cross-origin` ou plus strict.
- `Permissions-Policy` pour désactiver les fonctions non utilisées.
- `frame-ancestors 'none'` ou une liste blanche ; `X-Frame-Options` en complément pour les anciens navigateurs.

## CSP
Préférer les nonces ou hashs. Éviter `*`, `data:` pour les scripts, et les domaines trop larges. Attention aux scripts tiers : une CSP permissive annule une partie de la protection.

## Cookies
`Secure`, `HttpOnly`, `SameSite=Lax/Strict`, `Path` limité, `Max-Age` cohérent. Les cookies de session ne doivent pas contenir de données sensibles.

## CORS
N'utiliser `Access-Control-Allow-Origin: *` qu'avec des données publiques. Avec credentials, une origine précise est obligatoire. Ne pas refléter arbitrairement l'en-tête `Origin`.

## Limites
Les en-têtes ne remplacent pas la validation serveur. Une CSP peut être contournée par une injection HTML si le nonce est volé ; la défense en profondeur reste nécessaire.""",
    },
]


def seed_docs() -> None:
    now = _now()
    with db.db_cursor() as conn:
        for doc in KNOWLEDGE:
            conn.execute(
                """INSERT OR IGNORE INTO knowledge_docs(
                    id,title,category,content,source,tags,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?)""",
                (
                    doc["id"], doc["title"], doc["category"], doc["content"],
                    doc.get("source", "Cybbig"), doc.get("tags", ""), now, now,
                ),
            )


LAB_SCENARIOS = [
    {
        "id": "lab-sqli", "slug": "sql-injection",
        "title": "Injection SQL par concaténation",
        "category": "PHP", "level": "B",
        "description": "Une entrée utilisateur est concaténée dans une requête SQL. Le scénario montre le flux et la correction par requête préparée.",
        "objective": "Identifier le flux entrée → requête, corriger avec PDO et vérifier qu'une chaîne malveillante reste une donnée.",
        "vulnerable_code": "$email = $_GET['email'];\n$sql = \"SELECT * FROM users WHERE email = '\" . $email . \"'\";\n$rows = $pdo->query($sql);",
        "secure_code": "$stmt = $pdo->prepare('SELECT id,email FROM users WHERE email = :email');\n$stmt->execute(['email' => $_GET['email']]);\n$rows = $stmt->fetchAll(PDO::FETCH_ASSOC);",
        "test_steps": "1. Créer une base SQLite de test avec une table users.\n2. Envoyer une valeur contenant une apostrophe.\n3. Vérifier que la requête préparée la traite comme une valeur.\n4. Rejouer avec le scanner Cybbig et comparer.",
        "detection": "Rechercher les concaténations dans les appels SQL, les interpolations de variables et l'absence de requêtes préparées.",
        "references_json": '["https://owasp.org/www-community/attacks/SQL_Injection"]',
    },
    {
        "id": "lab-xss", "slug": "xss",
        "title": "XSS stocké et encodage contextuel",
        "category": "PHP", "level": "B",
        "description": "Une valeur est réaffichée sans encodage. La correction utilise htmlspecialchars avec le bon contexte.",
        "objective": "Comprendre la différence entre validation et encodage de sortie, puis vérifier le rendu.",
        "vulnerable_code": "$name = $_POST['name'];\necho '<h1>Bonjour ' . $name . '</h1>';",
        "secure_code": "$name = $_POST['name'] ?? '';\necho '<h1>Bonjour ' . htmlspecialchars($name, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '</h1>';",
        "test_steps": "1. Saisir une valeur contenant des caractères HTML dans un formulaire local.\n2. Observer le HTML produit.\n3. Appliquer l'encodage et vérifier que la valeur est affichée littéralement.",
        "detection": "Repérer les sorties HTML de variables issues de $_GET/$_POST sans encodage dans le même contexte.",
        "references_json": '["https://owasp.org/www-community/attacks/xss/"]',
    },
    {
        "id": "lab-idor", "slug": "bola-idor",
        "title": "BOLA/IDOR sur une commande",
        "category": "API", "level": "B",
        "description": "L'API vérifie l'authentification mais pas la propriété de l'objet. Deux comptes fictifs suffisent à révéler le défaut.",
        "objective": "Ajouter une vérification de propriété serveur et un test automatisé A/B.",
        "vulnerable_code": "order = db.get_order(order_id)\nif not current_user.is_authenticated:\n    return 401\nreturn jsonify(order)",
        "secure_code": "order = db.get_order(order_id)\nif not current_user.is_authenticated:\n    return 401\nif order.user_id != current_user.id:\n    log_security_event(current_user.id, order_id)\n    return 403\nreturn jsonify(order)",
        "test_steps": "1. Créer deux comptes A et B et une commande pour A.\n2. Tenter de lire la commande avec la session B.\n3. Attendre 403/404 et une entrée de journal.\n4. Vérifier que A peut toujours y accéder.",
        "detection": "Analyser chaque endpoint qui reçoit un identifiant et vérifier la présence d'un contrôle de propriété côté serveur.",
        "references_json": '["https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/"]',
    },
    {
        "id": "lab-session", "slug": "session-hardening",
        "title": "Fixation de session",
        "category": "PHP", "level": "B",
        "description": "L'identifiant de session n'est pas renouvelé après connexion. La correction régénère l'identifiant et durcit le cookie.",
        "objective": "Vérifier la rotation, les attributs du cookie et la destruction à la déconnexion.",
        "vulnerable_code": "session_start();\nif ($login_ok) {\n    $_SESSION['user_id'] = $user['id'];\n}",
        "secure_code": "session_start([\n  'use_strict_mode' => 1,\n  'cookie_httponly' => 1,\n  'cookie_secure' => 1,\n  'cookie_samesite' => 'Lax',\n]);\nif ($login_ok) {\n    session_regenerate_id(true);\n    $_SESSION['user_id'] = $user['id'];\n}",
        "test_steps": "1. Se connecter avec un identifiant de session fixé.\n2. Vérifier que l'identifiant change après authentification.\n3. Contrôler les attributs du cookie dans les outils du navigateur.",
        "detection": "Chercher session_start, les affectations après login et l'absence de session_regenerate_id.",
        "references_json": '["https://owasp.org/www-community/attacks/Session_fixation"]',
    },
    {
        "id": "lab-upload", "slug": "file-upload",
        "title": "Téléversement de fichiers",
        "category": "PHP", "level": "B",
        "description": "Un fichier est enregistré avec son nom d'origine dans un répertoire exécutable. La correction vérifie le contenu et sort le fichier de la racine web.",
        "objective": "Mettre en place une liste blanche, un nom généré, un stockage hors racine et des permissions non exécutables.",
        "vulnerable_code": "move_uploaded_file($_FILES['f']['tmp_name'], __DIR__.'/uploads/'.$_FILES['f']['name']);",
        "secure_code": "$finfo = new finfo(FILEINFO_MIME_TYPE);\n$mime = $finfo->file($_FILES['f']['tmp_name']);\nif (!in_array($mime, ['image/jpeg','image/png'], true) || $_FILES['f']['size'] > 2_000_000) {\n    http_response_code(422); exit;\n}\n$name = bin2hex(random_bytes(16)).'.bin';\nmove_uploaded_file($_FILES['f']['tmp_name'], '/var/app/storage/'.$name);\nchmod('/var/app/storage/'.$name, 0640);",
        "test_steps": "1. Téléverser un fichier image valide et un faux fichier.\n2. Vérifier le rejet du faux fichier.\n3. Vérifier que le fichier stocké n'est pas exécutable par le serveur web.",
        "detection": "Chercher move_uploaded_file, les noms d'origine, l'absence de finfo et un répertoire de destination sous la racine web.",
        "references_json": '["https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload"]',
    },
    {
        "id": "lab-race", "slug": "payment-idempotency",
        "title": "Double paiement et idempotence",
        "category": "Finance", "level": "B",
        "description": "Deux requêtes simultanées peuvent créer deux débits. La correction combine clé d'idempotence, contrainte unique et transaction.",
        "objective": "Garantir qu'une commande ne peut être payée qu'une fois, même en concurrence.",
        "vulnerable_code": "if (order.status != 'paid') {\n    charge(order.amount);\n    order.status = 'paid';\n    order.save();\n}",
        "secure_code": "with db.transaction():\n    order = Order.lock_for_update(order_id)\n    if Payment.exists(idempotency_key=key):\n        return existing_payment\n    if order.status != 'pending':\n        raise Conflict()\n    payment = Payment.create(order=order, key=key, status='processing')\n    charge(order.amount, idempotency_key=key)\n    payment.status = 'captured'\n    order.status = 'paid'",
        "test_steps": "1. Envoyer deux requêtes identiques avec la même clé.\n2. Vérifier qu'un seul paiement est capturé.\n3. Tester deux workers concurrents.",
        "detection": "Chercher les lectures d'état suivies d'écritures sans verrou, l'absence de clé d'idempotence et les contraintes uniques manquantes.",
        "references_json": '["https://owasp.org/www-community/attacks/Race_Condition"]',
    },
    {
        "id": "lab-webhook", "slug": "webhook-signature",
        "title": "Webhook non signé",
        "category": "Finance", "level": "B",
        "description": "Un webhook de paiement accepte un événement sans vérifier la signature ni l'horodatage. La correction valide le HMAC et l'anti-rejeu.",
        "objective": "Mettre en place une vérification de signature, une fenêtre temporelle et une déduplication.",
        "vulnerable_code": "payload = request.json()\nif payload['event'] == 'payment.succeeded':\n    mark_order_paid(payload['order_id'])\nreturn 'ok'",
        "secure_code": "raw = request.get_data()\nsig = request.headers.get('X-Signature', '')\nexpected = hmac.new(WEBHOOK_SECRET, raw, hashlib.sha256).hexdigest()\nif not hmac.compare_digest(sig, expected):\n    abort(401)\nevent = json.loads(raw)\nif abs(time.time() - event['created']) > 300:\n    abort(400)\nif Event.exists(event['id']):\n    return 'duplicate'\nEvent.create(id=event['id'])\n...",
        "test_steps": "1. Envoyer un événement avec une signature valide.\n2. Rejouer le même événement et vérifier la déduplication.\n3. Envoyer une signature invalide et vérifier le rejet.",
        "detection": "Chercher les handlers de webhook qui lisent le corps sans vérifier une signature, un timestamp ou une clé d'événement.",
        "references_json": '["https://owasp.org/www-project-web-security-testing-guide/"]',
    },
    {
        "id": "lab-checkout", "slug": "checkout-integrity",
        "title": "Indicateurs de skimmer sur le checkout",
        "category": "E-commerce", "level": "B",
        "description": "Une page de paiement contient des motifs inertes de skimming. Le scénario montre l'inventaire, la détection et la correction.",
        "objective": "Inventorier les scripts, identifier les motifs suspects, restaurer une page autorisée et vérifier par hash.",
        "vulnerable_code": "<!-- Exemple inerte : le scanner détecte les motifs -->\n<svg onload=\"atob('ZGVtby1vbmx5')\"></svg>\n<script>new Function(codeFromNetwork)()</script>\n<form action=\"https://pay.example.org\"><input name=\"card_number\"></form>",
        "secure_code": "<script src=\"/assets/checkout-v12.js\" integrity=\"sha384-...\" crossorigin=\"anonymous\"></script>\n<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'self'; script-src 'self' https://js.psp.example; frame-ancestors 'none'\">\n<form action=\"https://psp.example/checkout\">...</form>",
        "test_steps": "1. Scanner la page de démonstration locale.\n2. Comparer l'inventaire des scripts au registre autorisé.\n3. Corriger, rescanner et archiver les preuves.",
        "detection": "SVG onload, atob, new Function, WebSocket, localStorage, scripts sans intégrité et domaines inconnus.",
        "references_json": '["https://www.pcisecuritystandards.org/"]',
    },
    {
        "id": "lab-api", "slug": "openapi-auth",
        "title": "Spécification OpenAPI sans sécurité",
        "category": "API", "level": "B",
        "description": "Une spécification expose des endpoints financiers sans exigence de sécurité. Le scénario montre la revue statique du contrat.",
        "objective": "Déclarer les schémas d'authentification, appliquer la sécurité globale et vérifier chaque opération sensible.",
        "vulnerable_code": "paths:\n  /transfers:\n    post:\n      summary: Create transfer\n      responses: {'201': {description: Created}}",
        "secure_code": "components:\n  securitySchemes:\n    bearerAuth: {type: http, scheme: bearer, bearerFormat: JWT}\nsecurity:\n  - bearerAuth: []\npaths:\n  /transfers:\n    post:\n      security: [{bearerAuth: []}]\n      responses: {'201': {description: Created}}",
        "test_steps": "1. charger la spécification de démonstration.\n2. Repérer les opérations sans sécurité.\n3. Ajouter un schéma et vérifier que chaque endpoint mutatif l'exige.",
        "detection": "Absence de securitySchemes, absence de security global/par opération, serveurs HTTP, endpoints financiers non protégés.",
        "references_json": '["https://owasp.org/API-Security/"]',
    },
]


def seed_labs() -> None:
    now = _now()
    with db.db_cursor() as conn:
        for s in LAB_SCENARIOS:
            conn.execute(
                """INSERT OR IGNORE INTO lab_scenarios(
                    id,slug,title,category,level,description,objective,
                    vulnerable_code,secure_code,test_steps,detection,references_json,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    s["id"], s["slug"], s["title"], s["category"], s["level"],
                    s["description"], s["objective"], s["vulnerable_code"],
                    s["secure_code"], s["test_steps"], s["detection"],
                    s["references_json"], now,
                ),
            )


def seed_automation() -> None:
    existing = db.fetch_one("SELECT id FROM automations LIMIT 1")
    if existing:
        return
    now = datetime.now(timezone.utc)
    db.execute(
        """INSERT INTO automations(
            id,project_id,name,kind,interval_minutes,config_json,enabled,
            last_run_at,next_run_at,last_status,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            str(uuid4()), None, "Veille cyber quotidienne", "intel_sync", 1440,
            db.json_dumps({"sources": ["cisa_kev", "cert_fr", "php_releases", "nvd"]}),
            0, None, (now + timedelta(days=1)).isoformat(timespec="seconds"),
            "never", now.isoformat(timespec="seconds"), now.isoformat(timespec="seconds"),
        ),
    )


def seed_all() -> None:
    seed_settings()
    seed_sources()
    seed_project()
    seed_docs()
    from .knowledge_packs import install as install_knowledge_packs  # import tardif : les paquets utilisent db

    install_knowledge_packs()
    seed_labs()
    seed_automation()
