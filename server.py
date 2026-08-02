"""
Minimal local HTTP server for Sheng Ji.

Stdlib only -- no Flask/FastAPI. This file contains NO game rules. It only:
  - holds a Game / Round instance
  - calls existing backend methods (make_call, finish_calling, pick_up_bottom,
    discard_bottom, start_trick, play_move) and reports what they return
  - tracks whose turn it is to act next (calling_turn_index during calling;
    round.current_player, already tracked by round.py, during tricks) and
    exposes only that one player's hand at a time
  - serializes Round/Trick/Move state to JSON for the browser and reads
    JSON card selections back into Card(rank, suit) objects (Card has
    __eq__ by rank+suit, so these compare correctly against hand cards
    without needing to be the exact same object)

All four seats are manually controlled from the browser -- there are no
bots. Every call, discard, and play is a distinct request the frontend
makes on behalf of whichever player is currently active, which is what
gives the "reveal one player at a time" behavior for free.

Run with:
    python server.py
then open http://127.0.0.1:8765 in a browser.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from card import Card
from game import Game
from move import Move
from player import Player

PLAYER_NAMES = ["Player 1", "Player 2", "Player 3", "Player 4"]
PORT = 8765
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")


class GameSession:
    def __init__(self):
        self.players = [Player(name) for name in PLAYER_NAMES]
        self.game = Game(self.players)
        self.round = None
        self.phase = None
        self.message = ""
        self.last_round_summary = None

        # Index into self.players for whose turn it is to call/pass during
        # the calling phase. round.py has no turn concept during calling
        # (any player can call() at any time) -- this index exists only to
        # sequence "ask each player once, in order" for the UI. It never
        # affects what calls are legal; round.can_call() alone decides that.
        self.calling_turn_index = 0

        self.new_game()

    # ---------------- actions (called from HTTP handlers) ----------------

    def new_game(self):
        self.game.start_round()
        self.round = self.game.current_round
        self.phase = "calling"
        self.calling_turn_index = 0
        self.message = f"{self._active_player().name}'s turn to call or pass."
        self.last_round_summary = None

    def calling_action(self, action, cards):
        """
        One player's turn during calling: either call() with some cards, or
        pass. Advances to the next player afterwards. After all 4 players
        have had a turn, automatically finishes calling (same as the old
        "Finish Calling" button) and moves into discard/trick phase.
        """
        player = self._active_player()

        if action == "call":
            ok = self.round.make_call(player, cards)
            if not ok:
                self.message = f"That's not a legal call for {player.name}."
                return  # same player's turn again; do not advance
            self.message = f"{player.name} called."
        else:
            self.message = f"{player.name} passed."

        self.calling_turn_index += 1

        if self.calling_turn_index >= len(self.players):
            self._finish_calling()
        else:
            self.message += f" {self._active_player().name}'s turn."

    def discard_bottom(self, cards):
        needed = len(self.round.bottom_cards)

        if len(cards) != needed:
            self.message = f"Select exactly {needed} cards."
            return

        ok = self.round.discard_bottom(cards)

        if not ok:
            self.message = "Could not bury those cards."
            return

        self._begin_trick(self.round.it_player)

    def play_move(self, cards):
        player = self.round.current_player
        move = Move(cards, self.round)
        old_round = self.round

        ok = self.round.play_move(player, move)

        if not ok:
            self.message = "That's not a legal move."
            return

        self._after_move(old_round)

    # ---------------- internal orchestration ----------------

    def _active_player(self):
        if self.phase == "calling":
            return self.players[self.calling_turn_index]
        if self.phase == "discard":
            return self.round.it_player
        if self.phase == "trick":
            return self.round.current_player
        return None

    def _finish_calling(self):
        called = self.round.finish_calling()

        if called:
            self.round.pick_up_bottom()
            it = self.round.it_player
            it.sort_hand(self.round)
            self.phase = "discard"
            self.message = (
                f"{it.name} won the call and picked up the bottom. "
                f"Select exactly {len(self.round.bottom_cards)} cards to bury."
            )
        else:
            self.message = "No one called. Playing with no trump suit."
            self._begin_trick(self.players[0])

    def _begin_trick(self, lead_player):
        self.round.start_trick(lead_player)
        self.phase = "trick"
        self.message = f"{lead_player.name} leads."

    def _after_move(self, old_round):
        if self.game.current_round is not old_round:
            self._record_round_summary(old_round)
            return

        self.round = self.game.current_round

        if self.round.current_trick is None:
            self.message = "Trick complete."
        else:
            self.message = f"{self.round.current_player.name}'s turn."

    def _record_round_summary(self, finished_round):
        self.last_round_summary = {
            "attackerPoints": finished_round.attacker_points,
            "defendingLevel": finished_round.defending_team.level,
            "attackingLevel": finished_round.attacking_team.level,
        }
        self.round = self.game.current_round
        self.phase = "calling"
        self.calling_turn_index = 0
        self.message = (
            f"New round. {self._active_player().name}'s turn to call or pass."
        )

    # ---------------- serialization ----------------

    def _card_json(self, card):
        return {"rank": card.rank, "suit": card.suit}

    def state(self):
        current_call = None
        if self.round.current_call is not None:
            caller, cards = self.round.current_call
            current_call = {
                "callerName": caller.name,
                "cards": [self._card_json(c) for c in cards],
            }

        current_trick = None
        if self.round.current_trick is not None:
            current_trick = [
                {"playerName": p.name, "cards": [self._card_json(c) for c in m.cards]}
                for p, m in self.round.current_trick.moves
            ]

        active = self._active_player()

        return {
            "phase": self.phase,
            "level": self.round.level,
            "trumpSuit": self.round.trump_suit,
            "attackerPoints": self.round.attacker_points,
            "activePlayerName": active.name if active else None,
            "activeHand": [self._card_json(c) for c in active.hand] if active else [],
            "handSizes": [{"name": p.name, "count": len(p.hand)} for p in self.players],
            "currentCall": current_call,
            "bottomCount": len(self.round.bottom_cards),
            "currentTrick": current_trick,
            "message": self.message,
            "lastRoundSummary": self.last_round_summary,
        }


def cards_from_json(data):
    return [Card(c["rank"], c["suit"]) for c in data]


session = GameSession()


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path, content_type):
        try:
            with open(path, "rb") as f:
                body = f.read()
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def do_GET(self):
        path = urlparse(self.path).path

        routes = {
            "/": ("index.html", "text/html"),
            "/index.html": ("index.html", "text/html"),
            "/app.js": ("app.js", "application/javascript"),
            "/style.css": ("style.css", "text/css"),
        }

        if path == "/api/state":
            self._send_json(session.state())
            return

        if path in routes:
            filename, content_type = routes[path]
            self._send_file(os.path.join(WEB_DIR, filename), content_type)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_json_body()

        if path == "/api/new_game":
            session.new_game()
            self._send_json(session.state())
            return

        if path == "/api/calling_action":
            action = body.get("action")
            cards = cards_from_json(body.get("cards", []))
            session.calling_action(action, cards)
            self._send_json(session.state())
            return

        if path == "/api/discard_bottom":
            session.discard_bottom(cards_from_json(body.get("cards", [])))
            self._send_json(session.state())
            return

        if path == "/api/play_move":
            session.play_move(cards_from_json(body.get("cards", [])))
            self._send_json(session.state())
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        pass  # quiet by default; comment out to see request logs


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Serving Sheng Ji on http://127.0.0.1:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
