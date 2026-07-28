from rank import get_card_position
from rules import is_trump

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.team = None

    def sort_hand(self, round):
        self.hand.sort(key=lambda card: self.get_sort_key(card, round))

    def get_sort_key(self, card, round):
        # trumps come first
        if is_trump(card, round):
            return (0, -get_card_position(card, round))

        # non-trumps grouped by suit
        suit_order = {
            "Spades": 0,
            "Hearts": 1,
            "Diamonds": 2,
            "Clubs": 3
        }

        return (
            1,
            suit_order[card.suit],
            -get_card_position(card, round)
        )
