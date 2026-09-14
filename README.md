# KashRock Python SDK

Official Python client for the [KashRock esports API](https://www.kashrock.com).

Props, odds, matches, live scores, and history — one key, normalized IDs.

## Install

```bash
pip install git+https://github.com/ovitalszn-cyber/kashrock-python.git
```

PyPI `kashrock` is the same package once the first release is published.

## Four lines to a live prop

```python
from kashrock import KashRock

kr = KashRock("YOUR_API_KEY")
print(kr.props("cs2")["props"][0])
```

Get a free Sandbox key at [kashrock.com/pricing](https://www.kashrock.com/pricing). Docs: [kashrock.com/docs](https://www.kashrock.com/docs).

`KASHROCK_API_KEY` works if you do not want the key in code.

## What you can call

```python
kr.me()
kr.props("cs2", book="prizepicks", limit=20)
kr.lines("cs2")
kr.matches("cs2", status="upcoming")
kr.live_games("cs2")
kr.gamelogs("cs2", "zywoo")
kr.history_tape(market_key="kr_mk_…")
```

Same paths as the HTTP API and the [KashRock MCP](https://www.kashrock.com/mcp). Stacks are not included.

Sandbox keys are CS2 props only. Hobby+ unlocks the rest of the board. Builder+ unlocks matches, live, gamelogs, and history.

## License

MIT
