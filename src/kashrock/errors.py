from __future__ import annotations

from typing import Any, Optional


class KashRockError(Exception):
    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.body = body


class KashRockAuthError(KashRockError):
    pass


def _upgrade_block(body: Any) -> Optional[dict]:
    """The API's `upgrade` object — top level or inside the v7 error envelope.
    The link is tagged utm_source=api; a click that started in an SDK session
    counts under utm_source=sdk instead."""
    if not isinstance(body, dict):
        return None
    up = body.get("upgrade")
    if not (isinstance(up, dict) and up.get("url")):
        error = body.get("error")
        if isinstance(error, dict):
            up = error.get("upgrade")
    if isinstance(up, dict) and isinstance(up.get("url"), str):
        return {**up, "url": up["url"].replace("utm_source=api", "utm_source=sdk", 1)}
    return None


class KashRockPlanError(KashRockError):
    """A plan gate (403). The message is the one-sentence upgrade prompt the
    API wrote — safe to repeat to the user verbatim; `upgrade_url` is the
    tracked checkout link, `upgrade` the full object {message, url, plan}."""

    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        body: Any = None,
        upgrade_url: str = "https://www.kashrock.com/pricing",
        upgrade: Optional[dict] = None,
    ) -> None:
        upgrade = upgrade or _upgrade_block(body)
        if upgrade:
            message = f"{message} {upgrade['message']} {upgrade['url']}"
            upgrade_url = upgrade["url"]
        elif isinstance(body, dict) and isinstance(body.get("upgrade_url"), str):
            upgrade_url = body["upgrade_url"]
        super().__init__(message, status=status, body=body)
        self.upgrade_url = upgrade_url
        self.upgrade = upgrade


class KashRockRateLimitError(KashRockError):
    """A 429. Same upgrade surface as KashRockPlanError: the message carries
    the API's one-sentence prompt, `upgrade_url` the tracked checkout link."""

    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        body: Any = None,
        upgrade_url: Optional[str] = None,
        upgrade: Optional[dict] = None,
    ) -> None:
        upgrade = upgrade or _upgrade_block(body)
        if upgrade:
            message = f"{message} {upgrade['message']} {upgrade['url']}"
            upgrade_url = upgrade["url"]
        elif upgrade_url is None and isinstance(body, dict):
            upgrade_url = body.get("upgrade_url")
        super().__init__(message, status=status, body=body)
        self.upgrade_url = upgrade_url
        self.upgrade = upgrade
