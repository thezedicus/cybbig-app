from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import requests

from ... import db
from ...config import MAX_FILE_BYTES, MAX_FILES_DEFAULT, USER_AGENT
from ...utils import read_text, redact_secret, redact_text, safe_relpath, truncate
from .external_tools import run_all as run_external_tools

CODE_EXTENSIONS = {".php", ".phtml", ".inc", ".module", ".install", ".theme", ".php5", ".php7", ".phps"}
SOURCE_EXTENSIONS = {".js", ".mjs", ".ts", ".tsx", ".jsx", ".vue", ".svelte", ".py", ".rb", ".go", ".java", ".kt", ".cs", ".c", ".cpp", ".cc", ".rs", ".sh", ".sql", ".pl", ".lua"}
ALL_CODE_EXTENSIONS = CODE_EXTENSIONS | SOURCE_EXTENSIONS
CONFIG_NAMES = {".env", "php.ini", ".user.ini", ".htaccess"}
SKIP_DIRS = {".git", "node_modules", "vendor", "cache", "tmp", "uploads", "dist", "build", ".idea", ".vscode"}
SQL_WORDS = re.compile(r"\b(SELECT|INSERT|UPDATE|DELETE|REPLACE|ALTER|DROP)\b", re.I)
SUPERGLOBALS = re.compile(r"\$_(GET|POST|REQUEST|COOKIE|FILES|SERVER)\b")
SANITIZERS = re.compile(r"\b(htmlspecialchars|htmlentities|strip_tags|intval|floatval|filter_input|filter_var|basename|realpath|escapeshellarg|password_hash|hash_equals)\b", re.I)


@dataclass
class Rule:
    rule_id: str
    title: str
    severity: str
    confidence: str
    category: str
    pattern: re.Pattern[str]
    description: str
    remediation: str
    cwe: str = ""
    owasp: str = ""
    references: list[str] = field(default_factory=list)
    condition: Callable[[str, str], bool] | None = None


def _refs(*items: str) -> list[str]:
    return [i for i in items if i]


