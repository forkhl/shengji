# Running the web frontend

1. Start the backend server (stdlib only, no installs needed):

   ```
   python server.py
   ```

   This holds the Game/Round/Player objects in memory and serves both the
   API and the static frontend files from `web/`.

2. Open http://127.0.0.1:8765 in a browser.

## How play works now

All four seats ("Player 1" .. "Player 4") are manually controlled from the
same browser tab -- there are no bots. During calling, players act one at
a time in order (Call or Pass); only the active player's hand is shown and
selectable. During tricks, the same applies: whoever's turn it is has
their hand shown, and the trick reveals one play at a time as each person
acts.

## If you edit web/app.ts

The compiled `web/app.js` is checked in, but if you change `app.ts` you'll
need to recompile:

```
cd web
npx tsc -p tsconfig.json
```

(or `tsc -p tsconfig.json` if you have TypeScript installed globally).
This produces `web/app.js`, which `index.html` loads as a module.

## Architecture

- `server.py` — stdlib `http.server` only (no Flask/FastAPI). Holds the
  session, tracks whose turn it is (`calling_turn_index` during calling;
  `round.current_player`, already tracked by `round.py`, during tricks),
  calls your existing `Round`/`Trick`/`Move` methods, and serializes state
  to JSON. No bot logic exists anymore -- every move is an explicit
  request from the browser on behalf of whichever seat is active.
- `web/app.ts` — typed frontend. Renders whatever `GameState` JSON the
  server sends for the currently active player, lets you select cards,
  and POSTs your selection back. Contains no rules or legality logic.

All legality checks, scoring, and rules live where they already did:
`round.py`, `trick.py`, `move.py`, `rules.py` — none of these were
modified.

### API endpoints

- `GET /api/state` — current state
- `POST /api/new_game`
- `POST /api/calling_action` — `{action: "call", cards: [...]}` or
  `{action: "pass"}`, acts on behalf of whichever player's calling turn it
  is. After all 4 players have acted once, calling finishes automatically
  (same `round.finish_calling()` as before).
- `POST /api/discard_bottom` — `{cards: [...]}`, acts on `round.it_player`
- `POST /api/play_move` — `{cards: [...]}`, acts on `round.current_player`

### Known scoping choice

Calling is a single pass through all 4 players (one call-or-pass turn
each), not repeated bidding rounds after someone overcalls. The
underlying legality of any individual call is still fully decided by
`round.can_call()` in `round.py` — this only affects how many turns the
UI walks through before locking in the highest call made.
