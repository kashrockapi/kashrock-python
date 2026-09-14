from __future__ import annotations

import os
from typing import Any, Optional

from kashrock._http import DEFAULT_BASE, Http
from kashrock.errors import KashRockAuthError


class KashRock:
    """Thin client for https://kashrock.up.railway.app."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: str = DEFAULT_BASE,
        timeout: float = 60.0,
    ) -> None:
        key = api_key or os.environ.get("KASHROCK_API_KEY", "")
        if not key:
            raise KashRockAuthError(
                "Pass an API key or set KASHROCK_API_KEY. Get one at https://www.kashrock.com/pricing",
                status=401,
            )
        self._http = Http(key, base_url=base_url, timeout=timeout)

    def _get(self, path: str, **params: Any) -> Any:
        return self._http.get(path, params)

    def _sport(self, sport: str, suffix: str, **params: Any) -> Any:
        return self._get(f"/v6/esports/{sport}/{suffix}", **params)

    def me(self) -> Any:
        return self._get("/v6/me")

    def books(self) -> Any:
        return self._get("/v6/books")

    def props(self, sport: str, **params: Any) -> Any:
        return self._sport(sport, "props", **params)

    def player_props(self, sport: str, **params: Any) -> Any:
        return self._sport(sport, "player-props", **params)

    def media(self, sport: str, **params: Any) -> Any:
        return self._sport(sport, "media", **params)

    def lines(self, sport: str, **params: Any) -> Any:
        return self._sport(sport, "lines", **params)

    def gaps(self, sport: str, **params: Any) -> Any:
        return self._sport(sport, "gaps", **params)

    def coverage(self, sport: str, **params: Any) -> Any:
        params.setdefault("include_props", False)
        return self.props(sport, **params)

    def rankings(self, sport: str, **params: Any) -> Any:
        return self._sport(sport, "rankings", **params)

    def search_players(self, sport: str, q: str, **params: Any) -> Any:
        return self._sport(sport, "players/search", q=q, **params)

    def player(self, sport: str, player_id: str, **params: Any) -> Any:
        return self._sport(sport, f"players/{player_id}", **params)

    def player_stats(self, sport: str, player_id: str, **params: Any) -> Any:
        return self._sport(sport, f"players/{player_id}/stats", **params)

    def player_stats_full(self, sport: str, player_id: str, **params: Any) -> Any:
        return self._sport(sport, f"players/{player_id}/stats/full", **params)

    def gamelogs(self, sport: str, player: str, **params: Any) -> Any:
        return self._sport(sport, f"players/{player}/gamelogs", **params)

    def matches(self, sport: str, **params: Any) -> Any:
        return self._sport(sport, "matches", **params)

    def match(self, sport: str, kr_match_id: str, **params: Any) -> Any:
        return self._sport(sport, f"matches/id/{kr_match_id}", **params)

    def search_matches(self, sport: str, **params: Any) -> Any:
        return self._sport(sport, "matches/search", **params)

    def team_matches(self, sport: str, team: str, **params: Any) -> Any:
        return self._sport(sport, f"teams/{team}/matches", **params)

    def streams(self, sport: str, **params: Any) -> Any:
        return self._sport(sport, "streams", **params)

    def live_games(self, sport: str, **params: Any) -> Any:
        return self._sport(sport, "live/games", **params)

    def live_boxscore(self, sport: str, game_id: str, **params: Any) -> Any:
        return self._sport(sport, f"live/{game_id}/boxscore", **params)

    def live_frames(self, sport: str, game_id: str, **params: Any) -> Any:
        return self._sport(sport, f"live/{game_id}/frames", **params)

    def live_events(self, sport: str, game_id: str, **params: Any) -> Any:
        return self._sport(sport, f"live/{game_id}/events", **params)

    def boxscore(self, sport: str, match_slug: str, **params: Any) -> Any:
        return self._sport(sport, f"matches/{match_slug}/boxscore", **params)

    def boxscores(self, sport: str, **params: Any) -> Any:
        return self._sport(sport, "boxscores", **params)

    def results(self, sport: str, **params: Any) -> Any:
        return self._sport(sport, "results", **params)

    def history_tape(self, **params: Any) -> Any:
        return self._get("/v6/esports/history/contract", **params)

    def team_h2h(self, sport: str, **params: Any) -> Any:
        return self._sport(sport, "teams/h2h", **params)

    def research_board(self, **params: Any) -> Any:
        return self._get("/v6/esports/research/board", **params)

    def research_board_tapes(self, **params: Any) -> Any:
        return self._get("/v6/esports/research/board-tapes", **params)

    def research_player(self, **params: Any) -> Any:
        return self._get("/v6/esports/research/player", **params)

    def match_prep(self, match_slug: str, sport: str = "cs2", **params: Any) -> Any:
        return self._sport(sport, f"matches/{match_slug}/prep", **params)

    def player_board(self, match_slug: str, sport: str = "cs2", **params: Any) -> Any:
        return self._sport(sport, f"matches/{match_slug}/player-board", **params)

    def tournament_maps(self, match_slug: str, sport: str = "cs2", **params: Any) -> Any:
        return self._sport(sport, f"matches/{match_slug}/tournament-maps", **params)
