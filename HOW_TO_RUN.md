# Running the web frontend

1. Start the backend server (stdlib only, no installs needed):

   ```
   python server.py
   ```

   This holds the Game/Round/Player objects in memory and serves both the
   API and the static frontend files from `web/`.

2. Open http://127.0.0.1:8765 in a browser.

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
  session, calls your existing `Round`/`Trick`/`Move` methods, and
  serializes state to JSON. Also picks moves for the 3 bot seats by
  brute-force searching combinations of their hand and asking
  `Trick.is_valid_move()` — it never encodes what "legal" means itself.
- `web/app.ts` — typed frontend. Renders whatever `GameState` JSON the
  server sends, lets you select cards, and POSTs your selection back.
  Contains no rules or legality logic.

All legality checks, scoring, and rules live where they already did:
`round.py`, `trick.py`, `move.py`, `rules.py`.
