"""The V7 routes: one method per endpoint, reached as ``KashRock(...).v7``.

V7 takes KashRock ids only — ``kr_match_id``, ``kr_tm_*``, ``kr_pl_*``, ``kr_cb_*``, ``kr_prop_*``. A provider or
book id is never accepted. Every method passes extra keyword arguments straight through as query parameters, so a
parameter added to a route works here without an SDK release.

The V6 methods on the client are unchanged and keep working until V6 is sunset on 12 December 2026. See
https://www.kashrock.com/docs/migrate-v6-v7
"""

from __future__ import annotations

from typing import Any, Iterable, Optional, Union

from kashrock._http import Http

Ids = Optional[Union[str, Iterable[str]]]


def _joined(ids: Ids) -> Optional[str]:
    """A single id, or an iterable of them, as the comma list every V7 list parameter takes."""
    if ids is None or isinstance(ids, str):
        return ids
    return ",".join(str(one) for one in ids)


class V7:
    """One method per V7 route. ``sport`` is a short key (``cs2``, ``lol``, …); several routes take ``all``."""

    def __init__(self, http: Http) -> None:
        self._http = http

    def _get(self, path: str, **params: Any) -> Any:
        return self._http.get(path, params)

    def _sport(self, sport: str, suffix: str, **params: Any) -> Any:
        return self._get(f"/v7/{sport}/{suffix}", **params)

    # -- reference -------------------------------------------------------------------------------

    def meta(self, *, include: Optional[str] = None, **params: Any) -> Any:
        """Sports, books, markets, the routes table and your plan. Call this first.

        ``include`` adds ``boards``, ``coverage``, ``teams``, ``tournaments`` or ``changelog``.
        """
        return self._get("/v7/meta", include=include, **params)

    # -- matches ---------------------------------------------------------------------------------

    def matches(
        self,
        sport: str,
        *,
        status: Optional[str] = None,
        date: Optional[str] = None,
        q: Optional[str] = None,
        team: Optional[str] = None,
        ids: Ids = None,
        include: Optional[str] = None,
        limit: Optional[int] = None,
        **params: Any,
    ) -> Any:
        """Fixtures, in-progress and finished matches for one sport, or ``sport="all"``.

        ``ids`` takes one ``kr_match_id`` or up to 100. ``team`` takes a ``kr_tm_`` id, slug or name.
        ``include`` adds ``boxscore``, ``prep``, ``veto``, ``maps``, ``player_board``, ``lines``, ``streams``
        or ``h2h``.
        """
        return self._sport(sport, "matches", status=status, date=date, q=q, team=team,
                           ids=_joined(ids), include=include, limit=limit, **params)

    # -- markets ---------------------------------------------------------------------------------

    def props(
        self,
        sport: str,
        *,
        board: Optional[str] = None,
        view: Optional[str] = None,
        market: Optional[str] = None,
        player: Optional[str] = None,
        book: Optional[str] = None,
        limit: Optional[int] = None,
        **params: Any,
    ) -> Any:
        """Player and combo props across every book.

        ``board`` is ``dfs``, ``main`` or ``all``; ``view`` is ``groups``, ``rows`` or ``both``.
        ``player`` takes a ``kr_pl_`` or ``kr_cb_`` id.
        """
        return self._sport(sport, "props", board=board, view=view, market=market,
                           player=player, book=book, limit=limit, **params)

    def lines(
        self,
        sport: str,
        *,
        market: Optional[str] = None,
        view: Optional[str] = None,
        format: Optional[str] = None,
        include_started: Optional[bool] = None,
        **params: Any,
    ) -> Any:
        """Team and match markets with a KashRock fair price and EV.

        ``view`` is ``consensus`` or ``moneyline``; ``format`` is ``slim`` (default) or ``full``. With no
        ``market`` only the main markets return; round, kill, futures and objective markets need ``market=``.
        """
        return self._sport(sport, "lines", market=market, view=view, format=format,
                           include_started=include_started, **params)

    def parlays(
        self,
        sport: str,
        book: str,
        *,
        ticket: Optional[str] = None,
        market: Optional[str] = None,
        size: Optional[int] = None,
        include: Optional[str] = None,
        limit: Optional[int] = None,
        **params: Any,
    ) -> Any:
        """Price a multi-leg ticket, or discover ranked independent parlays for one ``book``. Hobby+.

        Pass ``ticket`` as comma-separated ``kr_match_id:market:selection`` to price, or omit it to discover
        (``size`` is 2 or 3). Same-match parlays are not supported.
        """
        return self._sport(sport, "parlays", book=book, ticket=ticket, market=market,
                           size=size, include=include, limit=limit, **params)

    def flow(
        self,
        sport: str,
        *,
        kind: Optional[str] = None,
        include: Optional[str] = None,
        limit: Optional[int] = None,
        **params: Any,
    ) -> Any:
        """Money-behind, shift, steam and whale plays. Hobby+.

        ``kind`` is ``all``, ``volume``, ``shift``, ``steam`` or ``whale``. ``include="all"`` keeps
        negative-EV volume.
        """
        return self._sport(sport, "flow", kind=kind, include=include, limit=limit, **params)

    def history(
        self,
        sport: str,
        *,
        kind: Optional[str] = None,
        match: Ids = None,
        prop: Optional[str] = None,
        **params: Any,
    ) -> Any:
        """The quote tape: open, close and every tick per book.

        ``kind`` is ``contract`` or ``lines`` (``props`` aliases ``contract``). ``match`` takes a
        ``kr_match_id``, ``prop`` a ``kr_prop_`` id.
        """
        return self._sport(sport, "history", kind=kind, match=_joined(match), prop=prop, **params)

    def results(
        self,
        sport: str,
        *,
        grade: Optional[str] = None,
        limit: Optional[int] = None,
        **params: Any,
    ) -> Any:
        """Graded bets: hit, miss, push. ``from_`` and ``to`` bound the window (pass as ``**{"from": ...}``)."""
        return self._sport(sport, "results", grade=grade, limit=limit, **params)

    # -- live ------------------------------------------------------------------------------------

    def live(
        self,
        sport: str,
        *,
        game: Optional[str] = None,
        include: Optional[str] = None,
        at: Optional[str] = None,
        **params: Any,
    ) -> Any:
        """Live matches. ``sport="all"`` lists every title in one call.

        ``game`` takes a ``kr_match_id``. ``include`` adds ``boxscore``, ``events``, ``frame``, ``odds``,
        ``odds_history`` or ``streams``.
        """
        return self._sport(sport, "live", game=game, include=include, at=at, **params)

    # -- people ----------------------------------------------------------------------------------

    def players(
        self,
        sport: str,
        *,
        q: Optional[str] = None,
        ids: Ids = None,
        sort: Optional[str] = None,
        include: Optional[str] = None,
        format: Optional[str] = None,
        limit: Optional[int] = None,
        **params: Any,
    ) -> Any:
        """Find a player, look one up, or rank them.

        ``ids`` takes ``kr_pl_`` and ``kr_cb_`` ids, one or up to 100; retired name-hash ids still resolve.
        ``sort="rank"`` ranks them. ``include`` adds ``research``, ``gamelogs``, ``stats`` or ``stats_full``.
        """
        return self._sport(sport, "players", q=q, ids=_joined(ids), sort=sort,
                           include=include, format=format, limit=limit, **params)

    def teams(
        self,
        sport: str,
        *,
        q: Optional[str] = None,
        ids: Ids = None,
        include: Optional[str] = None,
        limit: Optional[int] = None,
        **params: Any,
    ) -> Any:
        """Team research. ``ids`` takes ``kr_tm_`` ids.

        ``include`` adds ``form``, ``roster``, ``maps``, ``h2h``, ``main_lines`` or ``upcoming``.
        """
        return self._sport(sport, "teams", q=q, ids=_joined(ids), include=include, limit=limit, **params)

    # -- breakdown -------------------------------------------------------------------------------

    def breakdown(
        self,
        sport: str,
        *,
        match: Optional[str] = None,
        team: Optional[str] = None,
        team1: Optional[str] = None,
        team2: Optional[str] = None,
        **params: Any,
    ) -> Any:
        """One actionable fact bundle for a match or a team pairing. Builder+.

        ``match`` takes a ``kr_match_id`` or slug; ``team``, ``team1`` and ``team2`` take ``kr_tm_`` ids or names.
        """
        return self._sport(sport, "breakdown", match=match, team=team, team1=team1, team2=team2, **params)

    def breakdown_index(self, sport: str, *, kind: Optional[str] = None, **params: Any) -> Any:
        """The published breakdown pages. Needs no API key."""
        return self._sport(sport, "breakdown/index", kind=kind, **params)

    def breakdown_published(self, sport: str, kind: str, slug: str, **params: Any) -> Any:
        """One published breakdown page. Needs no API key."""
        return self._get(f"/v7/{sport}/breakdown/published/{kind}/{slug}", **params)
