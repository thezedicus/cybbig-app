"""Bibliothèques 6 à 8 fournies pour Cybbig, segmentées par titres et sections."""

PACK_ID = "user_libraries_6_7_8"
VERSION = "1"
PREFIX = "Bibliothèques Cybbig"
DOCS = [['6-bibliothque-n6-code-vpn-proxy-web-scraping-collecte-de-d',
  'Bibliothèque n°6 — Code, VPN, Proxy, Web Scraping, collecte de données et navigation réseau',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# Bibliothèque n°6 — Code, VPN, Proxy, Web Scraping, collecte de données et navigation réseau\n'
  '\n'
  "Cette bibliothèque complète les précédentes de Cybbig. Elle doit permettre à l'assistant IA de comprendre comment "
  'fonctionnent les réseaux, les VPN, les proxies, les navigateurs automatisés et les outils de scraping, mais aussi '
  'de savoir écrire, analyser, tester et orchestrer des scripts de collecte de données.\n'
  '\n'
  'Elle inclut notamment Scrapling, un framework Python de scraping, ainsi que Playwright, Scrapy, Selenium, '
  'BeautifulSoup, HTTPX et les outils réseau.\n'
  '\n'
  "L'objectif est de constituer une base technique exploitable par l'IA : expliquer les concepts, choisir le bon "
  'outil, générer du code, diagnostiquer les erreurs et construire des automatisations fiables, dans le respect des '
  "accès autorisés, des conditions d'utilisation et de la protection des données.",
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-1-les-grands-domaines-intgrer',
  '1. Les grands domaines à intégrer',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 1. Les grands domaines à intégrer\n'
  '\n'
  '| Domaine                 | Connaissances à enregistrer                                             |\n'
  '| ----------------------- | ----------------------------------------------------------------------- |\n'
  '| VPN                     | Tunneling, chiffrement, protocoles, routage, kill switch, fuites DNS/IP |\n'
  '| Proxy                   | HTTP, HTTPS, SOCKS4, SOCKS5, reverse proxy, forward proxy               |\n'
  '| Réseau                  | TCP/IP, UDP, DNS, TLS, ports, sockets, IPv4, IPv6                       |\n'
  '| Web scraping            | Extraction HTML, CSS, XPath, pagination, données structurées            |\n'
  '| Crawling                | Exploration de sites, liens internes, sitemap, robots.txt               |\n'
  '| Navigateurs automatisés | Playwright, Selenium, Chromium, Firefox                                 |\n'
  '| Identité réseau         | Adresse IP publique/privée, DNS, en-têtes HTTP, cookies, sessions       |\n'
  '| Collecte de données     | API publiques, flux RSS, JSON, CSV, XML, pages web                      |\n'
  '| Automatisation          | Scripts Python, tâches planifiées, files de travaux, exports            |\n'
  "| Sécurité réseau         | Certificats, TLS, authentification, contrôle d'accès, journalisation    |\n"
  '| Protection des données  | Minimisation, conservation, anonymisation, RGPD                         |\n'
  '| Diagnostic              | Latence, timeout, erreurs HTTP, DNS, connexion proxy, certificats       |',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-2-vpn-concepts-protocoles-et-outils',
  '2. VPN : concepts, protocoles et outils',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 2. VPN : concepts, protocoles et outils\n'
  '\n'
  '[How a VPN Works Diagram '
  '(Beginner-Friendly)](https://images.openai.com/static-rsc-4/fNWOiXL6rIV9Z6TCk6_5pzWiw7rpqFZFQDkndGek_wxXrLER4ihiCZ-Iv5I3UoIAKXgVGv8X4m23P_uhgrGtFgqnrTz9RPAWVBVDHRXMBAdts1o-xXy9zcYDKPWLzpNEz99ICAhLqchkpngxQUGmB4ZFGYIusR8SGfzjPacRXsE?purpose=inline)\n'
  '\n'
  'VPN — Virtual Private Network\n'
  '\n'
  'Crée un tunnel réseau entre un appareil et un serveur VPN. Le trafic entre les deux extrémités est protégé selon le '
  'protocole et la configuration utilisés. Un VPN ne rend pas automatiquement anonyme : les sites, comptes connectés, '
  'cookies et empreintes du navigateur peuvent toujours permettre de reconnaître une session.\n'
  '\n'
  '[WireGuard VPN Server - Sicherer Fernzugriff - Tutorial | '
  'NetzBastion.de](https://images.openai.com/static-rsc-4/kvExmDdUpmiUuWT35tGu0bpZ1w91sYhp-zLSJZqEgTpFKxLIne8GXtcIB1k6RwubPScje0yebx95ED69p6Jcl7vgT-Bmc2a7Wlx-MZI5D0Wge83ODYwvHX-fuzYuUcvG3ENI9-MMQeby3kwrr6etqVosetYnrG5rUjN1Fb3Xabc?purpose=inline)\n'
  '\n'
  'WireGuard\n'
  '\n'
  'Protocole VPN moderne, conçu pour être relativement simple et performant. À étudier : clés publiques/privées, '
  'pairs, interfaces, routes et configuration réseau.\n'
  '\n'
  '[Site officiel](https://www.wireguard.com/?utm_source=chatgpt.com)\n'
  '\n'
  '[OpenVPN Connect - Windows官方下载 | 微软应用商店 | Microsoft '
  'Store](https://images.openai.com/static-rsc-4/LJJ_vQDZhVqRNSWiH9mK5bcuQbM6q1mbkD_9tkVv6k2FiuEFSLK36MDkJ_AXfRRcaklI-oOKzmdgUN1HOsLZGrADvw68VZH9ez5zCiZEm7-kXNtSLaKslntPbVnuV8vao5xYv3iP6wqR4UIGCCfU0twy_q5dxZNHRjGOeQQQJVI?purpose=inline)\n'
  '\n'
  'OpenVPN\n'
  '\n'
  'Solution VPN reposant sur TLS, avec certificats, authentification et configurations client/serveur.\n'
  '\n'
  '[Site officiel](https://openvpn.net/?utm_source=chatgpt.com)\n'
  '\n'
  '[How to Use Tor Browser to Protect Your Privacy '
  'Online](https://images.openai.com/static-rsc-4/O_o2YxgvvCZlePiHB4cleuYygB3zEinMW2vCfH6RWGl8AO6TxcZqp9XwNRQRGtPIljR5toiqip0HG_duQYleFaZhpl9mmgPcyMaP6uK2gEPQXcr9oHUC2lPbD9XXWGt-imqTnDFSIBkD2yT2QrephBlHbypbnWEIG-o7Fxr5xFo?purpose=inline)\n'
  '\n'
  'Tor\n'
  '\n'
  "Réseau de routage en oignon, différent d'un VPN classique. À étudier : circuits, relais, nœuds de sortie, limites "
  'de confidentialité et usages légitimes.\n'
  '\n'
  '[Site officiel](https://www.torproject.org/?utm_source=chatgpt.com)\n'
  '\n'
  'Notions à documenter :\n'
  '\n'
  '- VPN site-à-site et VPN client-à-site.\n'
  '- Split tunneling et full tunneling.\n'
  '- Kill switch et protection contre les fuites DNS.\n'
  '- Fuites IPv6, DNS et WebRTC.\n'
  '- Routage, passerelles, tables de routage et MTU.\n'
  '- Authentification par certificats et clés.\n'
  "- VPN personnel, VPN d'entreprise et VPN auto-hébergé.\n"
  '- Différences entre VPN, proxy, Tor et DNS chiffré.\n'
  '- Limites : confiance envers le fournisseur, journaux de connexion, configuration et sécurité du terminal.\n'
  '\n'
  'Outils à référencer :\n'
  '\n'
  '- WireGuard — [Documentation](https://www.wireguard.com/?utm_source=chatgpt.com).\n'
  '- OpenVPN — [Documentation communautaire](https://openvpn.net/community-resources/?utm_source=chatgpt.com).\n'
  '- strongSwan — [Site officiel](https://www.strongswan.org/?utm_source=chatgpt.com).\n'
  '- Tailscale — [Documentation](https://tailscale.com/kb?utm_source=chatgpt.com).\n'
  '- Headscale — [Dépôt GitHub](https://github.com/juanfont/headscale?utm_source=chatgpt.com).\n'
  '- Mullvad VPN — [Site officiel](https://mullvad.net/?utm_source=chatgpt.com).',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-3-proxy-types-fonctionnement-et-utilisation',
  '3. Proxy : types, fonctionnement et utilisation',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 3. Proxy : types, fonctionnement et utilisation\n'
  '\n'
  '[How Istio’s “Ambient Mode” Transparent Proxy—tproxy—Works Under the '
  'Hood](https://images.openai.com/static-rsc-4/J9IKcL79bFb8aq8jhpnibdHw1j_iygFYmVotAphJmF6_JlGCcoOoGPZKu-O8MZ02Xx-gednpeOxjGDQEjeebSrLVjJ2cCw1OHE4WlfNGG_-y4UOTxRuCRKp_dRMcCd4Vv2K1qnIAYBworfyQjPZr7xlh0nAduRd4V3nwNuSjOPk?purpose=inline)\n'
  '\n'
  '[tetrate.io](https://tetrate.io/blog/what-is-tproxy-and-how-does-it-work?utm_source=chatgpt.com)\n'
  '\n'
  'Un proxy est un intermédiaire entre un client et une destination. Il peut servir à contrôler les accès, acheminer '
  'le trafic, mettre en cache des réponses, protéger un serveur ou faciliter des tests réseau.\n'
  '\n'
  '| Type              | Fonction                                                       |\n'
  '| ----------------- | -------------------------------------------------------------- |\n'
  '| HTTP proxy        | Transmet des requêtes HTTP                                     |\n'
  '| HTTPS proxy       | Transporte des connexions HTTPS, souvent via CONNECT           |\n'
  '| SOCKS4            | Relais réseau SOCKS, version ancienne                          |\n'
  "| SOCKS5            | Relais TCP et, selon l'implémentation, UDP                     |\n"
  '| Forward proxy     | Agit au nom du client                                          |\n'
  '| Reverse proxy     | Reçoit le trafic avant le serveur                              |\n'
  '| Transparent proxy | Intercepte ou redirige le trafic selon la configuration réseau |\n'
  '| Residential proxy | Adresse IP associée à un accès résidentiel                     |\n'
  "| Datacenter proxy  | Adresse IP issue d'une infrastructure de centre de données     |\n"
  "| Rotating proxy    | Change d'adresse selon une politique définie                   |\n"
  '\n'
  'Outils et projets à intégrer :\n'
  '\n'
  '- mitmproxy — inspection et débogage du trafic HTTP(S) dans des environnements autorisés. '
  '[GitHub](https://github.com/mitmproxy/mitmproxy?utm_source=chatgpt.com).\n'
  '- Squid — proxy HTTP et cache. [Site officiel](https://www.squid-cache.org/?utm_source=chatgpt.com).\n'
  '- HAProxy — répartition de charge et proxy. [Site officiel](https://www.haproxy.org/?utm_source=chatgpt.com).\n'
  '- NGINX — reverse proxy et serveur web. [Documentation](https://nginx.org/en/docs/?utm_source=chatgpt.com).\n'
  '- Caddy — serveur web et reverse proxy. [Documentation](https://caddyserver.com/docs/?utm_source=chatgpt.com).\n'
  '- Traefik — proxy et routage pour applications. '
  '[Documentation](https://doc.traefik.io/traefik/?utm_source=chatgpt.com).\n'
  '\n'
  'Notions importantes : authentification proxy, proxy chaining dans un environnement de test, rotation contrôlée, '
  "délais d'expiration, DNS via proxy, certificats, journaux, disponibilité, latence et détection des erreurs de "
  'configuration.',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-4-web-scraping-et-scrapling',
  '4. Web scraping et Scrapling',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 4. Web scraping et Scrapling\n'
  '\n'
  '[Scrapling: Adaptive Web Scraping for SRE Teams - Akmatori '
  'Blog](https://images.openai.com/static-rsc-4/jBYhRDkw5u9eHLrfF_ByWpOIijt62K-_auClGcACt7mE2ZFHHrmJsBju2EBmY621QqzbZdYucnG7501rvo2vYs7Az2IHxANDnOcdIx2unkpR0VZas4YrhF7bnc4r1jkdYwz4MUTJlc2wFu0N1GSXAWlfhAmSyofk-lymkIC8JWI?purpose=inline)\n'
  '\n'
  'Scrapling\n'
  '\n'
  "Framework Python de collecte et d'analyse de pages web. Il regroupe requêtes HTTP, extraction de contenu, "
  'navigateurs, spiders, sessions, rotation de proxies et exports. Il propose également une intégration destinée aux '
  'agents IA via MCP.&#x20;\n'
  '\n'
  '[image](https://www.google.com/s2/favicons?domain=https://scrapling.readthedocs.io\\&sz=32)\n'
  '\n'
  'Scrapling documentation+1\n'
  '\n'
  '[Documentation Scrapling](https://scrapling.readthedocs.io/fr/stable/index.html?utm_source=chatgpt.com) · '
  '[GitHub](https://github.com/arnoldwender/scrapling?utm_source=chatgpt.com)\n'
  '\n'
  'À intégrer en priorité\n'
  '\n'
  "&#x20;Scrapling peut devenir l'un des moteurs de collecte de données de Cybbig, notamment pour alimenter une base "
  'de connaissances avec des informations publiques et autorisées.',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-les-bibliothques-de-scraping-connatre',
  'Les bibliothèques de scraping à connaître',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Les bibliothèques de scraping à connaître\n'
  '\n'
  '| Technologie   | Fonction principale                            |\n'
  '| ------------- | ---------------------------------------------- |\n'
  '| Scrapling     | Scraping adaptatif et crawling                 |\n'
  '| Scrapy        | Crawling structuré à grande échelle            |\n'
  '| BeautifulSoup | Analyse HTML et XML                            |\n'
  '| lxml          | Analyse rapide de HTML/XML                     |\n'
  '| Playwright    | Automatisation de navigateurs modernes         |\n'
  '| Selenium      | Automatisation de navigateurs                  |\n'
  '| Requests      | Requêtes HTTP synchrones                       |\n'
  '| HTTPX         | Requêtes HTTP synchrones et asynchrones        |\n'
  '| selectolax    | Analyse HTML performante                       |\n'
  '| trafilatura   | Extraction du contenu principal des pages      |\n'
  "| newspaper4k   | Extraction d'articles                          |\n"
  '| feedparser    | Lecture de flux RSS et Atom                    |\n'
  '| extruct       | Extraction de données structurées              |\n'
  '| pandas        | Nettoyage et traitement des données collectées |\n'
  '\n'
  'Documentation : [Playwright — réseau et proxies](https://playwright.dev/python/docs/network?utm_source=chatgpt.com) '
  '· [Scrapy](https://docs.scrapy.org/?utm_source=chatgpt.com) · '
  '[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/?utm_source=chatgpt.com) · '
  '[HTTPX](https://www.python-httpx.org/?utm_source=chatgpt.com).',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-les-techniques-de-scraping-enregistrer',
  'Les techniques de scraping à enregistrer',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Les techniques de scraping à enregistrer\n'
  '\n'
  "1. Récupération d'une page HTML.\n"
  '2. Extraction de titres, paragraphes, images et liens.\n'
  '3. Extraction CSS et XPath.\n'
  '4. Exploration des pages avec pagination.\n'
  '5. Lecture des sitemaps XML.\n'
  '6. Analyse des données JSON intégrées dans une page.\n'
  '7. Extraction de données structurées Schema.org.\n'
  '8. Collecte de flux RSS.\n'
  '9. Automatisation des pages JavaScript.\n'
  '10. Gestion des sessions et cookies.\n'
  '11. Téléchargement de fichiers accessibles publiquement.\n'
  '12. Détection des changements de contenu.\n'
  '13. Nettoyage et normalisation du texte.\n'
  '14. Déduplication des résultats.\n'
  '15. Export JSON, JSONL, CSV et XML.\n'
  "16. Enregistrement des sources, dates et URL d'origine.\n"
  '17. Gestion des erreurs et nouvelles tentatives raisonnables.\n'
  '18. Mise en cache pour éviter les requêtes répétées.\n'
  "19. Respect des limites de fréquence et des conditions d'accès.\n"
  '20. Surveillance des changements de structure des pages.\n'
  '\n'
  "Important : la base doit enseigner à l'IA à privilégier les API officielles, les flux et les sources autorisées. "
  'Elle ne doit pas transformer la rotation de proxies ou les mécanismes anti-détection en moyen de contourner des '
  "restrictions d'accès, des CAPTCHA, des connexions privées ou des limitations explicites.",
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-5-exemples-de-commandes-et-de-code',
  '5. Exemples de commandes et de code',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 5. Exemples de commandes et de code',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-installer-l-environnement-python',
  "Installer l'environnement Python",
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  "### Installer l'environnement Python\n"
  '\n'
  '```\n'
  'python -m venv .venv',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-windows',
  'Windows',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# Windows\n'
  '.venv\\Scripts\\activate',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-linux-macos',
  'Linux / macOS',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# Linux / macOS\n'
  'source .venv/bin/activate\n'
  '\n'
  'python -m pip install --upgrade pip\n'
  'pip install "scrapling[fetchers]" requests httpx\n'
  'scrapling install\n'
  '```\n'
  '\n'
  "La documentation de Scrapling précise que l'installation de base ne suffit pas pour utiliser les fetchers et les "
  'spiders : il faut installer les dépendances correspondantes.&#x20;\n'
  '\n'
  '[image](https://www.google.com/s2/favicons?domain=https://scrapling.readthedocs.io\\&sz=32)\n'
  '\n'
  'Scrapling documentation',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-exemple-scrapling-extraire-une-page-publique-de-dmonstra',
  'Exemple Scrapling : extraire une page publique de démonstration',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Exemple Scrapling : extraire une page publique de démonstration\n'
  '\n'
  '```\n'
  'from scrapling.fetchers import Fetcherurl = "https://quotes.toscrape.com/"page = Fetcher.get(url)quotes = '
  'page.css(".quote")for quote in quotes:    text = quote.css(".text::text").get()    author = '
  'quote.css(".author::text").get()    print({        "citation": text,        "auteur": author    })\n'
  '```',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-exemple-vrifier-un-proxy-configur',
  'Exemple : vérifier un proxy configuré',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Exemple : vérifier un proxy configuré\n'
  '\n'
  '```\n'
  'import httpxproxy = "http://127.0.0.1:8080"try:    with httpx.Client(        proxy=proxy,        timeout=10    ) as '
  'client:        response = client.get("https://example.com")        print("Statut :", response.status_code)except '
  'httpx.ProxyError as error:    print("Erreur proxy :", error)except httpx.RequestError as error:    print("Erreur '
  'réseau :", error)\n'
  '```\n'
  '\n'
  "Cet exemple vérifie une connexion via un proxy local. Il ne configure pas de VPN et ne garantit pas l'absence de "
  'fuite réseau.',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-exemple-automatisation-de-navigateur-avec-playwright',
  'Exemple : automatisation de navigateur avec Playwright',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Exemple : automatisation de navigateur avec Playwright\n'
  '\n'
  '```\n'
  'from playwright.sync_api import sync_playwrightwith sync_playwright() as p:    browser = '
  'p.chromium.launch(headless=True)    page = browser.new_page()    page.goto("https://quotes.toscrape.com/")    '
  'titles = page.locator(".quote .text").all_text_contents()    for title in titles:        print(title)    '
  'browser.close()\n'
  '```\n'
  '\n'
  'La documentation Playwright décrit également la configuration de proxies HTTP(S) et SOCKS5 au niveau du navigateur '
  "ou d'un contexte.&#x20;\n"
  '\n'
  '[image](https://www.google.com/s2/favicons?domain=https://playwright.dev\\&sz=32)\n'
  '\n'
  'Playwright Python+1',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-6-dpts-github-intgrer-dans-la-bibliothque',
  '6. Dépôts GitHub à intégrer dans la bibliothèque',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 6. Dépôts GitHub à intégrer dans la bibliothèque\n'
  '\n'
  '| Projet        | Utilité                   | '
  'Dépôt                                                                                  |\n'
  '| ------------- | ------------------------- | '
  '-------------------------------------------------------------------------------------- |\n'
  '| Scrapling     | Scraping Python adaptatif | '
  '[GitHub](https://github.com/D4Vinci/Scrapling?utm_source=chatgpt.com)                  |\n'
  '| Scrapy        | Crawling et extraction    | '
  '[GitHub](https://github.com/scrapy/scrapy?utm_source=chatgpt.com)                      |\n'
  '| Playwright    | Navigateurs automatisés   | '
  '[GitHub](https://github.com/microsoft/playwright?utm_source=chatgpt.com)               |\n'
  '| Selenium      | Automatisation web        | '
  '[GitHub](https://github.com/SeleniumHQ/selenium?utm_source=chatgpt.com)                |\n'
  '| mitmproxy     | Analyse du trafic HTTP    | '
  '[GitHub](https://github.com/mitmproxy/mitmproxy?utm_source=chatgpt.com)                |\n'
  '| WireGuard     | VPN                       | '
  '[GitHub](https://github.com/WireGuard?utm_source=chatgpt.com)                          |\n'
  '| OpenVPN       | VPN                       | '
  '[GitHub](https://github.com/OpenVPN?utm_source=chatgpt.com)                            |\n'
  '| HTTPX         | Client HTTP Python        | '
  '[GitHub](https://github.com/encode/httpx?utm_source=chatgpt.com)                       |\n'
  '| BeautifulSoup | Analyse HTML              | [Site '
  'officiel](https://www.crummy.com/software/BeautifulSoup/?utm_source=chatgpt.com) |\n'
  '| Trafilatura   | Extraction de contenu web | '
  '[GitHub](https://github.com/adbar/trafilatura?utm_source=chatgpt.com)                  |\n'
  '| NGINX         | Reverse proxy             | '
  '[GitHub](https://github.com/nginx/nginx?utm_source=chatgpt.com)                        |\n'
  '| HAProxy       | Proxy et load balancing   | '
  '[GitHub](https://github.com/haproxy/haproxy?utm_source=chatgpt.com)                    |',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-7-scurit-confidentialit-et-conformit',
  '7. Sécurité, confidentialité et conformité',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 7. Sécurité, confidentialité et conformité\n'
  '\n'
  'Cette partie est indispensable : Stratege ne doit pas simplement apprendre à collecter des données, mais aussi à '
  'identifier les risques avant chaque opération.\n'
  '\n'
  "| Sujet                    | Ce que l'IA doit apprendre                                                 |\n"
  '| ------------------------ | -------------------------------------------------------------------------- |\n'
  '| RGPD                     | Base légale, finalité, minimisation et durée de conservation               |\n'
  '| Robots.txt               | Lire les directives de crawl et les restrictions annoncées                 |\n'
  "| Conditions d'utilisation | Identifier les règles d'accès et d'utilisation des données                 |\n"
  '| Données personnelles     | Reconnaître les données identifiantes et sensibles                         |\n'
  '| Secrets                  | Ne jamais enregistrer les mots de passe, cookies ou tokens en clair        |\n'
  "| SSRF                     | Empêcher un scraper d'accéder à des services internes ou métadonnées cloud |\n"
  '| TLS                      | Vérifier les certificats et éviter les connexions non sécurisées           |\n'
  '| Rate limiting            | Limiter les requêtes et respecter les réponses 429                         |\n'
  '| Journalisation           | Enregistrer les URL, dates, statuts et erreurs sans exposer de secrets     |\n'
  '| Stockage                 | Contrôler les accès, les suppressions et la durée de conservation          |\n'
  '\n'
  'Cas à apprendre à reconnaître et à bloquer :\n'
  '\n'
  "- Scraper une zone privée nécessitant une autorisation que l'utilisateur ne possède pas.\n"
  '- Collecter des données personnelles sans fondement légal approprié.\n'
  "- Utiliser un proxy pour contourner une interdiction d'accès.\n"
  "- Tenter de contourner un système de connexion, un CAPTCHA ou une limitation d'accès.\n"
  '- Extraire des secrets, identifiants, cookies ou informations confidentielles.\n'
  "- Laisser une URL fournie par un utilisateur accéder aux IP privées, à `localhost` ou aux métadonnées d'un serveur "
  'cloud.\n'
  '- Lancer des crawlers sans limite de fréquence, de durée ou de consommation.',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-8-structure-de-la-base-de-donnes-supabase',
  '8. Structure de la base de données Supabase',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 8. Structure de la base de données Supabase\n'
  '\n'
  'Je recommande de créer un module indépendant nommé `network_scraping_knowledge`.\n'
  '\n'
  '| Table                         | Contenu                                              |\n'
  '| ----------------------------- | ---------------------------------------------------- |\n'
  '| `network_domains`             | VPN, proxy, réseau, scraping, sécurité               |\n'
  '| `network_concepts`            | Définitions et explications techniques               |\n'
  '| `network_protocols`           | HTTP, HTTPS, SOCKS5, TCP, UDP, DNS, TLS              |\n'
  '| `network_vpn_technologies`    | WireGuard, OpenVPN, IPsec, Tor                       |\n'
  '| `network_proxy_types`         | Forward, reverse, HTTP, SOCKS, résidentiel           |\n'
  '| `network_proxy_tools`         | Squid, HAProxy, mitmproxy, NGINX                     |\n'
  '| `network_scraping_frameworks` | Scrapling, Scrapy, Playwright, Selenium              |\n'
  '| `network_scraping_methods`    | CSS, XPath, pagination, crawling                     |\n'
  '| `network_code_examples`       | Exemples Python, JavaScript, Bash                    |\n'
  '| `network_commands`            | Commandes terminal et diagnostic                     |\n'
  '| `network_github_repositories` | Dépôts, licences, langages, liens                    |\n'
  '| `network_documentation`       | Documentation officielle et tutoriels                |\n'
  '| `network_security_rules`      | Règles de sécurité et restrictions                   |\n'
  "| `network_compliance_rules`    | RGPD, conservation, conditions d'accès               |\n"
  '| `network_troubleshooting`     | Erreurs DNS, proxy, TLS, HTTP                        |\n'
  "| `network_workflows`           | Scénarios d'automatisation                           |\n"
  '| `network_scraping_sources`    | Sites, API et flux autorisés                         |\n'
  '| `network_execution_logs`      | Historique des exécutions                            |\n'
  '| `network_data_quality`        | Déduplication, validation et fraîcheur               |\n'
  '| `network_proxy_health`        | Disponibilité, latence et état des proxies autorisés |',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-exemple-de-modle-de-donnes',
  'Exemple de modèle de données',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Exemple de modèle de données\n'
  '\n'
  '```\n'
  '{\n'
  '  "name": "Scrapling",\n'
  '  "category": "web_scraping",\n'
  '  "type": "python_framework",\n'
  '  "description": "Framework de collecte et d\'analyse de pages web.",\n'
  '  "languages": ["Python"],\n'
  '  "capabilities": [\n'
  '    "http_fetching",\n'
  '    "html_parsing",\n'
  '    "browser_automation",\n'
  '    "crawling",\n'
  '    "proxy_support",\n'
  '    "json_export"\n'
  '  ],\n'
  '  "documentation_url": "https://scrapling.readthedocs.io/",\n'
  '  "github_url": "https://github.com/D4Vinci/Scrapling",\n'
  '  "security_level": "controlled",\n'
  '  "requires_authorized_access": true,\n'
  '  "knowledge_status": "documented"\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-relations-recommandes',
  'Relations recommandées',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Relations recommandées\n'
  '\n'
  '- Un concept peut être associé à plusieurs protocoles.\n'
  '- Un framework peut utiliser plusieurs bibliothèques.\n'
  '- Un workflow peut combiner un scraper, un proxy et un système de stockage.\n'
  '- Un exemple de code doit être relié à sa documentation et à ses tests.\n'
  "- Chaque source collectée doit conserver son URL, sa date de récupération et sa méthode d'extraction.\n"
  "- Les secrets d'authentification ne doivent jamais être stockés dans ces tables de connaissances.",
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-9-architecture-construire-pour-stratege-bizapp',
  '9. Architecture à construire pour Stratege BizApp',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 9. Architecture à construire pour Cybbig\n'
  '\n'
  'Assistant IA Stratege\n'
  '\n'
  'Comprend la demande et choisit une méthode de collecte autorisée\n'
  '\n'
  'Planificateur et contrôleur de sécurité\n'
  '\n'
  'Vérifie la source, les autorisations, les limites, le budget et les risques SSRF\n'
  '\n'
  'Collecte web\n'
  '\n'
  'Scrapling, Scrapy, HTTPX\n'
  '\n'
  'Navigation\n'
  '\n'
  'Playwright, Selenium\n'
  '\n'
  'Réseau\n'
  '\n'
  'VPN, DNS, proxies autorisés\n'
  '\n'
  'API et flux\n'
  '\n'
  'REST, RSS, JSON, XML\n'
  '\n'
  'Traitement et contrôle des données\n'
  '\n'
  'Nettoyage, déduplication, validation, filtrage, traçabilité\n'
  '\n'
  'Supabase / PostgreSQL\n'
  '\n'
  'Sources, documents, métadonnées et connaissances indexées pour le RAG\n'
  '\n'
  "Pour l'infrastructure existante de Stratege, je recommande de faire tourner les collecteurs dans des tâches isolées "
  'sur Cloud Run, avec une file de travaux, des limites de ressources et une validation avant insertion dans Supabase. '
  'Le frontend Vercel ne doit pas exécuter directement les crawlers.',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-10-prompt-prt-utiliser-dans-claude-code',
  '10. Prompt prêt à utiliser dans Claude Code',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 10. Prompt prêt à utiliser dans Claude Code\n'
  '\n'
  "Voici le prompt pour demander à Claude Code d'intégrer cette bibliothèque dans le projet existant, sans casser les "
  'fonctionnalités déjà développées.',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-mission-crer-la-bibliothque-network-vpn-proxy-web-scrapi',
  'MISSION — Créer la bibliothèque Network, VPN, Proxy & Web Scraping de Stratege BizApp',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# MISSION — Créer la bibliothèque Network, VPN, Proxy & Web Scraping de Cybbig\n'
  '\n'
  'Tu travailles sur le projet existant **Cybbig**.\n'
  '\n'
  'Stack connue :\n'
  '\n'
  '- Frontend : Vercel / Next.js\n'
  '- Base de données : Supabase / PostgreSQL\n'
  '- Backend : Google Cloud Run\n'
  '- Authentification : Firebase\n'
  '- Dépôt GitHub : `thezedicus/stratege_app`\n'
  '- Branche de travail : `prod-live`',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-1-objectif',
  '1. OBJECTIF',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 1. OBJECTIF\n'
  '\n'
  'Créer une bibliothèque technique complète consacrée à :\n'
  '\n'
  '- Programmation réseau et protocoles Internet.\n'
  '- VPN et confidentialité réseau.\n'
  '- Proxies et reverse proxies.\n'
  '- Web scraping et crawling.\n'
  '- Scrapling et ses fonctionnalités.\n'
  '- Playwright, Selenium et automatisation de navigateurs.\n'
  '- Extraction, nettoyage et traitement de données.\n'
  '- Automatisation des collectes.\n'
  '- Sécurité réseau et conformité.\n'
  '\n'
  "Cette bibliothèque doit alimenter l'assistant IA de Cybbig et lui permettre de répondre aux questions, expliquer "
  'les technologies, comparer les outils, générer des scripts et proposer des workflows adaptés.',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-2-technologies-documenter',
  '2. TECHNOLOGIES À DOCUMENTer',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 2. TECHNOLOGIES À DOCUMENTer',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-vpn',
  'VPN',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### VPN\n'
  '\n'
  'WireGuard, OpenVPN, IPsec, strongSwan, Tailscale, Headscale, Tor.',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-proxy',
  'Proxy',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Proxy\n'
  '\n'
  'HTTP, HTTPS, SOCKS4, SOCKS5, forward proxy, reverse proxy, proxy transparent, proxy authentifié, proxy de '
  'datacenter et proxy résidentiel.\n'
  '\n'
  'Outils : mitmproxy, Squid, HAProxy, NGINX, Caddy, Traefik.',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-web-scraping',
  'Web scraping',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Web scraping\n'
  '\n'
  'Scrapling, Scrapy, BeautifulSoup, lxml, selectolax, Requests, HTTPX, Playwright, Selenium, Trafilatura, feedparser, '
  'pandas et extruct.',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-rseau',
  'Réseau',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Réseau\n'
  '\n'
  'TCP, UDP, DNS, DoH, TLS, HTTP/1.1, HTTP/2, HTTP/3, IPv4, IPv6, WebSocket, cookies, sessions, certificats et '
  'routage.',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-3-contenu-crer',
  '3. CONTENU À CRÉER',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 3. CONTENU À CRÉER\n'
  '\n'
  'Pour chaque technologie, enregistrer :\n'
  '\n'
  '- Nom et description.\n'
  '- Domaine et sous-domaine.\n'
  '- Fonctionnement technique.\n'
  "- Cas d'utilisation.\n"
  '- Avantages et limites.\n'
  '- Langages compatibles.\n'
  "- Commandes d'installation.\n"
  '- Configuration.\n'
  '- Exemples de code fonctionnels.\n'
  '- Documentation officielle.\n'
  '- Dépôt GitHub.\n'
  '- Licence.\n'
  '- Prérequis.\n'
  '- Dépendances.\n'
  '- Risques de sécurité.\n'
  '- Erreurs fréquentes.\n'
  '- Méthodes de diagnostic.\n'
  '- Alternatives.\n'
  '- Tests de validation.\n'
  '\n'
  'Créer des exemples pratiques Python, JavaScript, TypeScript, Bash et PowerShell.\n'
  '\n'
  'Les exemples doivent être testables et accompagnés de leurs dépendances.',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-4-scrapling-module-prioritaire',
  '4. SCRAPLING : MODULE PRIORITAIRE',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 4. SCRAPLING : MODULE PRIORITAIRE\n'
  '\n'
  'Créer une section approfondie consacrée à Scrapling.\n'
  '\n'
  'Documenter :\n'
  '\n'
  '- Installation et configuration.\n'
  '- Fetcher et sessions.\n'
  '- Extraction CSS et XPath.\n'
  '- Gestion des pages JavaScript.\n'
  '- Spiders et crawling.\n'
  '- Pagination.\n'
  '- Sessions persistantes.\n'
  '- Rotation de proxies dans des environnements autorisés.\n'
  '- Export JSON, JSONL, CSV et XML.\n'
  '- Gestion des erreurs.\n'
  '- Gestion des délais et nouvelles tentatives.\n'
  '- Cache et reprise des collectes.\n'
  '- Extraction de contenu pour le RAG.\n'
  '- Intégration MCP avec les agents IA.\n'
  '- Intégration avec les pipelines de données de Stratege.\n'
  '\n'
  'Créer des scripts de démonstration utilisant des sites de test ou des sources explicitement autorisées.\n'
  '\n'
  'Vérifier systématiquement la documentation officielle actuelle avant de générer du code : ne pas inventer de '
  'méthodes ou de paramètres.',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-5-structure-supabase',
  '5. STRUCTURE SUPABASE',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 5. STRUCTURE SUPABASE\n'
  '\n'
  "Examiner d'abord le schéma existant et réutiliser les tables et composants pertinents.\n"
  '\n'
  'Créer si nécessaire :\n'
  '\n'
  '- network_domains\n'
  '- network_concepts\n'
  '- network_protocols\n'
  '- network_vpn_technologies\n'
  '- network_proxy_types\n'
  '- network_proxy_tools\n'
  '- network_scraping_frameworks\n'
  '- network_scraping_methods\n'
  '- network_code_examples\n'
  '- network_commands\n'
  '- network_github_repositories\n'
  '- network_documentation\n'
  '- network_security_rules\n'
  '- network_compliance_rules\n'
  '- network_troubleshooting\n'
  '- network_workflows\n'
  '- network_scraping_sources\n'
  '- network_execution_logs\n'
  '- network_data_quality\n'
  '- network_proxy_health\n'
  '\n'
  'Ajouter :\n'
  '\n'
  '- Identifiants UUID.\n'
  '- Relations et clés étrangères.\n'
  '- Index adaptés.\n'
  '- Dates de création et de mise à jour.\n'
  '- Métadonnées JSONB lorsque nécessaire.\n'
  '- Statut de validation du contenu.\n'
  '- Version de la documentation.\n'
  '- Source et date de vérification.\n'
  '\n'
  'Prévoir les migrations réversibles et les politiques RLS appropriées.\n'
  '\n'
  'Ne pas stocker les mots de passe, tokens, cookies ou identifiants de proxy en clair dans la base de connaissances.',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-6-moteur-de-collecte',
  '6. MOTEUR DE COLLECTE',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 6. MOTEUR DE COLLECTE\n'
  '\n'
  'Créer une architecture indépendante du frontend.\n'
  '\n'
  'Le système doit pouvoir :\n'
  '\n'
  '1. Recevoir une demande de collecte.\n'
  '2. Identifier la source.\n'
  '3. Vérifier que la collecte est autorisée.\n'
  "4. Choisir l'outil adapté.\n"
  "5. Construire un plan d'exécution.\n"
  '6. Exécuter dans un environnement isolé.\n'
  '7. Respecter les limites de fréquence.\n'
  '8. Nettoyer les données.\n'
  '9. Détecter les doublons.\n'
  '10. Valider les résultats.\n'
  '11. Enregistrer les sources.\n'
  '12. Insérer les données approuvées dans Supabase.\n'
  "13. Produire un rapport d'exécution.\n"
  '\n'
  'Prévoir des limites de durée, mémoire, CPU, nombre de pages, taille des réponses et consommation réseau.\n'
  '\n'
  'Les tâches longues doivent être asynchrones et pouvoir être interrompues.',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-7-scurit-obligatoire',
  '7. SÉCURITÉ OBLIGATOIRE',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 7. SÉCURITÉ OBLIGATOIRE\n'
  '\n'
  'Mettre en place :\n'
  '\n'
  '- Validation et normalisation des URL.\n'
  '- Protection SSRF contre localhost, IP privées, link-local et métadonnées cloud.\n'
  '- Contrôle des redirections et des destinations finales.\n'
  '- Blocage des schémas et ports dangereux.\n'
  '- Gestion sécurisée des secrets.\n'
  '- Limites de requêtes et de concurrence.\n'
  '- Timeouts.\n'
  '- Journalisation sans données sensibles.\n'
  '- Validation des fichiers téléchargés.\n'
  '- Protection contre les injections de prompt dans les pages collectées.\n'
  '- Isolation des scripts et des navigateurs.\n'
  '\n'
  'Ne pas développer de fonctionnalités destinées à accéder à des comptes sans autorisation, contourner des contrôles '
  "d'accès, collecter des données privées ou neutraliser les protections d'un site.\n"
  '\n'
  "Ne pas considérer qu'un robots.txt ou un accès techniquement possible constitue à lui seul une autorisation "
  'juridique.',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-8-intgration-avec-l-assistant-ia',
  "8. INTÉGRATION AVEC L'ASSISTANT IA",
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  "## 8. INTÉGRATION AVEC L'ASSISTANT IA\n"
  '\n'
  "L'assistant doit pouvoir :\n"
  '\n'
  '- Expliquer la différence entre VPN et proxy.\n'
  '- Comparer plusieurs technologies.\n'
  '- Recommander une bibliothèque selon un besoin.\n'
  '- Générer des scripts.\n'
  '- Expliquer chaque commande.\n'
  '- Détecter les erreurs.\n'
  '- Proposer une méthode de diagnostic.\n'
  '- Préparer des workflows de collecte.\n'
  '- Identifier les risques.\n'
  '- Produire un rapport de collecte.\n'
  '- Transformer des contenus autorisés en documents exploitables par le RAG.\n'
  '\n'
  "L'IA doit distinguer trois capacités :\n"
  '\n'
  '1. Connaître une technologie.\n'
  '2. Préparer une opération.\n'
  '3. Exécuter une opération avec autorisation et contrôles.\n'
  '\n'
  "Ne jamais prétendre avoir exécuté une opération qui n'a pas réellement été lancée.",
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-9-interface-stratege',
  '9. INTERFACE STRATEGE',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 9. INTERFACE STRATEGE\n'
  '\n'
  "Ajouter une section dans l'interface de gestion de la base de connaissances.\n"
  '\n'
  'Fonctions souhaitées :\n'
  '\n'
  '- Rechercher une technologie.\n'
  '- Filtrer par domaine.\n'
  '- Consulter les commandes.\n'
  '- Lire les exemples de code.\n'
  '- Afficher les documentations.\n'
  '- Comparer les outils.\n'
  '- Consulter les workflows.\n'
  "- Voir l'état des collectes.\n"
  '- Consulter les journaux.\n'
  '- Ajouter, modifier et valider des connaissances.\n'
  '- Tester les exemples dans un environnement sécurisé.\n'
  '\n'
  'Respecter le design existant, la navigation, les couleurs et les composants de Cybbig.',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-10-mthode-de-dveloppement',
  '10. MÉTHODE DE DÉVELOPPEMENT',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 10. MÉTHODE DE DÉVELOPPEMENT\n'
  '\n'
  'Avant toute modification :\n'
  '\n'
  '1. Analyser le dépôt et la branche actuelle.\n'
  "2. Identifier l'architecture réelle.\n"
  '3. Repérer les bibliothèques et composants déjà présents.\n'
  '4. Identifier les tables Supabase existantes.\n'
  '5. Vérifier les fonctions backend.\n'
  '6. Identifier les risques de régression.\n'
  '7. Proposer un plan de développement par étapes.\n'
  '\n'
  'Ensuite :\n'
  '\n'
  '- Développer par petites étapes.\n'
  '- Réutiliser les composants existants.\n'
  '- Éviter les dépendances inutiles.\n'
  '- Préserver les fonctionnalités existantes.\n'
  "- Ajouter des tests unitaires et d'intégration.\n"
  '- Vérifier le build frontend et backend.\n'
  '- Vérifier les migrations et les politiques RLS.\n'
  '- Documenter chaque nouvelle fonction.\n'
  '- Contrôler les coûts et les ressources.\n'
  '\n'
  'Ne jamais supprimer ou remplacer une fonctionnalité existante sans justification et validation.\n'
  '\n'
  'Ne jamais pousser sur GitHub ni déployer en production sans mon autorisation explicite.',
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-11-livrables',
  '11. LIVRABLES',
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 11. LIVRABLES\n'
  '\n'
  'À la fin, fournir :\n'
  '\n'
  '- Architecture mise en place.\n'
  '- Liste des fichiers créés et modifiés.\n'
  '- Tables et migrations créées.\n'
  '- Technologies documentées.\n'
  '- Exemples de code.\n'
  '- Tests effectués et résultats.\n'
  '- Dépendances ajoutées.\n'
  '- Risques restant à traiter.\n'
  '- Coûts potentiels.\n'
  '- Instructions pour tester.\n'
  '- Étapes restantes.\n'
  '\n'
  '**Priorité absolue : une bibliothèque fiable, structurée, sécurisée, évolutive et directement exploitable par '
  "l'assistant IA de Cybbig.**",
  'utilisateur, bibliothèque-6, code, référence'],
 ['6-11-ce-que-cette-bibliothque-permettra-d-ajouter-stratege',
  "11. Ce que cette bibliothèque permettra d'ajouter à Stratege",
  'Code, VPN, proxy et collecte',
  'Source : bibliothèque fournie par l’utilisateur, document 6. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  "## 11. Ce que cette bibliothèque permettra d'ajouter à Stratege\n"
  '\n'
  'Quelques scénarios concrets :\n'
  '\n'
  '- Veille concurrentielle : collecter des informations publiques sur des entreprises, produits et tendances, puis '
  'produire des comparatifs.\n'
  '- Veille tarifaire : suivre des prix publiquement accessibles, lorsque les conditions de collecte le permettent.\n'
  '- Veille sectorielle : surveiller des actualités, publications et flux RSS.\n'
  '- Enrichissement documentaire : transformer des pages autorisées en documents propres pour la base RAG.\n'
  '- Diagnostic technique : aider à comprendre les erreurs de connexion, DNS, proxy et TLS.\n'
  '- Automatisation : programmer des collectes périodiques et envoyer les résultats vers les tableaux de bord '
  'Stratege.\n'
  '\n'
  'Ma recommandation : faire de Scrapling un moteur de collecte parmi plusieurs, et non le moteur unique. Scrapling '
  'sera adapté à de nombreux sites ; Scrapy sera utile pour certains crawlers structurés ; Playwright sera pertinent '
  "pour les interfaces nécessitant un vrai navigateur ; les API officielles resteront prioritaires lorsqu'elles "
  'existent.\n'
  '\n'
  'La prochaine bibliothèque complémentaire logique serait celle des agents IA autonomes, navigateurs intelligents, '
  'MCP, orchestration multi-agents et systèmes de recherche web, afin de relier ces outils à un assistant capable de '
  'planifier et superviser des opérations.',
  'utilisateur, bibliothèque-6, code, référence'],
 ['7-stratege-bizapp-bibliothque-universelle-du-code-et-des-c',
  'STRATEGE BIZAPP — BIBLIOTHÈQUE UNIVERSELLE DU CODE ET DES COMMANDES',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# Cybbig — BIBLIOTHÈQUE UNIVERSELLE DU CODE ET DES COMMANDES',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-1-systmes-d-exploitation-et-terminaux',
  "PARTIE 1 — SYSTÈMES D'EXPLOITATION ET TERMINAUX",
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  "## PARTIE 1 — SYSTÈMES D'EXPLOITATION ET TERMINAUX",
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-1-1-windows-cmd',
  '1.1 — Windows CMD',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 1.1 — Windows CMD\n'
  '\n'
  'Commandes de navigation :\n'
  '\n'
  '```cmd\n'
  'dir\n'
  'cd\n'
  'cd ..\n'
  'cd \\\n'
  'mkdir dossier\n'
  'rmdir dossier\n'
  'tree\n'
  'cls\n'
  '```\n'
  '\n'
  'Fichiers :\n'
  '\n'
  '```cmd\n'
  'type fichier.txt\n'
  'copy fichier.txt sauvegarde.txt\n'
  'move fichier.txt dossier\\\n'
  'ren ancien.txt nouveau.txt\n'
  'del fichier.txt\n'
  '```\n'
  '\n'
  'Système :\n'
  '\n'
  '```cmd\n'
  'systeminfo\n'
  'hostname\n'
  'whoami\n'
  'tasklist\n'
  'tasklist /svc\n'
  'taskkill /PID 1234 /T\n'
  'ipconfig\n'
  'ipconfig /all\n'
  'ipconfig /flushdns\n'
  '```\n'
  '\n'
  'Réseau :\n'
  '\n'
  '```cmd\n'
  'ping example.com\n'
  'tracert example.com\n'
  'nslookup example.com\n'
  'netstat -ano\n'
  'arp -a\n'
  'route print\n'
  '```\n'
  '\n'
  'Disques :\n'
  '\n'
  '```cmd\n'
  'chkdsk\n'
  'diskpart\n'
  'wmic logicaldisk get name,size,freespace\n'
  '```\n'
  '\n'
  'Variables :\n'
  '\n'
  '```cmd\n'
  'set\n'
  'set APP_ENV=development\n'
  'echo %APP_ENV%\n'
  '```\n'
  '\n'
  'Scripts batch :\n'
  '\n'
  '```bat\n'
  '@echo off\n'
  'echo Demarrage du programme\n'
  '\n'
  'set ENVIRONMENT=development\n'
  '\n'
  'if exist "config.json" (\n'
  '    echo Configuration trouvee\n'
  ') else (\n'
  '    echo Configuration absente\n'
  ')\n'
  '\n'
  'pause\n'
  '```\n'
  '\n'
  'Boucle :\n'
  '\n'
  '```bat\n'
  '@echo off\n'
  '\n'
  'for %%F in (*.txt) do (\n'
  '    echo Fichier : %%F\n'
  ')\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-1-2-powershell',
  '1.2 — PowerShell',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 1.2 — PowerShell\n'
  '\n'
  'Navigation :\n'
  '\n'
  '```powershell\n'
  'Get-Location\n'
  'Get-ChildItem\n'
  'Set-Location .\n'
  'New-Item -ItemType Directory -Name "projet"\n'
  'Remove-Item "fichier.txt"\n'
  'Copy-Item "source.txt" "destination.txt"\n'
  'Move-Item "source.txt" ".\\archive\\"\n'
  '```\n'
  '\n'
  'Système :\n'
  '\n'
  '```powershell\n'
  'Get-ComputerInfo\n'
  'Get-Process\n'
  'Get-Service\n'
  'Get-NetIPConfiguration\n'
  'Get-NetTCPConnection\n'
  'Get-Disk\n'
  'Get-Volume\n'
  'Get-EventLog -LogName System -Newest 20\n'
  '```\n'
  '\n'
  'Processus :\n'
  '\n'
  '```powershell\n'
  'Get-Process | Sort-Object CPU -Descending\n'
  'Get-Process | Where-Object {$_.CPU -gt 10}\n'
  '```\n'
  '\n'
  'Fichiers :\n'
  '\n'
  '```powershell\n'
  'Get-Content ".\\data.txt"\n'
  'Set-Content ".\\data.txt" "Contenu"\n'
  'Add-Content ".\\data.txt" "Nouvelle ligne"\n'
  'Test-Path ".\\config.json"\n'
  '```\n'
  '\n'
  'HTTP :\n'
  '\n'
  '```powershell\n'
  'Invoke-WebRequest https://example.com\n'
  'Invoke-RestMethod https://api.github.com\n'
  '```\n'
  '\n'
  'Variables :\n'
  '\n'
  '```powershell\n'
  '$env:APP_ENV = "development"\n'
  '$env:APP_ENV\n'
  '```\n'
  '\n'
  'Script :\n'
  '\n'
  '```powershell\n'
  '$files = Get-ChildItem -File\n'
  '\n'
  'foreach ($file in $files) {\n'
  '    Write-Output $file.Name\n'
  '}\n'
  '```\n'
  '\n'
  'Fonction :\n'
  '\n'
  '```powershell\n'
  'function Get-Greeting {\n'
  '    param([string]$Name)\n'
  '\n'
  '    return "Bonjour $Name"\n'
  '}\n'
  '\n'
  'Get-Greeting -Name "Stratege"\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-1-3-linux-et-macos',
  '1.3 — Linux et macOS',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 1.3 — Linux et macOS\n'
  '\n'
  'Navigation :\n'
  '\n'
  '```bash\n'
  'pwd\n'
  'ls\n'
  'ls -la\n'
  'cd /home\n'
  'cd ..\n'
  'mkdir projet\n'
  'mkdir -p projet/src\n'
  'tree\n'
  'clear\n'
  '```\n'
  '\n'
  'Fichiers :\n'
  '\n'
  '```bash\n'
  'touch fichier.txt\n'
  'cat fichier.txt\n'
  'less fichier.txt\n'
  'head fichier.txt\n'
  'tail fichier.txt\n'
  'tail -f application.log\n'
  'cp source.txt destination.txt\n'
  'mv source.txt destination.txt\n'
  'find . -name "*.py"\n'
  'grep -R "TODO" .\n'
  '```\n'
  '\n'
  'Permissions :\n'
  '\n'
  '```bash\n'
  'ls -l\n'
  'chmod 644 fichier.txt\n'
  'chmod 755 script.sh\n'
  'chown utilisateur:groupe fichier.txt\n'
  '```\n'
  '\n'
  'Processus :\n'
  '\n'
  '```bash\n'
  'ps aux\n'
  'top\n'
  'pgrep python\n'
  'kill -TERM PID\n'
  'jobs\n'
  '```\n'
  '\n'
  'Réseau :\n'
  '\n'
  '```bash\n'
  'ip addr\n'
  'ip route\n'
  'ss -tulpn\n'
  'ping example.com\n'
  'curl -I https://example.com\n'
  'dig example.com\n'
  'traceroute example.com\n'
  '```\n'
  '\n'
  'Disque :\n'
  '\n'
  '```bash\n'
  'df -h\n'
  'du -sh .\n'
  'lsblk\n'
  'free -h\n'
  '```\n'
  '\n'
  'Compression :\n'
  '\n'
  '```bash\n'
  'tar -czf archive.tar.gz dossier/\n'
  'tar -xzf archive.tar.gz\n'
  'zip -r archive.zip dossier/\n'
  'unzip archive.zip\n'
  '```\n'
  '\n'
  'Recherche :\n'
  '\n'
  '```bash\n'
  'grep -n "erreur" application.log\n'
  'find /home -type f -name "*.json"\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-1-4-bash-scripting',
  '1.4 — Bash scripting',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 1.4 — Bash scripting\n'
  '\n'
  '```bash\n'
  '#!/usr/bin/env bash\n'
  '\n'
  'set -euo pipefail\n'
  '\n'
  'APP_NAME="Stratege"\n'
  'ENVIRONMENT="${APP_ENV:-development}"\n'
  '\n'
  'echo "Application : $APP_NAME"\n'
  'echo "Environnement : $ENVIRONMENT"\n'
  '```\n'
  '\n'
  'Conditions :\n'
  '\n'
  '```bash\n'
  'if [ -f "config.json" ]; then\n'
  '    echo "Configuration disponible"\n'
  'else\n'
  '    echo "Configuration manquante"\n'
  'fi\n'
  '```\n'
  '\n'
  'Boucle :\n'
  '\n'
  '```bash\n'
  'for file in *.txt; do\n'
  '    [ -e "$file" ] || continue\n'
  '    echo "$file"\n'
  'done\n'
  '```\n'
  '\n'
  'Fonction :\n'
  '\n'
  '```bash\n'
  'function greet() {\n'
  '    local name="$1"\n'
  '    echo "Bonjour $name"\n'
  '}\n'
  '\n'
  'greet "Stratege"\n'
  '```\n'
  '\n'
  'Arguments :\n'
  '\n'
  '```bash\n'
  '#!/usr/bin/env bash\n'
  '\n'
  'NAME="${1:-Utilisateur}"\n'
  '\n'
  'echo "Bienvenue $NAME"\n'
  '```\n'
  '\n'
  'Gestion des erreurs :\n'
  '\n'
  '```bash\n'
  'if ! command -v python3 >/dev/null 2>&1; then\n'
  '    echo "Python est absent"\n'
  '    exit 1\n'
  'fi\n'
  '```\n'
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-2-python-langage-commandes-et-bibliothques',
  'PARTIE 2 — PYTHON : LANGAGE, COMMANDES ET BIBLIOTHÈQUES',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 2 — PYTHON : LANGAGE, COMMANDES ET BIBLIOTHÈQUES',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-2-1-installation-et-environnement',
  '2.1 — Installation et environnement',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 2.1 — Installation et environnement\n'
  '\n'
  '```bash\n'
  'python --version\n'
  'python -m pip --version\n'
  'python -m venv .venv\n'
  '```\n'
  '\n'
  'Activation Windows :\n'
  '\n'
  '```powershell\n'
  '.venv\\Scripts\\Activate.ps1\n'
  '```\n'
  '\n'
  'Activation Linux/macOS :\n'
  '\n'
  '```bash\n'
  'source .venv/bin/activate\n'
  '```\n'
  '\n'
  'Installation :\n'
  '\n'
  '```bash\n'
  'python -m pip install requests\n'
  'python -m pip install httpx\n'
  'python -m pip install pandas\n'
  'python -m pip install numpy\n'
  'python -m pip install fastapi\n'
  'python -m pip install pytest\n'
  'python -m pip install beautifulsoup4\n'
  '```\n'
  '\n'
  'Gestion :\n'
  '\n'
  '```bash\n'
  'python -m pip list\n'
  'python -m pip freeze\n'
  'python -m pip show requests\n'
  'python -m pip uninstall requests\n'
  'python -m pip install --upgrade requests\n'
  'python -m pip freeze > requirements.txt\n'
  'python -m pip install -r requirements.txt\n'
  '```\n'
  '\n'
  'Exécution :\n'
  '\n'
  '```bash\n'
  'python main.py\n'
  'python -m module\n'
  'python -c "print(\'Hello World\')"\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-2-2-syntaxe-fondamentale',
  '2.2 — Syntaxe fondamentale',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 2.2 — Syntaxe fondamentale\n'
  '\n'
  'Variables :\n'
  '\n'
  '```python\n'
  'name = "Stratege"\n'
  'age = 5\n'
  'price = 19.99\n'
  'active = True\n'
  'items = None\n'
  '```\n'
  '\n'
  'Types :\n'
  '\n'
  '```python\n'
  'type(name)\n'
  'isinstance(age, int)\n'
  'str(age)\n'
  'int("25")\n'
  'float("19.99")\n'
  'bool(1)\n'
  '```\n'
  '\n'
  'Conditions :\n'
  '\n'
  '```python\n'
  'if price > 100:\n'
  '    print("Prix élevé")\n'
  'elif price > 50:\n'
  '    print("Prix moyen")\n'
  'else:\n'
  '    print("Prix accessible")\n'
  '```\n'
  '\n'
  'Boucles :\n'
  '\n'
  '```python\n'
  'for i in range(10):\n'
  '    print(i)\n'
  '\n'
  'while True:\n'
  '    break\n'
  '```\n'
  '\n'
  'Listes :\n'
  '\n'
  '```python\n'
  'items = ["Python", "JavaScript", "PHP"]\n'
  '\n'
  'items.append("Java")\n'
  'items.remove("PHP")\n'
  '\n'
  'print(items[0])\n'
  'print(len(items))\n'
  '```\n'
  '\n'
  'Dictionnaires :\n'
  '\n'
  '```python\n'
  'user = {\n'
  '    "name": "Utilisateur",\n'
  '    "role": "admin",\n'
  '    "active": True\n'
  '}\n'
  '\n'
  'print(user["name"])\n'
  'user["role"] = "editor"\n'
  '```\n'
  '\n'
  'Fonctions :\n'
  '\n'
  '```python\n'
  'def calculate_total(price, quantity):\n'
  '    return price * quantity\n'
  '\n'
  'total = calculate_total(25, 4)\n'
  'print(total)\n'
  '```\n'
  '\n'
  'Fonctions avancées :\n'
  '\n'
  '```python\n'
  'def greet(name: str) -> str:\n'
  '    return f"Bonjour {name}"\n'
  '\n'
  'def calculate_tax(price: float, rate: float = 0.20) -> float:\n'
  '    return price * rate\n'
  '```\n'
  '\n'
  'Classes :\n'
  '\n'
  '```python\n'
  'class Product:\n'
  '    def __init__(self, name, price):\n'
  '        self.name = name\n'
  '        self.price = price\n'
  '\n'
  '    def display(self):\n'
  '        return f"{self.name}: {self.price} €"\n'
  '\n'
  'product = Product("Livre", 20)\n'
  'print(product.display())\n'
  '```\n'
  '\n'
  'Exceptions :\n'
  '\n'
  '```python\n'
  'try:\n'
  '    result = 10 / 0\n'
  'except ZeroDivisionError as error:\n'
  '    print(error)\n'
  'finally:\n'
  '    print("Fin du traitement")\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-2-3-manipulation-des-fichiers',
  '2.3 — Manipulation des fichiers',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 2.3 — Manipulation des fichiers\n'
  '\n'
  '```python\n'
  'from pathlib import Path\n'
  '\n'
  'path = Path("data.txt")\n'
  '\n'
  'path.write_text("Bonjour Stratege", encoding="utf-8")\n'
  '\n'
  'content = path.read_text(encoding="utf-8")\n'
  '\n'
  'print(content)\n'
  '```\n'
  '\n'
  'JSON :\n'
  '\n'
  '```python\n'
  'import json\n'
  '\n'
  'data = {\n'
  '    "name": "Stratege",\n'
  '    "version": 1\n'
  '}\n'
  '\n'
  'with open("data.json", "w", encoding="utf-8") as file:\n'
  '    json.dump(data, file, indent=4)\n'
  '\n'
  'with open("data.json", encoding="utf-8") as file:\n'
  '    result = json.load(file)\n'
  '```\n'
  '\n'
  'CSV :\n'
  '\n'
  '```python\n'
  'import csv\n'
  '\n'
  'with open("data.csv", "w", newline="", encoding="utf-8") as file:\n'
  '    writer = csv.writer(file)\n'
  '    writer.writerow(["nom", "prix"])\n'
  '    writer.writerow(["Produit A", 20])\n'
  '```\n'
  '\n'
  'XML :\n'
  '\n'
  '```python\n'
  'import xml.etree.ElementTree as ET\n'
  '\n'
  'root = ET.Element("products")\n'
  '\n'
  'product = ET.SubElement(root, "product")\n'
  'product.text = "Produit A"\n'
  '\n'
  'tree = ET.ElementTree(root)\n'
  'tree.write("products.xml", encoding="utf-8", xml_declaration=True)\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-2-4-http-et-api',
  '2.4 — HTTP et API',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 2.4 — HTTP et API\n'
  '\n'
  '```python\n'
  'import requests\n'
  '\n'
  'response = requests.get(\n'
  '    "https://api.github.com",\n'
  '    timeout=10\n'
  ')\n'
  '\n'
  'print(response.status_code)\n'
  'print(response.json())\n'
  '```\n'
  '\n'
  'POST :\n'
  '\n'
  '```python\n'
  'import requests\n'
  '\n'
  'payload = {\n'
  '    "name": "Stratege",\n'
  '    "active": True\n'
  '}\n'
  '\n'
  'response = requests.post(\n'
  '    "https://httpbin.org/post",\n'
  '    json=payload,\n'
  '    timeout=10\n'
  ')\n'
  '\n'
  'print(response.status_code)\n'
  '```\n'
  '\n'
  'HTTPX asynchrone :\n'
  '\n'
  '```python\n'
  'import asyncio\n'
  'import httpx\n'
  '\n'
  'async def main():\n'
  '    async with httpx.AsyncClient(timeout=10) as client:\n'
  '        response = await client.get("https://example.com")\n'
  '        print(response.status_code)\n'
  '\n'
  'asyncio.run(main())\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-2-5-bibliothques-python-documenter',
  '2.5 — Bibliothèques Python à documenter',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 2.5 — Bibliothèques Python à documenter\n'
  '\n'
  'Système :\n'
  '- os\n'
  '- sys\n'
  '- pathlib\n'
  '- shutil\n'
  '- subprocess\n'
  '- platform\n'
  '- psutil\n'
  '\n'
  'Données :\n'
  '- pandas\n'
  '- numpy\n'
  '- polars\n'
  '- scipy\n'
  '- openpyxl\n'
  '- pyarrow\n'
  '\n'
  'Web :\n'
  '- requests\n'
  '- httpx\n'
  '- aiohttp\n'
  '- beautifulsoup4\n'
  '- scrapy\n'
  '- scrapling\n'
  '- trafilatura\n'
  '- playwright\n'
  '\n'
  'Backend :\n'
  '- fastapi\n'
  '- flask\n'
  '- django\n'
  '- pydantic\n'
  '- sqlalchemy\n'
  '- alembic\n'
  '\n'
  'IA :\n'
  '- transformers\n'
  '- torch\n'
  '- sentence-transformers\n'
  '- scikit-learn\n'
  '- langchain\n'
  '- llama-index\n'
  '- litellm\n'
  '\n'
  'Automatisation :\n'
  '- celery\n'
  '- prefect\n'
  '- apscheduler\n'
  '- playwright\n'
  '- pyautogui\n'
  '- paramiko\n'
  '\n'
  'Tests :\n'
  '- pytest\n'
  '- unittest\n'
  '- hypothesis\n'
  '- coverage\n'
  '- ruff\n'
  '- mypy\n'
  '\n'
  'Sécurité défensive :\n'
  '- cryptography\n'
  '- bcrypt\n'
  '- argon2-cffi\n'
  '- bandit\n'
  '- pip-audit',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-2-6-traitement-des-donnes',
  '2.6 — Traitement des données',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 2.6 — Traitement des données\n'
  '\n'
  '```python\n'
  'import pandas as pd\n'
  '\n'
  'df = pd.read_csv("data.csv")\n'
  '\n'
  'print(df.head())\n'
  'print(df.info())\n'
  'print(df.describe())\n'
  '\n'
  'df = df.drop_duplicates()\n'
  '\n'
  'df.to_csv("result.csv", index=False)\n'
  '```\n'
  '\n'
  'NumPy :\n'
  '\n'
  '```python\n'
  'import numpy as np\n'
  '\n'
  'values = np.array([10, 20, 30, 40])\n'
  '\n'
  'print(np.mean(values))\n'
  'print(np.sum(values))\n'
  'print(np.max(values))\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-2-7-programmation-concurrente',
  '2.7 — Programmation concurrente',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 2.7 — Programmation concurrente\n'
  '\n'
  'Threads :\n'
  '\n'
  '```python\n'
  'from concurrent.futures import ThreadPoolExecutor\n'
  '\n'
  'def process(value):\n'
  '    return value * 2\n'
  '\n'
  'with ThreadPoolExecutor(max_workers=4) as executor:\n'
  '    results = list(executor.map(process, range(10)))\n'
  '\n'
  'print(results)\n'
  '```\n'
  '\n'
  'Multiprocessing :\n'
  '\n'
  '```python\n'
  'from multiprocessing import Pool\n'
  '\n'
  'def square(number):\n'
  '    return number ** 2\n'
  '\n'
  'if __name__ == "__main__":\n'
  '    with Pool(4) as pool:\n'
  '        print(pool.map(square, range(10)))\n'
  '```\n'
  '\n'
  'Asyncio :\n'
  '\n'
  '```python\n'
  'import asyncio\n'
  '\n'
  'async def task(name):\n'
  '    await asyncio.sleep(1)\n'
  '    return f"Terminé : {name}"\n'
  '\n'
  'async def main():\n'
  '    results = await asyncio.gather(\n'
  '        task("A"),\n'
  '        task("B"),\n'
  '        task("C")\n'
  '    )\n'
  '    print(results)\n'
  '\n'
  'asyncio.run(main())\n'
  '```\n'
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-3-javascript-et-typescript',
  'PARTIE 3 — JAVASCRIPT ET TYPESCRIPT',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 3 — JAVASCRIPT ET TYPESCRIPT',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-3-1-node-js-et-npm',
  '3.1 — Node.js et npm',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 3.1 — Node.js et npm\n'
  '\n'
  '```bash\n'
  'node --version\n'
  'npm --version\n'
  'npm init -y\n'
  'npm install\n'
  'npm install express\n'
  'npm install axios\n'
  'npm install dotenv\n'
  'npm install -D typescript\n'
  'npm install -D eslint\n'
  'npm install -D prettier\n'
  'npm list\n'
  'npm outdated\n'
  'npm update\n'
  'npm uninstall axios\n'
  'npm run dev\n'
  'npm run build\n'
  'npm test\n'
  '```\n'
  '\n'
  'Exécution :\n'
  '\n'
  '```bash\n'
  'node index.js\n'
  'node --watch index.js\n'
  'npx tsc --init\n'
  'npx tsc\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-3-2-javascript',
  '3.2 — JavaScript',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 3.2 — JavaScript\n'
  '\n'
  '```javascript\n'
  'const name = "Stratege";\n'
  'let count = 10;\n'
  '\n'
  'function add(a, b) {\n'
  '    return a + b;\n'
  '}\n'
  '\n'
  'const multiply = (a, b) => a * b;\n'
  '\n'
  'console.log(add(5, 10));\n'
  '```\n'
  '\n'
  'Tableaux :\n'
  '\n'
  '```javascript\n'
  'const numbers = [1, 2, 3, 4];\n'
  '\n'
  'const doubled = numbers.map(n => n * 2);\n'
  'const filtered = numbers.filter(n => n > 2);\n'
  'const total = numbers.reduce((a, b) => a + b, 0);\n'
  '```\n'
  '\n'
  'Objets :\n'
  '\n'
  '```javascript\n'
  'const user = {\n'
  '    name: "Utilisateur",\n'
  '    role: "admin",\n'
  '    active: true\n'
  '};\n'
  '\n'
  'console.log(user.name);\n'
  '```\n'
  '\n'
  'Async :\n'
  '\n'
  '```javascript\n'
  'async function fetchData() {\n'
  '    const response = await fetch("https://api.github.com");\n'
  '\n'
  '    if (!response.ok) {\n'
  '        throw new Error(`HTTP ${response.status}`);\n'
  '    }\n'
  '\n'
  '    return response.json();\n'
  '}\n'
  '```\n'
  '\n'
  "Gestion d'erreurs :\n"
  '\n'
  '```javascript\n'
  'try {\n'
  '    const result = await fetchData();\n'
  '    console.log(result);\n'
  '} catch (error) {\n'
  '    console.error(error);\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-3-3-typescript',
  '3.3 — TypeScript',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 3.3 — TypeScript\n'
  '\n'
  '```typescript\n'
  'type User = {\n'
  '    id: string;\n'
  '    name: string;\n'
  '    active: boolean;\n'
  '};\n'
  '\n'
  'function greet(user: User): string {\n'
  '    return `Bonjour ${user.name}`;\n'
  '}\n'
  '```\n'
  '\n'
  'Génériques :\n'
  '\n'
  '```typescript\n'
  'function identity<T>(value: T): T {\n'
  '    return value;\n'
  '}\n'
  '\n'
  'const result = identity<string>("Stratege");\n'
  '```\n'
  '\n'
  'Interfaces :\n'
  '\n'
  '```typescript\n'
  'interface Product {\n'
  '    id: number;\n'
  '    name: string;\n'
  '    price: number;\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-3-4-manipulation-des-fichiers',
  '3.4 — Manipulation des fichiers',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 3.4 — Manipulation des fichiers\n'
  '\n'
  '```javascript\n'
  'import fs from "node:fs/promises";\n'
  '\n'
  'await fs.writeFile("data.txt", "Cybbig");\n'
  '\n'
  'const content = await fs.readFile("data.txt", "utf8");\n'
  '\n'
  'console.log(content);\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-3-5-serveur-express',
  '3.5 — Serveur Express',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 3.5 — Serveur Express\n'
  '\n'
  '```javascript\n'
  'import express from "express";\n'
  '\n'
  'const app = express();\n'
  '\n'
  'app.use(express.json());\n'
  '\n'
  'app.get("/health", (req, res) => {\n'
  '    res.json({ status: "ok" });\n'
  '});\n'
  '\n'
  'app.post("/api/data", (req, res) => {\n'
  '    res.json({\n'
  '        received: true,\n'
  '        data: req.body\n'
  '    });\n'
  '});\n'
  '\n'
  'app.listen(3000);\n'
  '```\n'
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-4-html-css-et-frontend',
  'PARTIE 4 — HTML, CSS ET FRONTEND',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 4 — HTML, CSS ET FRONTEND',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-4-1-html',
  '4.1 — HTML',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 4.1 — HTML\n'
  '\n'
  '```html\n'
  '<!DOCTYPE html>\n'
  '<html lang="fr">\n'
  '<head>\n'
  '    <meta charset="UTF-8">\n'
  '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
  '    <title>Stratege</title>\n'
  '</head>\n'
  '<body>\n'
  '    <header>\n'
  '        <h1>Cybbig</h1>\n'
  '    </header>\n'
  '\n'
  '    <main>\n'
  '        <section>\n'
  "            <h2>Gestion d'entreprise</h2>\n"
  '            <p>Bienvenue.</p>\n'
  '        </section>\n'
  '    </main>\n'
  '</body>\n'
  '</html>\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-4-2-css',
  '4.2 — CSS',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 4.2 — CSS\n'
  '\n'
  '```css\n'
  ':root {\n'
  '    --primary: #1e3a8a;\n'
  '    --secondary: #f97316;\n'
  '    --surface: #ffffff;\n'
  '}\n'
  '\n'
  'body {\n'
  '    margin: 0;\n'
  '    font-family: Arial, sans-serif;\n'
  '    background: var(--surface);\n'
  '}\n'
  '\n'
  '.card {\n'
  '    padding: 24px;\n'
  '    border-radius: 16px;\n'
  '    transition: transform 0.2s ease;\n'
  '}\n'
  '\n'
  '.card:hover {\n'
  '    transform: translateY(-4px);\n'
  '}\n'
  '```\n'
  '\n'
  'Flexbox :\n'
  '\n'
  '```css\n'
  '.container {\n'
  '    display: flex;\n'
  '    align-items: center;\n'
  '    justify-content: space-between;\n'
  '    gap: 20px;\n'
  '}\n'
  '```\n'
  '\n'
  'Grid :\n'
  '\n'
  '```css\n'
  '.grid {\n'
  '    display: grid;\n'
  '    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));\n'
  '    gap: 20px;\n'
  '}\n'
  '```\n'
  '\n'
  'Animations :\n'
  '\n'
  '```css\n'
  '@keyframes fadeIn {\n'
  '    from {\n'
  '        opacity: 0;\n'
  '        transform: translateY(15px);\n'
  '    }\n'
  '\n'
  '    to {\n'
  '        opacity: 1;\n'
  '        transform: translateY(0);\n'
  '    }\n'
  '}\n'
  '\n'
  '.fade-in {\n'
  '    animation: fadeIn 0.5s ease forwards;\n'
  '}\n'
  '```\n'
  '\n'
  'Responsive :\n'
  '\n'
  '```css\n'
  '@media (max-width: 768px) {\n'
  '    .container {\n'
  '        flex-direction: column;\n'
  '    }\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-4-3-dom-javascript',
  '4.3 — DOM JavaScript',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 4.3 — DOM JavaScript\n'
  '\n'
  '```javascript\n'
  'const button = document.querySelector("#button");\n'
  '\n'
  'button?.addEventListener("click", () => {\n'
  '    console.log("Action exécutée");\n'
  '});\n'
  '```\n'
  '\n'
  "Création d'éléments :\n"
  '\n'
  '```javascript\n'
  'const element = document.createElement("div");\n'
  '\n'
  'element.textContent = "Bonjour";\n'
  'document.body.appendChild(element);\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-4-4-react',
  '4.4 — React',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 4.4 — React\n'
  '\n'
  '```jsx\n'
  'function Counter() {\n'
  '    const [count, setCount] = React.useState(0);\n'
  '\n'
  '    return (\n'
  '        <button onClick={() => setCount(count + 1)}>\n'
  '            Compteur : {count}\n'
  '        </button>\n'
  '    );\n'
  '}\n'
  '```\n'
  '\n'
  'Effets :\n'
  '\n'
  '```jsx\n'
  'React.useEffect(() => {\n'
  '    document.title = "Cybbig";\n'
  '}, []);\n'
  '```\n'
  '\n'
  'Formulaire :\n'
  '\n'
  '```jsx\n'
  'function ContactForm() {\n'
  '    const [email, setEmail] = React.useState("");\n'
  '\n'
  '    function submit(event) {\n'
  '        event.preventDefault();\n'
  '        console.log(email);\n'
  '    }\n'
  '\n'
  '    return (\n'
  '        <form onSubmit={submit}>\n'
  '            <input\n'
  '                value={email}\n'
  '                onChange={event => setEmail(event.target.value)}\n'
  '            />\n'
  '            <button type="submit">Envoyer</button>\n'
  '        </form>\n'
  '    );\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-4-5-next-js',
  '4.5 — Next.js',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 4.5 — Next.js\n'
  '\n'
  '```bash\n'
  'npx create-next-app@latest stratege\n'
  'cd stratege\n'
  'npm run dev\n'
  'npm run build\n'
  'npm run start\n'
  '```\n'
  '\n'
  'Exemple de page :\n'
  '\n'
  '```tsx\n'
  'export default function Home() {\n'
  '    return (\n'
  '        <main>\n'
  '            <h1>Cybbig</h1>\n'
  '        </main>\n'
  '    );\n'
  '}\n'
  '```\n'
  '\n'
  'Route API :\n'
  '\n'
  '```typescript\n'
  'import { NextResponse } from "next/server";\n'
  '\n'
  'export async function GET() {\n'
  '    return NextResponse.json({\n'
  '        status: "ok"\n'
  '    });\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-4-6-bibliothques-frontend-intgrer',
  '4.6 — Bibliothèques frontend à intégrer',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 4.6 — Bibliothèques frontend à intégrer\n'
  '\n'
  '- React\n'
  '- Next.js\n'
  '- Vue.js\n'
  '- Nuxt\n'
  '- Angular\n'
  '- Svelte\n'
  '- SvelteKit\n'
  '- Astro\n'
  '- Tailwind CSS\n'
  '- Bootstrap\n'
  '- shadcn/ui\n'
  '- Radix UI\n'
  '- Framer Motion\n'
  '- Motion\n'
  '- GSAP\n'
  '- Three.js\n'
  '- D3.js\n'
  '- Chart.js\n'
  '- Recharts\n'
  '- TanStack Query\n'
  '- Zustand\n'
  '- Redux Toolkit\n'
  '- Zod\n'
  '- React Hook Form\n'
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-5-php-java-c-c-c-go-et-rust',
  'PARTIE 5 — PHP, JAVA, C#, C, C++, GO ET RUST',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 5 — PHP, JAVA, C#, C, C++, GO ET RUST',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-5-1-php',
  '5.1 — PHP',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 5.1 — PHP\n'
  '\n'
  '```bash\n'
  'php --version\n'
  'php -m\n'
  'php -S localhost:8000\n'
  'composer init\n'
  'composer install\n'
  'composer require monolog/monolog\n'
  'composer update\n'
  '```\n'
  '\n'
  'Code :\n'
  '\n'
  '```php\n'
  '<?php\n'
  '\n'
  '$name = "Stratege";\n'
  '\n'
  'function greet(string $name): string {\n'
  '    return "Bonjour " . $name;\n'
  '}\n'
  '\n'
  'echo greet($name);\n'
  '```\n'
  '\n'
  'Tableaux :\n'
  '\n'
  '```php\n'
  '$products = [\n'
  '    ["name" => "Produit A", "price" => 20],\n'
  '    ["name" => "Produit B", "price" => 30]\n'
  '];\n'
  '\n'
  'foreach ($products as $product) {\n'
  '    echo $product["name"];\n'
  '}\n'
  '```\n'
  '\n'
  'API :\n'
  '\n'
  '```php\n'
  '<?php\n'
  '\n'
  'header("Content-Type: application/json");\n'
  '\n'
  'echo json_encode([\n'
  '    "status" => "ok"\n'
  ']);\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-5-2-java',
  '5.2 — Java',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 5.2 — Java\n'
  '\n'
  '```bash\n'
  'java --version\n'
  'javac Main.java\n'
  'java Main\n'
  '```\n'
  '\n'
  '```java\n'
  'public class Main {\n'
  '    public static void main(String[] args) {\n'
  '        System.out.println("Cybbig");\n'
  '    }\n'
  '}\n'
  '```\n'
  '\n'
  'Classe :\n'
  '\n'
  '```java\n'
  'class Product {\n'
  '    String name;\n'
  '    double price;\n'
  '\n'
  '    Product(String name, double price) {\n'
  '        this.name = name;\n'
  '        this.price = price;\n'
  '    }\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-5-3-c',
  '5.3 — C',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 5.3 — C\n'
  '\n'
  '```bash\n'
  'gcc main.c -o main\n'
  './main\n'
  '```\n'
  '\n'
  '```c\n'
  '#include <stdio.h>\n'
  '\n'
  'int main() {\n'
  '    printf("Cybbig\\n");\n'
  '    return 0;\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-5-4-c',
  '5.4 — C++',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 5.4 — C++\n'
  '\n'
  '```bash\n'
  'g++ main.cpp -o main\n'
  './main\n'
  '```\n'
  '\n'
  '```cpp\n'
  '#include <iostream>\n'
  '#include <string>\n'
  '\n'
  'int main() {\n'
  '    std::string name = "Stratege";\n'
  '    std::cout << name << std::endl;\n'
  '    return 0;\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-5-5-c',
  '5.5 — C',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 5.5 — C#\n'
  '\n'
  '```bash\n'
  'dotnet --version\n'
  'dotnet new console\n'
  'dotnet run\n'
  'dotnet build\n'
  'dotnet test\n'
  '```\n'
  '\n'
  '```csharp\n'
  'using System;\n'
  '\n'
  'class Program {\n'
  '    static void Main() {\n'
  '        Console.WriteLine("Cybbig");\n'
  '    }\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-5-6-go',
  '5.6 — Go',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 5.6 — Go\n'
  '\n'
  '```bash\n'
  'go version\n'
  'go mod init stratege\n'
  'go run .\n'
  'go build\n'
  'go test ./...\n'
  'go fmt ./...\n'
  'go vet ./...\n'
  '```\n'
  '\n'
  '```go\n'
  'package main\n'
  '\n'
  'import "fmt"\n'
  '\n'
  'func main() {\n'
  '    fmt.Println("Cybbig")\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-5-7-rust',
  '5.7 — Rust',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 5.7 — Rust\n'
  '\n'
  '```bash\n'
  'rustc --version\n'
  'cargo new stratege\n'
  'cargo run\n'
  'cargo build\n'
  'cargo test\n'
  'cargo fmt\n'
  'cargo clippy\n'
  '```\n'
  '\n'
  '```rust\n'
  'fn main() {\n'
  '    let name = "Stratege";\n'
  '    println!("{}", name);\n'
  '}\n'
  '```\n'
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-6-sql-et-bases-de-donnes',
  'PARTIE 6 — SQL ET BASES DE DONNÉES',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 6 — SQL ET BASES DE DONNÉES',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-6-1-sql-gnral',
  '6.1 — SQL général',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 6.1 — SQL général\n'
  '\n'
  'Création :\n'
  '\n'
  '```sql\n'
  'CREATE TABLE products (\n'
  '    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,\n'
  '    name TEXT NOT NULL,\n'
  '    price NUMERIC(10,2) NOT NULL,\n'
  '    created_at TIMESTAMPTZ DEFAULT NOW()\n'
  ');\n'
  '```\n'
  '\n'
  'Insertion :\n'
  '\n'
  '```sql\n'
  'INSERT INTO products (name, price)\n'
  "VALUES ('Produit A', 19.99);\n"
  '```\n'
  '\n'
  'Lecture :\n'
  '\n'
  '```sql\n'
  'SELECT * FROM products;\n'
  '\n'
  'SELECT name, price\n'
  'FROM products\n'
  'WHERE price > 10\n'
  'ORDER BY price DESC;\n'
  '```\n'
  '\n'
  'Modification :\n'
  '\n'
  '```sql\n'
  'UPDATE products\n'
  'SET price = 24.99\n'
  "WHERE name = 'Produit A';\n"
  '```\n'
  '\n'
  'Suppression :\n'
  '\n'
  '```sql\n'
  'DELETE FROM products\n'
  'WHERE id = 10;\n'
  '```\n'
  '\n'
  'Agrégation :\n'
  '\n'
  '```sql\n'
  'SELECT\n'
  '    COUNT(*) AS total,\n'
  '    AVG(price) AS average_price,\n'
  '    MIN(price) AS minimum_price,\n'
  '    MAX(price) AS maximum_price\n'
  'FROM products;\n'
  '```\n'
  '\n'
  'Jointure :\n'
  '\n'
  '```sql\n'
  'SELECT\n'
  '    orders.id,\n'
  '    customers.name\n'
  'FROM orders\n'
  'JOIN customers\n'
  '    ON orders.customer_id = customers.id;\n'
  '```\n'
  '\n'
  'Index :\n'
  '\n'
  '```sql\n'
  'CREATE INDEX idx_products_name\n'
  'ON products(name);\n'
  '```\n'
  '\n'
  'Transaction :\n'
  '\n'
  '```sql\n'
  'BEGIN;\n'
  '\n'
  'UPDATE accounts\n'
  'SET balance = balance - 100\n'
  'WHERE id = 1;\n'
  '\n'
  'UPDATE accounts\n'
  'SET balance = balance + 100\n'
  'WHERE id = 2;\n'
  '\n'
  'COMMIT;\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-6-2-postgresql',
  '6.2 — PostgreSQL',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 6.2 — PostgreSQL\n'
  '\n'
  '```bash\n'
  'psql --version\n'
  'psql -h localhost -U postgres -d database\n'
  '```\n'
  '\n'
  'Dans psql :\n'
  '\n'
  '```sql\n'
  '\\l\n'
  '\\c database\n'
  '\\dt\n'
  '\\d products\n'
  '\\du\n'
  '\\conninfo\n'
  '```\n'
  '\n'
  'Export :\n'
  '\n'
  '```bash\n'
  'pg_dump -h localhost -U postgres database > backup.sql\n'
  '```\n'
  '\n'
  'Restauration :\n'
  '\n'
  '```bash\n'
  'psql -h localhost -U postgres database < backup.sql\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-6-3-supabase',
  '6.3 — Supabase',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 6.3 — Supabase\n'
  '\n'
  'Installation :\n'
  '\n'
  '```bash\n'
  'npm install @supabase/supabase-js\n'
  '```\n'
  '\n'
  'Client :\n'
  '\n'
  '```typescript\n'
  'import { createClient } from "@supabase/supabase-js";\n'
  '\n'
  'const supabase = createClient(\n'
  '    process.env.NEXT_PUBLIC_SUPABASE_URL!,\n'
  '    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!\n'
  ');\n'
  '```\n'
  '\n'
  'Lecture :\n'
  '\n'
  '```typescript\n'
  'const { data, error } = await supabase\n'
  '    .from("products")\n'
  '    .select("*")\n'
  '    .limit(50);\n'
  '```\n'
  '\n'
  'Insertion :\n'
  '\n'
  '```typescript\n'
  'const { data, error } = await supabase\n'
  '    .from("products")\n'
  '    .insert({\n'
  '        name: "Produit A",\n'
  '        price: 25\n'
  '    })\n'
  '    .select();\n'
  '```\n'
  '\n'
  'Modification :\n'
  '\n'
  '```typescript\n'
  'const { error } = await supabase\n'
  '    .from("products")\n'
  '    .update({ price: 30 })\n'
  '    .eq("id", 1);\n'
  '```\n'
  '\n'
  'Authentification :\n'
  '\n'
  '```typescript\n'
  'const { data, error } = await supabase.auth.signInWithPassword({\n'
  '    email: "user@example.com",\n'
  '    password: "password"\n'
  '});\n'
  '```\n'
  '\n'
  'Ne jamais exposer une clé `service_role` dans le navigateur.',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-6-4-mongodb',
  '6.4 — MongoDB',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 6.4 — MongoDB\n'
  '\n'
  '```bash\n'
  'mongosh\n'
  '```\n'
  '\n'
  '```javascript\n'
  'db.createCollection("products");\n'
  '\n'
  'db.products.insertOne({\n'
  '    name: "Produit A",\n'
  '    price: 20\n'
  '});\n'
  '\n'
  'db.products.find();\n'
  '\n'
  'db.products.find({\n'
  '    price: { $gt: 10 }\n'
  '});\n'
  '\n'
  'db.products.updateOne(\n'
  '    { name: "Produit A" },\n'
  '    { $set: { price: 25 } }\n'
  ');\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-6-5-redis',
  '6.5 — Redis',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 6.5 — Redis\n'
  '\n'
  '```bash\n'
  'redis-cli\n'
  '```\n'
  '\n'
  '```redis\n'
  'PING\n'
  'SET app_name Stratege\n'
  'GET app_name\n'
  'EXISTS app_name\n'
  'DEL app_name\n'
  'KEYS *\n'
  'INFO\n'
  'DBSIZE\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-6-6-sqlite',
  '6.6 — SQLite',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 6.6 — SQLite\n'
  '\n'
  '```bash\n'
  'sqlite3 database.db\n'
  '```\n'
  '\n'
  '```sql\n'
  'CREATE TABLE users (\n'
  '    id INTEGER PRIMARY KEY,\n'
  '    name TEXT NOT NULL\n'
  ');\n'
  '\n'
  'INSERT INTO users (name)\n'
  "VALUES ('Utilisateur');\n"
  '\n'
  'SELECT * FROM users;\n'
  '```\n'
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-7-api-http-et-webhooks',
  'PARTIE 7 — API, HTTP ET WEBHOOKS',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 7 — API, HTTP ET WEBHOOKS',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-7-1-curl',
  '7.1 — cURL',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 7.1 — cURL\n'
  '\n'
  '```bash\n'
  'curl https://example.com\n'
  'curl -I https://example.com\n'
  'curl -L https://example.com\n'
  'curl -o page.html https://example.com\n'
  '```\n'
  '\n'
  'GET JSON :\n'
  '\n'
  '```bash\n'
  'curl https://api.example.com/data \\\n'
  '  -H "Accept: application/json"\n'
  '```\n'
  '\n'
  'POST :\n'
  '\n'
  '```bash\n'
  'curl -X POST https://api.example.com/data \\\n'
  '  -H "Content-Type: application/json" \\\n'
  '  -d \'{"name":"Stratege"}\'\n'
  '```\n'
  '\n'
  'PUT :\n'
  '\n'
  '```bash\n'
  'curl -X PUT https://api.example.com/data/1 \\\n'
  '  -H "Content-Type: application/json" \\\n'
  '  -d \'{"name":"Updated"}\'\n'
  '```\n'
  '\n'
  'DELETE :\n'
  '\n'
  '```bash\n'
  'curl -X DELETE https://api.example.com/data/1\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-7-2-codes-http',
  '7.2 — Codes HTTP',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 7.2 — Codes HTTP\n'
  '\n'
  '```text\n'
  '200 OK\n'
  '201 Created\n'
  '202 Accepted\n'
  '204 No Content\n'
  '\n'
  '301 Moved Permanently\n'
  '302 Found\n'
  '304 Not Modified\n'
  '\n'
  '400 Bad Request\n'
  '401 Unauthorized\n'
  '403 Forbidden\n'
  '404 Not Found\n'
  '405 Method Not Allowed\n'
  '408 Request Timeout\n'
  '409 Conflict\n'
  '422 Unprocessable Entity\n'
  '429 Too Many Requests\n'
  '\n'
  '500 Internal Server Error\n'
  '502 Bad Gateway\n'
  '503 Service Unavailable\n'
  '504 Gateway Timeout\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-7-3-api-rest-avec-fastapi',
  '7.3 — API REST avec FastAPI',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 7.3 — API REST avec FastAPI\n'
  '\n'
  'Installation :\n'
  '\n'
  '```bash\n'
  'pip install fastapi uvicorn\n'
  '```\n'
  '\n'
  'Serveur :\n'
  '\n'
  '```python\n'
  'from fastapi import FastAPI\n'
  '\n'
  'app = FastAPI()\n'
  '\n'
  '@app.get("/health")\n'
  'def health():\n'
  '    return {"status": "ok"}\n'
  '\n'
  '@app.get("/products/{product_id}")\n'
  'def get_product(product_id: int):\n'
  '    return {"id": product_id}\n'
  '```\n'
  '\n'
  'Exécution :\n'
  '\n'
  '```bash\n'
  'uvicorn main:app --reload\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-7-4-webhook',
  '7.4 — Webhook',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 7.4 — Webhook\n'
  '\n'
  '```python\n'
  'from fastapi import FastAPI, Request\n'
  '\n'
  'app = FastAPI()\n'
  '\n'
  '@app.post("/webhook")\n'
  'async def webhook(request: Request):\n'
  '    payload = await request.json()\n'
  '\n'
  '    return {\n'
  '        "received": True,\n'
  '        "event": payload\n'
  '    }\n'
  '```\n'
  '\n'
  'Production : vérifier la signature cryptographique du webhook, empêcher les rejeux, contrôler la taille du corps et '
  'journaliser les événements sans secrets.',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-7-5-graphql',
  '7.5 — GraphQL',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 7.5 — GraphQL\n'
  '\n'
  'Exemple :\n'
  '\n'
  '```graphql\n'
  'query GetProducts {\n'
  '    products {\n'
  '        id\n'
  '        name\n'
  '        price\n'
  '    }\n'
  '}\n'
  '```\n'
  '\n'
  'Mutation :\n'
  '\n'
  '```graphql\n'
  'mutation CreateProduct {\n'
  '    createProduct(\n'
  '        name: "Produit A",\n'
  '        price: 20\n'
  '    ) {\n'
  '        id\n'
  '        name\n'
  '    }\n'
  '}\n'
  '```\n'
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-8-rseaux-vpn-proxies-et-diagnostic',
  'PARTIE 8 — RÉSEAUX, VPN, PROXIES ET DIAGNOSTIC',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 8 — RÉSEAUX, VPN, PROXIES ET DIAGNOSTIC',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-8-1-rseau-windows',
  '8.1 — Réseau Windows',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 8.1 — Réseau Windows\n'
  '\n'
  '```cmd\n'
  'ipconfig\n'
  'ipconfig /all\n'
  'ipconfig /flushdns\n'
  'ping example.com\n'
  'tracert example.com\n'
  'nslookup example.com\n'
  'netstat -ano\n'
  'arp -a\n'
  'route print\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-8-2-rseau-linux',
  '8.2 — Réseau Linux',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 8.2 — Réseau Linux\n'
  '\n'
  '```bash\n'
  'ip addr\n'
  'ip route\n'
  'ip neigh\n'
  'ss -tulpn\n'
  'dig example.com\n'
  'host example.com\n'
  'curl -v https://example.com\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-8-3-tls',
  '8.3 — TLS',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 8.3 — TLS\n'
  '\n'
  '```bash\n'
  'openssl version\n'
  '\n'
  'openssl s_client \\\n'
  '    -connect example.com:443 \\\n'
  '    -servername example.com\n'
  '```\n'
  '\n'
  'Certificat :\n'
  '\n'
  '```bash\n'
  'openssl x509 \\\n'
  '    -in certificate.crt \\\n'
  '    -noout \\\n'
  '    -subject \\\n'
  '    -issuer \\\n'
  '    -dates\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-8-4-vpn-wireguard',
  '8.4 — VPN WireGuard',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 8.4 — VPN WireGuard\n'
  '\n'
  '```bash\n'
  'wg --version\n'
  'wg show\n'
  'wg showconf wg0\n'
  '```\n'
  '\n'
  'Configuration type à adapter :\n'
  '\n'
  '```ini\n'
  '[Interface]\n'
  'PrivateKey = <PRIVATE_KEY>\n'
  'Address = 10.0.0.2/32\n'
  '\n'
  '[Peer]\n'
  'PublicKey = <SERVER_PUBLIC_KEY>\n'
  'Endpoint = vpn.example.com:51820\n'
  'AllowedIPs = 10.0.0.0/24\n'
  'PersistentKeepalive = 25\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-8-5-proxy-http',
  '8.5 — Proxy HTTP',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 8.5 — Proxy HTTP\n'
  '\n'
  "Variables d'environnement :\n"
  '\n'
  '```bash\n'
  'export HTTP_PROXY=http://127.0.0.1:8080\n'
  'export HTTPS_PROXY=http://127.0.0.1:8080\n'
  'export NO_PROXY=localhost,127.0.0.1\n'
  '```\n'
  '\n'
  'PowerShell :\n'
  '\n'
  '```powershell\n'
  '$env:HTTP_PROXY = "http://127.0.0.1:8080"\n'
  '$env:HTTPS_PROXY = "http://127.0.0.1:8080"\n'
  '```\n'
  '\n'
  'Test :\n'
  '\n'
  '```bash\n'
  'curl -x http://127.0.0.1:8080 https://example.com\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-8-6-analyse-rseau',
  '8.6 — Analyse réseau',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 8.6 — Analyse réseau\n'
  '\n'
  '```bash\n'
  'tcpdump -i any -c 100\n'
  '```\n'
  '\n'
  '```bash\n'
  'tshark --version\n'
  '```\n'
  '\n'
  '```bash\n'
  'nmap -sV -p 80,443 example.com\n'
  '```\n'
  '\n'
  "Utiliser les outils de diagnostic uniquement sur les systèmes et réseaux que l'on possède ou pour lesquels on "
  "dispose d'une autorisation.\n"
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-9-web-scraping-et-extraction',
  'PARTIE 9 — WEB SCRAPING ET EXTRACTION',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 9 — WEB SCRAPING ET EXTRACTION',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-9-1-installation',
  '9.1 — Installation',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 9.1 — Installation\n'
  '\n'
  '```bash\n'
  'pip install requests\n'
  'pip install beautifulsoup4\n'
  'pip install scrapy\n'
  'pip install scrapling\n'
  'pip install playwright\n'
  'pip install lxml\n'
  'pip install trafilatura\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-9-2-beautifulsoup',
  '9.2 — BeautifulSoup',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 9.2 — BeautifulSoup\n'
  '\n'
  '```python\n'
  'import requests\n'
  'from bs4 import BeautifulSoup\n'
  '\n'
  'url = "https://quotes.toscrape.com/"\n'
  '\n'
  'response = requests.get(url, timeout=10)\n'
  'response.raise_for_status()\n'
  '\n'
  'soup = BeautifulSoup(response.text, "html.parser")\n'
  '\n'
  'for quote in soup.select(".quote"):\n'
  '    print(quote.select_one(".text").get_text(strip=True))\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-9-3-scrapling',
  '9.3 — Scrapling',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 9.3 — Scrapling\n'
  '\n'
  '```python\n'
  'from scrapling.fetchers import Fetcher\n'
  '\n'
  'page = Fetcher.get("https://quotes.toscrape.com/")\n'
  '\n'
  'for quote in page.css(".quote"):\n'
  '    print({\n'
  '        "text": quote.css(".text::text").get(),\n'
  '        "author": quote.css(".author::text").get()\n'
  '    })\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-9-4-playwright',
  '9.4 — Playwright',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 9.4 — Playwright\n'
  '\n'
  '```bash\n'
  'pip install playwright\n'
  'playwright install chromium\n'
  '```\n'
  '\n'
  '```python\n'
  'from playwright.sync_api import sync_playwright\n'
  '\n'
  'with sync_playwright() as p:\n'
  '    browser = p.chromium.launch(headless=True)\n'
  '    page = browser.new_page()\n'
  '\n'
  '    page.goto("https://quotes.toscrape.com/")\n'
  '\n'
  '    results = page.locator(".quote .text").all_text_contents()\n'
  '\n'
  '    print(results)\n'
  '\n'
  '    browser.close()\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-9-5-scrapy',
  '9.5 — Scrapy',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 9.5 — Scrapy\n'
  '\n'
  '```bash\n'
  'scrapy startproject mycrawler\n'
  'cd mycrawler\n'
  'scrapy genspider quotes quotes.toscrape.com\n'
  'scrapy crawl quotes\n'
  '```\n'
  '\n'
  'Spider :\n'
  '\n'
  '```python\n'
  'import scrapy\n'
  '\n'
  'class QuotesSpider(scrapy.Spider):\n'
  '    name = "quotes"\n'
  '    start_urls = ["https://quotes.toscrape.com/"]\n'
  '\n'
  '    def parse(self, response):\n'
  '        for quote in response.css(".quote"):\n'
  '            yield {\n'
  '                "text": quote.css(".text::text").get(),\n'
  '                "author": quote.css(".author::text").get()\n'
  '            }\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-9-6-extraction-d-articles',
  "9.6 — Extraction d'articles",
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  "### 9.6 — Extraction d'articles\n"
  '\n'
  '```python\n'
  'import trafilatura\n'
  '\n'
  'downloaded = trafilatura.fetch_url("https://example.com/article")\n'
  '\n'
  'if downloaded:\n'
  '    text = trafilatura.extract(downloaded)\n'
  '    print(text)\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-9-7-traitement-de-donnes-collectes',
  '9.7 — Traitement de données collectées',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 9.7 — Traitement de données collectées\n'
  '\n'
  '```python\n'
  'import json\n'
  '\n'
  'records = [\n'
  '    {"name": "A", "price": 10},\n'
  '    {"name": "B", "price": 20}\n'
  ']\n'
  '\n'
  'with open("results.json", "w", encoding="utf-8") as file:\n'
  '    json.dump(records, file, ensure_ascii=False, indent=2)\n'
  '```\n'
  '\n'
  'Ne collecter que des sources accessibles et autorisées. Respecter les limitations de fréquence, les conditions '
  'applicables et la protection des données.\n'
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-10-git-github-et-versionnement',
  'PARTIE 10 — GIT, GITHUB ET VERSIONNEMENT',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 10 — GIT, GITHUB ET VERSIONNEMENT',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-10-1-commandes-git',
  '10.1 — Commandes Git',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 10.1 — Commandes Git\n'
  '\n'
  '```bash\n'
  'git --version\n'
  'git init\n'
  'git clone URL\n'
  'git status\n'
  'git add .\n'
  'git commit -m "Initial commit"\n'
  'git log --oneline\n'
  'git diff\n'
  'git branch\n'
  'git switch main\n'
  'git switch -c feature/new-feature\n'
  'git merge feature/new-feature\n'
  'git fetch\n'
  'git pull\n'
  'git push\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-10-2-dpt-distant',
  '10.2 — Dépôt distant',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 10.2 — Dépôt distant\n'
  '\n'
  '```bash\n'
  'git remote -v\n'
  'git remote add origin URL\n'
  'git remote set-url origin URL\n'
  'git fetch origin\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-10-3-annulation-et-rcupration',
  '10.3 — Annulation et récupération',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 10.3 — Annulation et récupération\n'
  '\n'
  '```bash\n'
  'git restore fichier.txt\n'
  'git restore --staged fichier.txt\n'
  'git stash\n'
  'git stash list\n'
  'git stash pop\n'
  'git revert COMMIT_ID\n'
  '```\n'
  '\n'
  "Ne pas utiliser `reset --hard`, `clean -fd` ou `push --force` sans comprendre les conséquences et disposer d'une "
  'sauvegarde.',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-10-4-branches',
  '10.4 — Branches',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 10.4 — Branches\n'
  '\n'
  '```bash\n'
  'git branch\n'
  'git branch feature\n'
  'git switch feature\n'
  'git merge main\n'
  'git branch -d feature\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-10-5-tags',
  '10.5 — Tags',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 10.5 — Tags\n'
  '\n'
  '```bash\n'
  'git tag v1.0.0\n'
  'git tag\n'
  'git push origin v1.0.0\n'
  '```\n'
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-11-docker-et-conteneurs',
  'PARTIE 11 — DOCKER ET CONTENEURS',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 11 — DOCKER ET CONTENEURS',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-11-1-commandes-docker',
  '11.1 — Commandes Docker',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 11.1 — Commandes Docker\n'
  '\n'
  '```bash\n'
  'docker --version\n'
  'docker info\n'
  'docker images\n'
  'docker ps\n'
  'docker ps -a\n'
  'docker pull nginx\n'
  'docker run --rm nginx\n'
  'docker build -t stratege-app .\n'
  'docker logs CONTAINER_ID\n'
  'docker inspect CONTAINER_ID\n'
  'docker exec -it CONTAINER_ID sh\n'
  'docker stop CONTAINER_ID\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-11-2-dockerfile-node-js',
  '11.2 — Dockerfile Node.js',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 11.2 — Dockerfile Node.js\n'
  '\n'
  '```dockerfile\n'
  'FROM node:22-alpine\n'
  '\n'
  'WORKDIR /app\n'
  '\n'
  'COPY package*.json ./\n'
  '\n'
  'RUN npm ci\n'
  '\n'
  'COPY . .\n'
  '\n'
  'RUN npm run build\n'
  '\n'
  'EXPOSE 3000\n'
  '\n'
  'CMD ["npm", "start"]\n'
  '```\n'
  '\n'
  'Adapter la version Node.js à celle validée dans le projet.',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-11-3-dockerfile-python',
  '11.3 — Dockerfile Python',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 11.3 — Dockerfile Python\n'
  '\n'
  '```dockerfile\n'
  'FROM python:3.12-slim\n'
  '\n'
  'WORKDIR /app\n'
  '\n'
  'COPY requirements.txt .\n'
  '\n'
  'RUN pip install --no-cache-dir -r requirements.txt\n'
  '\n'
  'COPY . .\n'
  '\n'
  'CMD ["python", "main.py"]\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-11-4-docker-compose',
  '11.4 — Docker Compose',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 11.4 — Docker Compose\n'
  '\n'
  '```yaml\n'
  'services:\n'
  '  app:\n'
  '    build: .\n'
  '    ports:\n'
  '      - "3000:3000"\n'
  '    environment:\n'
  '      NODE_ENV: production\n'
  '```\n'
  '\n'
  'Commandes :\n'
  '\n'
  '```bash\n'
  'docker compose up\n'
  'docker compose up -d\n'
  'docker compose ps\n'
  'docker compose logs\n'
  'docker compose down\n'
  'docker compose build\n'
  '```\n'
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-12-cloud-et-dploiement',
  'PARTIE 12 — CLOUD ET DÉPLOIEMENT',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 12 — CLOUD ET DÉPLOIEMENT',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-12-1-google-cloud-cli',
  '12.1 — Google Cloud CLI',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 12.1 — Google Cloud CLI\n'
  '\n'
  '```bash\n'
  'gcloud --version\n'
  'gcloud auth login\n'
  'gcloud config list\n'
  'gcloud projects list\n'
  'gcloud config set project PROJECT_ID\n'
  'gcloud services list --enabled\n'
  '```\n'
  '\n'
  'Cloud Run :\n'
  '\n'
  '```bash\n'
  'gcloud run services list\n'
  'gcloud run services describe SERVICE_NAME\n'
  'gcloud run services logs read SERVICE_NAME\n'
  'gcloud run deploy SERVICE_NAME --source .\n'
  '```\n'
  '\n'
  "Le déploiement doit être précédé d'une vérification de la configuration, des permissions et du projet cible.",
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-12-2-firebase-cli',
  '12.2 — Firebase CLI',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 12.2 — Firebase CLI\n'
  '\n'
  '```bash\n'
  'firebase --version\n'
  'firebase login\n'
  'firebase projects:list\n'
  'firebase use\n'
  'firebase emulators:start\n'
  'firebase deploy\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-12-3-vercel-cli',
  '12.3 — Vercel CLI',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 12.3 — Vercel CLI\n'
  '\n'
  '```bash\n'
  'npm install -g vercel\n'
  'vercel --version\n'
  'vercel login\n'
  'vercel link\n'
  'vercel env ls\n'
  'vercel build\n'
  'vercel deploy\n'
  '```\n'
  '\n'
  'Production :\n'
  '\n'
  '```bash\n'
  'vercel deploy --prod\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-12-4-terraform',
  '12.4 — Terraform',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 12.4 — Terraform\n'
  '\n'
  '```bash\n'
  'terraform version\n'
  'terraform init\n'
  'terraform fmt\n'
  'terraform validate\n'
  'terraform plan\n'
  'terraform apply\n'
  'terraform output\n'
  'terraform destroy\n'
  '```\n'
  '\n'
  '`terraform destroy` est une opération destructive et ne doit jamais être lancée automatiquement.',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-12-5-variables-d-environnement',
  "12.5 — Variables d'environnement",
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  "### 12.5 — Variables d'environnement\n"
  '\n'
  '```bash\n'
  'APP_ENV=production\n'
  'DATABASE_URL=<SECRET>\n'
  'API_URL=https://api.example.com\n'
  '```\n'
  '\n'
  'Ne jamais placer les secrets réels dans Git.\n'
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-13-ci-cd-et-automatisation',
  'PARTIE 13 — CI/CD ET AUTOMATISATION',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 13 — CI/CD ET AUTOMATISATION',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-13-1-github-actions',
  '13.1 — GitHub Actions',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 13.1 — GitHub Actions\n'
  '\n'
  'Exemple de workflow :\n'
  '\n'
  '```yaml\n'
  'name: CI\n'
  '\n'
  'on:\n'
  '  push:\n'
  '    branches: [main]\n'
  '  pull_request:\n'
  '\n'
  'jobs:\n'
  '  test:\n'
  '    runs-on: ubuntu-latest\n'
  '\n'
  '    steps:\n'
  '      - uses: actions/checkout@v4\n'
  '\n'
  '      - uses: actions/setup-node@v4\n'
  '        with:\n'
  '          node-version: 22\n'
  '\n'
  '      - run: npm ci\n'
  '      - run: npm run lint --if-present\n'
  '      - run: npm test --if-present\n'
  '      - run: npm run build\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-13-2-automatisation-python',
  '13.2 — Automatisation Python',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 13.2 — Automatisation Python\n'
  '\n'
  '```python\n'
  'from datetime import datetime\n'
  '\n'
  'def execute_task():\n'
  '    print("Tâche exécutée :", datetime.now())\n'
  '\n'
  'if __name__ == "__main__":\n'
  '    execute_task()\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-13-3-planification-linux',
  '13.3 — Planification Linux',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 13.3 — Planification Linux\n'
  '\n'
  '```bash\n'
  'crontab -e\n'
  '```\n'
  '\n'
  'Exemple :\n'
  '\n'
  '```cron\n'
  '0 8 * * * /usr/bin/python3 /app/report.py\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-13-4-planification-windows',
  '13.4 — Planification Windows',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 13.4 — Planification Windows\n'
  '\n'
  '```powershell\n'
  'Get-ScheduledTask\n'
  'Get-ScheduledTaskInfo -TaskName "MyTask"\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-13-5-n8n',
  '13.5 — n8n',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 13.5 — n8n\n'
  '\n'
  'Exemple de logique de workflow :\n'
  '\n'
  '```json\n'
  '{\n'
  '  "nodes": [\n'
  '    {\n'
  '      "name": "Schedule",\n'
  '      "type": "n8n-nodes-base.scheduleTrigger"\n'
  '    },\n'
  '    {\n'
  '      "name": "HTTP Request",\n'
  '      "type": "n8n-nodes-base.httpRequest"\n'
  '    }\n'
  '  ]\n'
  '}\n'
  '```\n'
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-14-intelligence-artificielle-et-machine-learning',
  'PARTIE 14 — INTELLIGENCE ARTIFICIELLE ET MACHINE LEARNING',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 14 — INTELLIGENCE ARTIFICIELLE ET MACHINE LEARNING',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-14-1-pytorch',
  '14.1 — PyTorch',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 14.1 — PyTorch\n'
  '\n'
  '```bash\n'
  'pip install torch\n'
  '```\n'
  '\n'
  '```python\n'
  'import torch\n'
  '\n'
  'x = torch.tensor([1.0, 2.0, 3.0])\n'
  '\n'
  'print(x.mean())\n'
  'print(x.sum())\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-14-2-scikit-learn',
  '14.2 — Scikit-learn',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 14.2 — Scikit-learn\n'
  '\n'
  '```bash\n'
  'pip install scikit-learn\n'
  '```\n'
  '\n'
  '```python\n'
  'from sklearn.linear_model import LinearRegression\n'
  '\n'
  'X = [[1], [2], [3], [4]]\n'
  'y = [2, 4, 6, 8]\n'
  '\n'
  'model = LinearRegression()\n'
  'model.fit(X, y)\n'
  '\n'
  'print(model.predict([[5]]))\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-14-3-hugging-face-transformers',
  '14.3 — Hugging Face Transformers',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 14.3 — Hugging Face Transformers\n'
  '\n'
  '```bash\n'
  'pip install transformers torch\n'
  '```\n'
  '\n'
  '```python\n'
  'from transformers import pipeline\n'
  '\n'
  'classifier = pipeline("sentiment-analysis")\n'
  '\n'
  'result = classifier("Cybbig est une application utile.")\n'
  '\n'
  'print(result)\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-14-4-embeddings',
  '14.4 — Embeddings',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 14.4 — Embeddings\n'
  '\n'
  '```python\n'
  'from sentence_transformers import SentenceTransformer\n'
  '\n'
  'model = SentenceTransformer("all-MiniLM-L6-v2")\n'
  '\n'
  'sentences = [\n'
  '    "Gestion d\'entreprise",\n'
  '    "Marketing digital",\n'
  '    "Analyse financière"\n'
  ']\n'
  '\n'
  'embeddings = model.encode(sentences)\n'
  '\n'
  'print(embeddings.shape)\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-14-5-recherche-vectorielle',
  '14.5 — Recherche vectorielle',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 14.5 — Recherche vectorielle\n'
  '\n'
  '```sql\n'
  'CREATE EXTENSION IF NOT EXISTS vector;\n'
  '\n'
  'CREATE TABLE knowledge_embeddings (\n'
  '    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,\n'
  '    content TEXT NOT NULL,\n'
  '    embedding VECTOR(384)\n'
  ');\n'
  '```\n'
  '\n'
  'Recherche :\n'
  '\n'
  '```sql\n'
  'SELECT content\n'
  'FROM knowledge_embeddings\n'
  "ORDER BY embedding <=> '[0.1,0.2,0.3]'::vector\n"
  'LIMIT 5;\n'
  '```\n'
  '\n'
  "Le vecteur de l'exemple doit être remplacé par un embedding réel de dimension compatible.",
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-14-6-appel-un-modle-ia',
  '14.6 — Appel à un modèle IA',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 14.6 — Appel à un modèle IA\n'
  '\n'
  '```python\n'
  'import os\n'
  'from openai import OpenAI\n'
  '\n'
  'client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])\n'
  '\n'
  'response = client.responses.create(\n'
  '    model=os.environ["OPENAI_MODEL"],\n'
  '    input="Explique le fonctionnement d\'une API REST."\n'
  ')\n'
  '\n'
  'print(response.output_text)\n'
  '```\n'
  '\n'
  'Le modèle doit être choisi à partir de la configuration du projet et des modèles réellement disponibles.',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-14-7-agents-et-outils',
  '14.7 — Agents et outils',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 14.7 — Agents et outils\n'
  '\n'
  '```python\n'
  'tools = [\n'
  '    {\n'
  '        "name": "search_knowledge",\n'
  '        "description": "Recherche dans la base documentaire",\n'
  '        "input_schema": {\n'
  '            "type": "object",\n'
  '            "properties": {\n'
  '                "query": {"type": "string"}\n'
  '            },\n'
  '            "required": ["query"]\n'
  '        }\n'
  '    },\n'
  '    {\n'
  '        "name": "analyze_data",\n'
  '        "description": "Analyse un jeu de données autorisé",\n'
  '        "input_schema": {\n'
  '            "type": "object",\n'
  '            "properties": {\n'
  '                "dataset_id": {"type": "string"}\n'
  '            },\n'
  '            "required": ["dataset_id"]\n'
  '        }\n'
  '    }\n'
  ']\n'
  '```\n'
  '\n'
  'Les outils réels doivent être connectés à des fonctions backend validées, avec permissions et contrôles.\n'
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-15-cyberscurit-dfensive',
  'PARTIE 15 — CYBERSÉCURITÉ DÉFENSIVE',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 15 — CYBERSÉCURITÉ DÉFENSIVE',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-15-1-hachage',
  '15.1 — Hachage',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 15.1 — Hachage\n'
  '\n'
  '```python\n'
  'import hashlib\n'
  '\n'
  'value = "Stratege"\n'
  '\n'
  'digest = hashlib.sha256(\n'
  '    value.encode()\n'
  ').hexdigest()\n'
  '\n'
  'print(digest)\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-15-2-gnration-de-secrets',
  '15.2 — Génération de secrets',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 15.2 — Génération de secrets\n'
  '\n'
  '```python\n'
  'import secrets\n'
  '\n'
  'token = secrets.token_urlsafe(32)\n'
  '\n'
  'print(token)\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-15-3-vrification-d-un-mot-de-passe-avec-argon2',
  "15.3 — Vérification d'un mot de passe avec Argon2",
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  "### 15.3 — Vérification d'un mot de passe avec Argon2\n"
  '\n'
  '```python\n'
  'from argon2 import PasswordHasher\n'
  '\n'
  'ph = PasswordHasher()\n'
  '\n'
  'hashed = ph.hash("mot-de-passe-exemple")\n'
  '\n'
  'try:\n'
  '    ph.verify(hashed, "mot-de-passe-exemple")\n'
  '    print("Mot de passe valide")\n'
  'except Exception:\n'
  '    print("Mot de passe invalide")\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-15-4-audit-de-dpendances',
  '15.4 — Audit de dépendances',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 15.4 — Audit de dépendances\n'
  '\n'
  '```bash\n'
  'npm audit\n'
  'pip-audit\n'
  'bandit -r .\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-15-5-analyse-de-code',
  '15.5 — Analyse de code',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 15.5 — Analyse de code\n'
  '\n'
  '```bash\n'
  'ruff check .\n'
  'mypy .\n'
  'pytest\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-15-6-recherche-de-secrets',
  '15.6 — Recherche de secrets',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 15.6 — Recherche de secrets\n'
  '\n'
  '```bash\n'
  'gitleaks detect\n'
  '```\n'
  '\n'
  'Ne jamais enregistrer ou afficher les secrets découverts dans les rapports publics.',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-15-7-vrification-des-permissions',
  '15.7 — Vérification des permissions',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 15.7 — Vérification des permissions\n'
  '\n'
  '```bash\n'
  'git status\n'
  'npm audit\n'
  'pip check\n'
  '```\n'
  '\n'
  'Les tests de sécurité doivent être réalisés sur des environnements contrôlés et des systèmes autorisés.\n'
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-16-tests-et-qualit-du-code',
  'PARTIE 16 — TESTS ET QUALITÉ DU CODE',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 16 — TESTS ET QUALITÉ DU CODE',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-16-1-pytest',
  '16.1 — Pytest',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 16.1 — Pytest\n'
  '\n'
  '```python\n'
  'def add(a, b):\n'
  '    return a + b\n'
  '\n'
  'def test_add():\n'
  '    assert add(2, 3) == 5\n'
  '```\n'
  '\n'
  'Commande :\n'
  '\n'
  '```bash\n'
  'pytest\n'
  'pytest -v\n'
  'pytest --cov\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-16-2-jest',
  '16.2 — Jest',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 16.2 — Jest\n'
  '\n'
  '```bash\n'
  'npm install -D jest\n'
  '```\n'
  '\n'
  '```javascript\n'
  'function add(a, b) {\n'
  '    return a + b;\n'
  '}\n'
  '\n'
  'test("addition", () => {\n'
  '    expect(add(2, 3)).toBe(5);\n'
  '});\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-16-3-playwright-tests',
  '16.3 — Playwright Tests',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 16.3 — Playwright Tests\n'
  '\n'
  '```bash\n'
  'npm install -D @playwright/test\n'
  'npx playwright install\n'
  'npx playwright test\n'
  'npx playwright test --ui\n'
  'npx playwright show-report\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-16-4-tests-api',
  '16.4 — Tests API',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 16.4 — Tests API\n'
  '\n'
  '```python\n'
  'from fastapi.testclient import TestClient\n'
  'from main import app\n'
  '\n'
  'client = TestClient(app)\n'
  '\n'
  'def test_health():\n'
  '    response = client.get("/health")\n'
  '\n'
  '    assert response.status_code == 200\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-16-5-couverture',
  '16.5 — Couverture',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 16.5 — Couverture\n'
  '\n'
  '```bash\n'
  'coverage run -m pytest\n'
  'coverage report\n'
  'coverage html\n'
  '```\n'
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-17-structures-de-donnes-et-algorithmes',
  'PARTIE 17 — STRUCTURES DE DONNÉES ET ALGORITHMES',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 17 — STRUCTURES DE DONNÉES ET ALGORITHMES',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-17-1-recherche-linaire',
  '17.1 — Recherche linéaire',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 17.1 — Recherche linéaire\n'
  '\n'
  '```python\n'
  'def linear_search(items, target):\n'
  '    for index, item in enumerate(items):\n'
  '        if item == target:\n'
  '            return index\n'
  '\n'
  '    return -1\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-17-2-recherche-binaire',
  '17.2 — Recherche binaire',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 17.2 — Recherche binaire\n'
  '\n'
  '```python\n'
  'def binary_search(items, target):\n'
  '    left = 0\n'
  '    right = len(items) - 1\n'
  '\n'
  '    while left <= right:\n'
  '        middle = (left + right) // 2\n'
  '\n'
  '        if items[middle] == target:\n'
  '            return middle\n'
  '\n'
  '        if items[middle] < target:\n'
  '            left = middle + 1\n'
  '        else:\n'
  '            right = middle - 1\n'
  '\n'
  '    return -1\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-17-3-tri',
  '17.3 — Tri',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 17.3 — Tri\n'
  '\n'
  '```python\n'
  'numbers = [5, 2, 9, 1, 3]\n'
  '\n'
  'numbers.sort()\n'
  '\n'
  'print(numbers)\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-17-4-rcursivit',
  '17.4 — Récursivité',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 17.4 — Récursivité\n'
  '\n'
  '```python\n'
  'def factorial(n):\n'
  '    if n <= 1:\n'
  '        return 1\n'
  '\n'
  '    return n * factorial(n - 1)\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-17-5-graphes',
  '17.5 — Graphes',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 17.5 — Graphes\n'
  '\n'
  '```python\n'
  'graph = {\n'
  '    "A": ["B", "C"],\n'
  '    "B": ["D"],\n'
  '    "C": ["D"],\n'
  '    "D": []\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-17-6-complexit',
  '17.6 — Complexité',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 17.6 — Complexité\n'
  '\n'
  'Documenter :\n'
  '- O(1)\n'
  '- O(log n)\n'
  '- O(n)\n'
  '- O(n log n)\n'
  '- O(n²)\n'
  '- O(2ⁿ)\n'
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-18-automatisation-de-fichiers-et-de-donnes',
  'PARTIE 18 — AUTOMATISATION DE FICHIERS ET DE DONNÉES',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 18 — AUTOMATISATION DE FICHIERS ET DE DONNÉES',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-18-1-organisation-automatique',
  '18.1 — Organisation automatique',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 18.1 — Organisation automatique\n'
  '\n'
  '```python\n'
  'from pathlib import Path\n'
  'import shutil\n'
  '\n'
  'source = Path("downloads")\n'
  '\n'
  'categories = {\n'
  '    ".pdf": "documents",\n'
  '    ".jpg": "images",\n'
  '    ".png": "images",\n'
  '    ".csv": "data"\n'
  '}\n'
  '\n'
  'for file in source.iterdir():\n'
  '    if not file.is_file():\n'
  '        continue\n'
  '\n'
  '    destination = categories.get(file.suffix.lower())\n'
  '\n'
  '    if destination:\n'
  '        target = source / destination\n'
  '        target.mkdir(exist_ok=True)\n'
  '        shutil.copy2(file, target / file.name)\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-18-2-dtection-de-doublons',
  '18.2 — Détection de doublons',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 18.2 — Détection de doublons\n'
  '\n'
  '```python\n'
  'from pathlib import Path\n'
  'import hashlib\n'
  '\n'
  'def file_hash(path):\n'
  '    digest = hashlib.sha256()\n'
  '\n'
  '    with open(path, "rb") as file:\n'
  '        for chunk in iter(lambda: file.read(65536), b""):\n'
  '            digest.update(chunk)\n'
  '\n'
  '    return digest.hexdigest()\n'
  '\n'
  'files = {}\n'
  '\n'
  'for path in Path(".").glob("*"):\n'
  '    if path.is_file():\n'
  '        digest = file_hash(path)\n'
  '        files.setdefault(digest, []).append(str(path))\n'
  '\n'
  'for digest, paths in files.items():\n'
  '    if len(paths) > 1:\n'
  '        print("Doublons :", paths)\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-18-3-gnration-de-rapport-csv',
  '18.3 — Génération de rapport CSV',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 18.3 — Génération de rapport CSV\n'
  '\n'
  '```python\n'
  'import csv\n'
  'from datetime import datetime\n'
  '\n'
  'rows = [\n'
  '    ["Produit A", 20],\n'
  '    ["Produit B", 35]\n'
  ']\n'
  '\n'
  'with open("rapport.csv", "w", newline="", encoding="utf-8") as file:\n'
  '    writer = csv.writer(file)\n'
  '\n'
  '    writer.writerow(["Produit", "Prix"])\n'
  '    writer.writerows(rows)\n'
  '\n'
  'print(datetime.now())\n'
  '```\n'
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-19-observabilit-logs-et-performance',
  'PARTIE 19 — OBSERVABILITÉ, LOGS ET PERFORMANCE',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 19 — OBSERVABILITÉ, LOGS ET PERFORMANCE',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-19-1-logs-python',
  '19.1 — Logs Python',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 19.1 — Logs Python\n'
  '\n'
  '```python\n'
  'import logging\n'
  '\n'
  'logging.basicConfig(\n'
  '    level=logging.INFO,\n'
  '    format="%(asctime)s %(levelname)s %(message)s"\n'
  ')\n'
  '\n'
  'logging.info("Application démarrée")\n'
  'logging.warning("Avertissement")\n'
  'logging.error("Erreur")\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-19-2-mesure-du-temps',
  '19.2 — Mesure du temps',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 19.2 — Mesure du temps\n'
  '\n'
  '```python\n'
  'import time\n'
  '\n'
  'start = time.perf_counter()',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-opration-mesurer',
  'Opération à mesurer',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# Opération à mesurer\n'
  '\n'
  'duration = time.perf_counter() - start\n'
  '\n'
  'print(f"Durée : {duration:.4f}s")\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-19-3-profilage',
  '19.3 — Profilage',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 19.3 — Profilage\n'
  '\n'
  '```bash\n'
  'python -m cProfile main.py\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-19-4-monitoring-docker',
  '19.4 — Monitoring Docker',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 19.4 — Monitoring Docker\n'
  '\n'
  '```bash\n'
  'docker stats\n'
  'docker system df\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-19-5-prometheus',
  '19.5 — Prometheus',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 19.5 — Prometheus\n'
  '\n'
  '```yaml\n'
  'global:\n'
  '  scrape_interval: 15s\n'
  '\n'
  'scrape_configs:\n'
  '  - job_name: "application"\n'
  '    static_configs:\n'
  '      - targets: ["localhost:8000"]\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-19-6-opentelemetry',
  '19.6 — OpenTelemetry',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### 19.6 — OpenTelemetry\n'
  '\n'
  '```bash\n'
  'pip install opentelemetry-api opentelemetry-sdk\n'
  '```\n'
  '\n'
  "Documenter les traces, métriques, logs, identifiants de corrélation et durées d'exécution.\n"
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-20-langages-et-technologies-complmentaires',
  'PARTIE 20 — LANGAGES ET TECHNOLOGIES COMPLÉMENTAIRES',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 20 — LANGAGES ET TECHNOLOGIES COMPLÉMENTAIRES\n'
  '\n'
  'Créer des fiches de syntaxe, commandes et scripts pour :',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-programmation-gnrale',
  'Programmation générale',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Programmation générale\n'
  '- Python\n'
  '- JavaScript\n'
  '- TypeScript\n'
  '- Java\n'
  '- PHP\n'
  '- Ruby\n'
  '- Go\n'
  '- Rust\n'
  '- C\n'
  '- C++\n'
  '- C#\n'
  '- Kotlin\n'
  '- Swift\n'
  '- Dart\n'
  '- Lua\n'
  '- Perl\n'
  '- R\n'
  '- Julia\n'
  '- Scala\n'
  '- Elixir\n'
  '- Erlang\n'
  '- Haskell\n'
  '- OCaml\n'
  '- F#\n'
  '- Clojure\n'
  '- Groovy\n'
  '- Objective-C',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-web',
  'Web',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Web\n'
  '- HTML\n'
  '- CSS\n'
  '- SCSS\n'
  '- Sass\n'
  '- JSX\n'
  '- TSX\n'
  '- WebAssembly\n'
  '- WebGL\n'
  '- WebGPU',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-donnes-et-requtes',
  'Données et requêtes',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Données et requêtes\n'
  '- SQL\n'
  '- PL/pgSQL\n'
  '- GraphQL\n'
  '- Cypher\n'
  '- SPARQL\n'
  '- JSON\n'
  '- JSON5\n'
  '- JSONL\n'
  '- YAML\n'
  '- TOML\n'
  '- XML\n'
  '- CSV\n'
  '- Protocol Buffers\n'
  '- Avro',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-systmes-et-infrastructure',
  'Systèmes et infrastructure',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Systèmes et infrastructure\n'
  '- Bash\n'
  '- Zsh\n'
  '- PowerShell\n'
  '- Batch\n'
  '- Makefile\n'
  '- Dockerfile\n'
  '- Terraform HCL\n'
  '- Ansible YAML\n'
  '- Kubernetes YAML\n'
  '- Nix\n'
  '- Assembly\n'
  '\n'
  'Pour chacun :\n'
  '- Installation.\n'
  '- Compilation.\n'
  '- Exécution.\n'
  '- Gestion des dépendances.\n'
  '- Syntaxe.\n'
  '- Variables.\n'
  '- Fonctions.\n'
  '- Classes.\n'
  '- Modules.\n'
  '- Erreurs.\n'
  '- Tests.\n'
  '- Exemples avancés.\n'
  '- Documentation.\n'
  '- Outils associés.\n'
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-21-outils-de-dveloppement-et-commandes',
  'PARTIE 21 — OUTILS DE DÉVELOPPEMENT ET COMMANDES',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 21 — OUTILS DE DÉVELOPPEMENT ET COMMANDES\n'
  '\n'
  'Créer des fiches opérationnelles pour :',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-gestion-des-dpendances',
  'Gestion des dépendances',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Gestion des dépendances\n'
  '- npm\n'
  '- pnpm\n'
  '- yarn\n'
  '- bun\n'
  '- pip\n'
  '- uv\n'
  '- poetry\n'
  '- pipenv\n'
  '- Composer\n'
  '- Maven\n'
  '- Gradle\n'
  '- Cargo\n'
  '- Go Modules\n'
  '- NuGet',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-diteurs-et-environnements',
  'Éditeurs et environnements',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Éditeurs et environnements\n'
  '- VS Code\n'
  '- Visual Studio\n'
  '- IntelliJ IDEA\n'
  '- PyCharm\n'
  '- WebStorm\n'
  '- Android Studio\n'
  '- Xcode\n'
  '- Jupyter\n'
  '- JupyterLab\n'
  '- GitHub Codespaces',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-compilation',
  'Compilation',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Compilation\n'
  '- GCC\n'
  '- Clang\n'
  '- MSVC\n'
  '- CMake\n'
  '- Ninja\n'
  '- Make\n'
  '- Webpack\n'
  '- Vite\n'
  '- esbuild\n'
  '- SWC\n'
  '- Babel',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-api-et-tests',
  'API et tests',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### API et tests\n'
  '- Postman\n'
  '- Insomnia\n'
  '- Bruno\n'
  '- HTTPie\n'
  '- cURL\n'
  '- OpenAPI\n'
  '- Swagger\n'
  '- Newman\n'
  '- k6\n'
  '- Locust',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-infrastructure',
  'Infrastructure',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Infrastructure\n'
  '- Docker\n'
  '- Podman\n'
  '- Kubernetes\n'
  '- Helm\n'
  '- Terraform\n'
  '- Ansible\n'
  '- Pulumi\n'
  '- Packer',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-bases-de-donnes',
  'Bases de données',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Bases de données\n'
  '- PostgreSQL\n'
  '- MySQL\n'
  '- MariaDB\n'
  '- SQLite\n'
  '- MongoDB\n'
  '- Redis\n'
  '- Elasticsearch\n'
  '- OpenSearch\n'
  '- Qdrant\n'
  '- Weaviate\n'
  '- Milvus\n'
  '- Chroma\n'
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-22-commandes-de-diagnostic-universelles',
  'PARTIE 22 — COMMANDES DE DIAGNOSTIC UNIVERSELLES',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 22 — COMMANDES DE DIAGNOSTIC UNIVERSELLES\n'
  '\n'
  "Créer des procédures par type d'erreur.",
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-application-qui-ne-dmarre-pas',
  'Application qui ne démarre pas',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Application qui ne démarre pas\n'
  '```bash\n'
  'node --version\n'
  'npm --version\n'
  'npm install\n'
  'npm run build\n'
  'npm run dev\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-python-qui-ne-dmarre-pas',
  'Python qui ne démarre pas',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Python qui ne démarre pas\n'
  '```bash\n'
  'python --version\n'
  'python -m pip --version\n'
  'python -m pip check\n'
  'python main.py\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-port-dj-utilis',
  'Port déjà utilisé',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Port déjà utilisé\n'
  'Windows :\n'
  '\n'
  '```cmd\n'
  'netstat -ano\n'
  '```\n'
  '\n'
  'Linux :\n'
  '\n'
  '```bash\n'
  'ss -tulpn\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-problme-rseau',
  'Problème réseau',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Problème réseau\n'
  '```bash\n'
  'ping example.com\n'
  'nslookup example.com\n'
  'curl -I https://example.com\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-problme-git',
  'Problème Git',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Problème Git\n'
  '```bash\n'
  'git status\n'
  'git branch\n'
  'git remote -v\n'
  'git log --oneline -10\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-problme-docker',
  'Problème Docker',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Problème Docker\n'
  '```bash\n'
  'docker ps -a\n'
  'docker logs CONTAINER_ID\n'
  'docker inspect CONTAINER_ID\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-problme-postgresql',
  'Problème PostgreSQL',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Problème PostgreSQL\n'
  '```bash\n'
  'pg_isready\n'
  'psql -h localhost -U postgres -d database\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-problme-de-certificat',
  'Problème de certificat',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '### Problème de certificat\n'
  '```bash\n'
  'openssl s_client -connect example.com:443 -servername example.com\n'
  '```\n'
  '\n'
  '---',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-23-format-universel-de-documentation-des-commande',
  'PARTIE 23 — FORMAT UNIVERSEL DE DOCUMENTATION DES COMMANDES',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 23 — FORMAT UNIVERSEL DE DOCUMENTATION DES COMMANDES\n'
  '\n'
  'Chaque commande enregistrée doit avoir ce format :\n'
  '\n'
  '```json\n'
  '{\n'
  '  "name": "npm run build",\n'
  '  "category": "development",\n'
  '  "subcategory": "build",\n'
  '  "language": "javascript",\n'
  '  "environment": ["windows", "linux", "macos"],\n'
  '  "description": "Construit l\'application selon le script configuré.",\n'
  '  "syntax": "npm run build",\n'
  '  "parameters": [],\n'
  '  "prerequisites": ["nodejs", "npm", "package.json"],\n'
  '  "expected_result": "Production build completed",\n'
  '  "risk_level": "low",\n'
  '  "requires_authorization": false,\n'
  '  "is_destructive": false,\n'
  '  "version_constraints": [],\n'
  '  "examples": [],\n'
  '  "documentation_url": null,\n'
  '  "last_verified_at": null\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-24-format-universel-des-exemples-de-code',
  'PARTIE 24 — FORMAT UNIVERSEL DES EXEMPLES DE CODE',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 24 — FORMAT UNIVERSEL DES EXEMPLES DE CODE\n'
  '\n'
  '```json\n'
  '{\n'
  '  "title": "Exemple de requête API",\n'
  '  "category": "api",\n'
  '  "language": "python",\n'
  '  "runtime": "python3",\n'
  '  "dependencies": ["requests"],\n'
  '  "source_code": "import requests\\nresponse = requests.get(\'https://example.com\', '
  'timeout=10)\\nprint(response.status_code)",\n'
  '  "input_schema": {},\n'
  '  "output_schema": {},\n'
  '  "tests": [],\n'
  '  "expected_output": "200",\n'
  '  "security_notes": [\n'
  '    "Utiliser un timeout",\n'
  '    "Vérifier le statut HTTP",\n'
  '    "Ne pas exposer les secrets"\n'
  '  ],\n'
  '  "documentation": []\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-25-rgles-de-qualit-de-la-bibliothque',
  'PARTIE 25 — RÈGLES DE QUALITÉ DE LA BIBLIOTHÈQUE',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 25 — RÈGLES DE QUALITÉ DE LA BIBLIOTHÈQUE\n'
  '\n'
  'Chaque élément doit être :\n'
  '\n'
  '1. Vérifiable.\n'
  '2. Exécutable dans un environnement défini.\n'
  '3. Associé à un langage ou à un système.\n'
  '4. Documenté.\n'
  '5. Versionné.\n'
  '6. Testé lorsque cela est possible.\n'
  '7. Classé par catégorie et sous-catégorie.\n'
  '8. Associé à des exemples.\n'
  '9. Accompagné des risques.\n'
  '10. Relié aux autres technologies.\n'
  '\n'
  'Ne pas mélanger :\n'
  '- Les commandes Windows et Linux.\n'
  '- Les syntaxes de langages différents.\n'
  '- Les versions incompatibles.\n'
  '- Les commandes de développement et de production.\n'
  '- Les commandes de lecture et les commandes destructives.\n'
  '- Les exemples pédagogiques et les scripts réellement prêts pour la production.\n'
  '\n'
  'Les commandes susceptibles de supprimer des données, de modifier des permissions, de déployer, de migrer une base '
  'ou de modifier un système doivent être clairement signalées.',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-26-architecture-de-stockage-pour-stratege',
  'PARTIE 26 — ARCHITECTURE DE STOCKAGE POUR STRATEGE',
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PARTIE 26 — ARCHITECTURE DE STOCKAGE POUR STRATEGE\n'
  '\n'
  "Créer les tables suivantes si elles n'existent pas déjà :\n"
  '\n'
  '- code_languages\n'
  '- code_syntaxes\n'
  '- code_examples\n'
  '- code_functions\n'
  '- code_algorithms\n'
  '- code_snippets\n'
  '- code_packages\n'
  '- code_dependencies\n'
  '- code_frameworks\n'
  '- code_commands\n'
  '- code_command_parameters\n'
  '- code_command_examples\n'
  '- code_environments\n'
  '- code_operating_systems\n'
  '- code_compilers\n'
  '- code_runtimes\n'
  '- code_build_tools\n'
  '- code_deployment_tools\n'
  '- code_database_queries\n'
  '- code_api_examples\n'
  '- code_automation_scripts\n'
  '- code_configurations\n'
  '- code_templates\n'
  '- code_errors\n'
  '- code_troubleshooting\n'
  '- code_tests\n'
  '- code_documentation\n'
  '- code_repositories\n'
  '- code_security_rules\n'
  '- code_version_compatibility\n'
  '- code_execution_history\n'
  '- code_execution_permissions\n'
  '\n'
  'Créer les relations entre les tables et les index nécessaires.',
  'utilisateur, bibliothèque-7, code, référence'],
 ['7-partie-27-objectif-final-de-l-assistant-ia',
  "PARTIE 27 — OBJECTIF FINAL DE L'ASSISTANT IA",
  'Commandes et développement universel',
  'Source : bibliothèque fournie par l’utilisateur, document 7. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  "## PARTIE 27 — OBJECTIF FINAL DE L'ASSISTANT IA\n"
  '\n'
  "L'assistant Stratege doit pouvoir :\n"
  '\n'
  '- Retrouver une commande parmi des milliers.\n'
  '- Expliquer son fonctionnement.\n'
  '- Comparer plusieurs commandes.\n'
  '- Générer du code dans différents langages.\n'
  "- Convertir du code d'un langage à un autre.\n"
  '- Corriger les erreurs.\n'
  '- Générer un projet complet.\n'
  '- Installer les dépendances.\n'
  '- Configurer les environnements.\n'
  '- Créer des scripts.\n'
  '- Construire des API.\n'
  '- Préparer des bases de données.\n'
  '- Écrire des requêtes.\n'
  '- Construire des automatisations.\n'
  '- Préparer des déploiements.\n'
  '- Diagnostiquer les problèmes.\n'
  '- Générer des tests.\n'
  '- Vérifier les résultats.\n'
  '- Produire une documentation technique.\n'
  '\n'
  "L'IA doit aussi savoir dire lorsqu'elle ne connaît pas une commande, lorsqu'une syntaxe dépend d'une version ou "
  "lorsqu'un exemple n'a pas été testé.\n"
  '\n'
  "**RÈGLE FONDAMENTALE :** le fait de connaître une commande ne signifie pas que l'IA est autorisée à l'exécuter. "
  'Toute exécution réelle doit passer par un moteur contrôlé, des permissions explicites, un environnement isolé et '
  'une validation du résultat.\n'
  '\n'
  'FIN DE LA BIBLIOTHÈQUE — VERSION 1.',
  'utilisateur, bibliothèque-7, code, référence'],
 ['8-encyclopdie-n8-collection-massive-de-code-source-scripts',
  'Encyclopédie n°8 — Collection massive de code source, scripts, algorithmes et commandes informatiques',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# Encyclopédie n°8 — Collection massive de code source, scripts, algorithmes et commandes informatiques\n'
  '\n'
  'Cette collection est indépendante de tout projet particulier. Elle rassemble des exemples de code et des lignes de '
  'programmation dans de nombreux langages, avec des scripts complets, des fonctions, des classes, des algorithmes, '
  'des commandes système et des configurations.\n'
  '\n'
  "L'objectif est de constituer un vaste répertoire de code réutilisable pour apprendre, expérimenter, développer, "
  'automatiser et résoudre des problèmes informatiques.',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-1-python-programmation-gnrale',
  '1. Python — programmation générale',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 1. Python — programmation générale',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-1-1-variables-types-et-conversions',
  '1.1 Variables, types et conversions',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 1.1 Variables, types et conversions\n'
  '\n'
  '```\n'
  'name = "Alex"age = 28price = 19.99is_active = Truedata = '
  'Noneprint(type(name))print(type(age))print(type(price))number = int("42")decimal = float("12.5")text = '
  'str(100)boolean = bool(1)print(number, decimal, text, boolean)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-1-2-manipulation-avance-des-chanes',
  '1.2 Manipulation avancée des chaînes',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 1.2 Manipulation avancée des chaînes\n'
  '\n'
  '```\n'
  'text = "  programmation informatique  '
  '"print(text.upper())print(text.lower())print(text.strip())print(text.title())print(text.replace("informatique", '
  '"logicielle"))print(text.split())words = ["Python", "JavaScript", "Rust"]sentence = " - '
  '".join(words)print(sentence)message = "Bonjour {} !".format("Alex")print(message)name = "Alex"message = f"Bonjour '
  '{name}"print(message)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-1-3-listes-tuples-ensembles-et-dictionnaires',
  '1.3 Listes, tuples, ensembles et dictionnaires',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 1.3 Listes, tuples, ensembles et dictionnaires\n'
  '\n'
  '```\n'
  'numbers = [10, 20, 30, 40, 50]numbers.append(60)numbers.insert(0, '
  '5)numbers.remove(30)print(numbers)print(numbers[0])print(numbers[-1])print(numbers[1:4])coordinates = (10, '
  '20)unique_values = {1, 2, 2, 3, 4}user = {    "name": "Alex",    "age": 28,    "role": "developer"}user["active"] = '
  'Truefor key, value in user.items():    print(key, value)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-1-4-comprhensions',
  '1.4 Compréhensions',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 1.4 Compréhensions\n'
  '\n'
  '```\n'
  'squares = [x ** 2 for x in range(20)]even_numbers = [    x for x in range(100)    if x % 2 == 0]dictionary = {    '
  'str(x): x ** 2    for x in range(10)}unique_lengths = {    len(word)    for word in ["Python", "Java", "Rust", '
  '"Python"]}print(squares)print(even_numbers)print(dictionary)print(unique_lengths)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-1-5-fonctions-avances',
  '1.5 Fonctions avancées',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 1.5 Fonctions avancées\n'
  '\n'
  '```\n'
  'def calculate(a, b, operation="add"):    operations = {        "add": lambda x, y: x + y,        "subtract": lambda '
  'x, y: x - y,        "multiply": lambda x, y: x * y,        "divide": lambda x, y: x / y if y != 0 else None    }    '
  'if operation not in operations:        raise ValueError("Opération inconnue")    return operations[operation](a, '
  'b)print(calculate(10, 5))print(calculate(10, 5, "multiply"))print(calculate(10, 5, "divide"))\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-1-6-dcorateurs',
  '1.6 Décorateurs',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 1.6 Décorateurs\n'
  '\n'
  '```\n'
  'import timefrom functools import wrapsdef execution_time(function):    @wraps(function)    def wrapper(*args, '
  '**kwargs):        start = time.perf_counter()        result = function(*args, **kwargs)        duration = '
  'time.perf_counter() - start        print(f"Temps : {duration:.6f} secondes")        return result    return '
  'wrapper@execution_timedef calculate_sum():    return sum(range(1_000_000))print(calculate_sum())\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-1-7-gnrateurs',
  '1.7 Générateurs',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 1.7 Générateurs\n'
  '\n'
  '```\n'
  'def generate_numbers(limit):    for number in range(limit):        yield numberfor value in '
  'generate_numbers(10):    print(value)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-1-8-classes-et-hritage',
  '1.8 Classes et héritage',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 1.8 Classes et héritage\n'
  '\n'
  '```\n'
  'class Animal:    def __init__(self, name):        self.name = name    def speak(self):        return "Son '
  'inconnu"class Dog(Animal):    def speak(self):        return "Woof!"class Cat(Animal):    def speak(self):        '
  'return "Meow!"animals = [    Dog("Max"),    Cat("Luna")]for animal in animals:    print(animal.name, '
  'animal.speak())\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-1-9-dataclasses',
  '1.9 Dataclasses',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 1.9 Dataclasses\n'
  '\n'
  '```\n'
  'from dataclasses import dataclass, field@dataclassclass Product:    name: str    price: float    tags: list[str] = '
  'field(default_factory=list)    def discounted_price(self, percentage):        return self.price * (1 - percentage / '
  '100)product = Product(    name="Laptop",    price=1200,    tags=["computer", '
  '"electronics"])print(product.discounted_price(15))\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-1-10-gestion-des-erreurs',
  '1.10 Gestion des erreurs',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 1.10 Gestion des erreurs\n'
  '\n'
  '```\n'
  'class InsufficientBalanceError(Exception):    passclass Account:    def __init__(self, balance):        '
  'self.balance = balance    def withdraw(self, amount):        if amount <= 0:            raise ValueError("Montant '
  'invalide")        if amount > self.balance:            raise InsufficientBalanceError("Solde insuffisant")        '
  'self.balance -= amount        return self.balanceaccount = Account(500)try:    print(account.withdraw(100))except '
  '(ValueError, InsufficientBalanceError) as error:    print("Erreur :", error)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-2-python-fichiers-systmes-et-automatisation',
  '2. Python — fichiers, systèmes et automatisation',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 2. Python — fichiers, systèmes et automatisation',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-2-1-parcourir-tous-les-fichiers-d-un-dossier',
  "2.1 Parcourir tous les fichiers d'un dossier",
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  "## 2.1 Parcourir tous les fichiers d'un dossier\n"
  '\n'
  '```\n'
  'from pathlib import Pathdirectory = Path("documents")for path in directory.rglob("*"):    if path.is_file():        '
  'print(path.name, path.suffix, path.stat().st_size)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-2-2-copier-un-dossier-complet',
  '2.2 Copier un dossier complet',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 2.2 Copier un dossier complet\n'
  '\n'
  '```\n'
  'import shutilfrom pathlib import Pathsource = Path("source")destination = Path("backup")if source.exists():    '
  'shutil.copytree(        source,        destination,        dirs_exist_ok=True    )print("Copie terminée")\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-2-3-lire-plusieurs-formats',
  '2.3 Lire plusieurs formats',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 2.3 Lire plusieurs formats\n'
  '\n'
  '```\n'
  'import jsonimport csvfrom pathlib import Pathjson_path = Path("data.json")if json_path.exists():    with '
  'json_path.open(encoding="utf-8") as file:        data = json.load(file)    print(data)with open("data.csv", '
  'newline="", encoding="utf-8") as file:    reader = csv.DictReader(file)    for row in reader:        print(row)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-2-4-surveiller-un-dossier',
  '2.4 Surveiller un dossier',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 2.4 Surveiller un dossier\n'
  '\n'
  '```\n'
  'from watchdog.observers import Observerfrom watchdog.events import FileSystemEventHandlerimport timeclass '
  'FileHandler(FileSystemEventHandler):    def on_created(self, event):        print("Création :", event.src_path)    '
  'def on_modified(self, event):        print("Modification :", event.src_path)    def on_deleted(self, event):        '
  'print("Suppression :", event.src_path)observer = Observer()observer.schedule(    FileHandler(),    path=".",    '
  'recursive=True)observer.start()try:    while True:        time.sleep(1)finally:    observer.stop()    '
  'observer.join()\n'
  '```\n'
  '\n'
  'Installation :\n'
  '\n'
  '```\n'
  'pip install watchdog\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-2-5-excuter-un-programme-externe',
  '2.5 Exécuter un programme externe',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 2.5 Exécuter un programme externe\n'
  '\n'
  '```\n'
  'import subprocessresult = subprocess.run(    ["python", "--version"],    capture_output=True,    text=True,    '
  'timeout=10,    check=True)print(result.stdout)print(result.stderr)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-2-6-crer-un-fichier-zip',
  '2.6 Créer un fichier ZIP',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 2.6 Créer un fichier ZIP\n'
  '\n'
  '```\n'
  'from zipfile import ZipFile, ZIP_DEFLATEDfrom pathlib import Pathfolder = Path("documents")with '
  'ZipFile("archive.zip", "w", ZIP_DEFLATED) as archive:    for file in folder.rglob("*"):        if '
  'file.is_file():            archive.write(                file,                '
  'arcname=file.relative_to(folder)            )\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-3-python-rseau-http-et-api',
  '3. Python — réseau, HTTP et API',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 3. Python — réseau, HTTP et API',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-3-1-requte-http',
  '3.1 Requête HTTP',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 3.1 Requête HTTP\n'
  '\n'
  '```\n'
  'import requestsurl = "https://httpbin.org/get"response = requests.get(    url,    params={"page": 1},    '
  'timeout=15)response.raise_for_status()print(response.status_code)print(response.headers)print(response.text)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-3-2-client-api-rutilisable',
  '3.2 Client API réutilisable',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 3.2 Client API réutilisable\n'
  '\n'
  '```\n'
  'import requestsclass APIClient:    def __init__(self, base_url, token=None):        self.base_url = '
  'base_url.rstrip("/")        self.session = requests.Session()        if token:            '
  'self.session.headers.update({                "Authorization": f"Bearer {token}"            })    def get(self, '
  'endpoint, params=None):        response = self.session.get(            '
  'f"{self.base_url}/{endpoint.lstrip(\'/\')}",            params=params,            timeout=15        )        '
  'response.raise_for_status()        return response.json()    def post(self, endpoint, payload):        response = '
  'self.session.post(            f"{self.base_url}/{endpoint.lstrip(\'/\')}",            json=payload,            '
  'timeout=15        )        response.raise_for_status()        return response.json()\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-3-3-requtes-asynchrones',
  '3.3 Requêtes asynchrones',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 3.3 Requêtes asynchrones\n'
  '\n'
  '```\n'
  'import asyncioimport httpxasync def fetch(client, url):    response = await client.get(url)    '
  'response.raise_for_status()    return response.status_codeasync def main():    urls = [        '
  '"https://example.com",        "https://httpbin.org/get",        "https://api.github.com"    ]    async with '
  'httpx.AsyncClient(timeout=15) as client:        results = await asyncio.gather(            *(fetch(client, url) for '
  'url in urls),            return_exceptions=True        )    for result in results:        '
  'print(result)asyncio.run(main())\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-3-4-vrifier-la-disponibilit-d-un-site',
  "3.4 Vérifier la disponibilité d'un site",
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  "## 3.4 Vérifier la disponibilité d'un site\n"
  '\n'
  '```\n'
  'import requestsdef check_website(url):    try:        response = requests.get(            url,            '
  'timeout=10,            allow_redirects=True        )        return {            "url": url,            "status": '
  'response.status_code,            "available": response.ok,            "final_url": response.url        }    except '
  'requests.RequestException as error:        return {            "url": url,            "available": '
  'False,            "error": str(error)        }print(check_website("https://example.com"))\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-3-5-tlcharger-un-fichier-avec-vrification',
  '3.5 Télécharger un fichier avec vérification',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 3.5 Télécharger un fichier avec vérification\n'
  '\n'
  '```\n'
  'import requestsfrom pathlib import Pathurl = "https://example.com/robots.txt"destination = Path("robots.txt")with '
  'requests.get(url, stream=True, timeout=20) as response:    response.raise_for_status()    with '
  'destination.open("wb") as file:        for chunk in response.iter_content(chunk_size=8192):            if '
  'chunk:                file.write(chunk)print("Téléchargement terminé")\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-3-6-pagination-api',
  '3.6 Pagination API',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 3.6 Pagination API\n'
  '\n'
  '```\n'
  'import requestsdef fetch_all_pages(base_url):    page = 1    results = []    while True:        response = '
  'requests.get(            base_url,            params={"page": page},            timeout=15        )        '
  'response.raise_for_status()        data = response.json()        items = data.get("results", [])        if not '
  'items:            break        results.extend(items)        page += 1    return results\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-4-python-algorithmes-et-mathmatiques',
  '4. Python — algorithmes et mathématiques',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 4. Python — algorithmes et mathématiques',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-4-1-factorielle',
  '4.1 Factorielle',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 4.1 Factorielle\n'
  '\n'
  '```\n'
  'def factorial(n):    if n < 0:        raise ValueError("Nombre négatif")    result = 1    for value in range(2, n + '
  '1):        result *= value    return resultprint(factorial(10))\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-4-2-suite-de-fibonacci',
  '4.2 Suite de Fibonacci',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 4.2 Suite de Fibonacci\n'
  '\n'
  '```\n'
  'def fibonacci(n):    a, b = 0, 1    results = []    for _ in range(n):        results.append(a)        a, b = b, a '
  '+ b    return resultsprint(fibonacci(20))\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-4-3-nombres-premiers',
  '4.3 Nombres premiers',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 4.3 Nombres premiers\n'
  '\n'
  '```\n'
  'def is_prime(number):    if number < 2:        return False    if number == 2:        return True    if number % 2 '
  '== 0:        return False    divisor = 3    while divisor * divisor <= number:        if number % divisor == '
  '0:            return False        divisor += 2    return Trueprimes = [    number    for number in range(2, '
  '1000)    if is_prime(number)]print(primes)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-4-4-tri-rapide',
  '4.4 Tri rapide',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 4.4 Tri rapide\n'
  '\n'
  '```\n'
  'def quicksort(values):    if len(values) <= 1:        return values    pivot = values[len(values) // 2]    lower = '
  '[x for x in values if x < pivot]    equal = [x for x in values if x == pivot]    greater = [x for x in values if x '
  '> pivot]    return quicksort(lower) + equal + quicksort(greater)print(quicksort([9, 3, 5, 1, 8, 2]))\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-4-5-recherche-binaire',
  '4.5 Recherche binaire',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 4.5 Recherche binaire\n'
  '\n'
  '```\n'
  'def binary_search(array, target):    left = 0    right = len(array) - 1    while left <= right:        middle = '
  '(left + right) // 2        if array[middle] == target:            return middle        if array[middle] < '
  'target:            left = middle + 1        else:            right = middle - 1    return -1\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-4-6-matrices-avec-numpy',
  '4.6 Matrices avec NumPy',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 4.6 Matrices avec NumPy\n'
  '\n'
  '```\n'
  'import numpy as npA = np.array([    [1, 2],    [3, 4]])B = np.array([    [5, 6],    [7, 8]])print(A + B)print(A @ '
  'B)print(A.T)print(np.linalg.det(A))print(np.linalg.inv(A))\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-5-javascript-programmation-avance',
  '5. JavaScript — programmation avancée',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 5. JavaScript — programmation avancée',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-5-1-manipulation-des-tableaux',
  '5.1 Manipulation des tableaux',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 5.1 Manipulation des tableaux\n'
  '\n'
  '```\n'
  'const products = [\n'
  '    { name: "A", price: 10 },\n'
  '    { name: "B", price: 25 },\n'
  '    { name: "C", price: 40 }\n'
  '];\n'
  '\n'
  'const expensive = products.filter(p => p.price > 20);\n'
  '\n'
  'const names = products.map(p => p.name);\n'
  '\n'
  'const total = products.reduce(\n'
  '    (sum, product) => sum + product.price,\n'
  '    0\n'
  ');\n'
  '\n'
  'console.log(expensive, names, total);\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-5-2-classes',
  '5.2 Classes',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 5.2 Classes\n'
  '\n'
  '```\n'
  'class BankAccount {\n'
  '    constructor(owner, balance = 0) {\n'
  '        this.owner = owner;\n'
  '        this.balance = balance;\n'
  '    }\n'
  '\n'
  '    deposit(amount) {\n'
  '        if (amount <= 0) {\n'
  '            throw new Error("Invalid amount");\n'
  '        }\n'
  '\n'
  '        this.balance += amount;\n'
  '    }\n'
  '\n'
  '    withdraw(amount) {\n'
  '        if (amount <= 0 || amount > this.balance) {\n'
  '            throw new Error("Invalid withdrawal");\n'
  '        }\n'
  '\n'
  '        this.balance -= amount;\n'
  '    }\n'
  '}\n'
  '\n'
  'const account = new BankAccount("Alex", 1000);\n'
  '\n'
  'account.deposit(500);\n'
  'account.withdraw(200);\n'
  '\n'
  'console.log(account.balance);\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-5-3-promesses',
  '5.3 Promesses',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 5.3 Promesses\n'
  '\n'
  '```\n'
  'function delay(milliseconds) {\n'
  '    return new Promise(resolve => {\n'
  '        setTimeout(resolve, milliseconds);\n'
  '    });\n'
  '}\n'
  '\n'
  'async function main() {\n'
  '    console.log("Début");\n'
  '\n'
  '    await delay(1000);\n'
  '\n'
  '    console.log("Fin");\n'
  '}\n'
  '\n'
  'main();\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-5-4-gestion-des-erreurs-asynchrones',
  '5.4 Gestion des erreurs asynchrones',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 5.4 Gestion des erreurs asynchrones\n'
  '\n'
  '```\n'
  'async function fetchJSON(url) {\n'
  '    const response = await fetch(url);\n'
  '\n'
  '    if (!response.ok) {\n'
  '        throw new Error(`HTTP ${response.status}`);\n'
  '    }\n'
  '\n'
  '    return response.json();\n'
  '}\n'
  '\n'
  'async function main() {\n'
  '    try {\n'
  '        const data = await fetchJSON(\n'
  '            "https://api.github.com"\n'
  '        );\n'
  '\n'
  '        console.log(data);\n'
  '    } catch (error) {\n'
  '        console.error(error);\n'
  '    }\n'
  '}\n'
  '\n'
  'main();\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-5-5-eventemitter',
  '5.5 EventEmitter',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 5.5 EventEmitter\n'
  '\n'
  '```\n'
  'import { EventEmitter } from "node:events";\n'
  '\n'
  'const events = new EventEmitter();\n'
  '\n'
  'events.on("user.created", user => {\n'
  '    console.log("Nouvel utilisateur :", user);\n'
  '});\n'
  '\n'
  'events.emit("user.created", {\n'
  '    id: 1,\n'
  '    name: "Alex"\n'
  '});\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-5-6-serveur-http-natif',
  '5.6 Serveur HTTP natif',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 5.6 Serveur HTTP natif\n'
  '\n'
  '```\n'
  'import http from "node:http";\n'
  '\n'
  'const server = http.createServer((request, response) => {\n'
  '    response.writeHead(200, {\n'
  '        "Content-Type": "application/json"\n'
  '    });\n'
  '\n'
  '    response.end(JSON.stringify({\n'
  '        message: "Hello World"\n'
  '    }));\n'
  '});\n'
  '\n'
  'server.listen(3000, () => {\n'
  '    console.log("Serveur sur le port 3000");\n'
  '});\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-6-typescript-typage-et-architecture',
  '6. TypeScript — typage et architecture',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 6. TypeScript — typage et architecture',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-6-1-interfaces-et-types',
  '6.1 Interfaces et types',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 6.1 Interfaces et types\n'
  '\n'
  '```\n'
  'interface Customer {\n'
  '    id: number;\n'
  '    name: string;\n'
  '    email: string;\n'
  '    active: boolean;\n'
  '}\n'
  '\n'
  'type OrderStatus =\n'
  '    | "pending"\n'
  '    | "paid"\n'
  '    | "cancelled";\n'
  '\n'
  'interface Order {\n'
  '    id: number;\n'
  '    customerId: number;\n'
  '    status: OrderStatus;\n'
  '    total: number;\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-6-2-classes-gnriques',
  '6.2 Classes génériques',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 6.2 Classes génériques\n'
  '\n'
  '```\n'
  'class Repository<T extends { id: number }> {\n'
  '    private items: T[] = [];\n'
  '\n'
  '    add(item: T): void {\n'
  '        this.items.push(item);\n'
  '    }\n'
  '\n'
  '    findById(id: number): T | undefined {\n'
  '        return this.items.find(item => item.id === id);\n'
  '    }\n'
  '\n'
  '    getAll(): T[] {\n'
  '        return [...this.items];\n'
  '    }\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-6-3-validation-avec-zod',
  '6.3 Validation avec Zod',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 6.3 Validation avec Zod\n'
  '\n'
  '```\n'
  'import { z } from "zod";\n'
  '\n'
  'const UserSchema = z.object({\n'
  '    name: z.string().min(2),\n'
  '    email: z.string().email(),\n'
  '    age: z.number().int().positive()\n'
  '});\n'
  '\n'
  'const result = UserSchema.safeParse({\n'
  '    name: "Alex",\n'
  '    email: "alex@example.com",\n'
  '    age: 28\n'
  '});\n'
  '\n'
  'if (result.success) {\n'
  '    console.log(result.data);\n'
  '} else {\n'
  '    console.error(result.error.issues);\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-7-php-programmation-et-backend',
  '7. PHP — programmation et backend',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 7. PHP — programmation et backend',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-7-1-programmation-oriente-objet',
  '7.1 Programmation orientée objet',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 7.1 Programmation orientée objet\n'
  '\n'
  '```\n'
  '<?php\n'
  '\n'
  'class Product {\n'
  '    public function __construct(\n'
  '        private string $name,\n'
  '        private float $price\n'
  '    ) {}\n'
  '\n'
  '    public function getName(): string {\n'
  '        return $this->name;\n'
  '    }\n'
  '\n'
  '    public function getPrice(): float {\n'
  '        return $this->price;\n'
  '    }\n'
  '}\n'
  '\n'
  '$product = new Product("Laptop", 1200);\n'
  '\n'
  'echo $product->getName();\n'
  'echo $product->getPrice();\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-7-2-gestion-des-tableaux',
  '7.2 Gestion des tableaux',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 7.2 Gestion des tableaux\n'
  '\n'
  '```\n'
  '<?php\n'
  '\n'
  '$numbers = [1, 2, 3, 4, 5];\n'
  '\n'
  '$doubled = array_map(\n'
  '    fn($number) => $number * 2,\n'
  '    $numbers\n'
  ');\n'
  '\n'
  '$filtered = array_filter(\n'
  '    $numbers,\n'
  '    fn($number) => $number > 2\n'
  ');\n'
  '\n'
  '$total = array_reduce(\n'
  '    $numbers,\n'
  '    fn($carry, $number) => $carry + $number,\n'
  '    0\n'
  ');\n'
  '\n'
  'print_r($doubled);\n'
  'print_r($filtered);\n'
  'echo $total;\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-7-3-api-json',
  '7.3 API JSON',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 7.3 API JSON\n'
  '\n'
  '```\n'
  '<?php\n'
  '\n'
  'header("Content-Type: application/json");\n'
  '\n'
  '$data = [\n'
  '    "status" => "success",\n'
  '    "message" => "API opérationnelle",\n'
  '    "timestamp" => time()\n'
  '];\n'
  '\n'
  'echo json_encode($data, JSON_PRETTY_PRINT);\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-7-4-pdo-et-sql',
  '7.4 PDO et SQL',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 7.4 PDO et SQL\n'
  '\n'
  '```\n'
  '<?php\n'
  '\n'
  '$pdo = new PDO(\n'
  '    "sqlite:database.db",\n'
  '    null,\n'
  '    null,\n'
  '    [\n'
  '        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION\n'
  '    ]\n'
  ');\n'
  '\n'
  '$stmt = $pdo->prepare(\n'
  '    "SELECT * FROM users WHERE id = :id"\n'
  ');\n'
  '\n'
  '$stmt->execute(["id" => 1]);\n'
  '\n'
  '$user = $stmt->fetch(PDO::FETCH_ASSOC);\n'
  '\n'
  'print_r($user);\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-8-java-objets-collections-et-concurrence',
  '8. Java — objets, collections et concurrence',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 8. Java — objets, collections et concurrence',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-8-1-collections',
  '8.1 Collections',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 8.1 Collections\n'
  '\n'
  '```\n'
  'import java.util.*;\n'
  '\n'
  'public class Main {\n'
  '    public static void main(String[] args) {\n'
  '        List<String> names = new ArrayList<>();\n'
  '\n'
  '        names.add("Alex");\n'
  '        names.add("Sam");\n'
  '        names.add("Jordan");\n'
  '\n'
  '        names.forEach(System.out::println);\n'
  '    }\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-8-2-streams',
  '8.2 Streams',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 8.2 Streams\n'
  '\n'
  '```\n'
  'import java.util.List;\n'
  '\n'
  'public class Main {\n'
  '    public static void main(String[] args) {\n'
  '        List<Integer> numbers =\n'
  '            List.of(1, 2, 3, 4, 5, 6);\n'
  '\n'
  '        List<Integer> results = numbers.stream()\n'
  '            .filter(n -> n % 2 == 0)\n'
  '            .map(n -> n * 10)\n'
  '            .toList();\n'
  '\n'
  '        System.out.println(results);\n'
  '    }\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-8-3-threads',
  '8.3 Threads',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 8.3 Threads\n'
  '\n'
  '```\n'
  'public class Main {\n'
  '    public static void main(String[] args)\n'
  '            throws InterruptedException {\n'
  '\n'
  '        Thread worker = new Thread(() -> {\n'
  '            System.out.println("Tâche exécutée");\n'
  '        });\n'
  '\n'
  '        worker.start();\n'
  '        worker.join();\n'
  '    }\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-9-c-et-c-programmation-systme',
  '9. C et C++ — programmation système',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 9. C et C++ — programmation système',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-9-1-c-tableaux-et-fonctions',
  '9.1 C : tableaux et fonctions',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 9.1 C : tableaux et fonctions\n'
  '\n'
  '```\n'
  '#include <stdio.h>\n'
  '\n'
  'int sum(const int values[], int size) {\n'
  '    int result = 0;\n'
  '\n'
  '    for (int i = 0; i < size; i++) {\n'
  '        result += values[i];\n'
  '    }\n'
  '\n'
  '    return result;\n'
  '}\n'
  '\n'
  'int main(void) {\n'
  '    int numbers[] = {1, 2, 3, 4, 5};\n'
  '\n'
  '    printf("Total : %d\\n", sum(numbers, 5));\n'
  '\n'
  '    return 0;\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-9-2-c-allocation-mmoire',
  '9.2 C : allocation mémoire',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 9.2 C : allocation mémoire\n'
  '\n'
  '```\n'
  '#include <stdio.h>\n'
  '#include <stdlib.h>\n'
  '\n'
  'int main(void) {\n'
  '    int *values = malloc(5 * sizeof(int));\n'
  '\n'
  '    if (values == NULL) {\n'
  '        return 1;\n'
  '    }\n'
  '\n'
  '    for (int i = 0; i < 5; i++) {\n'
  '        values[i] = i * 10;\n'
  '    }\n'
  '\n'
  '    for (int i = 0; i < 5; i++) {\n'
  '        printf("%d\\n", values[i]);\n'
  '    }\n'
  '\n'
  '    free(values);\n'
  '\n'
  '    return 0;\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-9-3-c-vector-et-algorithmes',
  '9.3 C++ : vector et algorithmes',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 9.3 C++ : vector et algorithmes\n'
  '\n'
  '```\n'
  '#include <iostream>\n'
  '#include <vector>\n'
  '#include <algorithm>\n'
  '\n'
  'int main() {\n'
  '    std::vector<int> numbers = {9, 2, 5, 1, 7};\n'
  '\n'
  '    std::sort(numbers.begin(), numbers.end());\n'
  '\n'
  '    for (int number : numbers) {\n'
  '        std::cout << number << " ";\n'
  '    }\n'
  '\n'
  '    return 0;\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-9-4-c-programmation-oriente-objet',
  '9.4 C++ : programmation orientée objet',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 9.4 C++ : programmation orientée objet\n'
  '\n'
  '```\n'
  '#include <iostream>\n'
  '#include <string>\n'
  '\n'
  'class User {\n'
  'private:\n'
  '    std::string name;\n'
  '\n'
  'public:\n'
  '    explicit User(std::string value)\n'
  '        : name(std::move(value)) {}\n'
  '\n'
  '    void display() const {\n'
  '        std::cout << name << std::endl;\n'
  '    }\n'
  '};\n'
  '\n'
  'int main() {\n'
  '    User user("Alex");\n'
  '    user.display();\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-10-go-serveurs-et-concurrence',
  '10. Go — serveurs et concurrence',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 10. Go — serveurs et concurrence',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-10-1-goroutines',
  '10.1 Goroutines',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 10.1 Goroutines\n'
  '\n'
  '```\n'
  'package main\n'
  '\n'
  'import (\n'
  '    "fmt"\n'
  '    "sync"\n'
  ')\n'
  '\n'
  'func worker(id int, wg *sync.WaitGroup) {\n'
  '    defer wg.Done()\n'
  '\n'
  '    fmt.Println("Worker", id)\n'
  '}\n'
  '\n'
  'func main() {\n'
  '    var wg sync.WaitGroup\n'
  '\n'
  '    for i := 0; i < 5; i++ {\n'
  '        wg.Add(1)\n'
  '        go worker(i, &wg)\n'
  '    }\n'
  '\n'
  '    wg.Wait()\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-10-2-serveur-http',
  '10.2 Serveur HTTP',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 10.2 Serveur HTTP\n'
  '\n'
  '```\n'
  'package main\n'
  '\n'
  'import (\n'
  '    "encoding/json"\n'
  '    "net/http"\n'
  ')\n'
  '\n'
  'func health(w http.ResponseWriter, r *http.Request) {\n'
  '    w.Header().Set("Content-Type", "application/json")\n'
  '\n'
  '    json.NewEncoder(w).Encode(map[string]string{\n'
  '        "status": "ok",\n'
  '    })\n'
  '}\n'
  '\n'
  'func main() {\n'
  '    http.HandleFunc("/health", health)\n'
  '\n'
  '    http.ListenAndServe(":8080", nil)\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-11-rust-scurit-mmoire-et-performances',
  '11. Rust — sécurité mémoire et performances',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 11. Rust — sécurité mémoire et performances',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-11-1-vecteurs-et-itrateurs',
  '11.1 Vecteurs et itérateurs',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 11.1 Vecteurs et itérateurs\n'
  '\n'
  '```\n'
  'fn main() {\n'
  '    let numbers = vec![1, 2, 3, 4, 5];\n'
  '\n'
  '    let doubled: Vec<i32> = numbers\n'
  '        .iter()\n'
  '        .map(|n| n * 2)\n'
  '        .collect();\n'
  '\n'
  '    println!("{:?}", doubled);\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-11-2-rsultats-et-erreurs',
  '11.2 Résultats et erreurs',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 11.2 Résultats et erreurs\n'
  '\n'
  '```\n'
  'fn divide(a: f64, b: f64) -> Result<f64, String> {\n'
  '    if b == 0.0 {\n'
  '        return Err("Division par zéro".to_string());\n'
  '    }\n'
  '\n'
  '    Ok(a / b)\n'
  '}\n'
  '\n'
  'fn main() {\n'
  '    match divide(10.0, 2.0) {\n'
  '        Ok(result) => println!("{}", result),\n'
  '        Err(error) => println!("{}", error),\n'
  '    }\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-12-sql-requtes-avances',
  '12. SQL — requêtes avancées',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 12. SQL — requêtes avancées',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-12-1-agrgation-et-classement',
  '12.1 Agrégation et classement',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 12.1 Agrégation et classement\n'
  '\n'
  '```\n'
  'SELECT\n'
  '    category,\n'
  '    COUNT(*) AS total_products,\n'
  '    AVG(price) AS average_price,\n'
  '    SUM(price) AS total_value\n'
  'FROM products\n'
  'GROUP BY category\n'
  'HAVING COUNT(*) > 1\n'
  'ORDER BY total_value DESC;\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-12-2-fonctions-de-fentre',
  '12.2 Fonctions de fenêtre',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 12.2 Fonctions de fenêtre\n'
  '\n'
  '```\n'
  'SELECT\n'
  '    name,\n'
  '    category,\n'
  '    price,\n'
  '    ROW_NUMBER() OVER (\n'
  '        PARTITION BY category\n'
  '        ORDER BY price DESC\n'
  '    ) AS ranking\n'
  'FROM products;\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-12-3-common-table-expressions',
  '12.3 Common Table Expressions',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 12.3 Common Table Expressions\n'
  '\n'
  '```\n'
  'WITH expensive_products AS (\n'
  '    SELECT *\n'
  '    FROM products\n'
  '    WHERE price > 100\n'
  ')\n'
  'SELECT\n'
  '    name,\n'
  '    price\n'
  'FROM expensive_products\n'
  'ORDER BY price DESC;\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-12-4-jsonb-postgresql',
  '12.4 JSONB PostgreSQL',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 12.4 JSONB PostgreSQL\n'
  '\n'
  '```\n'
  'CREATE TABLE events (\n'
  '    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,\n'
  '    payload JSONB NOT NULL,\n'
  '    created_at TIMESTAMPTZ DEFAULT NOW()\n'
  ');\n'
  '\n'
  'INSERT INTO events (payload)\n'
  'VALUES (\n'
  '    \'{"type":"user.created","user_id":42}\'::jsonb\n'
  ');\n'
  '\n'
  "SELECT payload ->> 'type'\n"
  'FROM events;\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-12-5-procdure-stocke',
  '12.5 Procédure stockée',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 12.5 Procédure stockée\n'
  '\n'
  '```\n'
  'CREATE OR REPLACE FUNCTION calculate_total(\n'
  '    price NUMERIC,\n'
  '    quantity INTEGER\n'
  ')\n'
  'RETURNS NUMERIC\n'
  'LANGUAGE SQL\n'
  'IMMUTABLE\n'
  'AS $$\n'
  '    SELECT price * quantity;\n'
  '$$;\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-13-html-css-et-animations',
  '13. HTML, CSS et animations',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 13. HTML, CSS et animations',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-13-1-formulaire-html',
  '13.1 Formulaire HTML',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 13.1 Formulaire HTML\n'
  '\n'
  '```\n'
  '<form id="contact-form">\n'
  '    <label for="email">Adresse email</label>\n'
  '\n'
  '    <input\n'
  '        type="email"\n'
  '        id="email"\n'
  '        name="email"\n'
  '        required\n'
  '    >\n'
  '\n'
  '    <button type="submit">\n'
  '        Envoyer\n'
  '    </button>\n'
  '</form>\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-13-2-css-grid',
  '13.2 CSS Grid',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 13.2 CSS Grid\n'
  '\n'
  '```\n'
  '.dashboard {\n'
  '    display: grid;\n'
  '    grid-template-columns: 250px 1fr;\n'
  '    grid-template-rows: 70px 1fr;\n'
  '    min-height: 100vh;\n'
  '}\n'
  '\n'
  '.sidebar {\n'
  '    grid-row: 1 / 3;\n'
  '}\n'
  '\n'
  '.content {\n'
  '    display: grid;\n'
  '    grid-template-columns: repeat(3, 1fr);\n'
  '    gap: 24px;\n'
  '}\n'
  '\n'
  '@media (max-width: 768px) {\n'
  '    .dashboard {\n'
  '        grid-template-columns: 1fr;\n'
  '    }\n'
  '\n'
  '    .content {\n'
  '        grid-template-columns: 1fr;\n'
  '    }\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-13-3-animation-css',
  '13.3 Animation CSS',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 13.3 Animation CSS\n'
  '\n'
  '```\n'
  '@keyframes float {\n'
  '    0%, 100% {\n'
  '        transform: translateY(0);\n'
  '    }\n'
  '\n'
  '    50% {\n'
  '        transform: translateY(-12px);\n'
  '    }\n'
  '}\n'
  '\n'
  '.floating-element {\n'
  '    animation: float 3s ease-in-out infinite;\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-13-4-canvas-javascript',
  '13.4 Canvas JavaScript',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 13.4 Canvas JavaScript\n'
  '\n'
  '```\n'
  '<canvas id="canvas" width="600" height="400"></canvas>\n'
  '\n'
  '<script>\n'
  'const canvas = document.getElementById("canvas");\n'
  'const ctx = canvas.getContext("2d");\n'
  '\n'
  'ctx.fillStyle = "orange";\n'
  'ctx.fillRect(50, 50, 150, 100);\n'
  '\n'
  'ctx.beginPath();\n'
  'ctx.arc(300, 150, 50, 0, Math.PI * 2);\n'
  'ctx.stroke();\n'
  '</script>\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-14-react-et-next-js',
  '14. React et Next.js',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 14. React et Next.js',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-14-1-gestion-d-tat',
  "14.1 Gestion d'état",
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  "## 14.1 Gestion d'état\n"
  '\n'
  '```\n'
  '"use client";\n'
  '\n'
  'import { useState } from "react";\n'
  '\n'
  'export default function Counter() {\n'
  '    const [count, setCount] = useState(0);\n'
  '\n'
  '    return (\n'
  '        <div>\n'
  '            <p>Valeur : {count}</p>\n'
  '\n'
  '            <button onClick={() => setCount(v => v + 1)}>\n'
  '                Ajouter\n'
  '            </button>\n'
  '\n'
  '            <button onClick={() => setCount(0)}>\n'
  '                Réinitialiser\n'
  '            </button>\n'
  '        </div>\n'
  '    );\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-14-2-custom-hook',
  '14.2 Custom Hook',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 14.2 Custom Hook\n'
  '\n'
  '```\n'
  'import { useEffect, useState } from "react";\n'
  '\n'
  'export function useOnlineStatus() {\n'
  '    const [online, setOnline] = useState(true);\n'
  '\n'
  '    useEffect(() => {\n'
  '        const update = () => {\n'
  '            setOnline(navigator.onLine);\n'
  '        };\n'
  '\n'
  '        window.addEventListener("online", update);\n'
  '        window.addEventListener("offline", update);\n'
  '\n'
  '        update();\n'
  '\n'
  '        return () => {\n'
  '            window.removeEventListener("online", update);\n'
  '            window.removeEventListener("offline", update);\n'
  '        };\n'
  '    }, []);\n'
  '\n'
  '    return online;\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-14-3-api-route-next-js',
  '14.3 API Route Next.js',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 14.3 API Route Next.js\n'
  '\n'
  '```\n'
  'import { NextResponse } from "next/server";\n'
  '\n'
  'export async function GET() {\n'
  '    return NextResponse.json({\n'
  '        message: "API opérationnelle",\n'
  '        timestamp: new Date().toISOString()\n'
  '    });\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-14-4-middleware',
  '14.4 Middleware',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 14.4 Middleware\n'
  '\n'
  '```\n'
  'import { NextResponse } from "next/server";\n'
  'import type { NextRequest } from "next/server";\n'
  '\n'
  'export function middleware(request: NextRequest) {\n'
  '    const response = NextResponse.next();\n'
  '\n'
  '    response.headers.set(\n'
  '        "X-Content-Type-Options",\n'
  '        "nosniff"\n'
  '    );\n'
  '\n'
  '    return response;\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-15-api-et-communication-entre-services',
  '15. API et communication entre services',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 15. API et communication entre services',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-15-1-express-avec-validation',
  '15.1 Express avec validation',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 15.1 Express avec validation\n'
  '\n'
  '```\n'
  'import express from "express";\n'
  'import { z } from "zod";\n'
  '\n'
  'const app = express();\n'
  '\n'
  'app.use(express.json());\n'
  '\n'
  'const schema = z.object({\n'
  '    name: z.string().min(2),\n'
  '    email: z.string().email()\n'
  '});\n'
  '\n'
  'app.post("/users", (req, res) => {\n'
  '    const result = schema.safeParse(req.body);\n'
  '\n'
  '    if (!result.success) {\n'
  '        return res.status(400).json({\n'
  '            errors: result.error.issues\n'
  '        });\n'
  '    }\n'
  '\n'
  '    return res.status(201).json({\n'
  '        user: result.data\n'
  '    });\n'
  '});\n'
  '\n'
  'app.listen(3000);\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-15-2-fastapi-avec-pydantic',
  '15.2 FastAPI avec Pydantic',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 15.2 FastAPI avec Pydantic\n'
  '\n'
  '```\n'
  'from fastapi import FastAPIfrom pydantic import BaseModel, EmailStrapp = FastAPI()class User(BaseModel):    name: '
  'str    email: EmailStr@app.post("/users")def create_user(user: User):    return {        "message": "Utilisateur '
  'créé",        "user": user    }\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-15-3-websocket',
  '15.3 WebSocket',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 15.3 WebSocket\n'
  '\n'
  '```\n'
  'from fastapi import FastAPI, WebSocketapp = FastAPI()@app.websocket("/ws")async def websocket_endpoint(websocket: '
  'WebSocket):    await websocket.accept()    try:        while True:            message = await '
  'websocket.receive_text()            await websocket.send_text(                f"Message reçu : '
  '{message}"            )    except Exception:        await websocket.close()\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-16-automatisation-et-tches-planifies',
  '16. Automatisation et tâches planifiées',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 16. Automatisation et tâches planifiées',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-16-1-threading-python',
  '16.1 Threading Python',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 16.1 Threading Python\n'
  '\n'
  '```\n'
  'from threading import Threadimport timedef task(name):    print("Début :", name)    time.sleep(2)    print("Fin :", '
  'name)threads = [    Thread(target=task, args=(f"Task {i}",))    for i in range(5)]for thread in threads:    '
  'thread.start()for thread in threads:    thread.join()\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-16-2-planificateur-apscheduler',
  '16.2 Planificateur APScheduler',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 16.2 Planificateur APScheduler\n'
  '\n'
  '```\n'
  'from apscheduler.schedulers.blocking import BlockingSchedulerfrom datetime import datetimedef scheduled_task():    '
  'print("Exécution :", datetime.now())scheduler = BlockingScheduler()scheduler.add_job(    scheduled_task,    '
  '"interval",    minutes=5)scheduler.start()\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-16-3-file-de-tches-avec-celery',
  '16.3 File de tâches avec Celery',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 16.3 File de tâches avec Celery\n'
  '\n'
  '```\n'
  'from celery import Celeryapp = Celery(    "tasks",    broker="redis://localhost:6379/0")@app.taskdef add(a, b):    '
  'return a + b\n'
  '```\n'
  '\n'
  'Exécution :\n'
  '\n'
  '```\n'
  'celery -A tasks worker --loglevel=info\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-16-4-workflow-prefect',
  '16.4 Workflow Prefect',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 16.4 Workflow Prefect\n'
  '\n'
  '```\n'
  'from prefect import flow, task@taskdef extract():    return [10, 20, 30]@taskdef transform(values):    return '
  '[value * 2 for value in values]@taskdef load(values):    print(values)@flowdef data_pipeline():    data = '
  'extract()    transformed = transform(data)    load(transformed)if __name__ == "__main__":    data_pipeline()\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-17-scraping-et-extraction-de-donnes',
  '17. Scraping et extraction de données',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 17. Scraping et extraction de données',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-17-1-beautifulsoup',
  '17.1 BeautifulSoup',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 17.1 BeautifulSoup\n'
  '\n'
  '```\n'
  'import requestsfrom bs4 import BeautifulSoupurl = "https://quotes.toscrape.com/"response = requests.get(url, '
  'timeout=15)response.raise_for_status()soup = BeautifulSoup(response.text, "html.parser")for item in '
  'soup.select(".quote"):    quote = item.select_one(".text")    author = item.select_one(".author")    print({        '
  '"quote": quote.get_text(strip=True),        "author": author.get_text(strip=True)    })\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-17-2-extraction-avec-lxml',
  '17.2 Extraction avec lxml',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 17.2 Extraction avec lxml\n'
  '\n'
  '```\n'
  'import requestsfrom lxml import htmlresponse = requests.get(    "https://example.com",    '
  'timeout=10)response.raise_for_status()document = html.fromstring(response.content)titles = '
  'document.xpath("//h1/text()")print(titles)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-17-3-playwright',
  '17.3 Playwright',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 17.3 Playwright\n'
  '\n'
  '```\n'
  'from playwright.sync_api import sync_playwrightwith sync_playwright() as p:    browser = '
  'p.chromium.launch(headless=True)    page = browser.new_page()    page.goto("https://example.com")    title = '
  'page.title()    print(title)    browser.close()\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-17-4-export-csv',
  '17.4 Export CSV',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 17.4 Export CSV\n'
  '\n'
  '```\n'
  'import csvdata = [    {"name": "A", "value": 10},    {"name": "B", "value": 20}]with open("output.csv", "w", '
  'newline="", encoding="utf-8") as file:    writer = csv.DictWriter(        file,        fieldnames=["name", '
  '"value"]    )    writer.writeheader()    writer.writerows(data)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-18-linux-bash-et-administration-systme',
  '18. Linux, Bash et administration système',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 18. Linux, Bash et administration système',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-18-1-scripts-de-sauvegarde',
  '18.1 Scripts de sauvegarde',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 18.1 Scripts de sauvegarde\n'
  '\n'
  '```\n'
  '#!/usr/bin/env bash\n'
  '\n'
  'set -euo pipefail\n'
  '\n'
  'SOURCE="$HOME/documents"\n'
  'DESTINATION="$HOME/backups"\n'
  '\n'
  'mkdir -p "$DESTINATION"\n'
  '\n'
  'DATE=$(date +%Y-%m-%d_%H-%M-%S)\n'
  '\n'
  'tar -czf "$DESTINATION/backup_$DATE.tar.gz" \\\n'
  '    -C "$SOURCE" .\n'
  '\n'
  'echo "Sauvegarde terminée"\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-18-2-recherche-de-fichiers-volumineux',
  '18.2 Recherche de fichiers volumineux',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 18.2 Recherche de fichiers volumineux\n'
  '\n'
  '```\n'
  'find . -type f -size +100M -print\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-18-3-afficher-les-processus',
  '18.3 Afficher les processus',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 18.3 Afficher les processus\n'
  '\n'
  '```\n'
  'ps aux\n'
  'top\n'
  'pgrep -a python\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-18-4-espace-disque',
  '18.4 Espace disque',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 18.4 Espace disque\n'
  '\n'
  '```\n'
  'df -h\n'
  'du -sh *\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-18-5-journaux-systme',
  '18.5 Journaux système',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 18.5 Journaux système\n'
  '\n'
  '```\n'
  'journalctl -n 100\n'
  'journalctl -u nginx\n'
  'journalctl -f\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-19-docker-et-kubernetes',
  '19. Docker et Kubernetes',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 19. Docker et Kubernetes',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-19-1-docker-compose-avec-postgresql',
  '19.1 Docker Compose avec PostgreSQL',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 19.1 Docker Compose avec PostgreSQL\n'
  '\n'
  '```\n'
  'services:\n'
  '  database:\n'
  '    image: postgres:17\n'
  '    environment:\n'
  '      POSTGRES_DB: app\n'
  '      POSTGRES_USER: app\n'
  '      POSTGRES_PASSWORD: ${DB_PASSWORD}\n'
  '    volumes:\n'
  '      - postgres_data:/var/lib/postgresql/data\n'
  '    ports:\n'
  '      - "5432:5432"\n'
  '\n'
  'volumes:\n'
  '  postgres_data:\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-19-2-kubernetes-deployment',
  '19.2 Kubernetes Deployment',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 19.2 Kubernetes Deployment\n'
  '\n'
  '```\n'
  'apiVersion: apps/v1\n'
  'kind: Deployment\n'
  '\n'
  'metadata:\n'
  '  name: web-app\n'
  '\n'
  'spec:\n'
  '  replicas: 2\n'
  '\n'
  '  selector:\n'
  '    matchLabels:\n'
  '      app: web-app\n'
  '\n'
  '  template:\n'
  '    metadata:\n'
  '      labels:\n'
  '        app: web-app\n'
  '\n'
  '    spec:\n'
  '      containers:\n'
  '        - name: web\n'
  '          image: nginx:stable\n'
  '          ports:\n'
  '            - containerPort: 80\n'
  '```\n'
  '\n'
  'Commandes :\n'
  '\n'
  '```\n'
  'kubectl get pods\n'
  'kubectl get deployments\n'
  'kubectl describe pod POD_NAME\n'
  'kubectl logs POD_NAME\n'
  'kubectl apply -f deployment.yaml\n'
  'kubectl rollout status deployment/web-app\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-20-data-science-et-statistiques',
  '20. Data science et statistiques',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 20. Data science et statistiques',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-20-1-analyse-avec-pandas',
  '20.1 Analyse avec pandas',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 20.1 Analyse avec pandas\n'
  '\n'
  '```\n'
  'import pandas as pddf = pd.DataFrame({    "product": ["A", "B", "C", "D"],    "sales": [100, 250, 175, 300],    '
  '"category": ["X", "Y", "X", "Y"]})print(df.describe())print(    df.groupby("category")["sales"].agg(        ["sum", '
  '"mean", "count"]    ))\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-20-2-corrlation',
  '20.2 Corrélation',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 20.2 Corrélation\n'
  '\n'
  '```\n'
  'import pandas as pddata = pd.DataFrame({    "advertising": [10, 20, 30, 40, 50],    "sales": [15, 25, 35, 48, '
  '60]})print(data.corr())\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-20-3-rgression-linaire',
  '20.3 Régression linéaire',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 20.3 Régression linéaire\n'
  '\n'
  '```\n'
  'from sklearn.linear_model import LinearRegressionX = [[1], [2], [3], [4], [5]]y = [2, 4, 6, 8, 10]model = '
  'LinearRegression()model.fit(X, y)print(model.coef_)print(model.intercept_)print(model.predict([[6]]))\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-20-4-clustering',
  '20.4 Clustering',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 20.4 Clustering\n'
  '\n'
  '```\n'
  'from sklearn.cluster import KMeansdata = [    [1, 2],    [1, 3],    [10, 11],    [10, 12]]model = KMeans(    '
  'n_clusters=2,    random_state=42,    n_init=10)model.fit(data)print(model.labels_)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-21-intelligence-artificielle-et-traitement-du-langage',
  '21. Intelligence artificielle et traitement du langage',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 21. Intelligence artificielle et traitement du langage',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-21-1-classification-de-texte',
  '21.1 Classification de texte',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 21.1 Classification de texte\n'
  '\n'
  '```\n'
  'from transformers import pipelineclassifier = pipeline("sentiment-analysis")texts = [    "Ce produit est '
  'excellent.",    "Le service est décevant."]for result in classifier(texts):    print(result)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-21-2-rsum-de-texte',
  '21.2 Résumé de texte',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 21.2 Résumé de texte\n'
  '\n'
  '```\n'
  'from transformers import pipelinesummarizer = pipeline("summarization")text = """L\'informatique regroupe plusieurs '
  "domaines :la programmation, les réseaux, les bases de données,les systèmes et l'intelligence "
  'artificielle."""result = summarizer(    text,    max_length=50,    min_length=10,    do_sample=False)print(result)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-21-3-recherche-smantique',
  '21.3 Recherche sémantique',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 21.3 Recherche sémantique\n'
  '\n'
  '```\n'
  'from sentence_transformers import SentenceTransformerfrom sklearn.metrics.pairwise import cosine_similaritymodel = '
  'SentenceTransformer(    "all-MiniLM-L6-v2")documents = [    "Python est un langage de programmation.",    '
  '"PostgreSQL est une base de données.",    "Docker permet de créer des conteneurs."]query = "Quel outil sert à '
  'stocker des données ?"document_vectors = model.encode(documents)query_vector = model.encode([query])scores = '
  'cosine_similarity(    query_vector,    document_vectors)[0]best_index = '
  'scores.argmax()print(documents[best_index])\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-21-4-calcul-matriciel-avec-pytorch',
  '21.4 Calcul matriciel avec PyTorch',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 21.4 Calcul matriciel avec PyTorch\n'
  '\n'
  '```\n'
  'import torchx = torch.tensor(    [[1.0, 2.0], [3.0, 4.0]])y = torch.tensor(    [[5.0, 6.0], [7.0, 8.0]])print(x + '
  'y)print(x @ y)print(x.mean())\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-22-cryptographie-et-scurit-informatique-dfensive',
  '22. Cryptographie et sécurité informatique défensive',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 22. Cryptographie et sécurité informatique défensive',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-22-1-gnration-de-cls-alatoires',
  '22.1 Génération de clés aléatoires',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 22.1 Génération de clés aléatoires\n'
  '\n'
  '```\n'
  'import secretssecret = secrets.token_urlsafe(48)print(secret)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-22-2-hmac',
  '22.2 HMAC',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 22.2 HMAC\n'
  '\n'
  '```\n'
  'import hmacimport hashlibkey = b"example-secret"message = b"important-message"signature = hmac.new(    key,    '
  'message,    hashlib.sha256).hexdigest()print(signature)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-22-3-vrifier-une-signature',
  '22.3 Vérifier une signature',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 22.3 Vérifier une signature\n'
  '\n'
  '```\n'
  'import hmacexpected = "signature-attendue"received = "signature-recue"valid = hmac.compare_digest(    expected,    '
  'received)print(valid)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-22-4-chiffrement-fernet',
  '22.4 Chiffrement Fernet',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## 22.4 Chiffrement Fernet\n'
  '\n'
  '```\n'
  'from cryptography.fernet import Fernetkey = Fernet.generate_key()cipher = Fernet(key)encrypted = cipher.encrypt(    '
  'b"Information confidentielle")decrypted = cipher.decrypt(encrypted)print(decrypted.decode())\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-22-5-gnration-d-un-certificat-de-dveloppement',
  "22.5 Génération d'un certificat de développement",
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  "## 22.5 Génération d'un certificat de développement\n"
  '\n'
  '```\n'
  'openssl req -x509 -newkey rsa:3072 \\\n'
  '  -keyout private.key \\\n'
  '  -out certificate.crt \\\n'
  '  -days 30 \\\n'
  '  -nodes\n'
  '```\n'
  '\n'
  'À réserver aux environnements de test ; ne pas utiliser ce certificat auto-signé comme solution de confiance en '
  'production.',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-23-commandes-de-compilation-et-d-excution',
  "23. Commandes de compilation et d'exécution",
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  "# 23. Commandes de compilation et d'exécution",
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-python-section-3',
  'Python',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Python\n'
  '\n'
  '```\n'
  'python main.py\n'
  'python -m compileall .\n'
  'python -m unittest\n'
  'python -m pytest\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-javascript-section-2',
  'JavaScript',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## JavaScript\n'
  '\n'
  '```\n'
  'node index.js\n'
  'npm run dev\n'
  'npm run build\n'
  'npm test\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-typescript',
  'TypeScript',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## TypeScript\n'
  '\n'
  '```\n'
  'npx tsc\n'
  'npx tsc --noEmit\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-php',
  'PHP',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PHP\n'
  '\n'
  '```\n'
  'php main.php\n'
  'php -l main.php\n'
  'composer validate\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-java',
  'Java',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Java\n'
  '\n'
  '```\n'
  'javac Main.java\n'
  'java Main\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-c-section-1',
  'C',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## C\n'
  '\n'
  '```\n'
  'gcc -Wall -Wextra -O2 main.c -o main\n'
  './main\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-c',
  'C++',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## C++\n'
  '\n'
  '```\n'
  'g++ -std=c++20 -Wall -Wextra main.cpp -o main\n'
  './main\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-go',
  'Go',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Go\n'
  '\n'
  '```\n'
  'go run .\n'
  'go build\n'
  'go test ./...\n'
  'go vet ./...\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-rust',
  'Rust',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Rust\n'
  '\n'
  '```\n'
  'cargo run\n'
  'cargo build --release\n'
  'cargo test\n'
  'cargo fmt\n'
  'cargo clippy\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-24-formats-de-fichiers-et-configurations',
  '24. Formats de fichiers et configurations',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 24. Formats de fichiers et configurations',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-json',
  'JSON',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## JSON\n'
  '\n'
  '```\n'
  '{\n'
  '  "application": "Example",\n'
  '  "version": "1.0.0",\n'
  '  "environment": "development",\n'
  '  "features": {\n'
  '    "logging": true,\n'
  '    "cache": false\n'
  '  }\n'
  '}\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-yaml',
  'YAML',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## YAML\n'
  '\n'
  '```\n'
  'application:\n'
  '  name: Example\n'
  '  version: 1.0.0\n'
  '\n'
  'server:\n'
  '  host: 127.0.0.1\n'
  '  port: 8080\n'
  '\n'
  'logging:\n'
  '  enabled: true\n'
  '  level: info\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-toml',
  'TOML',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## TOML\n'
  '\n'
  '```\n'
  '[application]\n'
  'name = "Example"\n'
  'version = "1.0.0"\n'
  '\n'
  '[server]\n'
  'host = "127.0.0.1"\n'
  'port = 8080\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-xml',
  'XML',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## XML\n'
  '\n'
  '```\n'
  '<?xml version="1.0" encoding="UTF-8"?>\n'
  '<application>\n'
  '    <name>Example</name>\n'
  '    <version>1.0.0</version>\n'
  '    <environment>development</environment>\n'
  '</application>\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-25-expressions-rgulires',
  '25. Expressions régulières',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 25. Expressions régulières',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-python-section-2',
  'Python',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Python\n'
  '\n'
  '```\n'
  'import retext = "Contact: alex@example.com"emails = re.findall(    r"[\\w.+-]+@[\\w.-]+\\.[A-Za-z]{2,}",    '
  'text)print(emails)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-javascript-section-1',
  'JavaScript',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## JavaScript\n'
  '\n'
  '```\n'
  'const text = "Order number: ORD-2026-001";\n'
  '\n'
  'const match = text.match(/ORD-\\d{4}-\\d{3}/);\n'
  '\n'
  'console.log(match?.[0]);\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-remplacements',
  'Remplacements',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Remplacements\n'
  '\n'
  '```\n'
  'import retext = "Produit    A       disponible"clean = re.sub(r"\\s+", " ", text)print(clean)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-26-graphes-et-parcours',
  '26. Graphes et parcours',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 26. Graphes et parcours',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-parcours-en-largeur-bfs',
  'Parcours en largeur (BFS)',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Parcours en largeur (BFS)\n'
  '\n'
  '```\n'
  'from collections import dequegraph = {    "A": ["B", "C"],    "B": ["D"],    "C": ["E"],    "D": [],    "E": []}def '
  'bfs(graph, start):    queue = deque([start])    visited = {start}    while queue:        node = '
  'queue.popleft()        print(node)        for neighbor in graph[node]:            if neighbor not in '
  'visited:                visited.add(neighbor)                queue.append(neighbor)bfs(graph, "A")\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-parcours-en-profondeur-dfs',
  'Parcours en profondeur (DFS)',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Parcours en profondeur (DFS)\n'
  '\n'
  '```\n'
  'def dfs(graph, node, visited=None):    if visited is None:        visited = set()    if node in visited:        '
  'return    visited.add(node)    print(node)    for neighbor in graph[node]:        dfs(graph, neighbor, visited)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-27-programmation-fonctionnelle',
  '27. Programmation fonctionnelle',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 27. Programmation fonctionnelle',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-python-section-1',
  'Python',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Python\n'
  '\n'
  '```\n'
  'from functools import reducenumbers = [1, 2, 3, 4, 5]result = reduce(    lambda a, b: a + b,    numbers,    '
  '0)print(result)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-javascript',
  'JavaScript',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## JavaScript\n'
  '\n'
  '```\n'
  'const compose = (...functions) => value =>\n'
  '    functions.reduceRight(\n'
  '        (result, fn) => fn(result),\n'
  '        value\n'
  '    );\n'
  '\n'
  'const double = x => x * 2;\n'
  'const increment = x => x + 1;\n'
  '\n'
  'const operation = compose(double, increment);\n'
  '\n'
  'console.log(operation(5));\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-28-programmation-oriente-vnements',
  '28. Programmation orientée événements',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 28. Programmation orientée événements',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-python',
  'Python',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Python\n'
  '\n'
  '```\n'
  'class EventBus:    def __init__(self):        self.listeners = {}    def subscribe(self, event, callback):        '
  'self.listeners.setdefault(event, []).append(callback)    def publish(self, event, data):        for callback in '
  'self.listeners.get(event, []):            callback(data)bus = EventBus()bus.subscribe(    "user.created",    lambda '
  'data: print("Utilisateur :", data))bus.publish("user.created", {"id": 1})\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-29-tests-unitaires-et-qualit',
  '29. Tests unitaires et qualité',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 29. Tests unitaires et qualité',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-python-unittest',
  'Python unittest',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Python unittest\n'
  '\n'
  '```\n'
  'import unittestdef multiply(a, b):    return a * bclass TestMath(unittest.TestCase):    def '
  'test_multiply(self):        self.assertEqual(multiply(3, 4), 12)    def test_zero(self):        '
  'self.assertEqual(multiply(0, 4), 0)if __name__ == "__main__":    unittest.main()\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-test-de-proprit',
  'Test de propriété',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Test de propriété\n'
  '\n'
  '```\n'
  'from hypothesis import givenfrom hypothesis import strategies as st@given(st.integers())def test_double(value):    '
  'assert value * 2 == value + value\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-30-architecture-logicielle-et-patrons-de-conception',
  '30. Architecture logicielle et patrons de conception',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 30. Architecture logicielle et patrons de conception',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-singleton',
  'Singleton',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Singleton\n'
  '\n'
  '```\n'
  'class Singleton:    _instance = None    def __new__(cls):        if cls._instance is None:            cls._instance '
  '= super().__new__(cls)        return cls._instance\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-factory',
  'Factory',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Factory\n'
  '\n'
  '```\n'
  'class Notification:    def send(self, message):        raise NotImplementedErrorclass '
  'EmailNotification(Notification):    def send(self, message):        print("Email :", message)class '
  'SMSNotification(Notification):    def send(self, message):        print("SMS :", message)def '
  'notification_factory(kind):    factories = {        "email": EmailNotification,        "sms": SMSNotification    '
  '}    if kind not in factories:        raise ValueError("Type inconnu")    return factories[kind]()\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-strategy',
  'Strategy',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Strategy\n'
  '\n'
  '```\n'
  'class DiscountStrategy:    def apply(self, price):        raise NotImplementedErrorclass '
  'NoDiscount(DiscountStrategy):    def apply(self, price):        return priceclass '
  'TenPercentDiscount(DiscountStrategy):    def apply(self, price):        return price * 0.9def checkout(price, '
  'strategy):    return strategy.apply(price)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-31-compilation-optimisation-et-performance',
  '31. Compilation, optimisation et performance',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 31. Compilation, optimisation et performance',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-profilage-python',
  'Profilage Python',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Profilage Python\n'
  '\n'
  '```\n'
  'python -m cProfile -s cumulative main.py\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-analyse-mmoire',
  'Analyse mémoire',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Analyse mémoire\n'
  '\n'
  '```\n'
  'pip install memory-profiler\n'
  'python -m memory_profiler main.py\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-benchmark',
  'Benchmark',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Benchmark\n'
  '\n'
  '```\n'
  'import timeitresult = timeit.timeit(    "sum(range(1000))",    number=10000)print(result)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-profilage-node-js',
  'Profilage Node.js',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Profilage Node.js\n'
  '\n'
  '```\n'
  'node --prof index.js\n'
  'node --trace-warnings index.js\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-32-commandes-de-gestion-des-paquets',
  '32. Commandes de gestion des paquets',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 32. Commandes de gestion des paquets',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-npm',
  'npm',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## npm\n'
  '\n'
  '```\n'
  'npm init -y\n'
  'npm install\n'
  'npm install package-name\n'
  'npm install -D package-name\n'
  'npm uninstall package-name\n'
  'npm update\n'
  'npm audit\n'
  'npm ci\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-pnpm',
  'pnpm',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## pnpm\n'
  '\n'
  '```\n'
  'pnpm init\n'
  'pnpm install\n'
  'pnpm add package-name\n'
  'pnpm add -D package-name\n'
  'pnpm remove package-name\n'
  'pnpm update\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-pip',
  'pip',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## pip\n'
  '\n'
  '```\n'
  'python -m pip install package-name\n'
  'python -m pip uninstall package-name\n'
  'python -m pip list\n'
  'python -m pip check\n'
  'python -m pip freeze\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-composer',
  'Composer',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Composer\n'
  '\n'
  '```\n'
  'composer init\n'
  'composer install\n'
  'composer require vendor/package\n'
  'composer update\n'
  'composer validate\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-cargo',
  'Cargo',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Cargo\n'
  '\n'
  '```\n'
  'cargo new project\n'
  'cargo add package-name\n'
  'cargo check\n'
  'cargo build\n'
  'cargo run\n'
  'cargo test\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-33-commandes-git-supplmentaires',
  '33. Commandes Git supplémentaires',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 33. Commandes Git supplémentaires\n'
  '\n'
  '```\n'
  'git init\n'
  'git clone URL\n'
  'git status\n'
  'git add .\n'
  'git commit -m "message"\n'
  'git log --graph --oneline --all\n'
  'git diff\n'
  'git diff --staged\n'
  'git branch -a\n'
  'git switch -c feature/test\n'
  'git fetch --all\n'
  'git pull --rebase\n'
  'git push\n'
  'git tag -a v1.0.0 -m "Release"\n'
  'git show HEAD\n'
  'git reflog\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-34-expressions-de-commande-et-outils-cli',
  '34. Expressions de commande et outils CLI',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 34. Expressions de commande et outils CLI',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-jq-json',
  'jq — JSON',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## jq — JSON\n'
  '\n'
  '```\n'
  "jq '.' data.json\n"
  "jq '.users' data.json\n"
  "jq '.users[] | .name' data.json\n"
  "jq 'length' data.json\n"
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-yq-yaml',
  'yq — YAML',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## yq — YAML\n'
  '\n'
  '```\n'
  "yq '.' config.yaml\n"
  "yq '.server.port' config.yaml\n"
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-sed',
  'sed',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## sed\n'
  '\n'
  '```\n'
  "sed 's/ancien/nouveau/g' fichier.txt\n"
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-awk',
  'awk',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## awk\n'
  '\n'
  '```\n'
  "awk '{print $1}' fichier.txt\n"
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-xargs',
  'xargs',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## xargs\n'
  '\n'
  '```\n'
  'find . -name "*.log" -print0 | xargs -0 ls -lh\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-curl-et-wget',
  'curl et wget',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## curl et wget\n'
  '\n'
  '```\n'
  'curl -I https://example.com\n'
  'wget -O page.html https://example.com\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-35-commandes-d-administration-de-bases-de-donnes',
  "35. Commandes d'administration de bases de données",
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  "# 35. Commandes d'administration de bases de données",
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-postgresql',
  'PostgreSQL',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## PostgreSQL\n'
  '\n'
  '```\n'
  'psql --version\n'
  'pg_isready\n'
  'pg_dump DATABASE_NAME > backup.sql\n'
  'psql DATABASE_NAME < backup.sql\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-mysql',
  'MySQL',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## MySQL\n'
  '\n'
  '```\n'
  'mysql --version\n'
  'mysql -u root -p\n'
  'mysqldump -u root -p database > backup.sql\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-sqlite',
  'SQLite',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## SQLite\n'
  '\n'
  '```\n'
  'sqlite3 database.db\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-mongodb',
  'MongoDB',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## MongoDB\n'
  '\n'
  '```\n'
  'mongosh\n'
  'mongodump --db database\n'
  'mongorestore --db database dump/database\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-36-commandes-de-diagnostic-et-de-rseau',
  '36. Commandes de diagnostic et de réseau',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 36. Commandes de diagnostic et de réseau',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-dns',
  'DNS',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## DNS\n'
  '\n'
  '```\n'
  'nslookup example.com\n'
  'dig example.com\n'
  'host example.com\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-connectivit',
  'Connectivité',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Connectivité\n'
  '\n'
  '```\n'
  'ping example.com\n'
  'traceroute example.com\n'
  'curl -I https://example.com\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-ports-locaux',
  'Ports locaux',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Ports locaux\n'
  '\n'
  '```\n'
  'ss -tulpn\n'
  '```\n'
  '\n'
  'Windows :\n'
  '\n'
  '```\n'
  'netstat -ano\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-certificats',
  'Certificats',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Certificats\n'
  '\n'
  '```\n'
  'openssl s_client -connect example.com:443 -servername example.com\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-analyse-de-paquets',
  'Analyse de paquets',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Analyse de paquets\n'
  '\n'
  '```\n'
  'tcpdump -i any -c 50\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-37-scripts-de-gestion-des-erreurs',
  '37. Scripts de gestion des erreurs',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 37. Scripts de gestion des erreurs',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-retry-avec-backoff-exponentiel',
  'Retry avec backoff exponentiel',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Retry avec backoff exponentiel\n'
  '\n'
  '```\n'
  'import timeimport randomdef retry(operation, attempts=5):    for attempt in range(attempts):        try:            '
  'return operation()        except Exception:            if attempt == attempts - 1:                raise            '
  'delay = min(2 ** attempt, 30)            delay += random.uniform(0, 0.5)            time.sleep(delay)\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-circuit-breaker-simplifi',
  'Circuit breaker simplifié',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Circuit breaker simplifié\n'
  '\n'
  '```\n'
  'import timeclass CircuitBreaker:    def __init__(self, threshold=3, cooldown=10):        self.threshold = '
  'threshold        self.cooldown = cooldown        self.failures = 0        self.opened_at = None    def call(self, '
  'function):        if self.opened_at is not None:            if time.time() - self.opened_at < '
  'self.cooldown:                raise RuntimeError("Circuit ouvert")            self.opened_at = None            '
  'self.failures = 0        try:            result = function()            self.failures = 0            return '
  'result        except Exception:            self.failures += 1            if self.failures >= '
  'self.threshold:                self.opened_at = time.time()            raise\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-38-commandes-de-virtualisation-et-environnements',
  '38. Commandes de virtualisation et environnements',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 38. Commandes de virtualisation et environnements',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-virtualbox',
  'VirtualBox',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## VirtualBox\n'
  '\n'
  '```\n'
  'VBoxManage list vms\n'
  'VBoxManage list runningvms\n'
  'VBoxManage showvminfo "VM_NAME"\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-vagrant',
  'Vagrant',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Vagrant\n'
  '\n'
  '```\n'
  'vagrant init\n'
  'vagrant up\n'
  'vagrant ssh\n'
  'vagrant halt\n'
  'vagrant destroy\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-wsl',
  'WSL',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## WSL\n'
  '\n'
  '```\n'
  'wsl --list --verbose\n'
  'wsl --status\n'
  'wsl --update\n'
  'wsl --shutdown\n'
  '```',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-39-langages-et-formats-supplmentaires',
  '39. Langages et formats supplémentaires',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 39. Langages et formats supplémentaires\n'
  '\n'
  'Créer des exemples de code pour :\n'
  '\n'
  '- Kotlin : classes, coroutines, Android.\n'
  '- Swift : structures, protocoles, SwiftUI.\n'
  '- Dart : classes, futures, Flutter.\n'
  '- Ruby : blocs, modules, Rails.\n'
  '- Lua : tables, fonctions, scripts embarqués.\n'
  '- R : statistiques, data frames, graphiques.\n'
  '- Julia : calcul scientifique, matrices.\n'
  '- Scala : collections, fonctions, concurrence.\n'
  '- Elixir : processus, supervision, OTP.\n'
  '- Haskell : fonctions pures, types, monades.\n'
  '- Assembly : registres, instructions, mémoire.\n'
  '- Solidity : contrats intelligents, événements, tests.\n'
  '- MATLAB : matrices, fonctions, calcul numérique.\n'
  '- Fortran : calcul scientifique.\n'
  '- COBOL : traitement de données et systèmes historiques.\n'
  '\n'
  'Pour chaque langage, créer des exemples de syntaxe, fonctions, classes, gestion des erreurs, tests, compilation, '
  'exécution et manipulation de fichiers.',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-40-format-de-conservation-des-codes',
  '40. Format de conservation des codes',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 40. Format de conservation des codes\n'
  '\n'
  'Chaque exemple de code doit être conservé avec des métadonnées permettant de le retrouver et de le réutiliser :\n'
  '\n'
  '```\n'
  '{\n'
  '  "title": "HTTP request with Python",\n'
  '  "language": "python",\n'
  '  "category": "network",\n'
  '  "subcategory": "http",\n'
  '  "runtime": "python3",\n'
  '  "code": "import requests\\nresponse = requests.get(\'https://example.com\', '
  'timeout=10)\\nprint(response.status_code)",\n'
  '  "dependencies": ["requests"],\n'
  '  "parameters": [],\n'
  '  "expected_output": "200",\n'
  '  "tests": [],\n'
  '  "difficulty": "beginner",\n'
  '  "version": "1.0",\n'
  '  "verified": false\n'
  '}\n'
  '```\n'
  '\n'
  'La propriété `verified` doit être vraie uniquement après un test réel dans un environnement défini.',
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-41-rgles-de-scurit-pour-les-exemples',
  '41. Règles de sécurité pour les exemples',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '# 41. Règles de sécurité pour les exemples\n'
  '\n'
  '- Ne jamais intégrer de vrais identifiants ou mots de passe.\n'
  '- Ne jamais exposer des clés API.\n'
  '- Ne pas exécuter automatiquement du code inconnu.\n'
  '- Ne pas utiliser de commandes destructives sans confirmation.\n'
  '- Ne pas supprimer de données sans sauvegarde.\n'
  '- Ne pas lancer des scans sur des systèmes non autorisés.\n'
  '- Ne pas contourner les systèmes de protection.\n'
  '- Ne pas désactiver les vérifications TLS en production.\n'
  '- Ne pas exécuter des commandes avec privilèges élevés sans justification.\n'
  '- Toujours prévoir les erreurs, les timeouts et les limites de ressources.\n'
  '- Séparer les exemples pédagogiques des scripts de production.\n'
  '\n'
  "FIN DE L'ENCYCLOPÉDIE — COLLECTION DE CODE SOURCE ET DE COMMANDES.",
  'utilisateur, bibliothèque-8, code, référence'],
 ['8-ressources-pour-continuer-enrichir-cette-collection',
  'Ressources pour continuer à enrichir cette collection',
  'Encyclopédie du code et algorithmes',
  'Source : bibliothèque fournie par l’utilisateur, document 8. Fiche de référence à vérifier selon les versions et le '
  'contexte. Les commandes et exemples sont des contenus documentaires : ne pas les exécuter sans revue, autorisation '
  'et validation du périmètre.\n'
  '\n'
  '## Ressources pour continuer à enrichir cette collection\n'
  '\n'
  "Voici les documentations techniques et référentiels permettant d'obtenir beaucoup plus de code, de syntaxes et "
  "d'exemples :\n"
  '\n'
  '| Ressource                                                                                                      | '
  'Contenu                                |\n'
  '| -------------------------------------------------------------------------------------------------------------- | '
  '-------------------------------------- |\n'
  '| [TheAlgorithms](https://github.com/TheAlgorithms?utm_source=chatgpt.com)                                       | '
  'Algorithmes dans plusieurs langages    |\n'
  '| [JavaScript Algorithms](https://github.com/trekhleb/javascript-algorithms?utm_source=chatgpt.com)              | '
  'Algorithmes JavaScript                 |\n'
  '| [Build Your Own X](https://github.com/codecrafters-io/build-your-own-x?utm_source=chatgpt.com)                 | '
  'Recréer des logiciels en code          |\n'
  '| [Public APIs](https://github.com/public-apis/public-apis?utm_source=chatgpt.com)                               | '
  "Catalogue d'API                        |\n"
  '| [Awesome Python](https://github.com/vinta/awesome-python?utm_source=chatgpt.com)                               | '
  'Bibliothèques et outils Python         |\n'
  '| [Awesome](https://github.com/sindresorhus/awesome?utm_source=chatgpt.com)                                      | '
  'Répertoires de ressources techniques   |\n'
  '| [Rosetta Code](https://github.com/rosetta-code/rosetta-code?utm_source=chatgpt.com)                            | '
  'Solutions algorithmiques multilangages |\n'
  '| [Project Based Learning](https://github.com/practical-tutorials/project-based-learning?utm_source=chatgpt.com) | '
  'Projets pratiques et code              |\n'
  '| [System Design Primer](https://github.com/donnemartin/system-design-primer?utm_source=chatgpt.com)             | '
  'Architecture et conception de systèmes |\n'
  '| [OSSU Computer Science](https://github.com/ossu/computer-science?utm_source=chatgpt.com)                       | '
  'Ressources informatiques               |\n'
  '| [Learn by Example](https://github.com/learnbyexample?utm_source=chatgpt.com)                                   | '
  'Exercices et exemples de code          |\n'
  '\n'
  'Pour obtenir une collection réellement massive, il serait préférable de construire plusieurs volumes '
  'complémentaires plutôt que de recopier des centaines de milliers de lignes sans classement : algorithmes avancés, '
  "programmation système, développement web, bases de données, IA, mathématiques, scripts d'administration, "
  'automatisation, compilateurs et architectures logicielles.',
  'utilisateur, bibliothèque-8, code, référence']]
