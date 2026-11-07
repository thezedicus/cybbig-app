from __future__ import annotations

from ..base import ScanContext


def dispatch(kind: str, ctx: ScanContext) -> None:
    if kind == "php":
        from .php_scanner import run as run_php

        run_php(ctx)
    elif kind == "web":
        from .web_scanner import run as run_web

        run_web(ctx)
    elif kind == "api":
        from .api_scanner import run as run_api

        run_api(ctx)
    elif kind == "checkout":
        from .checkout_scanner import run as run_checkout

        run_checkout(ctx)
    elif kind == "reverse":
        from .reverse_scanner import run as run_reverse

        run_reverse(ctx)
    else:
        raise ValueError(f"Moteur inconnu : {kind}")
