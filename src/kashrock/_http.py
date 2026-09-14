from __future__ import annotations

import json
from typing import Any, Mapping, Optional
from urllib.parse import urlencode

import httpx

from kashrock.errors import (
    KashRockAuthError,
    KashRockError,
    KashRockPlanError,
    KashRockRateLimitError,
)

DEFAULT_BASE = "https://kashrock.up.railway.app"


def _detail(body: Any) -> str:
    if isinstance(body, dict):
        detail = body.get("detail")
        if isinstance(detail, str):
            return detail
        if detail is not None:
            return json.dumps(detail)
    if isinstance(body, str):
        return body
    return json.dumps(body)


def raise_for_status(status: int, body: Any) -> None:
    text = _detail(body)
    if status in (401, 403) and "plan" in text.lower():
        raise KashRockPlanError(text, status=status, body=body)
    if status in (401, 403):
        raise KashRockAuthError(text, status=status, body=body)
    if status == 429:
        raise KashRockRateLimitError(text, status=status, body=body)
    raise KashRockError(text, status=status, body=body)


def clean_params(params: Optional[Mapping[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in (params or {}).items():
        if value is None or value == "":
            continue
        if isinstance(value, bool):
            out[key] = "true" if value else "false"
        else:
            out[key] = value
    return out


class Http:
    def __init__(self, api_key: str, *, base_url: str = DEFAULT_BASE, timeout: float = 60.0) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get(self, path: str, params: Optional[Mapping[str, Any]] = None) -> Any:
        query = clean_params(params)
        suffix = f"?{urlencode(query)}" if query else ""
        url = f"{self.base_url}{path}{suffix}"
        response = httpx.get(
            url,
            headers={"X-API-Key": self.api_key},
            timeout=self.timeout,
        )
        try:
            body = response.json()
        except json.JSONDecodeError:
            body = {"detail": response.text[:500]}
        if response.status_code >= 400:
            raise_for_status(response.status_code, body)
        return body