RULES: list[Rule] = [
    Rule(
        "php-sql-concat", "Requête SQL construite par concaténation", "high", "high", "Injection SQL",
        re.compile(r"(?:\$sql\s*=.*(?:\.|\{\$)|(?:->query|mysqli_query|pg_query|->exec)\s*\([^;]*\.\s*\$)", re.I),
        "Une donnée dynamique est concaténée dans une requête SQL. La structure de la requête peut être modifiée par une entrée non fiable.",
        "Utiliser PDO avec des requêtes préparées et des paramètres liés ; désactiver l'émulation des préparations.",
        "CWE-89", "A03:2021", _refs("https://owasp.org/www-community/attacks/SQL_Injection"),
    ),
    Rule(
        "php-sql-interpolation", "Variables interpolées dans une requête SQL", "medium", "medium", "Injection SQL",
        re.compile(r"[\"'][^\"']*\b(?:SELECT|INSERT|UPDATE|DELETE)\b[^\"']*\$[A-Za-z_][A-Za-z0-9_]*"),
        "Une requête SQL contient une variable interpolée. Selon l'origine de la variable, une injection est possible.",
        "Passer les valeurs en paramètres liés et ne jamais interpoler d'entrée utilisateur dans le SQL.",
        "CWE-89", "A03:2021", _refs("https://owasp.org/www-community/attacks/SQL_Injection"),
    ),
    Rule(
        "php-xss-echo", "Sortie HTML non encodée", "high", "medium", "XSS",
        re.compile(r"\b(echo|print|printf|vprintf)\b[^;]*(?:\$_ (?:GET|POST|REQUEST|COOKIE)|)", re.I),
        "Une variable est écrite dans une page HTML sans encodage contextuel visible.",
        "Encoder toute sortie avec htmlspecialchars($v, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') ou un moteur de template en auto-escape.",
        "CWE-79", "A03:2021", _refs("https://owasp.org/www-community/attacks/xss/"),
    ),
    Rule(
        "php-command-injection", "Commande système avec variable", "critical", "high", "Injection de commande",
        re.compile(r"\b(system|exec|shell_exec|passthru|popen|proc_open|pcntl_exec)\s*\([^;]*\$", re.I),
        "Une commande système semble recevoir une variable. Si elle provient d'une entrée utilisateur, une injection de commande est possible.",
        "Éviter les commandes système. Sinon, valider par liste blanche et utiliser escapeshellarg()/escapeshellcmd().",
        "CWE-78", "A03:2021", _refs("https://owasp.org/www-community/attacks/Command_Injection"),
    ),
    Rule(
        "php-code-eval", "Exécution dynamique de code", "critical", "high", "Exécution de code",
        re.compile(r"\b(eval|assert|create_function)\s*\(|\bpreg_replace\s*\([^;]*/e[^;]*\)", re.I),
        "Le code utilise une primitive d'exécution dynamique. Une entrée contrôlée peut mener à une exécution de code arbitraire.",
        "Supprimer eval/assert dynamique, remplacer preg_replace /e par preg_replace_callback.",
        "CWE-95", "A03:2021", _refs("https://owasp.org/www-community/attacks/Code_Injection"),
    ),
    Rule(
        "php-unserialize", "Désérialisation de données", "medium", "high", "Désérialisation",
        re.compile(r"\bunserialize\s*\(", re.I),
        "La désérialisation d'une donnée non fiable peut déclencher des méthodes magiques et des chaînes de gadgets.",
        "Préférer json_decode(). Si unserialize est indispensable, utiliser l'option allowed_classes et signer les données.",
        "CWE-502", "A08:2021", _refs("https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection"),
    ),
    Rule(
        "php-file-include", "Inclusion de fichier dynamique", "high", "medium", "Inclusion de fichier",
        re.compile(r"\b(include|include_once|require|require_once)\s*\(?\s*[^;]*\$", re.I),
        "Un chemin d'inclusion dépend d'une variable. Une entrée contrôlée peut provoquer une inclusion locale ou distante.",
        "Utiliser une liste blanche de pages, realpath() et vérifier le préfixe du dossier autorisé. Désactiver allow_url_include.",
        "CWE-98", "A03:2021", _refs("https://owasp.org/www-community/vulnerabilities/File_Inclusion"),
    ),
    Rule(
        "php-path-input", "Chemin de fichier influencé par une entrée", "medium", "medium", "Traversée de chemin",
        re.compile(r"\b(file_get_contents|file_put_contents|fopen|readfile|unlink|copy|rename|scandir|glob)\s*\([^;]*\$", re.I),
        "Une opération de fichier utilise une variable. Sans confinement, un chemin peut sortir du répertoire prévu.",
        "Valider avec realpath(), vérifier le préfixe autorisé et préférer basename() pour les noms de fichiers.",
        "CWE-22", "A01:2021", _refs("https://owasp.org/www-community/attacks/Path_Traversal"),
    ),
    Rule(
        "php-upload", "Téléversement sans contrôle visible", "high", "medium", "Téléversement",
        re.compile(r"\bmove_uploaded_file\s*\(", re.I),
        "Un fichier téléversé est déplacé. Vérifier le type réel, la taille, le nom généré et le répertoire de destination.",
        "Contrôler extension, MIME réel (finfo), taille et signature ; générer un nom ; stocker hors racine web ; retirer l'exécution.",
        "CWE-434", "A04:2021", _refs("https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload"),
    ),
    Rule(
        "php-weak-hash", "Hachage faible pour un mot de passe", "high", "medium", "Cryptographie",
        re.compile(r"\b(md5|sha1)\s*\([^;]*(password|passwd|pwd|secret)", re.I),
        "MD5/SHA1 sont inadaptés au stockage de mots de passe.",
        "Utiliser password_hash() avec PASSWORD_ARGON2ID ou PASSWORD_BCRYPT et password_verify().",
        "CWE-916", "A02:2021", _refs("https://www.php.net/manual/fr/function.password-hash.php"),
    ),
    Rule(
        "php-weak-random", "Générateur aléatoire non cryptographique", "medium", "medium", "Cryptographie",
        re.compile(r"\b(rand|mt_rand|uniqid)\s*\([^;]*(token|secret|password|nonce|csrf)", re.I),
        "Un générateur pseudo-aléatoire non cryptographique semble utilisé pour un secret ou un jeton.",
        "Utiliser random_bytes() ou random_int() pour les jetons de sécurité.",
        "CWE-338", "A02:2021", _refs("https://www.php.net/manual/fr/function.random-bytes.php"),
    ),
    Rule(
        "php-extract", "Extraction de variables depuis une entrée", "high", "high", "Injection de variables",
        re.compile(r"\bextract\s*\(\s*\$_(GET|POST|REQUEST|COOKIE)|\bparse_str\s*\([^;]*\$_(GET|POST|REQUEST)", re.I),
        "extract()/parse_str() sur une entrée utilisateur peut écraser des variables internes.",
        "Ne pas extraire d'entrées dans le scope local ; utiliser des tableaux explicites et valider les clés.",
        "CWE-621", "A03:2021", _refs("https://www.php.net/manual/fr/function.extract.php"),
    ),
    Rule(
        "php-header-input", "En-tête HTTP construit avec une entrée", "medium", "medium", "Injection d'en-tête",
        re.compile(r"\bheader\s*\([^;]*\$_(GET|POST|REQUEST|COOKIE|SERVER)", re.I),
        "Une valeur utilisateur est intégrée dans un en-tête, avec un risque d'injection ou de redirection ouverte.",
        "Valider les valeurs, éviter les URL fournies par l'utilisateur et utiliser une liste blanche de redirections.",
        "CWE-113", "A03:2021", _refs("https://owasp.org/www-community/attacks/HTTP_Response_Splitting"),
    ),
    Rule(
        "php-ssl-verify-off", "Vérification TLS désactivée", "high", "high", "Cryptographie",
        re.compile(r"CURLOPT_SSL_VERIFYPEER\s*,\s*(false|0)|CURLOPT_SSL_VERIFYHOST\s*,\s*(false|0)", re.I),
        "La vérification du certificat TLS est désactivée, ce qui permet une interception des communications.",
        "Laisser CURLOPT_SSL_VERIFYPEER et VERIFYHOST à true (2 pour host). Configurer le bundle CA.",
        "CWE-295", "A02:2021", _refs("https://curl.se/libcurl/c/CURLOPT_SSL_VERIFYPEER.html"),
    ),
    Rule(
        "php-ssrf", "Requête réseau pilotée par une entrée", "high", "medium", "SSRF",
        re.compile(r"\b(file_get_contents|fopen|readfile|curl_init|curl_setopt|fsockopen|stream_socket_client)\s*\([^;]*\$_(GET|POST|REQUEST|COOKIE)", re.I),
        "Une fonction réseau reçoit une valeur issue d'une entrée utilisateur. Une URL contrôlée peut viser des ressources internes.",
        "Valider l'URL par liste blanche de domaines, interdire les IP privées/localhost et désactiver les wrappers non nécessaires.",
        "CWE-918", "A10:2021", _refs("https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/"),
    ),
    Rule(
        "php-xxe", "Analyse XML avec entités externes", "high", "medium", "XXE",
        re.compile(r"\b(simplexml_load_(string|file)|DOMDocument|xml_parse|XMLReader)\b[^;]*(LIBXML_NOENT|->loadXML\s*\()", re.I),
        "Le traitement XML peut activer des entités externes ou charger du contenu non fiable.",
        "Désactiver LIBXML_NOENT, utiliser LIBXML_NONET et valider/désinfecter les sources XML.",
        "CWE-611", "A05:2021", _refs("https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing"),
    ),
    Rule(
        "php-backticks", "Exécution par backticks", "critical", "high", "Exécution de code",
        re.compile(r"`[^`]*\$[^`]*`"),
        "Des backticks exécutent une commande shell et peuvent inclure une variable.",
        "Supprimer l'exécution shell ou valider/échapper strictement les arguments.",
        "CWE-78", "A03:2021", _refs("https://www.php.net/manual/fr/language.operators.execution.php"),
    ),
    Rule(
        "php-variable-variable", "Variable variable", "medium", "low", "Injection de variables",
        re.compile(r"\$\$[A-Za-z_][A-Za-z0-9_]*"),
        "Les variables variables rendent le flux de données difficile à contrôler et peuvent exposer des variables internes.",
        "Remplacer par des tableaux explicites et valider les clés.",
        "CWE-621", "A03:2021", _refs("https://www.php.net/manual/fr/language.variables.variable.php"),
    ),
    Rule(
        "php-mail-header", "Fonction mail() avec entrée", "medium", "medium", "Injection d'en-tête",
        re.compile(r"\bmail\s*\([^)]*\$_(GET|POST|REQUEST|COOKIE)", re.I),
        "La fonction mail() reçoit une valeur issue d'une entrée, avec un risque d'injection d'en-tête.",
        "Valider les adresses, ne pas transmettre d'en-tête utilisateur et préférer un serveur SMTP dédié.",
        "CWE-93", "A03:2021", _refs("https://owasp.org/www-community/attacks/Email_Header_Injection"),
    ),
    Rule(
        "php-mass-assignment", "Affectation massive depuis une requête", "high", "medium", "Affectation massive",
        re.compile(r"->\s*(fill|update|create)\s*\(\s*\$_(POST|REQUEST|GET)\b", re.I),
        "Un tableau de requête est passé directement à un modèle, ce qui peut modifier des champs non prévus.",
        "Définir une liste blanche de champs (fillable/guarded) et valider explicitement l'entrée.",
        "CWE-915", "A04:2021", _refs("https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html"),
    ),
    Rule(
        "php-phar-wrapper", "Wrapper phar:// détecté", "medium", "low", "Désérialisation",
        re.compile(r"phar://", re.I),
        "L'usage du wrapper phar:// peut déclencher des chaînes de désérialisation si le fichier est contrôlé.",
        "Éviter phar:// sur des chemins non fiables et valider les fichiers téléversés.",
        "CWE-502", "A08:2021", _refs("https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection"),
    ),
    Rule(
        "php2shell-oom-handler", "Gestion manuelle du chemin OOM", "high", "medium", "PHP2Shell / OOM",
        re.compile(r"register_shutdown_function\s*\([^)]*(error_get_last|ini_set\s*\(\s*['\"]memory_limit)", re.I),
        "Un handler de fin d'exécution inspecte les erreurs ou modifie la limite mémoire, ce qui peut masquer ou exploiter un état OOM.",
        "Revoir le handler, éviter la gestion manuelle du chemin OOM et mettre à jour PHP vers une branche corrigée.",
        "CWE-400", "A05:2021", _refs("https://www.php.net/supported-versions.php"),
    ),
    Rule(
        "php2shell-memory-unlimited", "Limite mémoire non bornée", "high", "high", "PHP2Shell / OOM",
        re.compile(r"ini_set\s*\(\s*['\"]memory_limit['\"]\s*,\s*['\"]-1['\"]", re.I),
        "memory_limit=-1 retire la protection contre l'épuisement mémoire.",
        "Définir une limite mémoire adaptée et ne jamais la désactiver en production.",
        "CWE-770", "A05:2021", _refs("https://www.php.net/manual/fr/ini.core.php"),
    ),
    Rule(
        "php2shell-session-progress", "Manipulation de session.upload_progress", "medium", "medium", "PHP2Shell / session",
        re.compile(r"ini_set\s*\(\s*['\"]session\.upload_progress", re.I),
        "La configuration de session.upload_progress est modifiée à l'exécution, ce qui peut affaiblir la mitigation.",
        "Désactiver session.upload_progress.enabled jusqu'à confirmation du correctif, et ne pas le modifier dynamiquement.",
        "CWE-16", "A05:2021", _refs("https://www.php.net/manual/fr/session.configuration.php"),
    ),
    Rule(
        "php2shell-gc", "Collecte mémoire manuelle dans un chemin de requête", "low", "low", "PHP2Shell / OOM",
        re.compile(r"\b(gc_collect_cycles|gc_disable)\s*\(", re.I),
        "La gestion du garbage collector est modifiée manuellement, ce qui peut masquer un état mémoire anormal.",
        "Éviter de désactiver ou forcer la collecte dans le code applicatif.",
        "CWE-400", "A05:2021", _refs("https://www.php.net/manual/fr/function.gc-collect-cycles.php"),
    ),
    Rule(
        "php2shell-error-handler", "Handler d'erreur personnalisé sur erreurs fatales", "medium", "low", "PHP2Shell / OOM",
        re.compile(r"set_error_handler\s*\([^)]*(E_ERROR|E_CORE_ERROR|E_COMPILE_ERROR)", re.I),
        "Un handler tente d'intercepter des erreurs normalement non interceptables, ce qui peut masquer un crash.",
        "Ne pas tenter d'intercepter E_ERROR/E_CORE_ERROR/E_COMPILE_ERROR ; journaliser et redémarrer proprement.",
        "CWE-755", "A05:2021", _refs("https://www.php.net/manual/fr/function.set-error-handler.php"),
    ),
    Rule(
        "php-open-redirect", "Redirection construite avec une entrée", "medium", "high", "Redirection",
        re.compile(r"header\s*\(\s*['\"]Location:\s*['\"]?\s*\.\s*\$_(GET|POST|REQUEST)\b", re.I),
        "L'en-tête Location reprend une valeur fournie par le client : redirection ouverte possible vers un site d'hameçonnage.",
        "N'autoriser que des chemins relatifs ou une liste blanche de destinations, et refuser les URL absolues externes.",
        "CWE-601", "A01:2021", _refs("https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html"),
    ),
    Rule(
        "php-session-fixation", "Identifiant de session fourni par le client", "high", "high", "Session",
        re.compile(r"session_id\s*\(\s*\$_(GET|POST|REQUEST|COOKIE)\b", re.I),
        "L'identifiant de session est imposé par une donnée de requête (fixation de session).",
        "Laisser PHP générer l'identifiant et appeler session_regenerate_id(true) après authentification.",
        "CWE-384", "A07:2021", _refs("https://owasp.org/www-community/attacks/Session_fixation"),
    ),
    Rule(
        "php-insecure-cookie", "Cookie sans attributs de sécurité", "medium", "medium", "Session",
        re.compile(r"\bsetcookie\s*\((?![^;]*(httponly|samesite|['\"]secure['\"]\s*=>\s*true|,\s*true\s*,\s*true))[^;]*\)\s*;", re.I),
        "setcookie() est appelé sans HttpOnly/Secure/SameSite visibles : le cookie peut être lu par un script ou envoyé en clair.",
        "Utiliser la forme tableau : setcookie($nom, $valeur, ['secure' => true, 'httponly' => true, 'samesite' => 'Lax']).",
        "CWE-1004", "A05:2021", _refs("https://www.php.net/manual/fr/function.setcookie.php"),
    ),
    Rule(
        "php-loose-compare-secret", "Comparaison non stricte d'un secret", "medium", "medium", "Authentification",
        re.compile(r"\$\w*(password|passwd|token|secret|hash|signature)\w*\s*==\s*(?!=)", re.I),
        "Un secret est comparé avec == : la conversion de type PHP peut rendre la comparaison vraie à tort et le temps de comparaison est variable.",
        "Utiliser hash_equals() pour les jetons et password_verify() pour les mots de passe.",
        "CWE-697", "A07:2021", _refs("https://www.php.net/manual/fr/function.hash-equals.php"),
    ),
    Rule(
        "php-preg-eval", "Modificateur /e de preg_replace", "critical", "high", "Exécution de code",
        re.compile(r"preg_replace\s*\(\s*['\"](.).*\1[a-z]*e[a-z]*['\"]", re.I),
        "Le modificateur /e évalue le remplacement comme du code PHP (supprimé en PHP 7, signe de code très ancien).",
        "Remplacer par preg_replace_callback() et mettre à jour PHP.",
        "CWE-95", "A03:2021", _refs("https://www.php.net/manual/fr/reference.pcre.pattern.modifiers.php"),
    ),
    Rule(
        "php-assert-input", "assert() ou create_function() avec une entrée", "critical", "high", "Exécution de code",
        re.compile(r"\b(assert|create_function)\s*\([^)]*\$_(GET|POST|REQUEST|COOKIE)\b", re.I),
        "Une donnée de requête est évaluée comme du code PHP.",
        "Supprimer l'évaluation dynamique et utiliser des fonctions anonymes ou une logique explicite.",
        "CWE-95", "A03:2021", _refs("https://owasp.org/www-community/attacks/Code_Injection"),
    ),
    Rule(
        "php-ldap-injection", "Filtre LDAP construit avec une entrée", "high", "medium", "Injection LDAP",
        re.compile(r"ldap_(search|list|read)\s*\([^;]*\$_(GET|POST|REQUEST)\b", re.I),
        "Le filtre LDAP inclut une donnée de requête non échappée.",
        "Échapper les valeurs avec ldap_escape($v, '', LDAP_ESCAPE_FILTER).",
        "CWE-90", "A03:2021", _refs("https://cheatsheetseries.owasp.org/cheatsheets/LDAP_Injection_Prevention_Cheat_Sheet.html"),
    ),
    Rule(
        "php-cors-wildcard", "CORS ouvert à toutes les origines", "medium", "high", "CORS",
        re.compile(r"header\s*\(\s*['\"]Access-Control-Allow-Origin:\s*(\*|['\"]\s*\.\s*\$_SERVER\s*\[\s*['\"]HTTP_ORIGIN)", re.I),
        "L'API autorise n'importe quelle origine (ou reflète l'en-tête Origin), ce qui expose ses réponses aux sites tiers.",
        "Définir une liste fixe d'origines autorisées et ne jamais combiner origine reflétée et identifiants.",
        "CWE-942", "A05:2021", _refs("https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html"),
    ),
    Rule(
        "php-phpinfo", "Appel à phpinfo()", "medium", "high", "Divulgation d'informations",
        re.compile(r"\bphpinfo\s*\(", re.I),
        "phpinfo() expose la configuration complète du serveur (chemins, modules, variables d'environnement).",
        "Supprimer l'appel ou le restreindre à un environnement de développement non exposé.",
        "CWE-200", "A05:2021", _refs("https://www.php.net/manual/fr/function.phpinfo.php"),
    ),
    Rule(
        "php-display-errors", "Affichage des erreurs activé dans le code", "low", "high", "Divulgation d'informations",
        re.compile(r"ini_set\s*\(\s*['\"]display_errors['\"]\s*,\s*['\"]?(1|on|true)", re.I),
        "Les erreurs PHP sont affichées aux visiteurs, révélant chemins et requêtes.",
        "Mettre display_errors=Off en production et journaliser les erreurs (log_errors=On).",
        "CWE-209", "A05:2021", _refs("https://www.php.net/manual/fr/errorfunc.configuration.php"),
    ),
]

