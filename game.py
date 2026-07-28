from deck import Deck
from player import Player
from team import Team

players = [
    Player("p1"),
    Player("p2"),
    Player("p3"),
    Player("p4")
]

class Game:
    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.teams = [
            Team([players[0], players[2]]),
            Team([players[1], players[3]])
        ]
        self.current_round = None

    def start_round(self):
        pass

