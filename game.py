from deck import Deck
from player import Player

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
        self.current_round = None