SECRET_KEY_RE = re.compile(
    r"(?i)(api[_-]?key|secret|passw(?:or)?d|token|private[_-]?key|access[_-]?key|client[_-]?secret)"
    r"\s*[:=]\s*['\"]?([^\s'\";,]{8,})"
)
SECRET_KEY_NAME_RE = re.compile(
    r"(?i)(api[_-]?key|secret|passw(?:or)?d|token|private[_-]?key|access[_-]?key|client[_-]?secret)"
)
PLACEHOLDER_RE = re.compile(r"(?i)(change|example|demo|fake|your[_-]|xxxx|placeholder|none|null|test_|<.*>|\$\{.*\})")


def _line_evidence(line: str) -> str:
    return redact_text(line.strip(), 600)


def _secret_finding(ctx: ScanContext, path: Path, rel: str, line_no: int, line: str, key: str, value: str) -> None:
    if PLACEHOLDER_RE.search(value) and len(value) < 24:
        return
    if value.startswith("$") or value.startswith("getenv") or value.startswith("env("):
        return
    ctx.add_finding(
        engine="php", rule_id="php-hardcoded-secret",
        title=f"Secret potentiel en clair ({key})",
        severity="high" if re.search(r"live|prod|secret|private", key, re.I) else "medium",
        confidence="medium", category="Secrets exposés",
        description="Une valeur ressemblant à un secret est présente en clair dans le code ou la configuration.",
        evidence=f"{rel}:{line_no} — {key} = {redact_secret(value)}",
        file_path=rel, line_start=line_no,
        cwe="CWE-798", owasp="A07:2021",
        remediation="Retirer le secret du dépôt, le révoquer, le stocker dans un gestionnaire de secrets ou une variable d'environnement, et limiter les droits.",
        references=["https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password"],
    )


