from card import Card
from move import Move


class Game:
    level = "7"
    trump_suit = "Heart"


game = Game()


cards = [
    Card("Spade", "6"),
    Card("Spade", "6"),
    Card("Spade", "A"),
    Card("Spade", "A")
]


move = Move(cards, game)

print(move.type)