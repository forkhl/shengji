from collections import Counter
from rank import get_card_position
from rules import compare_cards


class Move:
    def __init__(self, cards, round):
        self.cards = cards
        self.type = self.get_type(round)

    def get_type(self, round):
        if len(self.cards) == 1:
            return "single"

        if self.is_pair():
            return "pair"

        if self.is_tractor(round):
            return "tractor"

        return "unknown"


    def is_pair(self):
        if len(self.cards) != 2:
            return False

        return (
            self.cards[0].rank == self.cards[1].rank
            and self.cards[0].suit == self.cards[1].suit
        )


    def is_tractor(self, round):
        # Must have at least two pairs
        if len(self.cards) < 4 or len(self.cards) % 2 != 0:
            return False

        # All cards must be same suit
        suits = {card.suit for card in self.cards}

        if len(suits) != 1:
            return False

        # Count pairs
        counts = Counter(card.rank for card in self.cards)

        if any(value != 2 for value in counts.values()):
            return False

        # Get the position of each pair
        positions = []

        for rank in counts:
            card = next(card for card in self.cards if card.rank == rank)
            positions.append(get_card_position(card, round))

        positions.sort()

        # Check consecutive
        for i in range(len(positions) - 1):
            if positions[i + 1] != positions[i] + 1:
                return False

        return True