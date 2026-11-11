# Two Worlds — Snoopyland × Penguinland

A cozy two-town browser game starter. Snoopyland is a sunny dog harbor;
Penguinland is a snowy penguin cove. The characters and canvas artwork are
original. The two communities can eventually grow into an interconnected
social adventure, with crafting, festivals, quests and player-run activities.

## Run locally or inside Taiga

Python 3.10 or newer. No pip, npm, API keys or downloaded assets needed.

```sh
python server.py --port 8777
```

Open **http://127.0.0.1:8777** in the browser on the same machine. In Taiga,
use Chrome **inside the Sandbox desktop**. The server's localhost is not
your personal computer's localhost. Keep the terminal/server running.

```sh
python -m unittest discover -s tests -v
```

Default data file: `data/world.sqlite3`. Override with `--db PATH` for an
isolated test world. Progress persists across restarts; browser session
cookies identify characters. Clearing cookies loses access to that character.
Different browser profiles can join as separate neighbors on the same server.

## What is playable now

- Choose an original dog or penguin character and a made-up nickname.
- Click to walk, or use WASD/arrows. E interacts with the nearest resource
  or ferry. Quick-route buttons provide mouse/touch alternatives.
- Gather sunberries and driftwood in Snoopyland; moon ice and driftwood in
  Penguinland. A spot regrows after 12 seconds, independently per player.
- Walk to the sky ferry to travel between maps.
- Inspect your saved backpack; other active players appear in the same town.
- Responsive interface, original procedural world art, and persistent state.

The browser intentionally stops at a small working foundation. The user can
develop the deeper game in Taiga rather than receiving a completed MMO.

## Existing backend building blocks

`game.py` also contains tested service methods for recipes, quest rewards,
timed fishing, resource gifting, room slots, emotes and shared parcel counts.
These are foundations, **not complete player-facing experiences**. The UI
does not yet offer the corresponding activity, workshop, room or quest flows.
The festival card displays saved shared project counters only.

## Natural directions for further development

These are product possibilities, not prewritten submission prompts:

- A fully playable workshop and cross-world delivery loop, with clear
  onboarding, recipe discovery, crafting feedback and festival milestones.
- A fishing experience around the existing server timing challenge, then
  genuinely different skill activities in each town.
- A room-decoration editor with layout choices, previews and saved rooms.
- Mutual player trading with offers, confirmation, cancellation and
  concurrency-safe inventory settlement; gifting is not a trade system.
- Connected quest stories and meaningful progression beyond simple counters.
- Better movement, collisions, animation, maps, environmental interactions,
  accessibility and mobile controls.
- Production multiplayer transport, hosting, moderation, account recovery
  and a real persistence/backup strategy.

Choose work that you actually want to accomplish and define your own scope
and verifiable completion criteria. No defects were deliberately introduced
to manufacture tasks or turns.

## Code map

| File | Responsibility |
| --- | --- |
| `content.py` | World locations, resource nodes, item/recipe/quest definitions |
| `game.py` | SQLite transactions and authoritative action rules |
| `server.py` | Static web assets, JSON API and session cookie |
| `web/art.js` | Original canvas scenery and characters |
| `web/game.js` | Browser rendering, controls, polling and basic panels |
| `web/index.html`, `web/styles.css` | Interface markup and responsive styling |
| `tests/` | Game rules, persistence and HTTP boundary tests |

## API overview

`POST /api/join` takes `{name, species}` and sets an HttpOnly, SameSite
session cookie. `GET /api/state` resumes the session. `POST /api/action`
takes `{action, args}`. The state includes the current player, nearby
active players, world content and shared project progress.

The server verifies movement speed, interaction distance, item costs,
quest eligibility and once-only fishing/quest reward use. SQLite writes
are serialized in transactions, so failed actions roll back.

## Limits

This is a localhost development prototype, not an internet-ready service.
There are no passwords, recovery system, moderation tools, rate limits,
production TLS or backups. It uses polling and a single SQLite database;
it is not a large-scale MMO architecture. Do not expose it to the public
internet without designing and testing those systems. The `--host` option
is for controlled development environments.

Only the open island coordinate bounds are enforced. Buildings and scenery
do not have collision geometry yet. Nicknames are player-chosen and not
globally unique. Resource growth is player-specific; delivery counters are
shared across all characters in that database. Shells are an earned counter,
not a complete spending economy yet. There is no real-money system.

Runtime sessions and player data are local and excluded from source packages.
Do not upload a populated database. MIT licensed; see `LICENSE`.
