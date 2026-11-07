"""Paquet « Cybersécurité défensive » : développement sécurisé (PHP, Python, Web), audit autorisé et remédiation.

Source : base de connaissances fournie par l'utilisateur (script Supabase « stratege_bizapp »). Fiches de départ,
à faire réviser périodiquement ; les références pointent vers les documentations officielles.
"""
from __future__ import annotations

PACK_ID = "cyfr"
VERSION = "1"

CATEGORIES = {
    "fondamentaux": "Cyber · Fondamentaux de cybersécurité",
    "php": "Cyber · PHP sécurisé",
    "python": "Cyber · Python sécurisé",
    "web": "Cyber · Sécurité des applications Web",
    "vulnerabilites": "Cyber · Vulnérabilités et remédiation",
    "infrastructure": "Cyber · Infrastructure et déploiement",
    "operations": "Cyber · Surveillance et réponse aux incidents",
    "gouvernance": "Cyber · Conformité et bonnes pratiques",
}

# (slug, titre, catégorie, résumé, contenu, difficulté, risque, technologies)
ARTICLES = [
("security-by-design", "Sécurité dès la conception", "fondamentaux", "Intégrer la sécurité à chaque étape du cycle de développement.",
"""La sécurité doit être une exigence fonctionnelle dès la conception, et non une vérification ajoutée à la fin. Définir les actifs à protéger, les utilisateurs, les frontières de confiance, les flux de données et les conséquences d'une compromission.

Méthode :
1. Cartographier les composants, les données et les flux.
2. Identifier les menaces et les abus plausibles.
3. Définir des contrôles préventifs, détectifs et correctifs.
4. Transformer les exigences en tests vérifiables.
5. Réévaluer le modèle de menace à chaque changement important.

Appliquer le moindre privilège, la défense en profondeur, des valeurs sûres par défaut, la réduction de la surface d'attaque et la séparation des environnements. Documenter les risques acceptés, leur propriétaire et leur date de réexamen.""", "beginner", "high", ["architecture", "secure-sdlc"]),
("threat-modeling", "Modélisation des menaces", "fondamentaux", "Structurer l'identification des menaces avant le développement.",
"""Utiliser une représentation simple des composants, magasins de données, acteurs et flux. Délimiter les frontières de confiance. Pour chaque flux, se demander : qui peut envoyer ces données, comment leur authenticité est-elle vérifiée, où sont-elles stockées et qui peut les lire ?

La méthode STRIDE aide à examiner l'usurpation d'identité, la falsification, la répudiation, la divulgation d'information, le déni de service et l'élévation de privilèges. Pour chaque menace, noter scénario, actif concerné, impact, vraisemblance, contrôle existant, action et responsable.

Le modèle de menace est un document vivant. Le mettre à jour lorsqu'une API, un fournisseur, un rôle, une donnée sensible ou une frontière de confiance change.""", "intermediate", "high", ["stride", "architecture"]),
("least-privilege", "Principe du moindre privilège", "fondamentaux", "Limiter les permissions à ce qui est strictement nécessaire.",
"""Chaque compte, processus, clé et service doit disposer du minimum de droits pour accomplir sa fonction. Séparer les comptes administrateurs des comptes ordinaires. Éviter les comptes partagés et les permissions globales.

Dans une application, vérifier l'autorisation côté serveur à chaque opération sensible. Masquer un bouton dans l'interface ne constitue pas un contrôle d'accès. Les droits doivent être vérifiés sur l'objet demandé, pas seulement sur le type d'action.

Réexaminer régulièrement les rôles, révoquer les accès obsolètes, limiter la durée des jetons et journaliser les opérations privilégiées.""", "beginner", "high", ["iam", "authorization"]),
("defense-in-depth", "Défense en profondeur", "fondamentaux", "Éviter qu'une seule défaillance entraîne une compromission totale.",
"""Combiner plusieurs couches indépendantes : validation côté serveur, requêtes paramétrées, contrôle d'accès, segmentation réseau, configuration restrictive, chiffrement, sauvegardes, surveillance et procédure de réponse.

Les couches doivent être complémentaires. Par exemple, un pare-feu applicatif ne remplace pas la correction d'une injection SQL. Un antivirus ne remplace pas la gestion des correctifs. Une sauvegarde connectée en écriture permanente au serveur compromis ne constitue pas une protection suffisante.

Tester régulièrement les hypothèses de chaque couche et surveiller les défaillances silencieuses.""", "beginner", "high", ["architecture", "controls"]),
("risk-assessment", "Évaluation des risques", "fondamentaux", "Classer les risques selon leur impact et leur vraisemblance.",
"""Inventorier les actifs : comptes, données personnelles, code source, secrets, paiements, services et disponibilité. Pour chaque scénario, évaluer la vraisemblance, l'impact métier, l'étendue potentielle et les mesures existantes.

Une matrice simple peut utiliser cinq niveaux de vraisemblance et cinq niveaux d'impact. Ne pas confondre score et certitude : un risque critique doit être expliqué par un scénario concret et des éléments observables.

Prioriser les risques exploitables à distance, sans authentification, touchant des données sensibles ou permettant une prise de contrôle. Attribuer un responsable, une échéance et une preuve de correction.""", "intermediate", "high", ["risk", "governance"]),
("secure-errors", "Gestion sûre des erreurs", "fondamentaux", "Éviter de divulguer des informations techniques aux utilisateurs.",
"""Afficher un message compréhensible et neutre à l'utilisateur. Conserver les détails techniques dans des journaux protégés : identifiant de corrélation, type d'erreur, composant et horodatage.

Ne jamais exposer en production les traces d'exécution, chemins locaux, variables d'environnement, requêtes SQL, secrets, jetons ou détails de configuration. Les erreurs doivent échouer de manière sûre : une erreur d'autorisation ne doit jamais être transformée en autorisation implicite.

Prévoir une page d'erreur générique et un mécanisme interne permettant de retrouver l'événement sans révéler les données sensibles.""", "beginner", "medium", ["logging", "information-disclosure"]),
("php-version", "Maintenir PHP à jour", "php", "Utiliser une version PHP maintenue et appliquer les correctifs.",
"""Choisir une branche PHP encore maintenue par le projet PHP et planifier les mises à niveau avant la fin du support. Les versions non maintenues ne reçoivent plus les correctifs de sécurité nécessaires.

Avant une mise à niveau : inventorier les extensions, vérifier la compatibilité, exécuter les tests, mettre à jour les dépendances et tester sur un environnement de préproduction. Surveiller les avis de sécurité PHP et ceux des extensions utilisées.

Ne pas considérer le masquage de la version dans les en-têtes comme une mesure de sécurité suffisante : la vraie protection consiste à maintenir le runtime et ses composants.""", "beginner", "high", ["php", "patch-management"]),
("php-production-config", "Configuration PHP de production", "php", "Réduire l'exposition des erreurs et fonctions sensibles.",
"""En production, désactiver l'affichage des erreurs au navigateur et activer une journalisation contrôlée. Vérifier les paramètres de session, les limites mémoire et de taille de requête, les délais d'exécution et la configuration des téléversements.

Exemple de principes de configuration :
- display_errors = Off
- log_errors = On
- expose_php = Off
- session.use_strict_mode = On
- session.cookie_httponly = On
- session.cookie_secure = On lorsque le site est servi en HTTPS
- session.cookie_samesite = Lax ou une politique plus stricte adaptée au parcours

Les valeurs exactes doivent être testées selon l'application, le proxy, le domaine et les besoins métier. Ne pas copier une configuration sans vérifier son effet.""", "intermediate", "high", ["php.ini", "configuration"]),
("php-sql-injection", "Prévenir les injections SQL en PHP", "php", "Utiliser PDO et les requêtes préparées.",
"""Ne jamais concaténer une entrée utilisateur dans une requête SQL. Utiliser PDO avec des paramètres liés ou un ORM correctement utilisé.

Exemple :
$stmt = $pdo->prepare('SELECT id, email FROM users WHERE email = :email');
$stmt->execute(['email' => $email]);
$user = $stmt->fetch();

Les paramètres liés protègent les valeurs, mais ne remplacent pas une liste blanche pour les noms de colonnes, tables ou directions de tri, qui ne peuvent généralement pas être liés comme des valeurs. Pour ces éléments dynamiques, choisir parmi des identifiants prédéfinis côté serveur.

Utiliser un compte SQL limité aux opérations nécessaires. Ne pas retourner les erreurs SQL brutes au client.""", "beginner", "critical", ["php", "pdo", "sql-injection"]),
("php-xss", "Prévenir les XSS en PHP", "php", "Encoder les données au moment de leur insertion dans un contexte HTML.",
"""Une XSS apparaît lorsqu'une donnée non fiable est interprétée comme du code actif dans le navigateur. Échapper les données selon le contexte de sortie, et non au moment de leur stockage.

Pour du texte HTML, utiliser htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'). Cela ne suffit pas pour tous les contextes : JavaScript, CSS, URL et attributs particuliers nécessitent des protections adaptées. Éviter de construire du JavaScript avec des données utilisateur.

Préférer les templates qui échappent automatiquement. Ajouter une Content Security Policy en défense complémentaire, sans la considérer comme un substitut à l'encodage contextuel.""", "beginner", "high", ["php", "xss", "output-encoding"]),
("php-csrf", "Protection CSRF en PHP", "php", "Protéger les actions sensibles déclenchées par le navigateur.",
"""Pour les requêtes qui modifient un état, utiliser un jeton CSRF imprévisible, lié à la session et vérifié côté serveur. Ne pas utiliser GET pour modifier des données.

Les cookies SameSite réduisent certaines attaques mais ne remplacent pas systématiquement les jetons CSRF. Vérifier également Origin ou Referer lorsque c'est pertinent, en tenant compte des proxys et des clients légitimes.

Le jeton ne doit pas être placé dans une URL ni journalisé. Après authentification ou changement de privilège, renouveler les éléments de session concernés.""", "intermediate", "high", ["php", "csrf", "sessions"]),
("php-session", "Sécuriser les sessions PHP", "php", "Protéger l'identifiant de session et son cycle de vie.",
"""Activer les cookies uniquement, le mode strict et les attributs Secure, HttpOnly et SameSite adaptés. Régénérer l'identifiant de session après connexion et changement de privilège avec session_regenerate_id.

Définir une expiration côté serveur, invalider la session lors de la déconnexion et prévoir une révocation des sessions sensibles. Ne pas placer d'identifiant de session dans l'URL. Utiliser HTTPS partout et éviter les sessions partagées sans contrôle entre applications.

Ne jamais stocker de mot de passe en clair dans la session. Éviter d'y placer des données sensibles inutiles.""", "intermediate", "high", ["php", "session", "authentication"]),
("php-passwords", "Stockage sécurisé des mots de passe en PHP", "php", "Utiliser les fonctions natives de hachage adaptées aux mots de passe.",
"""Utiliser password_hash() pour créer un hachage et password_verify() pour vérifier un mot de passe. Préférer l'algorithme recommandé par la version PHP maintenue, généralement PASSWORD_DEFAULT, et réévaluer les paramètres de coût selon les capacités du serveur.

Ne jamais utiliser MD5, SHA-1 ou un simple SHA-256 pour stocker des mots de passe. Ne pas inventer son propre algorithme cryptographique. Utiliser password_needs_rehash() pour faire évoluer les paramètres lors d'une authentification réussie.

Prévoir une limitation des tentatives, une détection des abus et une procédure de réinitialisation qui utilise un jeton aléatoire à durée limitée, stocké sous forme hachée.""", "beginner", "critical", ["php", "passwords", "cryptography"]),
("php-file-upload", "Sécuriser les téléversements de fichiers PHP", "php", "Valider les fichiers côté serveur et les isoler du code exécutable.",
"""Ne jamais faire confiance au nom, à l'extension ou au type MIME envoyé par le navigateur. Vérifier la taille, détecter le type réel avec une bibliothèque adaptée, appliquer une liste de formats autorisés et générer un nom de stockage aléatoire.

Stocker les fichiers hors de la racine Web lorsque possible. Interdire l'exécution dans le répertoire de stockage. Limiter les dimensions et le traitement des images, car les parseurs peuvent être vulnérables. Contrôler les droits d'accès au téléchargement.

Éviter les chemins fournis par l'utilisateur. Protéger les archives contre les chemins traversants et les décompressions disproportionnées. Analyser les fichiers selon le risque et les obligations du service.""", "intermediate", "critical", ["php", "uploads", "path-traversal"]),
("php-ssrf", "Prévenir les SSRF dans une application PHP", "php", "Contrôler les requêtes serveur vers des destinations externes.",
"""Une SSRF peut conduire un serveur à contacter des services internes ou des métadonnées cloud. Éviter de laisser l'utilisateur fournir une URL arbitraire à une fonction HTTP.

Préférer des destinations autorisées définies côté serveur. Valider le schéma, le nom d'hôte et le port ; résoudre et contrôler les adresses IP ; bloquer les plages privées, locales, link-local et réservées ; revalider après redirection et désactiver les redirections automatiques si elles ne sont pas nécessaires.

Ajouter des règles de sortie réseau au niveau infrastructure. Une validation applicative seule peut être contournée par des changements DNS ou des redirections.""", "advanced", "critical", ["php", "ssrf", "network"]),
("php-secrets", "Gestion des secrets en PHP", "php", "Ne pas placer les clés et mots de passe dans le dépôt.",
"""Les secrets comprennent les clés API, mots de passe de base de données, clés de chiffrement, jetons OAuth et clés privées. Les injecter depuis un gestionnaire de secrets ou des variables d'environnement protégées au runtime.

Ne jamais committer un fichier .env réel. Fournir un .env.example sans valeurs sensibles. Restreindre l'accès aux secrets, les faire tourner après une exposition et éviter de les afficher dans les logs ou messages d'erreur.

Les variables d'environnement ne sont pas un coffre-fort à elles seules : limiter les personnes et processus capables de les lire, et utiliser un gestionnaire dédié lorsque disponible.""", "beginner", "critical", ["php", "secrets", "configuration"]),
("php-dependencies", "Sécuriser les dépendances PHP avec Composer", "php", "Maîtriser les bibliothèques tierces et leur provenance.",
"""Conserver composer.lock dans le dépôt d'une application afin de reproduire les versions. Mettre à jour régulièrement les dépendances, examiner les changements et automatiser la détection des avis de sécurité.

N'installer que des paquets nécessaires provenant de sources fiables. Éviter les dépendances abandonnées et les scripts d'installation non compris. Utiliser des versions compatibles et tester les mises à jour dans un environnement isolé.

Un audit automatisé ne prouve pas l'absence de vulnérabilité : il complète la revue du code et la surveillance des avis fournisseurs.""", "intermediate", "high", ["php", "composer", "supply-chain"]),
("python-input-validation", "Validation des entrées en Python", "python", "Valider type, format, longueur et domaine métier.",
"""Traiter toute donnée provenant d'un utilisateur, d'un fichier, d'une API ou d'une file de messages comme non fiable. Valider côté serveur avec des schémas explicites : types, longueurs, plages, formats, valeurs autorisées et relations métier.

Privilégier les listes d'autorisation aux listes de blocage. Refuser les données invalides plutôt que de les corriger silencieusement lorsque cela peut modifier leur sens. Normaliser de manière cohérente avant la validation lorsque le format l'exige.

La validation ne remplace pas l'encodage de sortie, les requêtes paramétrées ou les contrôles d'autorisation.""", "beginner", "high", ["python", "validation"]),
("python-sql", "Requêtes SQL paramétrées en Python", "python", "Utiliser les paramètres du pilote SQL ou de l'ORM.",
"""Ne jamais construire une requête SQL en interpolant une chaîne issue d'une entrée utilisateur. Utiliser les paramètres du pilote, par exemple cursor.execute('SELECT ... WHERE id = %s', (user_id,)) selon la bibliothèque utilisée.

Ne pas confondre le marqueur de paramètre d'un pilote avec celui d'un autre. Les noms de colonnes et directions de tri doivent provenir d'une liste blanche. Accorder au compte de base de données des permissions minimales.

Tester les chemins d'erreur et s'assurer que les exceptions SQL ne révèlent pas les requêtes, identifiants ou données internes.""", "beginner", "critical", ["python", "sql-injection", "database"]),
("python-subprocess", "Utiliser subprocess de manière sûre", "python", "Éviter l'interprétation de commandes construites avec des données non fiables.",
"""Éviter shell=True lorsque des arguments peuvent être fournis ou influencés par un utilisateur. Préférer subprocess.run avec une liste d'arguments, un exécutable connu, un délai maximal, un environnement minimal et des permissions restreintes.

Ne pas considérer shlex.quote comme une solution universelle. Ne jamais laisser un utilisateur choisir librement l'exécutable ou les options sensibles. Vérifier le code de retour et limiter les ressources.

Si une commande externe n'est pas indispensable, préférer une bibliothèque Python qui fournit directement la fonctionnalité.""", "intermediate", "critical", ["python", "subprocess", "command-injection"]),
("python-deserialization", "Éviter la désérialisation non sûre", "python", "Ne jamais charger des objets pickle provenant d'une source non fiable.",
"""pickle peut exécuter du code pendant la désérialisation. Ne jamais charger un fichier pickle reçu d'un utilisateur, téléchargé ou fourni par un système non maîtrisé.

Pour des échanges de données, préférer JSON avec validation stricte du schéma. YAML doit être chargé avec une fonction sûre, telle que yaml.safe_load, et les données doivent ensuite être validées. Limiter la taille et la profondeur des documents.

La signature d'un fichier peut aider à vérifier son origine, mais ne transforme pas un format dangereux en format sûr si la clé de signature ou le producteur est compromis.""", "beginner", "critical", ["python", "pickle", "deserialization"]),
("python-secrets", "Génération aléatoire et secrets Python", "python", "Utiliser le module secrets pour les jetons de sécurité.",
"""Pour générer des jetons de réinitialisation, clés temporaires ou valeurs imprévisibles, utiliser le module secrets et non random, qui est conçu pour des simulations et non pour la cryptographie.

Exemple : token = secrets.token_urlsafe(32)

Stocker les jetons sensibles sous forme hachée lorsque cela est possible, leur associer une expiration, un usage unique et une révocation. Ne pas écrire les jetons dans les journaux. Utiliser une bibliothèque cryptographique reconnue pour les opérations de chiffrement et de signature.""", "beginner", "high", ["python", "secrets", "cryptography"]),
("python-path-traversal", "Prévenir le path traversal en Python", "python", "Empêcher l'accès à des fichiers en dehors du répertoire autorisé.",
"""Ne pas concaténer directement un chemin utilisateur avec un répertoire de stockage. Résoudre le chemin canonique, vérifier qu'il reste sous le répertoire racine autorisé et prendre en compte les liens symboliques et les courses entre vérification et ouverture.

Utiliser des identifiants internes plutôt que des chemins transmis par le client. Appliquer des permissions système minimales. Pour les archives, contrôler chaque entrée avant extraction et refuser les chemins absolus ou contenant des remontées de répertoire.

Les contrôles doivent être effectués au plus près de l'ouverture réelle du fichier.""", "intermediate", "high", ["python", "filesystem", "path-traversal"]),
("python-requests", "Sécuriser les appels HTTP Python", "python", "Contrôler TLS, délais, redirections et destinations.",
"""Utiliser la validation TLS par défaut et ne pas désactiver verify en production. Définir des délais de connexion et de lecture. Limiter la taille des réponses, contrôler les redirections et traiter les erreurs réseau.

Lorsque l'URL est influencée par l'utilisateur, appliquer des contrôles anti-SSRF : destinations autorisées, blocage des IP internes et link-local, résolution DNS contrôlée et filtrage réseau sortant.

Ne jamais transmettre automatiquement des en-têtes d'authentification à une destination différente après une redirection. Protéger les jetons et données personnelles dans les journaux.""", "intermediate", "high", ["python", "http", "ssrf"]),
("python-dependencies", "Sécuriser l'écosystème Python", "python", "Isoler les dépendances et contrôler leur intégrité.",
"""Utiliser un environnement virtuel par projet. Déclarer les dépendances et verrouiller leurs versions dans un fichier adapté à l'outil choisi. Mettre à jour les bibliothèques régulièrement et surveiller les avis de sécurité.

Installer depuis des dépôts fiables, éviter les paquets au nom proche d'un paquet connu et examiner les dépendances transitives. Réduire les dépendances inutiles et vérifier la provenance des artefacts.

Les outils d'analyse de dépendances doivent être intégrés à la CI, avec une procédure de traitement des alertes et des exceptions temporaires documentées.""", "beginner", "high", ["python", "pip", "supply-chain"]),
("python-flask-django", "Sécuriser les applications Flask et Django", "python", "Activer les protections natives des frameworks.",
"""En production, désactiver le mode debug. Définir les hôtes autorisés, les origines CORS nécessaires, les cookies sécurisés et les paramètres HTTPS. Protéger les secrets de configuration et ne pas utiliser la clé de développement par défaut.

Django fournit des protections CSRF, un système de templates avec échappement et des paramètres de sécurité à configurer. Flask nécessite une configuration rigoureuse des sessions, extensions, cookies et protections CSRF adaptées.

Mettre à jour le framework, limiter les extensions, vérifier les permissions sur chaque ressource et ne jamais faire confiance à une valeur simplement parce qu'elle vient du frontend.""", "intermediate", "critical", ["python", "flask", "django"]),
("http-https", "HTTPS et configuration TLS", "web", "Chiffrer les échanges et éviter les configurations obsolètes.",
"""Servir l'application en HTTPS avec un certificat valide et renouvelé automatiquement. Rediriger HTTP vers HTTPS. Désactiver les protocoles et suites cryptographiques obsolètes selon les recommandations actuelles du fournisseur TLS.

Activer HSTS uniquement après avoir vérifié que tous les sous-domaines concernés sont prêts à fonctionner en HTTPS. Ne pas activer preload à la légère, car son retrait peut être long.

Le chiffrement en transit protège le canal mais ne garantit ni l'autorisation, ni l'intégrité de l'application, ni la sécurité des données stockées.""", "beginner", "high", ["https", "tls", "web"]),
("http-security-headers", "En-têtes HTTP de sécurité", "web", "Renforcer les protections du navigateur.",
"""Évaluer et configurer notamment Content-Security-Policy, Strict-Transport-Security, X-Content-Type-Options: nosniff, Referrer-Policy et une politique de permissions adaptée.

La CSP doit être construite à partir des ressources réellement nécessaires. Commencer par un mode de rapport si utile, analyser les violations, puis appliquer une politique stricte. Éviter unsafe-inline et unsafe-eval lorsque l'architecture peut s'en passer.

Les en-têtes ne corrigent pas une faille serveur. Tester leur présence, leur portée, les sous-domaines et les parcours d'authentification.""", "intermediate", "high", ["headers", "csp", "browser"]),
("cors", "Configurer CORS correctement", "web", "Limiter les origines autorisées par les API.",
"""CORS est un mécanisme appliqué par les navigateurs ; ce n'est pas un système d'authentification ni un pare-feu. Autoriser uniquement les origines nécessaires, les méthodes et les en-têtes réellement utilisés.

Ne pas refléter aveuglément l'en-tête Origin. Ne pas combiner une origine générique avec l'envoi de credentials. Vérifier les réponses preflight et les règles sur les cookies.

Une API doit toujours authentifier et autoriser chaque requête indépendamment de CORS, car des clients non navigateur peuvent appeler directement ses endpoints.""", "intermediate", "high", ["cors", "api"]),
("authentication", "Concevoir une authentification robuste", "web", "Protéger les comptes, les sessions et les parcours de connexion.",
"""Utiliser un mécanisme éprouvé plutôt qu'un système d'authentification improvisé. Stocker les mots de passe avec un algorithme adapté, limiter les tentatives, protéger la récupération de compte et envisager une authentification multifacteur.

Éviter les messages qui révèlent si une adresse existe lorsque cela facilite l'énumération. Ajouter une limitation progressive, une détection des comportements anormaux et des alertes pour les opérations sensibles.

Les sessions et jetons doivent avoir une durée adaptée, une portée limitée, une révocation possible et une protection contre le vol. Réauthentifier l'utilisateur pour les actions à fort impact.""", "intermediate", "critical", ["authentication", "mfa", "account-security"]),
("authorization-idor", "Prévenir IDOR et BOLA", "web", "Vérifier les droits sur chaque objet demandé.",
"""Une référence d'objet prévisible ou aléatoire ne constitue pas une autorisation. Pour chaque lecture, modification, suppression ou export, vérifier que l'utilisateur connecté possède le droit d'agir sur cet objet précis.

Appliquer les contrôles dans le backend et dans les requêtes de données. Ne pas se fier à un user_id, role ou owner_id envoyé par le client. Pour une API, vérifier les droits au niveau de chaque ressource et propriété sensible.

Créer des tests avec plusieurs comptes : utilisateur A ne doit pas pouvoir accéder aux objets de B en changeant un identifiant ou un paramètre.""", "intermediate", "critical", ["idor", "bola", "authorization", "api"]),
("csrf-web", "Prévenir les attaques CSRF", "web", "Protéger les opérations déclenchées par des cookies de session.",
"""Les navigateurs peuvent joindre automatiquement des cookies à certaines requêtes intersites. Protéger les opérations qui modifient un état avec des jetons CSRF ou un mécanisme équivalent éprouvé.

Utiliser des méthodes HTTP cohérentes, des cookies SameSite appropriés et des vérifications Origin/Referer adaptées. Les opérations sensibles ne doivent pas être déclenchées par une simple navigation GET.

Tester les parcours réels, notamment formulaires, API, sous-domaines et intégrations tierces.""", "beginner", "high", ["csrf", "cookies"]),
("xss-web", "Comprendre et corriger les XSS", "web", "Éviter que des données deviennent du code exécuté dans le navigateur.",
"""Les XSS peuvent être réfléchies, stockées ou basées sur le DOM. La défense principale est l'encodage contextuel des sorties et l'utilisation d'API DOM sûres, par exemple textContent plutôt que innerHTML pour du texte non fiable.

Éviter les constructions HTML dynamiques à partir de chaînes. Si du HTML utilisateur est une fonctionnalité nécessaire, utiliser un assainisseur maintenu avec une configuration restrictive. Ajouter CSP en couche complémentaire.

Tester les contextes HTML, attribut, URL et JavaScript séparément. Une validation d'entrée générique ne remplace pas l'encodage à la sortie.""", "beginner", "critical", ["xss", "browser"]),
("sql-injection", "Comprendre les injections SQL", "vulnerabilites", "Identifier les constructions de requêtes dangereuses et les remplacer.",
"""Une injection SQL survient lorsque des données sont interprétées comme une partie de la syntaxe SQL. La correction standard consiste à utiliser des requêtes paramétrées, des ORM correctement utilisés et des permissions minimales sur le compte de base de données.

Examiner les concaténations, filtres, recherches, tris, rapports et requêtes dynamiques. Les noms de colonnes ou clauses dynamiques doivent être choisis dans une liste blanche.

Valider la correction avec des tests unitaires et d'intégration qui vérifient que les entrées restent des données. Ne pas effectuer de test sur un système tiers sans autorisation écrite.""", "beginner", "critical", ["sql-injection", "database"]),
("path-traversal", "Comprendre le path traversal", "vulnerabilites", "Empêcher les accès hors des répertoires autorisés.",
"""Le path traversal exploite une construction de chemin insuffisamment contrôlée. Il peut toucher les téléchargements, imports, exports, aperçus et extractions d'archives.

Utiliser des identifiants internes, canonicaliser les chemins et vérifier leur appartenance au répertoire racine prévu. Contrôler les liens symboliques, les séparateurs spécifiques au système et les courses entre contrôle et accès.

La meilleure architecture évite de laisser le client fournir un chemin de système de fichiers.""", "intermediate", "high", ["path-traversal", "filesystem"]),
("ssrf", "Comprendre les SSRF", "vulnerabilites", "Empêcher un serveur de contacter des destinations internes non autorisées.",
"""Une SSRF permet d'utiliser une fonctionnalité serveur pour effectuer des requêtes vers des destinations inattendues. Les fonctions d'import d'URL, d'aperçu de lien, de webhook et de conversion de document sont particulièrement sensibles.

Restreindre les destinations, les protocoles et les ports. Bloquer les plages internes et link-local, contrôler les redirections, les résolutions DNS et les adresses IPv4/IPv6. Compléter par un filtrage des sorties réseau.

Journaliser les destinations refusées sans conserver inutilement les paramètres qui pourraient contenir des secrets.""", "advanced", "critical", ["ssrf", "network"]),
("rce-prevention", "Réduire le risque d'exécution de code à distance", "vulnerabilites", "Supprimer les chemins d'exécution non nécessaires et isoler les traitements.",
"""L'exécution de code à distance peut provenir d'une injection de commande, d'une désérialisation dangereuse, d'un moteur de template mal utilisé ou d'un composant vulnérable.

Éviter d'interpréter des entrées comme du code. Supprimer les appels shell inutiles, désactiver les fonctionnalités dangereuses, maintenir les dépendances et exécuter les tâches dans des environnements isolés avec permissions minimales.

Un service qui traite des fichiers ou du code fourni par des utilisateurs doit être isolé du réseau interne, limité en CPU, mémoire, durée et espace disque, et ne doit pas recevoir de secrets de production.""", "advanced", "critical", ["rce", "sandbox", "command-injection"]),
("file-inclusion", "Prévenir les inclusions de fichiers non sûres", "vulnerabilites", "Ne jamais choisir un fichier inclus à partir d'une entrée arbitraire.",
"""Dans PHP ou d'autres environnements, ne pas construire un chemin d'inclusion à partir d'un paramètre utilisateur. Utiliser une table de correspondance fixe entre des identifiants fonctionnels et des fichiers connus.

Désactiver les fonctionnalités d'inclusion distante non nécessaires. Restreindre les permissions du processus et isoler les répertoires d'upload. Vérifier les chemins et les configurations de résolution.

Les tests doivent vérifier qu'une valeur inattendue ne permet ni de charger un fichier arbitraire, ni de divulguer des fichiers de configuration.""", "intermediate", "critical", ["php", "file-inclusion"]),
("deserialization", "Prévenir les désérialisations dangereuses", "vulnerabilites", "Utiliser des formats de données simples et valider les schémas.",
"""Ne pas désérialiser des objets provenant d'une source non fiable avec des mécanismes capables d'instancier des classes ou d'exécuter des comportements. Préférer JSON et des schémas de données explicites.

Limiter la taille, la profondeur, le nombre d'éléments et les types autorisés. Vérifier les bibliothèques et versions qui manipulent les formats sérialisés. Ne pas confondre intégrité cryptographique et innocuité du contenu.""", "intermediate", "critical", ["deserialization"]),
("rate-limiting", "Limiter les abus et le déni de service", "web", "Protéger les endpoints coûteux et les fonctions sensibles.",
"""Mettre en place des limites adaptées par compte, adresse, jeton, endpoint et période. Les limites doivent tenir compte des utilisateurs derrière des NAT et des réseaux partagés. Ajouter des plafonds de taille, des délais et des quotas pour les opérations coûteuses.

Protéger particulièrement la connexion, la récupération de compte, l'envoi d'e-mails, la recherche, les exports et les traitements IA. Utiliser une file de tâches pour les traitements longs et limiter la concurrence.

Surveiller les faux positifs et prévoir une réponse graduée. Un rate limit ne remplace pas une capacité d'infrastructure adaptée.""", "intermediate", "high", ["dos", "rate-limiting", "api"]),
("api-security", "Sécuriser les API REST", "web", "Appliquer authentification, autorisation, validation et limites.",
"""Inventorier les endpoints et versions. Exiger TLS, authentifier les clients, autoriser chaque action et chaque objet, valider les schémas et limiter les volumes. Éviter d'exposer des propriétés internes ou des champs non nécessaires.

Ne pas placer de secrets dans les URL. Définir des erreurs cohérentes, des quotas, des délais, une pagination bornée et une politique CORS minimale. Versionner les API et retirer les versions obsolètes selon un calendrier communiqué.

Documenter les scopes, rôles, limites et comportements d'erreur. Tester les contrôles d'accès avec plusieurs profils.""", "intermediate", "critical", ["api", "rest", "authorization"]),
("jwt-security", "Utiliser les JWT avec prudence", "web", "Vérifier strictement signature, algorithme, audience et expiration.",
"""Un JWT signé n'est pas nécessairement chiffré : son contenu peut être lisible. Ne pas y placer de secrets. Vérifier la signature avec une bibliothèque reconnue et une liste d'algorithmes autorisés, ainsi que issuer, audience, expiration et autres claims nécessaires.

Prévoir rotation des clés, durée de vie courte, révocation ou stratégie de rotation des refresh tokens. Ne jamais accepter un algorithme choisi sans contrôle par le jeton lui-même.

Stocker les jetons côté client avec une stratégie adaptée au modèle de menace. Les cookies HttpOnly réduisent l'accès JavaScript mais imposent une protection CSRF.""", "advanced", "high", ["jwt", "tokens", "authentication"]),
("password-reset", "Sécuriser la réinitialisation de mot de passe", "web", "Créer un parcours de récupération à usage unique et à durée limitée.",
"""Générer un jeton cryptographiquement aléatoire, lié à un compte, stocké sous forme hachée et expirant rapidement. Le rendre à usage unique et l'invalider après utilisation ou nouvelle demande selon la politique définie.

Ne pas révéler inutilement si un compte existe. Envoyer le lien vers une adresse déjà vérifiée, limiter les demandes et protéger les journaux. Après réinitialisation, informer l'utilisateur et proposer la révocation des sessions existantes.

Éviter les questions secrètes faibles et ne jamais envoyer un mot de passe en clair.""", "intermediate", "high", ["password-reset", "authentication"]),
("file-storage", "Sécuriser le stockage des fichiers", "web", "Isoler les fichiers et contrôler chaque accès.",
"""Stocker les fichiers privés dans un espace non public. Générer des noms internes, contrôler les autorisations au téléchargement et utiliser des URL signées de courte durée lorsque nécessaire.

Séparer le stockage des fichiers exécutables, désactiver l'exécution dans les répertoires d'upload, vérifier les types réels et appliquer des limites de taille. Prévoir un cycle de vie : quarantaine, validation, disponibilité, suppression et conservation.

Éviter les buckets publics par défaut. Auditer les permissions, les règles de partage et les journaux d'accès.""", "intermediate", "high", ["storage", "uploads", "cloud"]),
("database-security", "Sécuriser une base de données", "web", "Réduire les privilèges, protéger les sauvegardes et surveiller les accès.",
"""Ne pas exposer le port de base de données à Internet sans nécessité. Utiliser un réseau privé, TLS lorsque disponible, des comptes distincts par application et des permissions minimales.

Chiffrer les sauvegardes, contrôler leur accès, tester les restaurations et définir des durées de conservation. Éviter les données réelles dans les environnements de développement. Masquer ou anonymiser les jeux de test.

Surveiller les connexions inhabituelles, les modifications de privilèges, les exports volumineux et les erreurs répétées.""", "intermediate", "critical", ["database", "postgresql", "backup"]),
("supabase-rls", "Sécuriser Supabase avec RLS", "infrastructure", "Activer et tester les politiques Row Level Security.",
"""Pour chaque table exposée via l'API Supabase, déterminer si RLS doit être activé. Définir des politiques explicites pour SELECT, INSERT, UPDATE et DELETE selon le rôle et la propriété des lignes.

Ne jamais exposer la clé service_role dans le navigateur : elle contourne les politiques RLS. La clé anon/public est conçue pour être utilisée côté client uniquement avec des politiques correctement configurées.

Tester les politiques avec plusieurs utilisateurs, y compris sans session, utilisateur standard et administrateur. Vérifier aussi les vues, fonctions, tables de stockage et accès indirects.""", "intermediate", "critical", ["supabase", "postgresql", "rls"]),
("cloud-secrets", "Protéger les secrets dans le cloud", "infrastructure", "Utiliser des identités de service et des secrets à portée limitée.",
"""Attribuer une identité distincte à chaque service. Éviter les clés statiques lorsque des identités managées sont disponibles. Limiter les rôles IAM, les ressources accessibles et les permissions d'écriture.

Ne jamais inclure de secret dans une image de conteneur, un dépôt, un frontend ou des logs de build. Injecter les secrets au runtime via un gestionnaire dédié. Faire tourner les secrets et auditer les accès.

En cas de fuite, révoquer immédiatement la clé, rechercher son usage dans les journaux et évaluer les données accessibles pendant la période d'exposition.""", "intermediate", "critical", ["cloud", "iam", "secrets"]),
("secure-headers-proxy", "Configurer le proxy et les en-têtes de confiance", "infrastructure", "Éviter de faire confiance aux en-têtes transmis par un client.",
"""Les en-têtes X-Forwarded-For, X-Forwarded-Proto et similaires ne sont fiables que lorsqu'ils proviennent d'un proxy explicitement approuvé. Configurer correctement la liste des proxys de confiance.

Une mauvaise configuration peut fausser les journaux, les contrôles d'accès IP, les redirections HTTPS et la génération d'URL. Éviter de faire confiance à n'importe quelle valeur envoyée directement par Internet.

Documenter la chaîne proxy-load balancer-application et tester les accès directs au backend.""", "advanced", "high", ["proxy", "network"]),
("container-hardening", "Durcir les conteneurs", "infrastructure", "Exécuter les conteneurs avec une surface et des privilèges minimaux.",
"""Utiliser des images de base maintenues et de taille réduite. Épingler les versions ou digests, scanner les images et reconstruire régulièrement. Exécuter en utilisateur non-root, supprimer les capacités inutiles et utiliser un système de fichiers en lecture seule lorsque possible.

Ne pas monter le socket Docker dans un conteneur applicatif sans raison exceptionnelle. Limiter CPU, mémoire, processus et accès réseau. Ne pas embarquer de secrets dans les couches d'image.

Séparer build et runtime, signer les artefacts lorsque possible et conserver la traçabilité des images déployées.""", "intermediate", "high", ["docker", "containers", "hardening"]),
("ci-cd-security", "Sécuriser la chaîne CI/CD", "infrastructure", "Protéger les workflows, jetons et artefacts de déploiement.",
"""Limiter les permissions des jetons CI au strict nécessaire. Épingler les actions tierces à des versions ou commits vérifiés, protéger les branches, exiger des revues et éviter d'exposer des secrets aux contributions non fiables.

Séparer les environnements, utiliser des approbations pour la production et produire des artefacts traçables. Scanner les dépendances et secrets, exécuter les tests de sécurité et conserver les journaux de déploiement.

Un pipeline doit échouer clairement en cas de configuration critique manquante. Ne pas contourner un contrôle de sécurité pour faire passer un build.""", "intermediate", "critical", ["github-actions", "ci-cd", "supply-chain"]),
("backup-recovery", "Sauvegardes et restauration", "infrastructure", "Préparer une reprise réelle après incident.",
"""Définir RPO et RTO selon les besoins métier. Appliquer une stratégie comprenant des copies séparées, protégées contre la suppression et, lorsque possible, immuables ou hors ligne.

Chiffrer les sauvegardes, limiter les droits de suppression et surveiller les échecs. Tester les restaurations régulièrement dans un environnement isolé. Une sauvegarde non restaurable n'est pas une sauvegarde fiable.

Documenter l'ordre de reprise : identité, réseau, base de données, stockage, application, secrets et validation métier.""", "beginner", "critical", ["backup", "disaster-recovery"]),
("logging-monitoring", "Journalisation et surveillance", "operations", "Détecter les événements utiles sans collecter trop de données.",
"""Journaliser les connexions, échecs d'authentification, changements de privilèges, opérations administratives, accès sensibles, erreurs applicatives et événements de déploiement.

Inclure horodatage cohérent, identifiant de requête, service et résultat. Éviter les mots de passe, jetons, clés, données bancaires et contenus personnels non nécessaires. Protéger les journaux contre la modification et limiter leur accès.

Créer des alertes actionnables : pics d'échecs, connexions inhabituelles, accès refusés répétés, changements de configuration, erreurs 5xx et consommation anormale. Tester le fonctionnement des alertes.""", "intermediate", "high", ["logging", "monitoring", "siem"]),
("incident-response", "Réponse à un incident de sécurité", "operations", "Contenir, préserver les preuves, éradiquer et rétablir.",
"""Préparer à l'avance les contacts, rôles, procédures et moyens de communication hors bande. En cas d'incident : qualifier, préserver les éléments utiles, contenir sans détruire les preuves, révoquer les secrets compromis, corriger la cause, restaurer depuis une source saine et surveiller une éventuelle réapparition.

Documenter la chronologie, les systèmes touchés, les données potentiellement concernées, les décisions et les actions. Respecter les obligations légales et contractuelles applicables, notamment en matière de données personnelles.

Après l'incident, réaliser un retour d'expérience sans recherche de blâme et suivre les actions correctives jusqu'à leur validation.""", "intermediate", "critical", ["incident-response", "forensics"]),
("vulnerability-management", "Gestion du cycle de vie des vulnérabilités", "vulnerabilites", "Inventorier, prioriser, corriger et vérifier les failles.",
"""Maintenir un inventaire des applications, composants, versions, propriétaires et environnements. Recevoir les alertes fournisseurs et analyser l'exposition réelle.

Prioriser selon la gravité technique, l'exploitabilité, l'exposition réseau, la sensibilité des données et les contrôles compensatoires. Une note CVSS est un indicateur, pas une décision métier complète.

Pour chaque vulnérabilité : créer un ticket, nommer un responsable, fixer une échéance, déployer le correctif, effectuer un test de non-régression et conserver une preuve de clôture. Documenter les exceptions et leur date d'expiration.""", "intermediate", "high", ["cve", "cvss", "patch-management"]),
("secure-code-review", "Revue de code sécurisée", "vulnerabilites", "Examiner les zones sensibles et les changements à risque.",
"""Prioriser les changements touchant l'authentification, les permissions, les paiements, les imports, les uploads, les requêtes SQL, les appels réseau, les secrets et les opérations administratives.

Vérifier les entrées, les encodages de sortie, les permissions, les erreurs, les journaux et les tests. Rechercher les secrets accidentels, dépendances inutiles, appels shell, désérialisations, chemins dynamiques et configurations de debug.

Une revue efficace explique le scénario de risque, la preuve, l'impact et le correctif. Éviter les commentaires vagues comme « code non sécurisé » sans contexte.""", "intermediate", "high", ["code-review", "secure-sdlc"]),
("authorized-testing", "Cadre d'un audit de sécurité autorisé", "gouvernance", "Définir un périmètre et des règles écrites avant tout test.",
"""Obtenir une autorisation écrite du propriétaire du système. Définir les domaines, adresses IP, environnements, comptes de test, horaires, techniques permises, limites de charge, contacts d'urgence et conditions d'arrêt.

Ne tester que les actifs explicitement inclus. Exclure les données réelles non nécessaires, les tiers et les systèmes de production non autorisés. Préférer les environnements de préproduction et les comptes synthétiques.

À la fin, fournir un rapport reproductible avec preuves minimales, impact, niveau de risque, recommandation et procédure de validation du correctif. Ne pas conserver les données découvertes au-delà de ce qui est autorisé.""", "beginner", "high", ["audit", "authorization", "pentest"]),
("security-testing-pipeline", "Tests de sécurité dans le pipeline", "infrastructure", "Automatiser les contrôles sans bloquer inutilement les livraisons.",
"""Combiner analyse statique du code, analyse des dépendances, détection de secrets, tests unitaires, tests d'intégration, vérification de configuration et tests dynamiques sur un environnement autorisé.

Définir des seuils adaptés : bloquer les secrets confirmés et vulnérabilités critiques exploitables ; créer des tickets pour les alertes moins certaines. Éviter les exceptions permanentes. Conserver les rapports de scan et relier les alertes au commit concerné.

Les outils automatisés produisent des faux positifs et des faux négatifs. Compléter par une revue humaine des zones sensibles.""", "intermediate", "high", ["sast", "dast", "sca", "ci-cd"]),
("privacy-data-minimization", "Minimisation et protection des données", "gouvernance", "Ne collecter que les données nécessaires et limiter leur durée de vie.",
"""Cartographier les données personnelles, finalités, bases légales, destinataires, transferts, durées de conservation et mesures de sécurité. Limiter les données collectées et les copies dans les logs, exports et environnements de test.

Mettre en place des contrôles d'accès, chiffrement adapté, pseudonymisation lorsque pertinente et procédures de gestion des demandes des personnes. Définir une politique de conservation et de suppression.

En France et dans l'Union européenne, vérifier les obligations applicables auprès des ressources officielles de la CNIL et du RGPD. Ce contenu est informatif et ne remplace pas un conseil juridique.""", "intermediate", "high", ["privacy", "gdpr", "data-protection"]),
("security-headers-cookies", "Politique de cookies sécurisés", "web", "Réduire le risque de vol et d'envoi intersite des cookies.",
"""Pour les cookies de session, évaluer Secure, HttpOnly, SameSite, Domain et Path. Utiliser le périmètre le plus étroit compatible avec l'application. Éviter les cookies de session accessibles à JavaScript.

Ne pas placer de données sensibles directement dans un cookie sans conception cryptographique adaptée. Prévoir expiration, rotation et invalidation côté serveur.

Tester les sous-domaines, les redirections, les flux OAuth et les intégrations qui peuvent nécessiter des comportements différents.""", "beginner", "high", ["cookies", "session"]),
("oauth-security", "Sécuriser OAuth et les connexions fédérées", "web", "Appliquer les flux modernes et vérifier les paramètres de sécurité.",
"""Utiliser les bibliothèques et fournisseurs reconnus. Pour les applications publiques, privilégier Authorization Code avec PKCE. Vérifier strictement redirect_uri, state et nonce selon le protocole utilisé. Ne pas accepter de redirections ouvertes.

Protéger les secrets des clients confidentiels et ne pas les embarquer dans les applications navigateur. Vérifier issuer, audience, signature et expiration des jetons d'identité. Prévoir la révocation et la rotation des jetons.

Ne jamais confondre authentification OAuth et autorisation métier locale : l'application doit encore décider ce que l'utilisateur peut faire.""", "advanced", "critical", ["oauth", "oidc", "authentication"]),
("websocket-security", "Sécuriser les WebSockets", "web", "Authentifier les connexions et contrôler chaque message.",
"""Vérifier l'origine lors de l'établissement de la connexion, authentifier le client et autoriser chaque canal ou opération. Ne pas supposer qu'une connexion déjà ouverte reste autorisée indéfiniment.

Limiter taille et fréquence des messages, nombre de connexions et durée d'inactivité. Valider le schéma de chaque message et éviter les contenus HTML non assainis.

Protéger les jetons transmis lors de la connexion et éviter de les exposer dans les URL ou journaux.""", "intermediate", "high", ["websocket", "api"]),
("email-security", "Sécuriser les e-mails transactionnels", "web", "Éviter les abus d'envoi et les fuites d'informations.",
"""Protéger les formulaires contre l'envoi massif, limiter les volumes par compte et adresse, et utiliser des modèles qui échappent les contenus dynamiques. Ne pas inclure de secrets ou données excessives dans les e-mails.

Configurer SPF, DKIM et DMARC pour le domaine d'envoi selon les capacités du fournisseur. Utiliser des liens HTTPS à durée limitée pour les actions sensibles et ne pas envoyer de mot de passe en clair.

Surveiller les rebonds, plaintes, volumes inhabituels et changements de configuration du fournisseur.""", "intermediate", "medium", ["email", "spf", "dkim", "dmarc"]),
("dependency-supply-chain", "Sécurité de la chaîne d'approvisionnement logicielle", "infrastructure", "Contrôler les composants, builds et artefacts tiers.",
"""Tenir un inventaire des dépendances directes et transitives. Épingler les versions, vérifier les signatures ou sommes de contrôle disponibles, utiliser des sources fiables et surveiller les avis de sécurité.

Protéger les comptes de publication, les jetons, les workflows et les registres d'artefacts. Séparer les environnements de build et de production. Générer une nomenclature logicielle (SBOM) lorsque cela est pertinent.

Évaluer les mainteneurs, la fréquence de mise à jour, la licence et les risques de dépendance abandonnée.""", "advanced", "high", ["supply-chain", "sbom"]),
("secure-defaults", "Valeurs sûres par défaut", "fondamentaux", "Rendre le choix le plus sûr automatique.",
"""Une installation neuve doit être restrictive : debug désactivé, accès privés par défaut, permissions minimales, secrets non prédéfinis, endpoints administratifs protégés et stockage non public.

Les options dangereuses doivent nécessiter une action explicite, documentée et limitée. Prévoir des contrôles de configuration au démarrage pour refuser les paramètres critiques manquants.

Documenter les exceptions nécessaires et leur justification. Les exemples et fichiers de démonstration ne doivent jamais contenir de véritables secrets.""", "beginner", "high", ["secure-defaults", "configuration"]),
("security-backups-ransomware", "Préparer les sauvegardes face aux rançongiciels", "operations", "Empêcher qu'un incident unique détruise les sauvegardes.",
"""Séparer les identifiants de sauvegarde des identifiants de production. Utiliser des copies immuables ou hors ligne lorsque possible, protéger les consoles d'administration avec MFA et limiter strictement les droits de suppression.

Tester les restaurations et vérifier l'intégrité des sauvegardes. Documenter les dépendances nécessaires à la reprise, y compris clés de chiffrement, DNS, identité et configurations.

En cas de suspicion de rançongiciel, isoler les systèmes touchés selon le plan d'incident et ne pas reconnecter une sauvegarde avant d'avoir évalué son intégrité.""", "intermediate", "critical", ["ransomware", "backup"]),
("security-acceptance-checklist", "Checklist de mise en production sécurisée", "gouvernance", "Contrôler les éléments essentiels avant une livraison.",
"""Avant production, vérifier :
- versions runtime et dépendances maintenues ;
- secrets absents du dépôt et du frontend ;
- HTTPS et cookies sécurisés ;
- erreurs de debug désactivées ;
- authentification et autorisations testées côté serveur ;
- protections contre injections, XSS et CSRF adaptées ;
- limites de débit, taille et délais ;
- téléversements isolés ;
- RLS et permissions de base de données vérifiées ;
- sauvegardes restaurables ;
- journaux sans secrets ;
- alertes et procédure d'incident opérationnelles ;
- tests de non-régression et revue des changements sensibles réalisés.

La checklist doit être adaptée au contexte et chaque point doit être associé à une preuve vérifiable.""", "beginner", "high", ["checklist", "deployment"]),
]

