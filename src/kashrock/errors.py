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


class KashRockPlanError(KashRockError):
    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        body: Any = None,
        upgrade_url: str = "https://www.kashrock.com/pricing",
    ) -> None:
        super().__init__(message, status=status, body=body)
        self.upgrade_url = upgrade_url


class KashRockRateLimitError(KashRockError):
    pass
