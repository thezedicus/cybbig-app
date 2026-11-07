from __future__ import annotations

import html
import json
from pathlib import Path

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from ..config import SAMPLES_DIR

router = APIRouter(prefix="/demo", tags=["démonstration locale"])

# Catalogue fictif et sans stock réel, utilisé pour explorer davantage les parcours du scanner.
PRODUCTS = [
    {"slug": "clavier-mecanique", "name": "Clavier mécanique compact", "category": "accessoires", "price": 89.90, "color": "violet", "description": "Clavier compact avec touches programmables et connexion USB-C."},
    {"slug": "souris-ergonomique", "name": "Souris ergonomique", "category": "accessoires", "price": 54.00, "color": "blue", "description": "Souris sans fil de démonstration, avec réglage de sensibilité."},
    {"slug": "ecran-studio", "name": "Écran Studio 27 pouces", "category": "informatique", "price": 329.00, "color": "cyan", "description": "Écran de catalogue fictif pour tester les pages produit."},
    {"slug": "mini-pc-lab", "name": "Mini PC Lab", "category": "informatique", "price": 499.00, "color": "orange", "description": "Ordinateur de démonstration sans commande ni stock réel."},
    {"slug": "sac-urbain", "name": "Sac urbain", "category": "mobilite", "price": 72.50, "color": "green", "description": "Accessoire fictif présenté dans le parcours de boutique."},
    {"slug": "gourde-isotherme", "name": "Gourde isotherme", "category": "mobilite", "price": 24.90, "color": "pink", "description": "Produit factice pour tester recherche, navigation et panier."},
]
CATEGORIES = {
    "informatique": "Informatique",
    "accessoires": "Accessoires",
    "mobilite": "Mobilité",
}

STYLE = """
<style>
:root{color-scheme:light;--ink:#172235;--muted:#64748b;--line:#dce4ee;--brand:#5b4ce2;--paper:#f6f8fc}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.55 system-ui,Segoe UI,sans-serif}
a{color:var(--brand)}header,main,footer{max-width:1080px;margin:auto;padding:20px}header{padding-top:14px}
.notice{background:#edf5ff;border:1px solid #c9ddf5;border-radius:12px;padding:12px 16px;color:#284364}
nav{display:flex;gap:14px;flex-wrap:wrap;padding:15px 0;border-bottom:1px solid var(--line)}nav a{text-decoration:none;font-weight:650}
.hero,.panel,.product{background:white;border:1px solid var(--line);border-radius:16px;padding:22px;margin:14px 0}
.hero{background:linear-gradient(120deg,#f0efff,#fff 65%)}h1{font-size:clamp(28px,4vw,42px);line-height:1.12;margin:.4em 0}h2{margin-top:0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}.product{margin:0}.art{height:112px;border-radius:11px;margin-bottom:14px;background:linear-gradient(135deg,#8a7cf3,#d8d4ff)}
.art.blue{background:linear-gradient(135deg,#52a4e8,#d3ecff)}.art.cyan{background:linear-gradient(135deg,#22b8c6,#d0fbff)}.art.orange{background:linear-gradient(135deg,#f59e0b,#ffedc2)}.art.green{background:linear-gradient(135deg,#34a875,#d3f5e4)}.art.pink{background:linear-gradient(135deg,#ef75a8,#ffe0ee)}
.muted,.small{color:var(--muted)}.price{font-size:20px;font-weight:750}.button,button{display:inline-block;background:var(--brand);color:white;border:0;border-radius:9px;padding:10px 14px;text-decoration:none;font:inherit;font-weight:650;cursor:pointer}
input{padding:10px;border:1px solid #bdc8d8;border-radius:8px;font:inherit;max-width:100%}label{display:grid;gap:5px;margin:12px 0}.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
footer{color:var(--muted);border-top:1px solid var(--line);margin-top:35px;font-size:13px}
</style>
"""


def _shell(title: str, content: str) -> str:
    safe_title = html.escape(title)
    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{safe_title} — Boutique de démonstration Cybbig</title><meta name="generator" content="DemoShop 1.0">