# slug -> [(libellé, url, type)]
REFERENCES = {
    "security-by-design": [("OWASP Application Security Verification Standard (ASVS)", "https://owasp.org/www-project-application-security-verification-standard/"),
                           ("NIST Secure Software Development Framework (SSDF)", "https://csrc.nist.gov/Projects/ssdf")],
    "php-version": [("PHP — versions maintenues", "https://www.php.net/supported-versions.php")],
    "php-production-config": [("PHP Manual — configuration à l'exécution", "https://www.php.net/manual/en/configuration.php")],
    "php-sql-injection": [("PHP Manual — requêtes préparées PDO", "https://www.php.net/manual/en/pdo.prepared-statements.php")],
    "php-passwords": [("PHP Manual — hachage des mots de passe", "https://www.php.net/manual/en/book.password.php")],
    "python-secrets": [("Python — module secrets", "https://docs.python.org/3/library/secrets.html")],
    "python-subprocess": [("Python — module subprocess", "https://docs.python.org/3/library/subprocess.html")],
    "python-deserialization": [("Python — sécurité de pickle", "https://docs.python.org/3/library/pickle.html")],
    "http-security-headers": [("OWASP Secure Headers Project", "https://owasp.org/www-project-secure-headers/")],
    "api-security": [("OWASP API Security Top 10", "https://owasp.org/www-project-api-security/")],
    "vulnerability-management": [("NIST National Vulnerability Database", "https://nvd.nist.gov/"), ("FIRST CVSS", "https://www.first.org/cvss/")],
    "authorized-testing": [("OWASP Web Security Testing Guide", "https://owasp.org/www-project-web-security-testing-guide/")],
    "privacy-data-minimization": [("CNIL — sécurité des données personnelles", "https://www.cnil.fr/fr/securite")],
    "supabase-rls": [("Supabase — Row Level Security", "https://supabase.com/docs/guides/database/postgres/row-level-security")],
    "ci-cd-security": [("GitHub — durcissement de GitHub Actions", "https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions")],
    "container-hardening": [("OWASP Docker Security Cheat Sheet", "https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html")],
    "oauth-security": [("OAuth 2.0 Security Best Current Practice (RFC 9700)", "https://www.rfc-editor.org/rfc/rfc9700")],
}
