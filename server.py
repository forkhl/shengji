"""
Minimal local HTTP server for Sheng Ji.

Stdlib only -- no Flask/FastAPI. This file contains NO game rules. It only:
  - holds a Game / Round instance
  - calls existing backend methods (make_call, finish_calling, pick_up_bottom,
    discard_bottom, start_trick, play_move) and reports what they return
  - for the 3 bot seats, brute-force searches combinations of a bot's hand
    and asks Trick.is_valid_move() whether each one is legal -- it never
    encodes what "legal" means itself
  - serializes Round/Trick/Move state to JSON for the browser and reads
    JSON card selections back into Card(rank, suit) objects (Card now has
    __eq__ by rank+suit, so these compare correctly against hand cards
    without needing to be the exact same object)

Run with:
    python server.py
then open http://127.0.0.1:8765 in a browser.
"""

import json
import os
import random
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from itertools import combinations
from urllib.parse import urlparse

from card import Card
from game import Game
from move import Move
from player import Player

PLAYER_NAMES = ["You", "Bot 1", "Bot 2", "Bot 3"]
PORT = 8765
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")


class GameSession:
    def __init__(self):
        self.players = [Player(name) for name in PLAYER_NAMES]
        self.human = self.players[0]
        self.game = Game(self.players)
        self.round = None
        self.phase = None
        self.message = ""
        self.last_round_summary = None
        self.new_game()

    # ---------------- actions (called from HTTP handlers) ----------------

    def new_game(self):
        self.game.start_round()
        self.round = self.game.current_round
        self.phase = "calling"
        self.message = "Calling phase: select level cards and call, or finish calling."
        self.last_round_summary = None

    def make_call(self, cards):
        ok = self.round.make_call(self.human, cards)
        self.message = "Call made." if ok else "That's not a legal call."

    def finish_calling(self):
        called = self.round.finish_calling()

        if called:
            self.round.pick_up_bottom()

            if self.round.it_player is self.human:
                self.human.sort_hand(self.round)
                self.phase = "discard"
                self.message = f"Select exactly {len(self.round.bottom_cards)} cards to bury."
            else:
                # Bots never call in this version, so this is a placeholder
                # for when they do -- bury arbitrary cards so play continues.
                it = self.round.it_player
                self.round.discard_bottom(it.hand[: len(self.round.bottom_cards)])
                self._begin_trick(it)
        else:
            self.message = "No one called. Playing with no trump suit."
            self._begin_trick(self.human)

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
        move = Move(cards, self.round)
        old_round = self.round

        ok = self.round.play_move(self.human, move)

        if not ok:
            self.message = "That's not a legal move."
            return

        self.message = ""
        self._after_move(old_round)

    # ---------------- internal orchestration ----------------

    def _begin_trick(self, lead_player):
        self.round.start_trick(lead_player)
        self.phase = "trick"
        self.message = f"{lead_player.name} leads."
        self._run_bots_until_human_or_round_end()

    def _after_move(self, old_round):
        if self.game.current_round is not old_round:
            self._record_round_summary(old_round)
            return

        self.round = self.game.current_round

        if self.round.current_trick is None:
            self.message = "Trick complete."

        self._run_bots_until_human_or_round_end()

    def _run_bots_until_human_or_round_end(self):
        while True:
            if self.round.current_trick is None:
                return

            current = self.round.current_player

            if current is None or current is self.human:
                return

            move = self._pick_bot_move(current)

            if move is None:
                self.message = f"{current.name} has no legal move -- stuck."
                return

            old_round = self.round
            self.round.play_move(current, move)

            if self.game.current_round is not old_round:
                self._record_round_summary(old_round)
                return

            self.round = self.game.current_round

    def _record_round_summary(self, finished_round):
        self.last_round_summary = {
            "attackerPoints": finished_round.attacker_points,
            "defendingLevel": finished_round.defending_team.level,
            "attackingLevel": finished_round.attacking_team.level,
        }
        self.round = self.game.current_round
        self.phase = "calling"
        self.message = "New round. Calling phase."

    def _pick_bot_move(self, player):
        """
        Brute-force search over combinations of the bot's hand, asking the
        backend (Move.type / Trick.is_valid_move) whether each candidate is
        legal. Encodes no Sheng Ji rule itself.
        """
        trick = self.round.current_trick

        if trick.lead_move is None:
            cards = player.hand[:]
            random.shuffle(cards)
            for card in cards:
                move = Move([card], self.round)
                if move.type != "unknown":
                    return move
            return None

        needed = len(trick.lead_move.cards)
        cards = player.hand[:]
        random.shuffle(cards)

        for chosen in combinations(cards, needed):
            move = Move(list(chosen), self.round)
            if trick.is_valid_move(player, move):
                return move

        return None

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

        current_player_name = None
        if self.round.current_player is not None:
            current_player_name = self.round.current_player.name

        return {
            "phase": self.phase,
            "level": self.round.level,
            "trumpSuit": self.round.trump_suit,
            "attackerPoints": self.round.attacker_points,
            "humanHand": [self._card_json(c) for c in self.human.hand],
            "handSizes": [{"name": p.name, "count": len(p.hand)} for p in self.players],
            "currentCall": current_call,
            "bottomCount": len(self.round.bottom_cards),
            "currentTrick": current_trick,
            "currentPlayerName": current_player_name,
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

        if path == "/api/make_call":
            session.make_call(cards_from_json(body.get("cards", [])))
            self._send_json(session.state())
            return

        if path == "/api/finish_calling":
            session.finish_calling()
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