<meta name="description" content="Boutique fictive locale pour les démonstrations Cybbig.">
<script src="https://cdn.example.net/demo-analytics.js"></script>{STYLE}</head><body>
<header><div class="notice"><strong>Démo locale fictive.</strong> Aucun compte, paiement, stock ni renseignement saisi n’est enregistré.</div>
<nav aria-label="Navigation principale"><a href="/demo/shop">Accueil</a><a href="/demo/shop/category/informatique">Informatique</a>
<a href="/demo/shop/category/accessoires">Accessoires</a><a href="/demo/shop/category/mobilite">Mobilité</a>
<a href="/demo/shop/cart">Panier (démo)</a><a href="/demo/shop/account">Compte</a><a href="/demo/shop/help">Aide</a></nav></header>
<main>{content}</main><footer>Cybbig · Boutique de test locale · Les actions de commande sont neutralisées. <a href="/demo/shop/openapi.json">API fictive</a></footer>
</body></html>"""


def _response(title: str, content: str, status_code: int = 200) -> HTMLResponse:
    response = HTMLResponse(content=_shell(title, content), status_code=status_code)
    # Ces en-têtes volontairement incomplets illustrent des constats passifs sur un site fictif local.
    response.headers["X-Powered-By"] = "PHP/7.4.33-demo"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers.append("Set-Cookie", "demo_session=abc123; Path=/")
    response.headers["Cache-Control"] = "no-store"
    return response


def _card(product: dict) -> str:
    name = html.escape(product["name"])
    slug = html.escape(product["slug"], quote=True)
    category = html.escape(CATEGORIES[product["category"]])
    description = html.escape(product["description"])
    price = f"{product['price']:.2f}".replace(".", ",")
    color = html.escape(product["color"], quote=True)
    return f"""<article class="product"><div class="art {color}" aria-hidden="true"></div>
<p class="small">{category}</p><h3><a href="/demo/shop/product/{slug}">{name}</a></h3>
<p class="muted">{description}</p><p class="price">{price} €</p>
<a class="button" href="/demo/shop/product/{slug}">Voir le produit</a></article>"""


@router.get("")
def demo_root() -> RedirectResponse:
    return RedirectResponse(url="/demo/shop")


@router.get("/shop", response_class=HTMLResponse)
def demo_shop() -> HTMLResponse:
    cards = "".join(_card(product) for product in PRODUCTS)
    content = f"""<section class="hero"><p class="small">CYBBIG · ENVIRONNEMENT DE TEST</p>
<h1>La boutique de démonstration</h1><p>Un mini-site e-commerce fictif avec catalogue, recherche, compte, panier, aide et checkout simulé.
Parcourez les pages pour explorer les analyses Web, checkout et API de Cybbig.</p>
<form class="row" method="get" action="/demo/shop/search"><label for="q">Rechercher un produit</label>
<input id="q" name="q" placeholder="Clavier, écran, sac…"><button type="submit">Rechercher</button></form></section>
<section class="panel"><h2>Explorer les rayons</h2><div class="row">{''.join(f'<a class="button" href="/demo/shop/category/{slug}">{html.escape(label)}</a>' for slug, label in CATEGORIES.items())}</div></section>
<section><h2>Catalogue de démonstration</h2><div class="grid">{cards}</div></section>
<section class="panel"><h2>Autres parcours</h2><div class="row"><a href="/demo/shop/cart">Panier</a><a href="/demo/shop/checkout">Paiement simulé</a>
<a href="/demo/shop/account">Connexion</a><a href="/demo/shop/orders">Suivi de commande</a><a href="/demo/shop/help">Centre d’aide</a>
<a href="/demo/shop/api">Découvrir l’API</a></div></section>
<!-- Motifs inertes réservés aux exercices de détection; placés dans un template non exécuté. -->
<template id="demo-patterns"><svg onload="atob('ZGVtby1vbmx5')"></svg><script>new Function(atob("ZGVtby1vbmx5"));</script></template>"""
    return _response("Accueil", content)


@router.get("/shop/category/{category}", response_class=HTMLResponse)
def demo_category(category: str) -> HTMLResponse:
    label = CATEGORIES.get(category)
    if not label:
        return _response("Rayon introuvable", "<section class='panel'><h1>Rayon introuvable</h1><a href='/demo/shop'>Retour à l’accueil</a></section>", 404)
    products = [product for product in PRODUCTS if product["category"] == category]
    return _response(label, f"<section class='hero'><p class='small'>CATALOGUE DE DÉMO</p><h1>{html.escape(label)}</h1><p>Produits fictifs de cette catégorie.</p></section><div class='grid'>{''.join(_card(p) for p in products)}</div>")


@router.get("/shop/product/{slug}", response_class=HTMLResponse)
def demo_product(slug: str) -> HTMLResponse:
    product = next((item for item in PRODUCTS if item["slug"] == slug), None)
    if not product:
        return _response("Produit introuvable", "<section class='panel'><h1>Produit introuvable</h1><a href='/demo/shop'>Retour au catalogue</a></section>", 404)
    name = html.escape(product["name"])
    price = f"{product['price']:.2f}".replace(".", ",")
    body = f"""<section class="product"><div class="art {html.escape(product['color'])}" aria-hidden="true"></div>
