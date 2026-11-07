"""Outil du propriétaire de Cybbig (à lancer uniquement sur votre propre poste).

  python scripts/owner-sign.py keygen          crée la clé privée propriétaire (une seule fois)
  python scripts/owner-sign.py pubkey          affiche la clé publique à placer dans backend/app/services/owner.py
  python scripts/owner-sign.py sign <défi>     signe le défi affiché par Cybbig (Administration > Activation)

La clé privée est stockée HORS du dépôt : %USERPROFILE%\\.cybbig\\owner_ed25519.key
(ou le chemin de la variable CYBBIG_OWNER_KEY). Ne la publiez jamais, ne la copiez
pas dans le projet ; sauvegardez-la hors ligne (clé USB chiffrée, gestionnaire de mots de passe).
"""
from __future__ import annotations

import os
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
from app.services import ed25519  # noqa: E402

KEY_PATH = Path(os.environ.get("CYBBIG_OWNER_KEY", Path.home() / ".cybbig" / "owner_ed25519.key"))


def _load() -> bytes:
    if not KEY_PATH.exists():
        sys.exit(f"Clé privée introuvable : {KEY_PATH}  (lancez d'abord : keygen)")
    return bytes.fromhex(KEY_PATH.read_text(encoding="ascii").strip())


def main(argv: list[str]) -> None:
    if len(argv) < 2 or argv[1] not in {"keygen", "pubkey", "sign"}:
        sys.exit(__doc__)
    command = argv[1]
    if command == "keygen":
        if KEY_PATH.exists():
            sys.exit(f"Une clé existe déjà ({KEY_PATH}) : elle n'est pas écrasée.")
        KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
        secret = secrets.token_bytes(32)
        KEY_PATH.write_text(secret.hex(), encoding="ascii")
        print(f"Clé privée créée : {KEY_PATH}")
        print(f"Clé publique     : {ed25519.public_key(secret).hex()}")
    elif command == "pubkey":
        print(ed25519.public_key(_load()).hex())
    else:
        if len(argv) < 3:
            sys.exit("Usage : owner-sign.py sign <défi>")
        challenge = argv[2].strip()
        print(ed25519.sign(_load(), challenge.encode("utf-8")).hex())


if __name__ == "__main__":
    main(sys.argv)
