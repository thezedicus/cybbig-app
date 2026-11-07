"""Références défensives pour les proxys, VPN et accès distants."""

PACK_ID = "network_privacy"
VERSION = "1"
PREFIX = "Réseaux et confidentialité"
CATEGORIES = {
    "proxy": "Proxy et HTTP",
    "trust": "Architecture et confiance",
    "privacy": "Confidentialité",
    "vpn": "VPN",
    "wireguard": "WireGuard",
    "openvpn": "OpenVPN",
    "leaks": "DNS, IPv6 et routage",
    "hardening": "Durcissement et exploitation",
    "cybbig": "Intégration Cybbig",
}

DOCS = [
    ("proxy-fundamentals", "Proxy HTTP : rôles et protocoles", "proxy", """Un proxy direct reçoit des requêtes d'un client et les relaie vers des serveurs de destination. Un proxy inverse reçoit des requêtes comme un serveur public et les transmet à un ou plusieurs services internes. Un tunnel relaie des octets sans interpréter les messages applicatifs. Ces rôles ont des modèles de confiance et des politiques différents.

Pour HTTPS, HTTP CONNECT établit généralement un tunnel vers un hôte et un port ; le proxy ne lit pas le contenu TLS tant qu'il ne termine pas explicitement TLS. Restreindre CONNECT aux ports et destinations nécessaires, exiger une authentification adaptée et limiter les connexions, car un relais ouvert peut être détourné pour atteindre des services tiers.

Pour un proxy inverse, limiter l'accès direct aux serveurs d'origine, appliquer TLS sur les segments concernés, fixer des délais et plafonds de taille, et valider les noms d'hôte transmis. Éviter les listes de destinations non bornées et vérifier les redirections pour prévenir l'accès involontaire à des réseaux internes.

Références : RFC 9110, intermédiaires HTTP et CONNECT : https://www.rfc-editor.org/rfc/rfc9110.html""", "proxy,http,CONNECT,reverse-proxy"),
    ("trusted-forwarded-headers", "En-têtes Forwarded : limiter la confiance aux proxys connus", "trust", """Les en-têtes Forwarded, X-Forwarded-For et X-Forwarded-Proto sont des métadonnées de transit, pas des preuves d'identité. Un client peut envoyer lui-même des valeurs arbitraires. L'application ne doit les considérer fiables que si la connexion vient d'un proxy explicitement approuvé et si ce proxy supprime ou remplace les valeurs non fiables avant de les ajouter.

Définir une liste précise d'adresses ou de sauts de confiance, préserver l'ordre de la chaîne selon la configuration du frontal, protéger le trafic entre proxy et application, et tester les accès directs au backend. Ne pas faire confiance à tous les proxys ni à toute adresse privée par commodité. N'activer que les champs nécessaires : Forwarded peut divulguer des adresses et la structure interne.

Pour Cybbig : les contrôles SSRF et le périmètre déclaré doivent s'appliquer avant toute requête, même si un proxy est configuré ; un proxy ne transforme pas une destination non autorisée en destination autorisée.

Références : RFC 7239, validation et implications de confidentialité : https://www.rfc-editor.org/rfc/rfc7239.html ; RFC 9110 : https://www.rfc-editor.org/rfc/rfc9110.html""", "Forwarded,X-Forwarded-For,reverse-proxy,trust,SSRF"),
    ("proxy-privacy-limits", "Proxy et confidentialité : ce qu'il protège et ce qu'il ne protège pas", "privacy", """Un proxy peut masquer l'adresse réseau du client au serveur de destination et centraliser des politiques de filtrage, de cache ou de journalisation. Le fournisseur du proxy voit au minimum les métadonnées nécessaires au relais ; un proxy HTTPS par tunnel ne déchiffre normalement pas le TLS de bout en bout, alors qu'une interception TLS le termine et exige un certificat racine de confiance. Cette interception permet l'inspection mais accroît fortement les risques et doit être documentée, autorisée et limitée.

Un proxy ne chiffre pas automatiquement les données entre l'utilisateur et le proxy, ne protège pas les applications qui l'ignorent et ne garantit pas l'anonymat. Les cookies, comptes connectés, empreintes de navigateur, DNS hors proxy, WebRTC et données applicatives peuvent révéler des informations. Évaluer les journaux, la rétention, le contrôle d'accès, la juridiction, les mises à jour et la disponibilité du fournisseur.

Ne jamais utiliser un proxy ouvert ou tiers sans comprendre ses politiques. Ne pas désactiver les validations TLS pour contourner une erreur de certificat. Les journaux doivent être minimisés, protégés et conservés le temps nécessaire à l'exploitation ou à une obligation clairement définie.

Référence : RFC 7239, considérations de sécurité et de confidentialité : https://www.rfc-editor.org/rfc/rfc7239.html""", "privacy,proxy,TLS,logs"),
    ("vpn-fundamentals", "VPN : tunnel, routage et modèle de confiance", "vpn", """Un VPN crée un tunnel chiffré entre des pairs ou entre un poste et une passerelle. Il peut protéger le trafic sur un réseau non fiable et donner accès à des ressources privées, mais la confiance se déplace vers la passerelle et son opérateur. Un VPN commercial ne rend pas anonyme et ne corrige ni les logiciels compromis ni les erreurs de configuration.

Distinguer tunnel complet (routes par défaut envoyées dans le tunnel) et tunnel fractionné (seuls certains préfixes passent par lui). Déterminer explicitement le traitement d'IPv4, d'IPv6, du DNS, des routes locales, des réseaux de confiance et de la reconnexion. Un tunnel fractionné mal documenté peut laisser sortir des flux hors VPN ; un tunnel complet mal configuré peut couper l'accès local ou la résolution DNS.

Pour l'accès d'entreprise, limiter les ressources accessibles, appliquer MFA lorsqu'il s'agit d'une authentification utilisateur, tenir le client et la passerelle à jour, révoquer rapidement les identités et appareils, journaliser proportionnellement et surveiller les connexions. Vérifier les recommandations actuelles de l'organisation et du fournisseur.

Références : CISA, conseils sur le durcissement des VPN et MFA : https://www.cisa.gov/sites/default/files/publications/AA20-283A-APT_Actors_Chaining_Vulnerabilities.pdf ; CISA, sécurité des accès distants : https://www.cisa.gov/resources-tools/resources/guide-securing-remote-access-software""", "VPN,remote-access,MFA,routing"),
    ("wireguard-overview", "WireGuard : clés, pairs et routage cryptographique", "wireguard", """WireGuard associe des clés publiques de pairs à des préfixes IP autorisés, modèle appelé cryptokey routing. La clé privée reste secrète sur son appareil ; seule la clé publique correspondante est distribuée. Les fichiers de configuration sont des secrets opérationnels : protéger leurs ACL et sauvegardes, éviter les dépôts Git, journaux, captures et tickets non maîtrisés. En cas de compromission, remplacer et révoquer les clés concernées.

AllowedIPs joue deux rôles importants : il participe à la sélection du pair pour une destination et définit les adresses source acceptées de ce pair. 0.0.0.0/0 et ::/0 expriment les routes IPv4 et IPv6 par défaut ; leur emploi peut créer un tunnel complet et nécessite une stratégie de routage et de DNS cohérente. PersistentKeepalive n'est utile que pour maintenir une correspondance NAT lorsque le scénario le demande ; ne pas l'activer partout sans raison.

Le port UDP, les routes, le MTU et le DNS dépendent du réseau et de la plateforme. Commencer par les valeurs documentées par le fournisseur, inspecter les journaux du client officiel et valider IPv4, IPv6, DNS, accès aux ressources requises et comportement après coupure. Ne pas modifier les règles de pare-feu du poste sans comprendre l'impact.

Références officielles : guide de démarrage : https://www.wireguard.com/quickstart/ ; protocole et cryptokey routing : https://www.wireguard.com/protocol/""", "WireGuard,AllowedIPs,keys,VPN"),
    ("openvpn-overview", "OpenVPN : vérifier versions, options et profils", "openvpn", """OpenVPN est un VPN TLS configurable avec transports UDP/TCP, interfaces virtuelles et options d'authentification. La richesse de configuration rend les profils dépendants de la version et de la plateforme. N'appliquer que les options documentées pour la version effectivement installée, maintenir client et serveur à jour et vérifier la matrice de support officielle avant un changement.

Protéger les profils contenant certificats, clés ou secrets comme des identifiants. Éviter de transmettre un profil complet à un assistant en ligne ou de le placer dans des journaux. Préférer les suites modernes négociées par des versions actuelles ; ne pas réactiver des méthodes statiques, options obsolètes ou compression héritée pour faire disparaître un problème de compatibilité. Diagnostiquer avec les messages d'erreur réels et un profil de test, pas par désactivation générale des contrôles TLS.

Pour l'accès distant, limiter les réseaux routés, gérer les certificats et révocations, appliquer une authentification renforcée adaptée et documenter le tunnel complet ou fractionné, DNS et IPv6.

Références officielles : manuel OpenVPN 2.7 : https://openvpn.net/community-docs/community-articles/openvpn-2-7-manual/ ; versions maintenues : https://community.openvpn.net/Pages/Supported%20versions""", "OpenVPN,TLS,VPN,certificates"),
    ("vpn-dns-ipv6-validation", "Validation d'un VPN : DNS, IPv6, routes et coupures", "leaks", """La simple indication « connecté » ne prouve pas que tout le trafic suit le tunnel. Valider les routes IPv4 et IPv6, les résolveurs DNS utilisés, les domaines internes requis, la connectivité vers la passerelle et le comportement au redémarrage. Les tests d'adresse publique ne révèlent qu'une partie de la chaîne et ne démontrent pas l'absence de fuite pour toutes les applications.

Tester sur un réseau et des ressources que vous contrôlez : relever l'état avant/après, vérifier les routes et DNS côté OS, observer les journaux du client et comparer les résultats sans inclure de secrets. Simuler une perte de tunnel peut révéler si la politique de blocage prévue fonctionne, mais ne pas présumer qu'un client possède un coupe-circuit : vérifier sa documentation et ses paramètres effectifs. Inclure IPv6 si l'interface en dispose.

Un proxy par application et un VPN au niveau réseau peuvent se cumuler et entraîner des chemins, DNS et adresses de sortie différents. Documenter l'ordre des couches et retirer une seule variable à la fois pour diagnostiquer.

Références : WireGuard Quick Start : https://www.wireguard.com/quickstart/ ; OpenVPN manual : https://openvpn.net/community-docs/community-articles/openvpn-2-7-manual/""", "DNS,IPv6,VPN,routing,diagnostics"),
    ("vpn-proxy-operational-hardening", "Durcir l'exploitation d'un proxy ou d'une passerelle VPN", "hardening", """Inventorier les points d'entrée et propriétaires, désactiver les fonctions non utilisées, appliquer les mises à jour du fournisseur, limiter l'administration au réseau de gestion, utiliser MFA pour les accès utilisateur, restreindre les destinations et ports, et surveiller les échecs ainsi que les changements de configuration. Prévoir sauvegarde chiffrée, rotation/révocation des secrets, procédure de restauration et test de reprise.

Un proxy ne doit pas être un relais ouvert : authentifier les utilisateurs selon le contexte, filtrer destinations et ports, plafonner connexions et bande passante, isoler l'administration, empêcher l'accès depuis le relais aux interfaces de gestion et protéger les journaux. Le frontal inverse ne doit exposer que les routes nécessaires et le backend ne doit pas être joignable publiquement par un chemin contournant le frontal.

Une passerelle VPN ne doit donner que l'accès utile : segmenter les routes, séparer comptes administrateurs et utilisateurs, appliquer MFA pour les comptes, révoquer les accès inutiles et surveiller l'activité selon une politique annoncée. Un tunnel chiffré n'empêche pas le poste distant compromis d'attaquer des ressources internes.

Références : CISA, mises à jour et MFA pour VPN : https://www.cisa.gov/sites/default/files/publications/AA20-283A-APT_Actors_Chaining_Vulnerabilities.pdf ; RFC 9110 CONNECT : https://www.rfc-editor.org/rfc/rfc9110.html""", "hardening,proxy,VPN,MFA,segmentation"),
    ("cybbig-network-architecture", "Cybbig : place des proxys et VPN dans le moteur", "cybbig", """La base de connaissances Cybbig alimente le RAG de l'assistant, les tâches IA et les ateliers de génération de code. Les fiches proxys/VPN doivent soutenir l'analyse de configuration, le diagnostic de routage et la conception défensive ; elles n'autorisent pas automatiquement une connexion, un scan, une modification de proxy ou une modification de routes.

Les contrôles réseau doivent rester à plusieurs niveaux : validation du périmètre et des hôtes, protection SSRF, filtrage DNS/IP, limites de délai et de taille, validation TLS, restriction des redirections, liste de proxys de confiance, journalisation des actions et consentement explicite aux opérations avec effets réseau. Le chemin proxy choisi ne doit jamais élargir le périmètre autorisé.

Pour toute nouvelle configuration générée, exposer les hypothèses, les ports, les routes, le traitement DNS/IPv6, les limites de confidentialité et les étapes de validation. Conserver le texte comme proposition à relire ; les identifiants et clés privées ne doivent pas apparaître dans les prompts, fiches ou rapports.

Sources de référence : https://www.rfc-editor.org/rfc/rfc9110.html ; https://www.rfc-editor.org/rfc/rfc7239.html ; https://www.wireguard.com/quickstart/ ; https://openvpn.net/community-docs/community-articles/openvpn-2-7-manual/ ; https://www.cisa.gov/resources-tools/resources/guide-securing-remote-access-software""", "Cybbig,architecture,RAG,SSRF,proxy,VPN"),
]
