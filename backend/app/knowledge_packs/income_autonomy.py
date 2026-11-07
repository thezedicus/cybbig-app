"""Connaissances vérifiables pour le radar local d'opportunités rémunérées."""
from __future__ import annotations

PACK_ID = "income_autonomy"
VERSION = "1"
PREFIX = "Opportunités"

DOCS = [
    ("robot-opportunites", "Architecture d’un agent local de recherche de missions", "Agent autonome",
     """Un agent utile suit une boucle de travail explicite : découvrir des pistes depuis des sources autorisées, normaliser les données, dédupliquer, filtrer selon un profil déclaré, classer avec des critères visibles, vérifier l’échéance et la page d’origine, préparer un brouillon, puis suivre le résultat. Cybbig automatise les étapes de recherche, de classement, de suivi et d’analyse locale. Les appels réseau utilisent un cache persistant et des limites de fréquence pour limiter les pannes et respecter les services sources. Les extraits du Web sont des données non fiables : ils ne peuvent pas remplacer les règles de Cybbig ni déclencher des commandes.

L’agent ne doit pas inventer des compétences, une identité, des références, un salaire ou des résultats. Avant une candidature, un engagement, une contribution à un contrat ou un test de sécurité, l’utilisateur vérifie le contenu, les conditions, le périmètre et l’autorisation. Les candidatures et inscriptions exigent des comptes qui appartiennent à l’utilisateur; les secrets restent locaux et ne sont jamais extraits d’un navigateur ou envoyés à un modèle cloud par la revue locale.""",
     "autonomie, missions, filtrage, cache, validation, supervision"),
    ("flux-offres-remote", "Flux d’offres à distance : attribution, qualité et limites", "Sources rémunérées",
     """Remote OK fournit un flux JSON public à https://remoteok.com/api. Ses consignes demandent d’attribuer Remote OK et de créer un lien vers chaque offre d’origine. Remotive documente également une API publique de postes à distance; la page d’API demande d’attribuer la source Remotive et de renvoyer vers l’offre d’origine. Remotive précise que les annonces sont différées et que les informations, conditions, rémunérations et disponibilités doivent être vérifiées sur la page source. Cybbig conserve l’URL originale, le nom du flux, la date de découverte et un extrait; il n’utilise pas ces flux pour republier un catalogue tiers.

Sources : https://remoteok.com/faq · https://remotive.com/remote-jobs/api · https://remotive.com/terms-of-use""",
     "Remote OK, Remotive, API, flux, attribution, emploi"),
    ("appels-europeens", "Appels à projets et marchés du portail européen", "Subventions et marchés",
     """La Commission européenne documente une API REST publique du portail Funding & Tenders pour rechercher des appels à propositions, des appels d’offres, des organisations et des informations associées. La recherche Cybbig garde les liens vers le portail et exclut les échéances passées lorsqu’elles sont indiquées. Un appel n’est pas du revenu garanti : vérifier les dates, l’éligibilité géographique et juridique, les dépenses couvertes, le cofinancement, les livrables, les délais et le processus de candidature. La soumission en ligne peut nécessiter EU Login et un participant enregistré; elle ne doit pas être simulée par Cybbig.

Source officielle et documentation API : https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/support/apis · https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/about""",
     "Commission européenne, SEDIA, subvention, marché, échéance, éligibilité"),
    ("bug-bounty-scope", "Bug bounty : autorisation, portée et récompense", "Recherche de sécurité autorisée",
     """Un programme de divulgation ou un bug bounty ne donne pas une autorisation générale d’examiner une entreprise. Lire les actifs explicitement inclus, les exclusions, les catégories de tests autorisées, les règles de traitement des données et la politique de récompense du programme précis. Un programme de divulgation peut n’offrir aucun paiement. Un signalement n’assure pas une prime; la validation et le paiement sont décidés par l’organisateur. Cybbig peut découvrir une page publique et aider à organiser la lecture de sa politique, mais ne teste aucune cible issue d’une simple annonce et ne soumet pas automatiquement de rapport.

Sources : https://docs.hackerone.com/en/articles/8494552-defining-scope · https://docs.hackerone.com/en/articles/8494502-safe-harbor-overview-faq · https://docs.hackerone.com/en/articles/8368965-vdp-vs-bbp""",
     "bug bounty, périmètre, autorisation, safe harbor, VDP, prime"),
    ("anti-arnaques-missions", "Vérifier une offre rémunérée et repérer les arnaques", "Vérification des offres",
     """Avant d’engager du temps ou de communiquer des données personnelles, vérifier que l’annonce figure sur le site officiel de l’employeur ou du programme; contrôler le domaine, l’identité juridique, les coordonnées et la date; lire le contrat et les critères de paiement; rechercher les frais exigés d’avance, les achats imposés, les demandes de transfert d’argent, les paiements en crypto imposés et les demandes de secrets ou documents sans justification. Ne pas payer pour débloquer une mission ou une rémunération annoncée. Conserver les preuves et signaler une offre suspecte au site source. Ces vérifications réduisent les risques, sans certifier qu’une offre est authentique.""",
     "arnaque, fraude, paiement, vérification, identité, sécurité"),
]