def _scan_env_file(ctx: ScanContext, path: Path, rel: str) -> None:
    content = read_text(path, MAX_FILE_BYTES)
    if not content:
        return
    for idx, line in enumerate(content.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip("'\"")
        if SECRET_KEY_NAME_RE.search(key):
            _secret_finding(ctx, path, rel, idx, line, key.strip(), value)
        if re.match(r"(?i)APP_DEBUG\s*=\s*(true|1|on)", line.strip()):
            ctx.add_finding(
                engine="php", rule_id="php-debug-env", title="Debug activé dans un fichier d'environnement",
                severity="medium", confidence="high", category="Configuration",
                description="APP_DEBUG=true peut exposer des traces détaillées et des informations internes.",
                evidence=f"{rel}:{idx} — APP_DEBUG=true", file_path=rel, line_start=idx,
                cwe="CWE-489", owasp="A05:2021",
                remediation="Désactiver le debug en production et journaliser les erreurs sans les afficher au visiteur.",
                references=["https://owasp.org/Top10/A05_2021-Security_Misconfiguration/"],
            )
    if path.name == ".env":
        ctx.add_finding(
            engine="php", rule_id="php-env-present", title="Fichier .env présent dans le projet",
            severity="info", confidence="high", category="Secrets exposés",
            description="Un fichier .env contient la configuration sensible. Vérifier qu'il n'est pas accessible depuis le Web.",
            evidence=f"{rel} — contenu non reproduit", file_path=rel,
            cwe="CWE-538", owasp="A05:2021",
            remediation="Ajouter .env au .gitignore, le placer hors racine web et bloquer son accès au serveur.",
            references=["https://owasp.org/Top10/A05_2021-Security_Misconfiguration/"],
        )


def _scan_ini(ctx: ScanContext, path: Path, rel: str) -> None:
    content = read_text(path, MAX_FILE_BYTES)
    insecure = {
        "display_errors": ("on", "medium", "Les erreurs PHP sont affichées au visiteur."),
        "log_errors": ("off", "low", "Les erreurs ne sont pas journalisées."),
        "expose_php": ("on", "low", "La version de PHP peut être divulguée."),
        "allow_url_include": ("on", "critical", "L'inclusion d'URL distantes est activée."),
        "allow_url_fopen": ("on", "medium", "L'ouverture d'URL distantes est activée."),
        "session.use_strict_mode": ("0", "high", "Le mode strict des sessions est désactivé."),
        "session.use_only_cookies": ("0", "high", "Les identifiants de session peuvent transiter autrement que par cookie."),
        "session.cookie_httponly": ("0", "high", "Le cookie de session n'est pas HttpOnly."),
        "session.cookie_secure": ("0", "high", "Le cookie de session peut être transmis sans TLS."),
        "session.upload_progress.enabled": ("on", "medium", "session.upload_progress est activé ; c'est un vecteur historique d'exploitation OOM."),
    }
    for idx, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith(";") or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = [x.strip() for x in stripped.split("=", 1)]
        key_l = key.lower()
        val_l = value.lower().strip('"\'')
        if key_l in insecure:
            bad, sev, why = insecure[key_l]
            if val_l == bad:
                ctx.add_finding(
                    engine="php", rule_id=f"php-config-{key_l.replace('.', '-')}",
                    title=f"Configuration PHP à risque : {key}", severity=sev, confidence="high",
                    category="Configuration", description=why,
                    evidence=f"{rel}:{idx} — {key} = {value}", file_path=rel, line_start=idx,
                    cwe="CWE-16", owasp="A05:2021",
                    remediation="Corriger la directive dans php.ini/le pool FPM et redémarrer les workers. Vérifier la valeur effective avec phpinfo() sur un environnement isolé.",
                    references=["https://www.php.net/manual/fr/configuration.file.php"],
                )
    if "upload_max_filesize" in content.lower():
        m = re.search(r"(?im)^\s*upload_max_filesize\s*=\s*([0-9]+)\s*([GMK])?", content)
        if m:
            size = int(m.group(1))
            unit = (m.group(2) or "M").upper()
            if (unit == "G") or (unit == "M" and size > 32) or (unit == "K" and size > 32768):
                ctx.add_finding(
                    engine="php", rule_id="php-upload-limit", title="Limite de téléversement élevée",
                    severity="medium", confidence="medium", category="Configuration",
                    description="Une limite de téléversement très élevée augmente le risque de saturation et d'abus.",
                    evidence=f"{rel} — upload_max_filesize = {m.group(1)}{m.group(2) or ''}", file_path=rel,
                    cwe="CWE-770", owasp="A04:2021",
                    remediation="Définir une limite adaptée au besoin métier, ainsi qu'un contrôle de taille côté application.",
                    references=["https://www.php.net/manual/fr/ini.core.php"],
                )


def _scan_htaccess(ctx: ScanContext, path: Path, rel: str) -> None:
    content = read_text(path, MAX_FILE_BYTES)
    for idx, line in enumerate(content.splitlines(), 1):
        s = line.strip().lower()
        if s.startswith("options") and "+indexes" in s:
            ctx.add_finding(
                engine="php", rule_id="php-apache-indexes", title="Listage de répertoire activé",
                severity="medium", confidence="high", category="Configuration",
                description="Options +Indexes expose la liste des fichiers d'un répertoire.",
                evidence=f"{rel}:{idx} — {line.strip()}", file_path=rel, line_start=idx,
                cwe="CWE-548", owasp="A05:2021",
                remediation="Désactiver l'indexation et ajouter un fichier index ou une règle de refus.",
                references=["https://httpd.apache.org/docs/current/mod/core.html#options"],
            )
        if "php_value" in s and "display_errors" in s and re.search(r"\bon\b", s):
            ctx.add_finding(
                engine="php", rule_id="php-apache-display-errors", title="display_errors activé via .htaccess",
                severity="medium", confidence="high", category="Configuration",
                description="Les erreurs PHP seront affichées aux visiteurs.",
                evidence=f"{rel}:{idx} — {line.strip()}", file_path=rel, line_start=idx,
                cwe="CWE-209", owasp="A05:2021",
                remediation="Retirer cette directive et configurer log_errors/display_errors au niveau global.",
                references=["https://owasp.org/Top10/A05_2021-Security_Misconfiguration/"],
            )


def _collect_files(root: Path, max_files: int) -> tuple[list[Path], list[Path], list[Path], int]:
    code: list[Path] = []
    configs: list[Path] = []
    manifests: list[Path] = []
    visited = 0
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIRS and not d.startswith(".cache")]
        for name in files:
            visited += 1
            if visited > max_files * 2:
                break
            path = Path(current) / name
            lower = name.lower()
            suffix = path.suffix.lower()
            if lower in CONFIG_NAMES or lower.startswith(".env."):
                configs.append(path)
            elif lower in {"composer.json", "composer.lock"}:
                manifests.append(path)
            elif suffix in ALL_CODE_EXTENSIONS:
                code.append(path)
            if len(code) >= max_files:
                break
        if len(code) >= max_files or visited > max_files * 2:
            break
    return code, configs, manifests, visited


