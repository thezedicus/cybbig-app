# Créer vos propres clés API

Cybbig fonctionne **sans aucune clé** : analyses PHP/Web/API, laboratoire, rapports, assistant IA local
(Ollama) et recherche DuckDuckGo sont disponibles dès l'installation.

Les clés ci-dessous sont **facultatives** et **personnelles**. Aucune clé n'est fournie avec
l'application : chaque utilisateur crée les siennes, gratuitement pour la plupart, et les saisit
dans **Paramètres**. Elles restent dans la base locale de votre poste (`%APPDATA%\Cybbig\data\cybbig.db`),
sont masquées (`********`) dans l'interface et ne sont envoyées qu'au service concerné.

| Clé | À quoi elle sert | Où la créer | Où la saisir dans Cybbig |
|---|---|---|---|
| **Ollama Cloud** | Assistant IA en ligne (modèles plus puissants), entraînement | <https://ollama.com/settings/keys> (compte ollama.com) | Paramètres › *IA en ligne (Ollama Cloud)* › Clé API |
| **Brave Search** | Recherche web supplémentaire en parallèle de DuckDuckGo | <https://api-dashboard.search.brave.com/> (offre gratuite disponible) | Paramètres › *IA en ligne (Ollama Cloud)* › Clé Brave Search |
| **NVD (NIST)** | Synchronisation plus rapide des CVE (limite de débit plus élevée) | <https://nvd.nist.gov/developers/request-an-api-key> (envoyée par e-mail) | Paramètres › *Veille et sources* › Clé API NVD |
| **Ollama local protégé** | Seulement si votre serveur Ollama local exige une clé | Votre propre serveur | Paramètres › *Assistant local (Ollama)* › Clé API |

## Pas à pas

1. Créez un compte sur le service voulu et générez une clé (lien du tableau).
2. Dans Cybbig : **Paramètres**, collez la clé dans le champ correspondant, puis **Enregistrer**.
3. Pour l'IA en ligne : cochez *Autoriser l'IA en ligne*, puis **Tester la connexion en ligne**.
4. Pour remplacer une clé : collez la nouvelle valeur. Laisser le champ vide ou `********` conserve
   la clé actuelle.

## Bonnes pratiques

- Une clé = un usage. Révoquez-la sur le site du fournisseur si vous pensez qu'elle a fuité.
- Ne collez jamais une clé dans une question à l'assistant ni dans un fichier du projet.
- Ne partagez pas votre base `cybbig.db` : elle contient vos clés.
- Si vous forkez ce dépôt, ne commitez jamais de fichier `.env`, de base de données ni de clé :
  le `.gitignore` les exclut déjà.

## Et l'administration ?

L'espace **Administration** (terminal, SQL, édition du code) n'est pas nécessaire pour utiliser
Cybbig et n'a pas d'identifiants par défaut. Il est réservé au propriétaire du projet
(voir [ADMIN.md](ADMIN.md)).
