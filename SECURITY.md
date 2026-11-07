# Sécurité, périmètre et usage responsable

## Usage prévu
Cybbig est un outil **défensif** de recherche, d'audit et de validation. Il doit être utilisé sur :
- vos propres systèmes ;
- des environnements de laboratoire isolés ;
- des systèmes tiers pour lesquels vous disposez d'une **autorisation écrite** du propriétaire ou de l'exploitant habilité.

Le consentement affiché au premier lancement est une acceptation des conditions d'utilisation. **Il ne constitue pas une autorisation juridique** de tester un système appartenant à un tiers.

## Cadre français
Les articles 323-1 et suivants du Code pénal sanctionnent les atteintes aux systèmes de traitement automatisé de données. Une autorisation doit émaner de la personne ou de l'organisation compétente. En cas de doute, consultez un juriste.

## Limites techniques de la version 0.1
- Aucun exploit, fuzzing, brute force ou contournement d'authentification.
- Aucune modification des systèmes analysés.
- Scans Web passifs, limités en débit et en volume.
- Vérification de chemins exposés : requêtes GET tronquées, contenu non conservé.
- Analyse PHP statique : le code n'est jamais exécuté.
- Le laboratoire fournit du code pédagogique à exécuter uniquement dans un environnement isolé, avec des données fictives.

## Niveaux d'activité
| Niveau | Activité | Exemple |
|---|---|---|
| A | Recherche documentaire | Lire une CVE, une fiche OWASP |
| B | Simulation locale | Analyser le projet PHP d'exemple |
| C | Infrastructure contrôlée | Scanner votre serveur de préproduction |
| D | Tiers autorisé | Audit avec autorisation écrite |
| E | Impact potentiel | Non implémenté ; validation renforcée requise |

## Données et vie privée
- Les données restent dans `backend/data/` sur la machine, **sauf** si vous configurez l'IA en ligne (voir ci-dessous).
- La recherche web manuelle envoie la requête à DuckDuckGo ; si une clé Brave est configurée, elle interroge aussi Brave. La recherche automatique de l'assistant est désactivée par défaut et s'active séparément des liens collés.
- Les secrets détectés sont masqués.
- Aucune télémétrie.

### IA en ligne (Ollama Cloud) — opt-in
- Inactive tant qu'aucune clé API n'est saisie. Le mode **Local uniquement** n'effectue aucun appel vers l'extérieur.
- En mode *Automatique* ou *En ligne*, sont envoyés au service : la question, l'historique récent, les extraits de la base de connaissances et le contexte des projets (titres, descriptions et remédiations des résultats d'analyse). Les clés, jetons, Bearer, JWT et clés privées reconnus sont masqués avant l'envoi ; ce masquage est heuristique, ne collez pas de secret dans une question.
- Les preuves de résultats sont déjà expurgées des secrets détectés (ADR-007). Pour un projet confidentiel, utilisez *Local uniquement*.
- La clé en ligne est stockée dans la base locale, masquée dans l'interface et envoyée uniquement à l'adresse HTTPS configurée ; celle d'un serveur Ollama local n'est jamais envoyée en ligne.
- L'entraînement n'envoie que le contenu de la bibliothèque (jamais les résultats des projets) et est refusé en mode *Coupé*. Le mode *Entraînement seulement* autorise ce seul usage : le chat et les tâches IA restent locaux. Le pilote automatique d'entraînement respecte ces modes.

- **Modèles « -cloud » de l'Ollama local** : traités comme l'IA en ligne (mêmes données envoyées, même masquage), activés seulement si « Autoriser l'IA en ligne » est coché ; exclus du mode *Local uniquement*. Ils exigent un serveur Ollama connecté à ollama.com.
- **Générateur** (Confidentialité) : la description saisie part vers le modèle actif, donc en ligne si c'est lui. Ne collez ni clé ni mot de passe ; le résultat n'est jamais appliqué automatiquement.

### Cybbig Tunnel (VPN personnel)
- Le profil client contient sa clé privée dans `…/data/vpn/` : protégez ce dossier. La configuration du serveur (clé privée du serveur) n'est affichée qu'une fois et n'est pas conservée.
- Aucune règle de pare-feu ni paramètre système n'est modifié ; le tunnel est établi par le client WireGuard officiel (droits administrateur requis).
- L'analyse d'un profil ne renvoie jamais les clés. Les durcissements créent une copie : le fichier d'origine n'est pas modifié.

### Atelier IA (Administration)
- Réservé à la session administrateur. Le code des fichiers choisis est envoyé au modèle actif : avec le modèle en ligne, il quitte le poste (secrets reconnus masqués). Les fichiers d'environnement, clés, bases de données et dossiers de données ne sont jamais envoyés.
- Le modèle ne fait que proposer : l'écriture exige un clic, est tout-ou-rien, sauvegardée et journalisée. Le contenu des fichiers est présenté au modèle comme une donnée.
- Aucun identifiant administrateur n'est livré : l'administration est activée uniquement par le propriétaire, par signature Ed25519 d'un défi à usage unique (voir [docs/ADMIN.md](docs/ADMIN.md)). Seule la clé publique figure dans le dépôt.

### Clés API des utilisateurs
- Aucune clé API n'est fournie. Chaque utilisateur crée ses propres clés (Ollama Cloud, Brave Search, NVD) et les saisit dans Paramètres : voir [docs/CLES-API.md](docs/CLES-API.md).

### Visite de sites web
- Lecture seule (GET), sites publics uniquement : adresses privées, loopback, link-local et métadonnées cloud refusés, y compris après redirection ; ports 80/443/8080/8443 ; robots.txt respecté par défaut ; 2 Mo et 12 s maximum par page.
- La clé Brave Search facultative est stockée dans la base locale et masquée dans l'interface. Les requêtes web de l'assistant omettent le code, les URL et les secrets reconnus ; ne collez pas de données confidentielles dans une recherche externe.
- Le mode propriétaire « Recherche étendue » augmente la couverture documentaire ; il ne désactive pas les contrôles d'accès aux hôtes internes et aux adresses privées.
- Le texte lu est une **donnée non fiable** : il est présenté comme tel à l'IA, n'alimente jamais l'entraînement et ne donne accès à aucun outil. Limite connue : la résolution DNS est contrôlée avant la requête, pas au niveau du socket (DNS rebinding).
- Sauvegardez `backend/data/cybbig.db` et `backend/data/reports/`.

## Signalement
En cas de vulnérabilité dans Cybbig, ne publiez pas de données sensibles. Documentez les étapes de reproduction avec des données fictives.