def _scan_generic_source(ctx: ScanContext, path: Path, rel: str, content: str, lines: list[str]) -> None:
    seen: set[tuple[str, int]] = set()
    suffix = path.suffix.lower()
    # Secrets dans le code source.
    for idx, line in enumerate(lines, 1):
        if ctx.cancelled():
            return
        if line.strip().startswith(("//", "#", "*", "/*")):
            continue
        for sm in SECRET_KEY_RE.finditer(line):
            key, value = sm.group(1), sm.group(2)
            if not _likely_secret_value(value):
                continue
            key_id = ("source-secret", idx)
            if key_id in seen:
                continue
            seen.add(key_id)
            _secret_finding(ctx, path, rel, idx, line, key, value)
    # Motifs dangereux courants selon le langage.
    patterns = [
        ("source-eval", "Exécution dynamique de code", "critical", r"\b(eval|exec)\s*\(", "Une primitive d'exécution dynamique est présente."),
        ("source-command", "Commande système", "high", r"\b(system|os\.system|subprocess\.(run|call|Popen)|Runtime\.getRuntime\(\)\.exec)\b", "Une commande système est invoquée."),
        ("source-sql-concat", "Requête SQL construite par concaténation", "high", r"(?i)(SELECT|INSERT|UPDATE|DELETE).*(\+|\.|%)\s*[A-Za-z_]", "Une requête SQL semble être construite avec une variable."),
        ("source-path-traversal", "Lecture/écriture de fichier avec variable", "medium", r"\b(open|readFile|writeFile|fopen|file_get_contents)\s*\([^)]*[A-Za-z_][A-Za-z0-9_]*\)", "Un chemin de fichier dépend d'une variable."),
        ("source-innerhtml", "Écriture HTML non encodée", "medium", r"\.innerHTML\s*=", "Une écriture HTML directe peut exposer à des XSS."),
        ("source-document-write", "document.write()", "medium", r"document\.write\s*\(", "document.write() peut injecter du HTML non filtré."),
        ("source-pickle", "Désérialisation non sûre", "high", r"\bpickle\.loads\s*\(|yaml\.load\s*\(", "Une désérialisation non sûre est présente."),
        ("source-hardcoded-ip", "Adresse IP codée en dur", "low", r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "Une adresse IP est codée en dur dans le code source."),
    ]
    for rule_id, title, severity, pattern, description in patterns:
        for idx, line in enumerate(lines, 1):
            if ctx.cancelled():
                return
            if line.strip().startswith(("//", "#", "*", "/*")):
                continue
            if not re.search(pattern, line, re.I):
                continue
            key = (rule_id, idx)
            if key in seen:
                continue
            seen.add(key)
            ctx.add_finding(
                engine="php", rule_id=rule_id, title=title, severity=severity, confidence="low",
                category="Code source", description=description,
                evidence=f"{rel}:{idx} — {redact_text(line.strip(), 300)}", file_path=rel,
                line_start=idx, cwe="CWE-000", owasp="A04:2021",
                remediation="Revoir manuellement cet extrait et le corriger selon les bonnes pratiques du langage.",
                references=[],
            )
            break