<p><a href="/demo/shop/category/{html.escape(product['category'], quote=True)}">{html.escape(CATEGORIES[product['category']])}</a></p>
<h1>{name}</h1><p>{html.escape(product['description'])}</p><p class="price">{price} €</p>
<p class="muted">Référence fictive : DEMO-{html.escape(product['slug'].upper())} · disponibilité simulée</p>
<a class="button" href="/demo/shop/cart?item={html.escape(product['slug'], quote=True)}">Ajouter au panier de démo</a></section>
<section class="panel"><h2>Informations</h2><p>Livraison, avis et caractéristiques sont simulés pour étendre la couverture des pages.</p>
<a href="/demo/shop/help">Questions sur une commande ?</a></section>"""
    return _response(name, body)


@router.get("/shop/search", response_class=HTMLResponse)
def demo_search(q: str = Query(default="", max_length=120)) -> HTMLResponse:
    query = q.strip()
    results = [item for item in PRODUCTS if query.lower() in (item["name"] + " " + item["description"] + " " + CATEGORIES[item["category"]]).lower()] if query else PRODUCTS
    escaped = html.escape(query)
    body = f"""<section class="hero"><h1>Recherche catalogue</h1><form class="row" method="get" action="/demo/shop/search">
<label for="q">Mot-clé</label><input id="q" name="q" maxlength="120" value="{escaped}"><button>Rechercher</button></form>
<p>La recherche affiche {len(results)} produit(s) de démonstration. La saisie est échappée et rien n’est conservé.</p></section>
<div class="grid">{''.join(_card(item) for item in results) or '<section class="panel"><p>Aucun produit correspondant.</p></section>'}</div>"""
    return _response("Recherche", body)


@router.get("/shop/cart", response_class=HTMLResponse)
def demo_cart(item: str = "") -> HTMLResponse:
    product = next((value for value in PRODUCTS if value["slug"] == item), None)
    cart_line = f"<p>{html.escape(product['name'])} — {product['price']:.2f} € (quantité simulée : 1)</p>" if product else "<p>Le panier de démonstration est vide.</p>"
    return _response("Panier", f"<section class='panel'><p class='small'>PANIER FICTIF</p><h1>Votre panier</h1>{cart_line}<p>Aucune ligne n’est enregistrée côté serveur.</p><div class='row'><a class='button' href='/demo/shop'>Continuer les achats</a><a class='button' href='/demo/shop/checkout'>Passer au paiement de démo</a></div></section>")


@router.get("/shop/checkout", response_class=HTMLResponse)
def demo_checkout() -> HTMLResponse:
    body = """<section class="panel"><p class="small">CHECKOUT FICTIF · AUCUNE TRANSACTION</p><h1>Paiement de démonstration</h1>
