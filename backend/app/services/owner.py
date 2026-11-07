"""Activation de l'administration réservée au propriétaire de Cybbig.

Aucun identifiant ni mot de passe administrateur n'est livré avec l'application.
Seule la CLÉ PUBLIQUE du propriétaire figure ici : elle permet de vérifier une
signature, jamais d'en produire une. La clé privée correspondante reste sur le poste
du propriétaire (scripts/owner-sign.py) et n'est ni dans le dépôt ni dans l'installateur.

Déroulé : Cybbig affiche un défi unique (valable 10 minutes, usage unique) ; le
propriétaire le signe hors ligne et colle la signature ; Cybbig la vérifie puis
enregistre les identifiants choisis, uniquement sous forme de hachés PBKDF2 locaux.
"""
from __future__ import annotations

import secrets
import threading
import time

from .. import db
from . import ed25519

# Clé publique Ed25519 du propriétaire (publique par nature, sans valeur pour un attaquant).
OWNER_PUBLIC_KEY = "035f891b39f16e1529fe24ca7a48054fa64a3a9378e0bfa8cbf64176b6398ba6"

CHALLENGE_TTL_SECONDS = 10 * 60
CHALLENGE_PREFIX = "cybbig-owner-v1"

_challenges: dict[str, float] = {}
_lock = threading.Lock()


def install_id() -> str:
    value = str(db.get_setting("install_id", "") or "")
    if not value:
        value = secrets.token_hex(8)
        db.set_setting("install_id", value)
    return value


def new_challenge() -> dict[str, object]:
    challenge = f"{CHALLENGE_PREFIX}.{install_id()}.{secrets.token_hex(12)}"
    now = time.time()
    with _lock:
        for key, expires in list(_challenges.items()):
            if expires < now:
                _challenges.pop(key, None)
        _challenges[challenge] = now + CHALLENGE_TTL_SECONDS
    return {"challenge": challenge, "expires_in": CHALLENGE_TTL_SECONDS,
            "command": f'python scripts/owner-sign.py sign {challenge}'}


def consume(challenge: str, signature_hex: str) -> bool:
    """Vérifie la signature du défi ; le défi est consommé même en cas d'échec."""
    challenge = (challenge or "").strip()
    with _lock:
        expires = _challenges.pop(challenge, None)
    if not expires or expires < time.time():
        return False
    try:
        signature = bytes.fromhex((signature_hex or "").strip())
        public = bytes.fromhex(OWNER_PUBLIC_KEY)
    except ValueError:
        return False
    return ed25519.verify(public, challenge.encode("utf-8"), signature)
