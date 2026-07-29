class Card:
    def __init__(self, rank, suit):
        self.suit = suit
        self.rank = rank
    def __str__(self):
        return f"{self.rank} of {self.suit}"
    def __repr__(self):
        return f"{self.rank} of {self.suit}"
    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit