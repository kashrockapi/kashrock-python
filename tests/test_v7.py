"""The V7 surface: every method hits the right path with the right query, and a V7 refusal maps to the right error.

Runs against a local stub, so it proves URL construction and error handling with no network and no API key.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any, Dict, List, Optional, Tuple

import pytest

from kashrock import KashRock, KashRockPlanError, KashRockRateLimitError, V7


def _stub(canned: Optional[Tuple[int, Dict[str, Any]]] = None):
    """A server that records every request line and echoes it back, or serves one canned refusal."""
    seen: List[str] = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler's name
            seen.append(self.path)
            status, body = canned or (200, {"available": True, "url": self.path})
            payload = json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *_args: Any) -> None:
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    Thread(target=server.serve_forever, daemon=True).start()
    client = KashRock("kr_test_key", base_url="http://127.0.0.1:%d" % server.server_port)
    return client, seen, server


@pytest.fixture(name="stub")
def _stub_fixture():
    client, seen, server = _stub()
    yield client, seen
    server.shutdown()


def test_v7_is_attached(stub) -> None:
    client, _ = stub
    assert isinstance(client.v7, V7)


def test_every_v7_route_builds_its_documented_path(stub) -> None:
    client, seen = stub
    v7 = client.v7
    v7.meta(include="books")
    v7.matches("cs2", status="upcoming", limit=2)
    v7.props("lol", board="all", view="rows")
    v7.lines("cs2", view="consensus", format="full")
    v7.parlays("cs2", "thunderpick", size=2)
    v7.flow("cs2", kind="steam")
    v7.live("all", include="boxscore")
    v7.players("cs2", sort="rank", include="stats")
    v7.teams("cs2", include="form")
    v7.history("cs2", kind="lines", match="kr_cs2_a-vs-b-13-10-2026")
    v7.results("cs2", grade="hit")
    v7.breakdown("cs2", team="vitality")
    v7.breakdown_index("cs2", kind="match")
    v7.breakdown_published("cs2", "match", "a-vs-b-13-10-2026")

    assert seen == [
        "/v7/meta?include=books",
        "/v7/cs2/matches?status=upcoming&limit=2",
        "/v7/lol/props?board=all&view=rows",
        "/v7/cs2/lines?view=consensus&format=full",
        "/v7/cs2/parlays?book=thunderpick&size=2",
        "/v7/cs2/flow?kind=steam",
        "/v7/all/live?include=boxscore",
        "/v7/cs2/players?sort=rank&include=stats",
        "/v7/cs2/teams?include=form",
        "/v7/cs2/history?kind=lines&match=kr_cs2_a-vs-b-13-10-2026",
        "/v7/cs2/results?grade=hit",
        "/v7/cs2/breakdown?team=vitality",
        "/v7/cs2/breakdown/index?kind=match",
        "/v7/cs2/breakdown/published/match/a-vs-b-13-10-2026",
    ]


def test_ids_takes_one_id_or_a_list_and_sends_a_comma_list(stub) -> None:
    client, seen = stub
    client.v7.matches("cs2", ids="kr_cs2_a-vs-b-13-10-2026")
    client.v7.matches("cs2", ids=["kr_cs2_a-vs-b-13-10-2026", "kr_cs2_c-vs-d-13-10-2026"])
    client.v7.players("cs2", ids=["kr_pl_33863a5e1393", "kr_cb_000000000000"])
    assert seen == [
        "/v7/cs2/matches?ids=kr_cs2_a-vs-b-13-10-2026",
        "/v7/cs2/matches?ids=kr_cs2_a-vs-b-13-10-2026%2Ckr_cs2_c-vs-d-13-10-2026",
        "/v7/cs2/players?ids=kr_pl_33863a5e1393%2Ckr_cb_000000000000",
    ]


def test_an_unset_parameter_is_not_sent(stub) -> None:
    client, seen = stub
    client.v7.matches("cs2")
    client.v7.lines("cs2")
    assert seen == ["/v7/cs2/matches", "/v7/cs2/lines"]


def test_the_v6_methods_still_call_v6(stub) -> None:
    client, seen = stub
    client.props("cs2")
    client.live_games("cs2")
    assert all(path.startswith("/v6/") for path in seen), seen


def test_a_v7_plan_refusal_raises_the_plan_error() -> None:
    body = {
        "error": {
            "code": "plan_required",
            "message": "Consensus lines and live odds require Hobby plan or higher.",
            "status": 403,
            "current_plan": "sandbox",
            "required_plan": "hobby",
            "upgrade_url": "https://www.kashrock.com/pricing",
        }
    }
    client, _, server = _stub((403, body))
    try:
        with pytest.raises(KashRockPlanError) as caught:
            client.v7.lines("cs2")
        assert caught.value.args[0] == "Consensus lines and live odds require Hobby plan or higher."
        assert caught.value.status == 403
    finally:
        server.shutdown()


def test_a_v7_quota_refusal_raises_the_rate_limit_error() -> None:
    body = {"error": {"code": "quota_exceeded", "message": "Daily quota used up.", "status": 429}}
    client, _, server = _stub((429, body))
    try:
        with pytest.raises(KashRockRateLimitError) as caught:
            client.v7.props("cs2")
        assert caught.value.args[0] == "Daily quota used up."
    finally:
        server.shutdown()


def test_a_v6_flat_detail_refusal_still_works() -> None:
    client, _, server = _stub((401, {"detail": "API key required."}))
    try:
        with pytest.raises(Exception) as caught:
            client.props("cs2")
        assert caught.value.args[0] == "API key required."
    finally:
        server.shutdown()
