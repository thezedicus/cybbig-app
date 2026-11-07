# Tests Cybbig

## Tests automatisés

```powershell
.\scripts\test.ps1
```

Le script :

1. exécute `pytest -q tests` dans `backend/` sur une base SQLite temporaire ;
2. démarre un backend de test si nécessaire ;
3. exécute `backend/smoke.py` (parcours de bout en bout).

Pour ignorer le smoke :

```powershell
.\scripts\test.ps1 -SkipSmoke
```

## Couverture actuelle

- santé et consentement ;
- projet de démonstration ;
- scans PHP, Web, API, checkout ;
- laboratoire et validation ;
- recherche documentaire ;
- assistant hors ligne ;
- paramètres ;
- génération de rapport ;
- moteurs et audit.

## Vérification manuelle de l'interface

1. Lancer `.\scripts\start.ps1`.
2. Ouvrir l'application (ou `http://127.0.0.1:8765`).
3. Vérifier le tableau de bord, les pages secondaires, le laboratoire et les paramètres.
4. Lancer un scan et consulter le détail.
5. Générer un rapport et l'ouvrir depuis le dossier de téléchargements.
