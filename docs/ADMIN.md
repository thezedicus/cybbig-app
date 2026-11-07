# Administration : accès réservé au propriétaire

## Principe

- **Aucun identifiant ni mot de passe administrateur n'existe dans le code, le dépôt ou l'installateur.**
  Sur une nouvelle installation, l'espace Administration est verrouillé.
- Le dépôt ne contient que la **clé publique** Ed25519 du propriétaire
  (`backend/app/services/owner.py`). Une clé publique sert uniquement à *vérifier* une signature :
  elle ne permet pas d'en produire une, ni de se connecter.
- La **clé privée** correspondante n'existe que sur le poste du propriétaire, hors du dépôt
  (`%USERPROFILE%\.cybbig\owner_ed25519.key`).
- Les identifiants choisis à l'activation sont stockés localement sous forme de hachés
  PBKDF2-SHA256 (240 000 itérations, sel aléatoire), jamais en clair.

## Activer l'administration sur un poste (propriétaire)

1. Ouvrez Cybbig › **Administration**. L'écran *Activation propriétaire* affiche un défi
   (valable 10 minutes, utilisable une seule fois, lié à cette installation).
2. Cliquez **Copier la commande**, puis sur votre poste, depuis le dossier du dépôt :

   ```powershell
   python scripts/owner-sign.py sign cybbig-owner-v1.<installation>.<nonce>
   ```

3. Collez la signature (128 caractères hexadécimaux), choisissez un identifiant et un mot de passe
   (10 caractères minimum), puis **Activer**.
4. Connectez-vous avec ces identifiants.

Identifiants oubliés : écran de connexion › *Identifiants oubliés ? Activation propriétaire*
(même procédure, les anciens identifiants sont remplacés et les sessions fermées).

Cinq échecs (connexion ou signature) bloquent l'accès cinq minutes. Chaque tentative est journalisée.

## Clé privée du propriétaire

| Commande | Effet |
|---|---|
| `python scripts/owner-sign.py keygen` | Crée la clé privée (refuse d'écraser une clé existante) |
| `python scripts/owner-sign.py pubkey` | Affiche la clé publique correspondante |
| `python scripts/owner-sign.py sign <défi>` | Signe un défi |

- **Sauvegardez la clé privée hors ligne** (clé USB chiffrée, gestionnaire de mots de passe).
  Si elle est perdue, plus aucune activation n'est possible : il faut générer une nouvelle paire
  et publier une nouvelle version avec la nouvelle clé publique.
- **Si elle fuit** : générez une nouvelle paire (`CYBBIG_OWNER_KEY=<nouveau chemin>` puis `keygen`),
  remplacez `OWNER_PUBLIC_KEY` dans `backend/app/services/owner.py` et publiez une nouvelle version.
- Le chemin peut être changé avec la variable d'environnement `CYBBIG_OWNER_KEY`.

## Limite à connaître

Cybbig est un logiciel local et open source : une personne qui modifie *sa propre copie* du code
peut évidemment retirer cette protection sur *son propre poste*. Le mécanisme garantit en revanche
qu'aucun accès administrateur n'est livré, que l'application officielle ne peut être administrée
qu'avec votre clé privée, et que vos identifiants ne figurent nulle part dans le dépôt.
