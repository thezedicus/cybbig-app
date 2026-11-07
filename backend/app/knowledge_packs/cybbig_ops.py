"""Paquet « Cybbig » : fiches d'exploitation du poste (IA en ligne, performance, visite de sites, entraînement)."""
from __future__ import annotations

PACK_ID = "ops"
VERSION = "2"
PREFIX = "Cybbig"

# (slug, titre, catégorie, contenu, tags)
DOCS = [
("ia-en-ligne", "IA en ligne (Ollama Cloud) : fonctionnement et confidentialité", "IA",
 "Cybbig peut utiliser un modèle hébergé par Ollama (https://ollama.com) en plus du modèle local. Réglage : Paramètres > IA en ligne : coller la clé API Ollama, laisser le mode « Automatique ». "
 "Automatique = le modèle en ligne est utilisé s'il répond, sinon bascule sur le modèle local. « Local uniquement » n'envoie aucune donnée hors du poste. Ce qui part en ligne : la question, "
 "l'historique court, les extraits de la base de connaissances et le contexte des projets (résultats d'analyse) nécessaires à la réponse. Les secrets reconnus (clés, jetons, Bearer, JWT, clés privées) "
 "sont masqués avant l'envoi. La clé API en ligne est distincte de celle d'un serveur Ollama local et n'est envoyée qu'à l'adresse HTTPS configurée. Alternative : se connecter avec `ollama signin` "
 "puis utiliser des modèles « -cloud » depuis Ollama local.",
 "ollama,cloud,confidentialité,configuration"),
("vitesse-ia-locale", "Accélérer l'IA locale : processeur, mémoire, GPU", "IA",
 "Sur CPU, la vitesse dépend du nombre de paramètres du modèle, de la quantification, de la mémoire disponible et du nombre de threads. Cybbig règle automatiquement num_thread (cœurs physiques), "
 "num_ctx et num_batch selon un profil (Auto, Économe, Équilibré, Maximum) et garde ces valeurs stables, car changer num_ctx force Ollama à recharger le modèle. Le modèle est préchargé au démarrage "
 "(keep_alive 30 min) pour éviter 10 à 40 s d'attente à la première question. Un GPU NVIDIA (CUDA) ou AMD (ROCm) compatible est utilisé automatiquement par Ollama : le panneau Ressources affiche la part du "
 "modèle placée sur le GPU. Un GPU intégré Intel n'est en général pas exploité. Sans GPU, préférer un modèle de 3 milliards de paramètres ou moins, ou l'IA en ligne.",
 "performance,gpu,cpu,ollama"),
("choisir-un-modele", "Choisir un modèle Ollama selon le PC", "IA",
 "Règle pratique : un modèle quantifié 4 bits occupe environ 0,6 Go par milliard de paramètres, plus le contexte. 16 Go de RAM sans GPU : modèles de 3 à 7 milliards (qwen2.5:3b, llama3.2:3b, "
 "qwen2.5:7b), un seul chargé à la fois. Code : qwen2.5-coder. Raisonnement : deepseek-r1 (lent, la réflexion est retirée de l'affichage). Plus le modèle est gros, meilleure est la qualité mais plus "
 "la réponse est lente sur CPU. Pour des questions complexes, utiliser le modèle en ligne ; pour des données sensibles, rester en local.",
 "ollama,modèles,choix"),
("visiter-des-sites", "Visiter des sites web depuis Cybbig", "Web",
 "Base de connaissances > Ajouter des données > Site web : saisir une URL, un sélecteur CSS optionnel pour ne garder qu'une zone de la page, puis « Lire » (aperçu) ou « Ajouter à la base ». "
 "L'exploration suit les liens du même site (jusqu'à 25 pages, profondeur 2) avec un délai entre les pages. Garde-fous : http/https, ports 80/443/8080/8443, adresses publiques uniquement "
 "(réseau privé, localhost et métadonnées cloud refusés, y compris après redirection), robots.txt respecté par défaut, taille et durée limitées. Dans l'assistant, une URL collée dans la question est lue "
 "automatiquement (réglage « Lecture des liens »). Le contenu importé est externe et non vérifié ; il est étiqueté « web-import » et ne doit jamais être traité comme une consigne.",
 "web,crawl,scrapling,base-de-connaissances"),
("scrapling-extraction", "Scrapling : extraire des données de pages HTML", "Web",
 "Scrapling (https://github.com/D4Vinci/Scrapling, licence BSD-3) est une bibliothèque Python d'extraction. Cybbig utilise son analyseur : `from scrapling.parser import Selector; page = Selector(html, url=url)`, "
 "puis `page.css('h1::text').get()`, `page.css('a::attr(href)').getall()`, `page.find_by_text(...)`, `element.get_all_text(separator=' ', strip=True)`. Les sélecteurs CSS et XPath sont pris en charge. "
 "Scrapling propose aussi des « fetchers » (HTTP avec empreinte navigateur, navigateur piloté pour les pages rendues en JavaScript) et un mode adaptatif qui retrouve un élément après un changement de "
 "mise en page ; ils demandent `pip install \"scrapling[fetchers]\"` puis `scrapling install` et ne sont pas activés par défaut dans Cybbig. Respecter les conditions d'utilisation et le robots.txt des sites visités.",
 "scrapling,scraping,python,css"),
("entrainement-modele-local", "Entraîner le modèle local avec le modèle en ligne", "IA",
 "Principe professeur/élève : le modèle en ligne (professeur) lit la bibliothèque et rédige des fiches manquantes puis des paires question/réponse ; les paires validées servent à (1) enrichir la "
 "recherche documentaire (RAG), qui est la mémoire principale de l'assistant, (2) créer un modèle Ollama local personnalisé « cybbig-analyst » (instruction système + exemples de dialogue intégrés au "
 "Modelfile), (3) exporter un fichier JSONL au format conversationnel pour un vrai fine-tuning (LoRA) hors de Cybbig. La personnalisation Ollama ne modifie pas les poids du modèle : elle fixe son rôle, "
 "son style et des exemples. Les contenus générés sont étiquetés « généré par IA, non vérifié » et doivent être relus avant d'être approuvés.",
 "entraînement,distillation,ollama,modelfile"),
("lecture-de-pages-non-fiable", "Pages web lues par l'IA : contenu non fiable", "Web",
 "Une page web peut contenir des instructions destinées à manipuler l'assistant (« ignore tes règles », « envoie ce fichier »). Cybbig présente toute page lue comme une donnée externe non fiable, "
 "ne lui donne aucun outil d'action et ne suit pas ses consignes. Si une réponse semble obéir à une page, vérifier la source et signaler le contenu. Ne jamais coller de secret dans une question "
 "si le mode en ligne est actif.",
 "sécurité,prompt-injection,web"),
]