def _scan_code_file(ctx: ScanContext, path: Path, rel: str) -> None:
    content = read_text(path, MAX_FILE_BYTES)
    if not content:
        return
    lines = content.splitlines()
    if path.suffix.lower() not in CODE_EXTENSIONS:
        _scan_generic_source(ctx, path, rel, content, lines)
        return
    seen: set[tuple[str, int]] = set()
    for idx, line in enumerate(lines, 1):
        if ctx.cancelled():
            return
        stripped = line.strip()
        # Propagation de taint très simple : affectation depuis un superglobal ou une variable déjà taintée.
        assign = re.search(r"\$([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", line)
        if assign:
            var, rhs = assign.group(1), assign.group(2)
            if SUPERGLOBALS.search(rhs) or "php://input" in rhs:
                tainted[var] = idx
            elif SANITIZERS.search(rhs):
                tainted.pop(var, None)
            else:
                for other in list(tainted):
                    if re.search(rf"\${re.escape(other)}\b", rhs):
                        tainted[var] = idx
                        break
        for rule in RULES:
            if rule.rule_id == "php-xss-echo":
                if not re.search(r"\b(echo|print|printf|vprintf)\b", line, re.I):
                    continue
                if SANITIZERS.search(line):
                    continue
                has_source = bool(SUPERGLOBALS.search(line)) or any(
                    re.search(rf"\${re.escape(var)}\b", line) for var in tainted
                )
                if not has_source:
                    continue
                key = ("xss", idx)
                if key in seen:
                    continue
                seen.add(key)
                ctx.add_finding(
                    engine="php", rule_id=rule.rule_id, title=rule.title, severity="high",
                    confidence="medium", category=rule.category, description=rule.description,
                    evidence=_line_evidence(line), file_path=rel, line_start=idx,
                    cwe=rule.cwe, owasp=rule.owasp, remediation=rule.remediation, references=rule.references,
                )
                continue
            match = rule.pattern.search(line)
            if not match:
                continue
            if rule.condition and not rule.condition(line, content):
                continue
            # Réduire les faux positifs évidents sur les commentaires.
            if stripped.startswith(("//", "#", "*")):
                continue
            if rule.rule_id == "php-command-injection" and SANITIZERS.search(line):
                sev = "low"
                conf = "low"
            elif rule.rule_id == "php-unserialize" and "allowed_classes" in line:
                sev = "low"
                conf = "low"
            else:
                sev = rule.severity
                conf = rule.confidence
            key = (rule.rule_id, idx)
            if key in seen:
                continue
            seen.add(key)
            ctx.add_finding(
                engine="php", rule_id=rule.rule_id, title=rule.title, severity=sev,
                confidence=conf, category=rule.category, description=rule.description,
                evidence=_line_evidence(line), file_path=rel, line_start=idx,
                cwe=rule.cwe, owasp=rule.owasp, remediation=rule.remediation, references=rule.references,
            )
        # Taint vers sinks non couverts ou pour renforcer la confiance.
        tainted_on_line = [v for v in tainted if re.search(rf"\${re.escape(v)}\b", line)]
        if tainted_on_line and not SANITIZERS.search(line):
            sink = _classify_sink(line)
            if sink:
                key = (sink[0], idx)
                if key not in seen:
                    seen.add(key)
                    ctx.add_finding(
                        engine="php", rule_id=sink[0], title=sink[1], severity=sink[2],
                        confidence="medium", category=sink[3],
                        description=sink[4], evidence=_line_evidence(line),
                        file_path=rel, line_start=idx, cwe=sink[5], owasp=sink[6],
                        remediation=sink[7], references=[],
                    )
        # Secrets sur la ligne (hors variables d'environnement).
        if not stripped.startswith(("//", "#", "*")):
            for sm in SECRET_KEY_RE.finditer(line):
                key, value = sm.group(1), sm.group(2)
                if not _likely_secret_value(value):
                    continue
                _secret_finding(ctx, path, rel, idx, line, key, value)
        # Sessions sans rotation dans le fichier.
    if re.search(r"\bsession_start\s*\(", content) and not re.search(r"session_regenerate_id\s*\(\s*true", content):
        if re.search(r"\$_SESSION\s*\[[^\]]*(user|auth|admin|role|login)", content, re.I):
            first = next((i for i, l in enumerate(lines, 1) if "session_start" in l), None)
            ctx.add_finding(
                engine="php", rule_id="php-session-fixation", title="Session d'authentification sans rotation visible",
                severity="medium", confidence="low", category="Sessions",
                description="Une session est créée et des données d'authentification sont stockées, mais session_regenerate_id(true) n'apparaît pas dans le fichier.",
                evidence=f"{rel}:{first or 1} — session_start() sans rotation visible", file_path=rel,
                line_start=first, cwe="CWE-384", owasp="A07:2021",
                remediation="Appeler session_regenerate_id(true) après authentification et après élévation de privilège.",
                references=["https://owasp.org/www-community/attacks/Session_fixation"],
            )


def _likely_secret_value(value: str) -> bool:
    if len(value) < 8:
        return False
    if re.match(r"(?i)sk_(test|live)_", value):
        return True
    if PLACEHOLDER_RE.search(value):
        return False
    if value.startswith(("$", "env(", "getenv", "%", "{{")):
        return False
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        return False
    if value.lower() in {"true", "false", "null", "none", "password", "secret", "token"}:
        return False
    return bool(re.search(r"[0-9]", value) or len(value) >= 16)


def _classify_sink(line: str) -> tuple[str, str, str, str, str, str, str, str] | None:
    if re.search(r"(?:->query|->exec|mysqli_query|pg_query)\s*\(", line, re.I):
        return ("php-tainted-sql", "Flux tainté vers une requête SQL", "high", "Injection SQL",
                "Une variable issue d'une entrée semble atteindre une requête SQL.", "CWE-89", "A03:2021",
                "Utiliser des requêtes préparées et des paramètres liés.")
    if re.search(r"\b(echo|print)\b", line, re.I):
        return ("php-tainted-xss", "Flux tainté vers une sortie HTML", "high", "XSS",
                "Une variable issue d'une entrée semble atteinte par une sortie HTML non encodée.", "CWE-79", "A03:2021",
                "Encoder la sortie avec htmlspecialchars ou un moteur de template auto-échappé.")
    if re.search(r"\b(include|require)(_once)?\b", line, re.I):
        return ("php-tainted-include", "Flux tainté vers une inclusion de fichier", "high", "Inclusion de fichier",
                "Une entrée utilisateur peut influencer un chemin d'inclusion.", "CWE-98", "A03:2021",
                "Utiliser une liste blanche et confiner les chemins avec realpath().")
    if re.search(r"\b(system|exec|shell_exec|passthru|popen|proc_open)\b", line, re.I):
        return ("php-tainted-command", "Flux tainté vers une commande système", "critical", "Injection de commande",
                "Une entrée utilisateur peut atteindre une commande système.", "CWE-78", "A03:2021",
                "Supprimer la commande ou valider par liste blanche et échapper les arguments.")
    if re.search(r"\bunserialize\s*\(", line, re.I):
        return ("php-tainted-unserialize", "Flux tainté vers une désérialisation", "high", "Désérialisation",
                "Une entrée utilisateur peut atteindre unserialize().", "CWE-502", "A08:2021",
                "Utiliser JSON et restreindre allowed_classes si nécessaire.")
    if re.search(r"\bheader\s*\([^;]*Location", line, re.I):
        return ("php-tainted-redirect", "Redirection influencée par une entrée", "medium", "Redirection ouverte",
                "Une entrée peut influencer une redirection HTTP.", "CWE-601", "A01:2021",
                "Valider la destination avec une liste blanche de chemins internes.")
    if re.search(r"\b(file_get_contents|fopen|curl_init|curl_setopt|fsockopen|stream_socket_client)\b", line, re.I):
        return ("php-tainted-ssrf", "Flux tainté vers une requête réseau", "high", "SSRF",
                "Une entrée utilisateur peut influencer une requête réseau côté serveur.", "CWE-918", "A10:2021",
                "Valider l'URL par liste blanche et bloquer les destinations internes.")
    if re.search(r"\bheader\s*\(", line, re.I):
        return ("php-tainted-header", "Flux tainté vers un en-tête HTTP", "medium", "Injection d'en-tête",
                "Une entrée utilisateur peut influencer un en-tête HTTP.", "CWE-113", "A03:2021",
                "Valider les valeurs et éviter les en-têtes construits dynamiquement.")
    return None


