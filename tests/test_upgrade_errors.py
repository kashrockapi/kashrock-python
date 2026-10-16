"""Plan-gate and rate-limit exceptions carry the API's upgrade prompt."""
from __future__ import annotations

import pytest

from kashrock._http import raise_for_status
from kashrock.errors import (
    KashRockAuthError,
    KashRockError,
    KashRockPlanError,
    KashRockRateLimitError,
)

UPGRADE = {
    "message": "You're on the Sandbox plan. Hobby removes the daily cap — upgrade takes 60 seconds.",
    "url": "https://www.kashrock.com/checkout/start?plan=hobby&utm_source=api&utm_medium=upgrade_prompt&utm_campaign=upgrade&utm_content=quota_daily",
    "plan": "hobby",
}


def test_429_carries_upgrade_object():
    body = {
        "detail": "Daily request limit reached (1k/day).",
        "limit_type": "daily",
        "limit": 1000,
        "remaining": 0,
        "upgrade_url": UPGRADE["url"],
        "upgrade": UPGRADE,
    }
    with pytest.raises(KashRockRateLimitError) as exc:
        raise_for_status(429, body)
    e = exc.value
    assert e.upgrade["url"].startswith("https://www.kashrock.com/checkout/start")
    assert "utm_source=sdk" in e.upgrade["url"]
    assert "utm_source=sdk" in e.upgrade_url
    assert UPGRADE["message"] in e.message
    assert e.upgrade["url"] in e.message
    # Original fields preserved
    assert e.status == 429
    assert e.body is body


def test_429_legacy_flat_upgrade_url_still_works():
    body = {"detail": "Slow down.", "upgrade_url": "https://www.kashrock.com/pricing"}
    with pytest.raises(KashRockRateLimitError) as exc:
        raise_for_status(429, body)
    assert exc.value.upgrade_url == "https://www.kashrock.com/pricing"
    assert exc.value.upgrade is None


def test_429_without_any_upgrade_info():
    with pytest.raises(KashRockRateLimitError) as exc:
        raise_for_status(429, {"detail": "Slow down."})
    assert exc.value.upgrade_url is None
    assert exc.value.upgrade is None


def test_403_plan_gate_carries_upgrade_object():
    body = {
        "detail": "This endpoint requires the Builder plan or higher.",
        "reason": "not_in_plan",
        "missing": ["v7_board"],
        "upgrade": {
            "message": "This needs Builder. Upgrade takes 60 seconds.",
            "url": "https://www.kashrock.com/checkout/start?plan=builder&utm_source=api&utm_medium=upgrade_prompt&utm_campaign=upgrade&utm_content=plan_gate",
            "plan": "builder",
        },
    }
    with pytest.raises(KashRockPlanError) as exc:
        raise_for_status(403, body)
    e = exc.value
    assert "utm_source=sdk" in e.upgrade_url
    assert "utm_content=plan_gate" in e.upgrade_url
    assert "Upgrade takes 60 seconds." in e.message


def test_403_with_upgrade_but_no_plan_word_still_plan_error():
    body = {"detail": "Denied.", "upgrade": UPGRADE}
    with pytest.raises(KashRockPlanError):
        raise_for_status(403, body)


def test_403_without_upgrade_and_no_plan_word_is_auth_error():
    with pytest.raises(KashRockAuthError):
        raise_for_status(403, {"detail": "Key disabled."})


def test_401_plan_text_is_plan_error():
    with pytest.raises(KashRockPlanError):
        raise_for_status(401, {"detail": "plan trial expired"})


def test_v7_error_envelope_message_and_upgrade():
    body = {
        "error": {
            "message": "v7 board requires Builder.",
            "upgrade": UPGRADE,
        }
    }
    with pytest.raises(KashRockPlanError) as exc:
        raise_for_status(403, body)
    assert "v7 board requires Builder." in exc.value.message
    assert "utm_source=sdk" in exc.value.upgrade_url


def test_normal_errors_unchanged():
    with pytest.raises(KashRockError):
        raise_for_status(500, {"detail": "boom"})
    with pytest.raises(KashRockError):
        raise_for_status(404, {"detail": "not found"})
