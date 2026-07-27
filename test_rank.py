from card import Card
from rank import get_card_position


class Game:
    level = "7"
    trump_suit = "Heart"


game = Game()


cards = [
    Card("Spade", "6"),
    Card("Spade", "8"),
    Card("Heart", "A"),
    Card("Spade", "7"),
    Card("Heart", "7"),
]


for card in cards:
    print(card, get_card_position(card, game))