def _parse_composer(root: Path, manifests: list[Path]) -> list[dict[str, Any]]:
    packages: list[dict[str, Any]] = []
    lock = next((p for p in manifests if p.name.lower() == "composer.lock"), None)
    if lock:
        try:
            data = json.loads(read_text(lock, MAX_FILE_BYTES))
            for section in ("packages", "packages-dev"):
                for pkg in data.get(section, []) or []:
                    if isinstance(pkg, dict) and pkg.get("name"):
                        packages.append({
                            "name": pkg.get("name"),
                            "version": str(pkg.get("version", "")).lstrip("v"),
                            "dev": section == "packages-dev",
                        })
        except (json.JSONDecodeError, OSError):
            pass
    return packages


def _osv_lookup(packages: list[dict[str, Any]], api_key: str = "") -> tuple[dict[str, list[dict]], str]:
    """Interroge OSV par lots. Retourne {package@version: [vulns]} et un statut."""
    if not packages:
        return {}, "no_packages"
    queries = []
    keys = []
    for pkg in packages[:300]:
        if not pkg.get("version"):
            continue
        queries.append({"package": {"name": pkg["name"], "ecosystem": "Packagist"}, "version": pkg["version"]})
        keys.append(f"{pkg['name']}@{pkg['version']}")
    if not queries:
        return {}, "no_versions"
    results: dict[str, list[dict]] = {}
    headers = {"User-Agent": USER_AGENT, "Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    try:
        for start in range(0, len(queries), 100):
            chunk = queries[start:start + 100]
            response = requests.post(
                "https://api.osv.dev/v1/querybatch",
                json={"queries": chunk}, headers=headers, timeout=20,
            )
            response.raise_for_status()
            data = response.json()
            for key, result in zip(keys[start:start + 100], data.get("results", [])):
                if result and result.get("vulns"):
                    results[key] = result["vulns"]
        return results, "online"
    except (requests.RequestException, ValueError) as exc:
        return {}, f"error: {type(exc).__name__}"


def _osv_fixed_version(vuln: dict) -> str:
    fixed: list[str] = []
    for affected in vuln.get("affected", []) or []:
        for rng in affected.get("ranges", []) or []:
            for event in rng.get("events", []) or []:
                if event.get("fixed"):
                    fixed.append(event["fixed"])
    if not fixed:
        return ""
    try:
        from packaging.version import Version
        return str(max((Version(v.lstrip("v")) for v in fixed), default=fixed[0]))
    except Exception:
        return sorted(fixed)[-1]


def _osv_severity(vuln: dict) -> tuple[str, str]:
    sev = (vuln.get("database_specific", {}) or {}).get("severity", "")
    # GitHub advisories fournissent parfois database_specific.severity.
    if sev:
        return str(sev).lower(), "high"
    return "medium", "low"


def _scan_log_file(ctx: ScanContext, path: Path, rel: str) -> None:
    content = read_text(path, MAX_FILE_BYTES)
    if not content:
        return
    lines = content.splitlines()
    oom = 0
    progress = 0
    fatal = 0
    for line in lines:
        lower = line.lower()
        if "allowed memory size" in lower and "exhausted" in lower:
            if "multipart" in lower or "upload" in lower:
                oom += 1
        if "php_session_upload_progress" in lower and len(line) > 250:
            progress += 1
        if "fatal error" in lower or "__php_incomplete_class" in lower:
            fatal += 1
    if oom >= 3:
        ctx.add_finding(
            engine="php", rule_id="php2shell-log-oom", title="Indicateurs OOM répétés dans les logs",
            severity="high", confidence="medium", category="PHP2Shell / logs",
            description="Des erreurs de mémoire sont corrélées à des requêtes multipart/upload dans les logs locaux.",
            evidence=f"{rel} — {oom} occurrence(s) OOM suspecte(s)", file_path=rel,
            cwe="CWE-400", owasp="A05:2021",
            remediation="Mettre à jour PHP, désactiver session.upload_progress.enabled et inspecter les workers concernés.",
            references=["https://www.php.net/supported-versions.php"],
        )
    if progress >= 1:
        ctx.add_finding(
            engine="php", rule_id="php2shell-log-upload-progress", title="Requête suspecte sur session.upload_progress",
            severity="high", confidence="medium", category="PHP2Shell / logs",
            description="Des entrées de log mentionnent PHP_SESSION_UPLOAD_PROGRESS avec un contenu anormalement long.",
            evidence=f"{rel} — {progress} occurrence(s) suspecte(s)", file_path=rel,
            cwe="CWE-400", owasp="A05:2021",
            remediation="Analyser les requêtes concernées, bloquer les motifs suspects et mettre à jour PHP.",
            references=["https://www.php.net/supported-versions.php"],
        )
    if fatal >= 5:
        ctx.add_finding(
            engine="php", rule_id="php2shell-log-fatal-burst", title="Rafale d'erreurs fatales dans les logs",
            severity="medium", confidence="low", category="PHP2Shell / logs",
            description="Une rafale d'erreurs fatales ou de classes incomplètes est présente dans les logs locaux.",
            evidence=f"{rel} — {fatal} occurrence(s)", file_path=rel,
            cwe="CWE-755", owasp="A05:2021",
            remediation="Inspecter les workers et les traces pour identifier la cause et corriger le code.",
            references=[],
        )


def run(ctx: ScanContext) -> None:
    root = Path(ctx.project.get("path") or "").resolve()
    max_files = int(ctx.config.get("max_files") or MAX_FILES_DEFAULT)
    ctx.log("Cartographie des fichiers", 5)
    code_files, config_files, manifests, visited = _collect_files(root, max_files)
    ctx.extra.update({
        "files_scanned": len(code_files),
        "config_files": len(config_files),
        "manifest_files": len(manifests),
        "visited": visited,
        "root": str(root),
        "tools": ["cybbig-rules", "taint-heuristic"],
    })
    ctx.log(f"Analyse de {len(code_files)} fichier(s) PHP", 12)
    for i, path in enumerate(code_files, 1):
        if ctx.cancelled():
            return
        rel = safe_relpath(path, root)
        try:
            _scan_code_file(ctx, path, rel)
        except Exception as exc:  # noqa: BLE001
            ctx.extra.setdefault("file_errors", []).append(f"{rel}: {type(exc).__name__}")
        if i % 20 == 0:
            pct = 12 + int(60 * i / max(1, len(code_files)))
            ctx.log(f"Analyse {i}/{len(code_files)} — {rel}", pct)

    ctx.log("Analyse des configurations", 75)
    for path in config_files:
        if ctx.cancelled():
            return
        rel = safe_relpath(path, root)
        if path.name.lower().startswith(".env"):
            _scan_env_file(ctx, path, rel)
        elif path.name.lower() in {"php.ini", ".user.ini"}:
            _scan_ini(ctx, path, rel)
        elif path.name.lower() == ".htaccess":
            _scan_htaccess(ctx, path, rel)

    # Logs locaux (lecture seule, passif)
    log_files: list[Path] = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIRS and not d.startswith(".cache")]
        for name in files:
            if name.lower().endswith(".log"):
                log_files.append(Path(current) / name)
        if len(log_files) >= 5:
            break
    for path in log_files[:5]:
        if ctx.cancelled():
            return
        _scan_log_file(ctx, path, safe_relpath(path, root))

    # Manifestes et dépendances
    ctx.log("Inventaire des dépendances Composer", 82)
    packages = _parse_composer(root, manifests)
    composer_json = next((p for p in manifests if p.name.lower() == "composer.json"), None)
    if composer_json:
        try:
            data = json.loads(read_text(composer_json, MAX_FILE_BYTES))
            php_req = (data.get("require", {}) or {}).get("php", "")
            ctx.extra["php_requirement"] = php_req
            if php_req:
                m = re.search(r"(\d+)\.(\d+)", str(php_req))
                if m:
                    major, minor = int(m.group(1)), int(m.group(2))
                    if major < 8 or (major == 8 and minor < 1):
                        ctx.add_finding(
                            engine="php", rule_id="php-eol-version", title="Version PHP déclarée en fin de vie",
                            severity="high", confidence="high", category="Composants obsolètes",
                            description=f"Le projet déclare PHP {php_req}. Cette branche ne reçoit plus de correctifs de sécurité.",
                            evidence=f"composer.json — require.php = {php_req}", file_path="composer.json",
                            cwe="CWE-1104", owasp="A06:2021",
                            remediation="Migrer vers une branche PHP maintenue (8.2+ à la date du scan) et vérifier les extensions.",
                            references=["https://www.php.net/supported-versions.php"],
                        )
                    elif major == 8 and minor in {1, 2}:
                        ctx.add_finding(
                            engine="php", rule_id="php-outdated-branch", title="Branche PHP bientôt ou plus maintenue",
                            severity="medium", confidence="medium", category="Composants obsolètes",
                            description=f"Le projet déclare PHP {php_req}. Vérifier le calendrier de support et les correctifs disponibles.",
                            evidence=f"composer.json — require.php = {php_req}", file_path="composer.json",
                            cwe="CWE-1104", owasp="A06:2021",
                            remediation="Planifier la montée de version et tester les extensions/frameworks.",
                            references=["https://www.php.net/supported-versions.php"],
                        )
        except (json.JSONDecodeError, OSError):
            pass
    if not packages:
        if composer_json:
            ctx.add_finding(
                engine="php", rule_id="php-no-lock", title="Fichier composer.lock absent",
                severity="medium", confidence="high", category="Chaîne d'approvisionnement",
                description="Sans composer.lock, les versions installées ne sont pas reproductibles et l'audit des dépendances est incomplet.",
                evidence="composer.json sans composer.lock", file_path="composer.json",
                cwe="CWE-1104", owasp="A06:2021",
                remediation="Versionner composer.lock, exécuter composer audit en CI et générer un SBOM.",
                references=["https://getcomposer.org/doc/03-cli.md#audit"],
            )
    else:
        # Données locales par défaut : la liste des dépendances n'est envoyée à OSV.dev que sur accord explicite.
        if str(db.get_setting("osv_online", "false")).lower() in {"1", "true", "yes", "on"}:
            ctx.log(f"Audit OSV de {len(packages)} paquet(s)", 88)
            osv_map, osv_status = _osv_lookup(packages, ctx.config.get("osv_api_key", ""))
        else:
            osv_map, osv_status = {}, "local_only"
        ctx.extra["dependency_audit"] = osv_status
        fixed_findings = 0
        for pkg in packages:
            key = f"{pkg['name']}@{pkg['version']}"
            vulns = osv_map.get(key, [])
            if vulns:
                for vuln in vulns[:6]:
                    sev, conf = _osv_severity(vuln)
                    fixed = _osv_fixed_version(vuln)
                    ctx.add_dependency(
                        ecosystem="Packagist", package=pkg["name"], version=pkg["version"],
                        vulnerable=True, vuln_id=vuln.get("id", ""), severity=sev,
                        summary=truncate(vuln.get("summary") or vuln.get("details") or "", 400),
                        fixed_version=fixed, source="OSV",
                    )
                    if fixed_findings < 30:
                        ctx.add_finding(
                            engine="php", rule_id="php-vulnerable-dependency",
                            title=f"Dépendance vulnérable : {pkg['name']} {pkg['version']}",
                            severity=sev if sev in {"critical", "high", "medium", "low"} else "high",
                            confidence=conf, category="Chaîne d'approvisionnement",
                            description=truncate(vuln.get("summary") or vuln.get("details") or "Vulnérabilité signalée par OSV.", 1200),
                            evidence=f"{pkg['name']} {pkg['version']} → {vuln.get('id','inconnu')}"
                                     + (f" (corrigé en {fixed})" if fixed else ""),
                            file_path="composer.lock", cwe="CWE-1104", owasp="A06:2021",
                            remediation=(f"Mettre à jour vers {fixed} ou une version supérieure, puis vérifier la compatibilité et redéployer." if fixed else "Consulter l'avis OSV, appliquer une version corrigée et vérifier la compatibilité."),
                            references=[f"https://osv.dev/vulnerability/{vuln.get('id','')}"],
                        )
                        fixed_findings += 1
            else:
                ctx.add_dependency(
                    ecosystem="Packagist", package=pkg["name"], version=pkg["version"],
                    vulnerable=False, source="OSV" if osv_status == "online" else "inventaire local",
                )
        if osv_status == "local_only":
            ctx.extra["dependency_audit_warning"] = (
                "Mode local : les dépendances sont inventoriées sans être envoyées à OSV.dev. "
                "L'interrogation en ligne s'active dans Paramètres (elle transmet les noms et versions des paquets)."
            )
        elif osv_status != "online":
            ctx.extra["dependency_audit_warning"] = (
                "OSV n'a pas pu être interrogé ; les dépendances sont inventoriées mais non qualifiées en ligne."
            )
    ctx.log("Outils externes optionnels", 92)
    try:
        run_external_tools(ctx, root)
    except Exception as exc:  # noqa: BLE001
        ctx.extra.setdefault("external_tools", {})["error"] = f"{type(exc).__name__}: {exc}"
    ctx.log("Consolidation des résultats", 96)