<p>Utilisez uniquement des valeurs fictives. Le formulaire ne transmet et ne stocke aucune donnée.</p>
<form action="https://pay.example.org/checkout" method="post" onsubmit="event.preventDefault();document.getElementById('demo-result').hidden=false;return false;">
<label>E-mail fictif<input type="email" autocomplete="email" placeholder="demo@example.invalid"></label>
<label>Numéro de carte de test<input name="card_number" autocomplete="cc-number" inputmode="numeric" placeholder="0000 0000 0000 0000"></label>
<div class="row"><label>Expiration<input name="card_exp" autocomplete="cc-exp" placeholder="MM/AA"></label><label>CVC fictif<input name="card_cvc" autocomplete="cc-csc" placeholder="000"></label></div>
<button type="submit">Simuler le paiement</button></form><p id="demo-result" hidden role="status">Démonstration : paiement neutralisé, aucune donnée envoyée.</p>
<p class="muted">Le bouton est neutralisé par JavaScript et ne contacte pas le prestataire fictif.</p></section>"""
    return _response("Checkout", body)


@router.api_route("/shop/account", methods=["GET", "POST"], response_class=HTMLResponse)
def demo_account() -> HTMLResponse:
    body = """<section class="panel"><p class="small">COMPTE DE DÉMONSTRATION</p><h1>Connexion</h1>
<p>Aucun compte ne peut être créé. Les champs ne sont pas envoyés ni enregistrés.</p>
<form action="/demo/shop/account" method="post" onsubmit="event.preventDefault();document.getElementById('account-result').hidden=false;return false;">
<label>E-mail<input name="email" type="email" autocomplete="username" placeholder="demo@example.invalid"></label>
<label>Mot de passe fictif<input name="password" type="password" autocomplete="current-password"></label>
<button type="submit">Tester le formulaire</button></form><p id="account-result" hidden role="status">Connexion fictive désactivée.</p>
<a href="/demo/shop/orders">Suivi de commande fictif</a></section>"""
    return _response("Compte", body)


@router.get("/shop/orders", response_class=HTMLResponse)
def demo_orders() -> HTMLResponse:
    return _response("Suivi de commande", """<section class="panel"><h1>Suivre une commande</h1><p>Les commandes n’existent pas dans cette boutique fictive.</p>
<form action="/demo/shop/orders" method="get"><label>Référence de démonstration<input name="order" placeholder="DEMO-0000"></label><button>Rechercher</button></form>
<p>Le suivi ne consulte aucun service externe.</p></section>""")


@router.get("/shop/help", response_class=HTMLResponse)
def demo_help() -> HTMLResponse:
    return _response("Centre d’aide", """<section class="hero"><h1>Centre d’aide</h1><p>Informations fictives pour explorer les pages d’assistance et leurs liens internes.</p></section>
<section class="panel"><h2>Livraison et retours</h2><p>Aucune commande réelle n’est préparée ou expédiée.</p><a href="/demo/shop/orders">Consulter le suivi de démo</a></section>
<section class="panel"><h2>Nous contacter</h2><form action="/demo/shop/help" method="get"><label>Sujet<input name="subject" maxlength="120"></label><label>Message<textarea name="message" maxlength="500"></textarea></label><button type="button" onclick="document.getElementById('help-result').hidden=false">Afficher le résultat fictif</button></form><p id="help-result" hidden>La messagerie de démonstration ne transmet rien.</p></section>""")


@router.get("/shop/api", response_class=HTMLResponse)
def demo_api_info() -> HTMLResponse:
    return _response("API de démonstration", """<section class="panel"><h1>API catalogue fictive</h1><p>Spécification OpenAPI statique destinée à l’audit local. Aucun endpoint ne crée de transaction.</p>
<ul><li><a href="/demo/shop/openapi.json">Spécification OpenAPI</a></li><li><a href="/demo/openapi.json">Spécification alternative</a></li></ul></section>""")


@router.get("/openapi.json")
def demo_openapi() -> JSONResponse:
    path = SAMPLES_DIR / "openapi-demo.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return JSONResponse(content=data)


@router.get("/shop/openapi.json")
def demo_shop_openapi() -> JSONResponse:
    """Spécification accessible depuis le chemin relatif de l’URL de base de la boutique."""
    return demo_openapi()
